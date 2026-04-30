"""Application-level ViewModel – orchestrates core services and sub-VMs."""

import io
import json
import math
import os
import struct
import subprocess
import tempfile
import threading
import time
import wave
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer

from core.config_manager import FullConfig
from core.batch_generator import BatchGenerator
from core.clipboard_monitor import ClipboardMonitor
from core.task_history import TaskHistoryManager, STATUS_COMPLETED, STATUS_PARTIAL, STATUS_FAILED
from core.download_tracker import (
    fetch_expected_files, snapshot_directory, get_new_files, find_failed_urls
)
from .session_viewmodel import SessionViewModel
from .download_viewmodel import DownloadViewModel
from .export_viewmodel import ExportViewModel
from .queue_viewmodel import QueueViewModel
from .url_list_model import UrlListModel
from .history_viewmodel import HistoryViewModel


class AppViewModel(QObject):
    """Top-level ViewModel exposed to QML as ``appVM``."""

    # ── Signals ─────────────────────────────────────────────────────
    commandPreviewChanged = Signal()
    exportCommandPreviewChanged = Signal()
    floatingPanelVisibleChanged = Signal()
    clipboardMonitoringChanged = Signal()
    tdlStatusChanged = Signal()
    notificationRequested = Signal(str, str, str)  # title, message, severity
    # ── Download-tracking signals ─────────────────────────────
    isDownloadingChanged   = Signal()            # bool property changed
    exportProgressChanged  = Signal(int, int)    # (done_chats, total_chats)
    exportResultReady      = Signal(list)        # list of {id,file} dicts
    downloadFinished       = Signal(str, int, int, str)  # status, downloaded, expected, failed_urls_json
    def __init__(
        self,
        session_vm: SessionViewModel,
        download_vm: DownloadViewModel,
        export_vm: ExportViewModel,
        queue_vm: QueueViewModel,
        url_model: UrlListModel,
        parent=None,
    ):
        super().__init__(parent)
        self._session_vm = session_vm
        self._download_vm = download_vm
        self._export_vm = export_vm
        self._queue_vm = queue_vm
        self._url_model = url_model

        # Internal state
        self._command_preview = ""
        self._floating_panel_visible = True
        self._clipboard_monitoring = True
        self._tdl_status = ""  # "ready" | "no_tdl" | "not_logged_in"
        self._last_alert_sound_at = 0.0
        self._alert_sound_data = self._build_alert_sound_data()

        # Internal state – export preview
        self._export_command_preview = ""

        # Internal state – download tracking
        self._is_downloading  = False
        self._confirm_event: threading.Event = None   # set when user confirms/cancels
        self._confirm_result  = False                 # True = confirmed, False = cancelled

        # Task history (persist-queue backed)
        data_dir = os.path.join(os.getcwd(), ".tdl_data")
        self._history_mgr = TaskHistoryManager(data_dir)
        self.history_vm   = HistoryViewModel(self._history_mgr, parent=self)
        self.history_vm.retryRequested.connect(self._on_retry_requested)

        # Core services
        self._batch = BatchGenerator()
        self._clipboard = ClipboardMonitor()

        # Wiring
        self._clipboard.new_urls_detected.connect(self._on_new_urls)
        self._url_model.urlsChanged.connect(self._sync_clipboard_urls)

        # Debounced download preview update
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(300)
        self._preview_timer.timeout.connect(self._do_update_preview)

        # Debounced export preview update
        self._export_preview_timer = QTimer(self)
        self._export_preview_timer.setSingleShot(True)
        self._export_preview_timer.setInterval(300)
        self._export_preview_timer.timeout.connect(self._do_update_export_preview)

        # Connect config changes to auto-preview
        self._session_vm.configChanged.connect(self.schedulePreviewUpdate)
        self._download_vm.configChanged.connect(self.schedulePreviewUpdate)
        self._url_model.urlsChanged.connect(self.schedulePreviewUpdate)

        # Connect export config changes to export preview
        self._session_vm.configChanged.connect(self._schedule_export_preview_update)
        self._export_vm.configChanged.connect(self._schedule_export_preview_update)

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

    # ── Export Preview ───────────────────────────────────────────────

    def _schedule_export_preview_update(self):
        self._export_preview_timer.start()

    def _do_update_export_preview(self):
        try:
            export_cfg = self._export_vm.get_config()
            session_cfg = self._session_vm.get_config()
            preview = self._batch.get_export_preview_command(export_cfg, session_cfg)
        except Exception as e:
            preview = f"Error: {e}"
        if self._export_command_preview != preview:
            self._export_command_preview = preview
            self.exportCommandPreviewChanged.emit()

    def _get_export_command_preview(self):
        return self._export_command_preview

    exportCommandPreview = Property(
        str, _get_export_command_preview, notify=exportCommandPreviewChanged
    )

    # ── Export batch generation ──────────────────────────────────────

    @Slot(result=bool)
    def generateExportBatch(self) -> bool:
        export_cfg = self._export_vm.get_config()
        session_cfg = self._session_vm.get_config()
        ok, msg = self._batch.generate_export_batch(export_cfg, session_cfg)
        self.notificationRequested.emit(
            "生成导出批处理", msg, "success" if ok else "error"
        )
        return ok

    @Slot()
    def executeExportBatch(self):
        export_cfg = self._export_vm.get_config()
        session_cfg = self._session_vm.get_config()
        ok, msg = self._batch.generate_export_batch(export_cfg, session_cfg, auto_close=True)
        if ok:
            import subprocess
            subprocess.Popen(
                ["cmd", "/c", "start", "", "tdl_export.bat"],
                shell=True,
            )
            self.notificationRequested.emit("导出", "导出任务已启动", "success")
        else:
            self.notificationRequested.emit("导出", msg, "error")

    # ── Queue ────────────────────────────────────────────────────────

    @Slot(str, result=str)
    def exportToQueue(self, name: str) -> str:
        """Save current URL list as a named queue JSON.  Returns "" on success
        or an error message string on failure."""
        from core.queue_manager import save_queue, queue_name_exists
        name = name.strip()
        if not name:
            return "队列名称不能为空"
        urls = self._url_model.get_urls()
        if not urls:
            return "链接列表为空，请先添加链接"
        queue_dir = self._queue_vm.queueDir
        if queue_name_exists(name, queue_dir):
            return f"队列「{name}」已存在，请换一个名称"
        ok, msg = save_queue(name, urls, queue_dir)
        if ok:
            self._url_model.clear()
            self._queue_vm.refreshQueues()
            self.notificationRequested.emit("导出队列", msg, "success")
            return ""
        self.notificationRequested.emit("导出队列", msg, "error")
        return msg

    @Slot(result=bool)
    def generateQueueBatch(self) -> bool:
        from core.queue_manager import list_queues
        queues = list_queues(self._queue_vm.queueDir)
        session_cfg = self._session_vm.get_config()
        ok, msg = self._batch.generate_queue_batch(
            queues, self._queue_vm.outputDir, session_cfg, auto_close=False
        )
        self.notificationRequested.emit(
            "生成队列批处理", msg, "success" if ok else "error"
        )
        return ok

    @Slot()
    def executeQueueBatch(self):
        from core.queue_manager import list_queues
        queues = list_queues(self._queue_vm.queueDir)
        session_cfg = self._session_vm.get_config()
        ok, msg = self._batch.generate_queue_batch(
            queues, self._queue_vm.outputDir, session_cfg, auto_close=True
        )
        if ok:
            subprocess.Popen(
                ["cmd", "/c", "start", "", "tdl_queue.bat"],
                shell=True,
            )
            self.notificationRequested.emit("队列下载", f"已启动 {len(queues)} 个队列的下载", "success")
        else:
            self.notificationRequested.emit("队列下载", msg, "error")

    # ── isDownloading property ──────────────────────────────────────

    def _get_is_downloading(self) -> bool:
        return self._is_downloading

    isDownloading = Property(bool, _get_is_downloading, notify=isDownloadingChanged)

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
        """Smart execute: export → confirm dialog → download → verify → history."""
        if self._is_downloading:
            self.notificationRequested.emit("下载", "已有下载任务正在进行中", "warning")
            return

        config = self._build_config()
        ok, msg = self._batch.generate_batch(config, auto_close=True)
        if not ok:
            self.notificationRequested.emit("执行", msg, "error")
            return

        urls = self._url_model.get_urls()
        download_dir = config.download.directory
        if config.download.subfolder_enabled and config.download.subfolder.strip():
            download_dir = os.path.join(download_dir, config.download.subfolder.strip())

        # Gather session args for chat export
        session_args = self._build_session_export_args(config)

        self._start_tracked_download(urls, download_dir, session_args)

    def _build_session_export_args(self, config: FullConfig) -> list:
        """Extract session-related CLI flags for use in tdl chat export."""
        args = []
        if config.session.basic_settings_enabled:
            args += ["-n", config.session.namespace]
        if config.session.network_settings_enabled:
            if config.session.proxy.strip():
                args += ["--proxy", config.session.proxy]
        if config.session.storage_settings_enabled:
            storage = f"type={config.session.storage_type},path={config.session.storage_path}"
            args += ["--storage", storage]
        return args

    def _start_tracked_download(self, urls: list, download_dir: str, session_args: list):
        """Launch the full tracking flow in a background thread."""
        self._is_downloading = True
        self.isDownloadingChanged.emit()

        # Prepare confirm event
        self._confirm_event = threading.Event()
        self._confirm_result = False

        tdl_path = str(self._batch.tdl_path)
        batch_path = str(self._batch.current_dir / self._batch.batch_filename)

        def _worker():
            # ── Step 1: Create task record ──────────────────────────
            task = self._history_mgr.begin_task(urls, download_dir)

            # ── Step 2: Fetch expected file list via chat export ────
            def _progress(done, total):
                self.exportProgressChanged.emit(done, total)

            expected = fetch_expected_files(urls, tdl_path, session_args, _progress)
            task.expected_files = expected
            task.expected_count = len(expected)
            self.exportResultReady.emit(expected)   # → QML opens confirm dialog

            # ── Step 3: Wait for user confirmation ─────────────────
            self._confirm_event.wait()

            if not self._confirm_result:
                # User cancelled
                task.status = STATUS_FAILED
                self._history_mgr.complete_task(task)
                self.history_vm.refresh()
                self._is_downloading = False
                self.isDownloadingChanged.emit()
                self.downloadFinished.emit("cancelled", 0, task.expected_count, "[]")
                return

            # ── Step 4: Snapshot directory before download ──────────
            before = snapshot_directory(download_dir)

            # ── Step 5: Run download (blocking with visible console) ─
            try:
                proc = subprocess.Popen(
                    ["cmd", "/c", batch_path],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
                proc.wait()
            except Exception as e:
                task.status = STATUS_FAILED
                self._history_mgr.complete_task(task)
                self.history_vm.refresh()
                self._is_downloading = False
                self.isDownloadingChanged.emit()
                self.downloadFinished.emit("failed", 0, task.expected_count, "[]")
                return

            # ── Step 6: Verify downloads ────────────────────────────
            after    = snapshot_directory(download_dir)
            new_files = get_new_files(before, after)
            task.new_files        = new_files
            task.downloaded_count = len(new_files)

            if task.expected_count > 0:
                if task.downloaded_count >= task.expected_count:
                    task.status = STATUS_COMPLETED
                elif task.downloaded_count > 0:
                    task.status = STATUS_PARTIAL
                    task.failed_urls = find_failed_urls(
                        task.expected_files, new_files, urls
                    )
                else:
                    task.status = STATUS_FAILED
                    task.failed_urls = list(urls)
            else:
                # Export failed – judge by whether any files appeared
                task.status = STATUS_COMPLETED if new_files else STATUS_FAILED

            # ── Step 7: Persist result ──────────────────────────────
            self._history_mgr.complete_task(task)
            self.history_vm.refresh()

            failed_urls_json = json.dumps(task.failed_urls, ensure_ascii=False)

            self._is_downloading = False
            self.isDownloadingChanged.emit()
            self.downloadFinished.emit(
                task.status,
                task.downloaded_count,
                task.expected_count,
                failed_urls_json,
            )
            # Clear URL model on success/partial
            if task.status != STATUS_FAILED:
                self._url_model.clear()

        threading.Thread(target=_worker, daemon=True).start()

    # ── Confirm / cancel slots (called from QML dialog) ─────────────

    @Slot()
    def confirmDownload(self):
        """User confirmed the pre-download file list dialog."""
        if self._confirm_event:
            self._confirm_result = True
            self._confirm_event.set()

    @Slot()
    def cancelDownload(self):
        """User cancelled the pre-download file list dialog."""
        if self._confirm_event:
            self._confirm_result = False
            self._confirm_event.set()

    # ── Retry from history ──────────────────────────────────────────

    def _on_retry_requested(self, urls_json: str, retry_failed_only: bool):
        """Handle retry requests from the history panel."""
        try:
            urls = json.loads(urls_json)
        except Exception:
            return
        if not urls:
            return

        # Build config for retry
        config = self._build_config()
        config.download.urls = urls

        if retry_failed_only:
            config.download.skip_same = True
            config.download.restart   = False
        else:
            config.download.restart   = True
            config.download.skip_same = False

        ok, msg = self._batch.generate_batch(config, auto_close=True)
        if not ok:
            self.notificationRequested.emit("重试", msg, "error")
            return

        download_dir = config.download.directory
        if config.download.subfolder_enabled and config.download.subfolder.strip():
            download_dir = os.path.join(download_dir, config.download.subfolder.strip())

        session_args = self._build_session_export_args(config)
        self._start_tracked_download(urls, download_dir, session_args)

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
        added_count = 0
        for url in urls:
            if self._url_model.addUrl(url):
                added_count += 1
        if added_count > 0:
            self._play_link_detected_sound()
            self.notificationRequested.emit(
                "剪贴板",
                f"检测到 {added_count} 个新链接",
                "info",
            )

    def _sync_clipboard_urls(self):
        self._clipboard.sync_known_urls(self._url_model.get_urls())

    def _play_link_detected_sound(self):
        now = time.monotonic()
        if now - self._last_alert_sound_at < 0.9:
            return
        self._last_alert_sound_at = now

        data = self._alert_sound_data

        def _play():
            try:
                import winsound
                winsound.PlaySound(data, winsound.SND_MEMORY)
            except Exception:
                pass

        threading.Thread(target=_play, daemon=True).start()

    def _build_alert_sound_data(self) -> bytes:
        sample_rate = 22050
        duration_s = 0.18
        frequency = 1046.5
        frame_count = int(sample_rate * duration_s)
        amplitude = 1.0
        fade_samples = max(1, int(sample_rate * 0.015))

        pcm_frames = bytearray()
        for i in range(frame_count):
            envelope = 1.0
            if i < fade_samples:
                envelope = i / fade_samples
            elif i > frame_count - fade_samples:
                envelope = max(0.0, (frame_count - i) / fade_samples)

            sample = math.sin(2.0 * math.pi * frequency * (i / sample_rate))
            value = int(32767 * amplitude * envelope * sample)
            pcm_frames.extend(struct.pack("<h", value))

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(bytes(pcm_frames))
        return buffer.getvalue()

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
