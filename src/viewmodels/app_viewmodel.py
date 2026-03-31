"""Application-level ViewModel – orchestrates core services and sub-VMs."""

import os
import subprocess
import tempfile
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer

from core.config_manager import FullConfig
from core.batch_generator import BatchGenerator
from core.clipboard_monitor import ClipboardMonitor
from .session_viewmodel import SessionViewModel
from .download_viewmodel import DownloadViewModel
from .url_list_model import UrlListModel


class AppViewModel(QObject):
    """Top-level ViewModel exposed to QML as ``appVM``."""

    # ── Signals ─────────────────────────────────────────────────────
    commandPreviewChanged = Signal()
    floatingPanelVisibleChanged = Signal()
    clipboardMonitoringChanged = Signal()
    tdlStatusChanged = Signal()
    notificationRequested = Signal(str, str, str)  # title, message, severity

    def __init__(
        self,
        session_vm: SessionViewModel,
        download_vm: DownloadViewModel,
        url_model: UrlListModel,
        parent=None,
    ):
        super().__init__(parent)
        self._session_vm = session_vm
        self._download_vm = download_vm
        self._url_model = url_model

        # Internal state
        self._command_preview = ""
        self._floating_panel_visible = True
        self._clipboard_monitoring = True
        self._tdl_status = ""  # "ready" | "no_tdl" | "not_logged_in"

        # Core services
        self._batch = BatchGenerator()
        self._clipboard = ClipboardMonitor()

        # Wiring
        self._clipboard.new_urls_detected.connect(self._on_new_urls)
        self._url_model.urlsChanged.connect(self._sync_clipboard_urls)

        # Debounced preview update
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(300)
        self._preview_timer.timeout.connect(self._do_update_preview)

        # Connect config changes to auto-preview
        self._session_vm.configChanged.connect(self.schedulePreviewUpdate)
        self._download_vm.configChanged.connect(self.schedulePreviewUpdate)
        self._url_model.urlsChanged.connect(self.schedulePreviewUpdate)

        # Start clipboard monitor
        self._clipboard.start()

        # Initial tdl check
        self._check_tdl_status()

    # ── Config builder ──────────────────────────────────────────────

    def _build_config(self) -> FullConfig:
        session = self._session_vm.get_config()
        download = self._download_vm.get_config()
        download.urls = self._url_model.get_urls()
        return FullConfig(session=session, download=download)

    # ── Preview ─────────────────────────────────────────────────────

    @Slot()
    def schedulePreviewUpdate(self):
        self._preview_timer.start()

    def _do_update_preview(self):
        try:
            config = self._build_config()
            preview = self._batch.get_preview_command(config)
        except Exception as e:
            preview = f"Error: {e}"
        if self._command_preview != preview:
            self._command_preview = preview
            self.commandPreviewChanged.emit()

    # ── Batch generation ────────────────────────────────────────────

    @Slot(result=bool)
    def generateBatch(self) -> bool:
        config = self._build_config()
        ok, msg = self._batch.generate_batch(config)
        self.notificationRequested.emit(
            "生成批处理", msg, "success" if ok else "error"
        )
        return ok

    @Slot()
    def executeBatch(self):
        config = self._build_config()
        ok, msg = self._batch.generate_batch(config, auto_close=True)
        if ok:
            subprocess.Popen(
                ["cmd", "/c", "start", "", "telegram_downloader.bat"],
                shell=True,
            )
            self._url_model.clear()
            self.notificationRequested.emit("执行", "下载已启动", "success")
        else:
            self.notificationRequested.emit("执行", msg, "error")

    # ── Login ───────────────────────────────────────────────────────

    @Slot(str, result=bool)
    def login(self, telegram_path: str) -> bool:
        valid, msg = self._batch.validate_telegram_path(telegram_path)
        if not valid:
            self.notificationRequested.emit("登录", msg, "error")
            return False
        login_args = self._batch.get_login_command(telegram_path)
        bat = "@echo off\nchcp 65001 >nul\ntitle Telegram Login\n"
        bat += " ".join(str(a) for a in login_args) + "\npause\n"
        bat_path = os.path.join(tempfile.gettempdir(), "tdl_login.bat")
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat)
        subprocess.Popen(["cmd", "/c", "start", "", bat_path], shell=True)
        return True

    @Slot(result=bool)
    def verifyLogin(self) -> bool:
        ok, _ = self._batch.check_login_status()
        self._tdl_status = "ready" if ok else "not_logged_in"
        self.tdlStatusChanged.emit()
        return ok

    @Slot()
    def recheckTdl(self):
        self._check_tdl_status()

    @Slot(result=int)
    def importFromClipboard(self) -> int:
        """Read clipboard text and add any Telegram URLs found."""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            return self._url_model.addUrlsFromText(text)
        return 0

    # ── Floating panel ──────────────────────────────────────────────

    @Slot()
    def toggleFloatingPanel(self):
        self._floating_panel_visible = not self._floating_panel_visible
        self.floatingPanelVisibleChanged.emit()

    # ── Clipboard ───────────────────────────────────────────────────

    def _on_new_urls(self, urls: list):
        for url in urls:
            self._url_model.addUrl(url)
        if urls:
            n = len(urls)
            self.notificationRequested.emit(
                "剪贴板",
                f"检测到 {n} 个新链接",
                "info",
            )

    def _sync_clipboard_urls(self):
        self._clipboard.sync_known_urls(self._url_model.get_urls())

    # ── Internal ────────────────────────────────────────────────────

    def _check_tdl_status(self):
        ok_exe, _ = self._batch.validate_tdl_executable()
        if not ok_exe:
            self._tdl_status = "no_tdl"
        else:
            ok_login, _ = self._batch.check_login_status()
            self._tdl_status = "ready" if ok_login else "not_logged_in"
        self.tdlStatusChanged.emit()

    # ── QML Properties ──────────────────────────────────────────────

    def _get_commandPreview(self):
        return self._command_preview
    commandPreview = Property(str, _get_commandPreview, notify=commandPreviewChanged)

    def _get_floatingPanelVisible(self):
        return self._floating_panel_visible
    def _set_floatingPanelVisible(self, v):
        if self._floating_panel_visible != v:
            self._floating_panel_visible = v
            self.floatingPanelVisibleChanged.emit()
    floatingPanelVisible = Property(bool, _get_floatingPanelVisible, _set_floatingPanelVisible, notify=floatingPanelVisibleChanged)

    def _get_clipboardMonitoring(self):
        return self._clipboard_monitoring
    def _set_clipboardMonitoring(self, v):
        if self._clipboard_monitoring != v:
            self._clipboard_monitoring = v
            if v:
                self._clipboard.start()
            else:
                self._clipboard.stop()
            self.clipboardMonitoringChanged.emit()
    clipboardMonitoring = Property(bool, _get_clipboardMonitoring, _set_clipboardMonitoring, notify=clipboardMonitoringChanged)

    def _get_tdlStatus(self):
        return self._tdl_status
    tdlStatus = Property(str, _get_tdlStatus, notify=tdlStatusChanged)
