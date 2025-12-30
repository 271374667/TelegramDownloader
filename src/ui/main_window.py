"""
Main window for the Telegram Downloader GUI application
Contains the tabbed interface for session and download configuration
"""

import sys
import platform

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QTextEdit, QLabel, QMessageBox, QSplitter,
    QGroupBox, QStatusBar, QSystemTrayIcon, QMenu, QCheckBox
)
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QFont, QIcon, QAction, QPixmap, QPainter, QColor

# Windows sound and notification support
if platform.system() == "Windows":
    import winsound
    try:
        from winotify import Notification, audio
        WINOTIFY_AVAILABLE = True
    except ImportError:
        WINOTIFY_AVAILABLE = False
else:
    WINOTIFY_AVAILABLE = False

from .session_tab import SessionTab
from .download_tab import DownloadTab
from .floating_panel import FloatingPanel
from core.config_manager import FullConfig
from core.batch_generator import BatchGenerator
from core.clipboard_monitor import ClipboardMonitor


class MainWindow(QMainWindow):
    """Main application window with tabbed interface"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telegram Downloader - TDL GUI")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize configuration and generator
        self.config = FullConfig()
        self.batch_generator = BatchGenerator()

        # Initialize clipboard monitor
        self.clipboard_monitor = ClipboardMonitor(check_interval_ms=500)
        self.clipboard_monitor.new_urls_detected.connect(self.on_new_urls_detected)
        self.clipboard_monitoring_enabled = True

        # Setup UI
        self.setup_ui()
        self.setup_status_bar()
        self.setup_system_tray()
        self.setup_floating_panel()
        self.setup_keyboard_shortcuts()

        # Check for tdl.exe
        self.check_tdl_executable()

        # Start clipboard monitoring
        self.start_clipboard_monitoring()

    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 1px solid #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
        """)

        # Create tabs
        self.session_tab = SessionTab()
        self.download_tab = DownloadTab()

        # Connect download tab clipboard monitoring signal
        self.download_tab.clipboard_monitoring_changed.connect(self.on_clipboard_monitoring_ui_changed)

        # Connect URL list changes to sync clipboard monitor known URLs
        self.download_tab.url_list.urls_changed.connect(self.on_url_list_changed)

        # Add tabs to widget
        self.tab_widget.addTab(self.session_tab, "🔧 Session Configuration")
        self.tab_widget.addTab(self.download_tab, "📥 Download Configuration")

        # Create bottom section for preview and generation
        bottom_widget = self.create_bottom_section()

        # Create splitter for main tabs and bottom section
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.tab_widget)
        splitter.addWidget(bottom_widget)
        splitter.setStretchFactor(0, 5)  # Tabs take more space
        splitter.setStretchFactor(1, 1)  # Bottom takes less space
        splitter.setSizes([600, 150])  # Set initial sizes (tabs=600px, bottom=150px)

        main_layout.addWidget(splitter)

    def create_bottom_section(self):
        """Create the bottom section with command preview and generate button"""
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)

        # Command preview section
        preview_group = QGroupBox("Command Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.command_preview = QTextEdit()
        self.command_preview.setMaximumHeight(100)
        self.command_preview.setReadOnly(True)
        self.command_preview.setFont(QFont("Consolas", 9))
        self.command_preview.setPlaceholderText("Command will be displayed here...")
        preview_layout.addWidget(self.command_preview)

        bottom_layout.addWidget(preview_group)

        # Button section
        button_layout = QHBoxLayout()

        self.preview_button = QPushButton("👁️ Update Preview")
        self.preview_button.clicked.connect(self.update_command_preview)
        button_layout.addWidget(self.preview_button)

        button_layout.addStretch()

        self.generate_button = QPushButton("🚀 Generate Batch File")
        self.generate_button.clicked.connect(self.generate_batch_file)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        button_layout.addWidget(self.generate_button)

        bottom_layout.addLayout(button_layout)

        return bottom_widget

    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def check_tdl_executable(self):
        """Check if tdl.exe exists and show appropriate status"""
        exists, message = self.batch_generator.validate_tdl_executable()
        if exists:
            self.status_bar.showMessage("✅ " + message)
        else:
            self.status_bar.showMessage("❌ " + message)
            QMessageBox.warning(
                self,
                "tdl.exe Not Found",
                "tdl.exe was not found in the bin directory. "
                "Please ensure tdl.exe is in the 'bin' folder "
                "for the generated batch file to work properly."
            )

    @Slot()
    def update_command_preview(self):
        """Update the command preview with current configuration"""
        try:
            # Get configuration from tabs
            self.config.session = self.session_tab.get_session_config()
            self.config.download = self.download_tab.get_download_config()

            # Validate configuration
            errors = self.config.validate()
            if errors:
                error_msg = "Configuration Errors:\n" + "\n".join(f"• {error}" for error in errors)
                self.command_preview.setPlainText(error_msg)
                self.status_bar.showMessage("⚠️ Configuration has errors")
            else:
                # Get command preview
                command = self.batch_generator.get_preview_command(self.config)
                self.command_preview.setPlainText(command)
                self.status_bar.showMessage("✅ Configuration valid - Command preview updated")

        except Exception as e:
            self.command_preview.setPlainText(f"Error generating preview: {str(e)}")
            self.status_bar.showMessage("❌ Error generating preview")

    @Slot()
    def generate_batch_file(self):
        """Generate the batch file with current configuration"""
        try:
            # Get configuration from tabs
            self.config.session = self.session_tab.get_session_config()
            self.config.download = self.download_tab.get_download_config()

            # Validate configuration
            errors = self.config.validate()
            if errors:
                QMessageBox.critical(
                    self,
                    "Configuration Errors",
                    "Please fix the following configuration errors:\n\n" +
                    "\n".join(f"• {error}" for error in errors)
                )
                return

            # Generate batch file
            success, message = self.batch_generator.generate_batch(self.config)

            if success:
                self.status_bar.showMessage("✅ " + message)
                QMessageBox.information(
                    self,
                    "Batch File Generated",
                    f"{message}\n\nFile location: {self.batch_generator.get_batch_file_path()}\n\n"
                    "You can now run this batch file to start downloading with tdl."
                )
            else:
                self.status_bar.showMessage("❌ " + message)
                QMessageBox.critical(
                    self,
                    "Generation Failed",
                    message
                )

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.status_bar.showMessage("❌ " + error_msg)
            QMessageBox.critical(
                self,
                "Unexpected Error",
                error_msg
            )

    def setup_system_tray(self):
        """Setup the system tray icon and menu"""
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("Warning: System tray is not available on this system")

        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)

        # Create a simple icon (blue circle with T)
        icon = self._create_tray_icon()
        self.tray_icon.setIcon(icon)
        self.setWindowIcon(icon)

        # Create tray menu
        tray_menu = QMenu()

        # Show/Hide action
        self.show_action = QAction("显示主窗口", self)
        self.show_action.triggered.connect(self.show_window)
        tray_menu.addAction(self.show_action)

        tray_menu.addSeparator()

        # Floating panel toggle
        self.floating_panel_action = QAction("🎛️ 快捷面板 (Ctrl+Shift+F)", self)
        self.floating_panel_action.setCheckable(True)
        self.floating_panel_action.setChecked(True)
        self.floating_panel_action.triggered.connect(self.on_tray_toggle_floating_panel)
        tray_menu.addAction(self.floating_panel_action)

        # Clipboard monitoring toggle
        self.clipboard_action = QAction("📋 剪贴板监控", self)
        self.clipboard_action.setCheckable(True)
        self.clipboard_action.setChecked(True)
        self.clipboard_action.triggered.connect(self.toggle_clipboard_monitoring)
        tray_menu.addAction(self.clipboard_action)

        tray_menu.addSeparator()

        # URL count display
        self.url_count_action = QAction("📥 当前链接: 0", self)
        self.url_count_action.setEnabled(False)
        tray_menu.addAction(self.url_count_action)

        tray_menu.addSeparator()

        # Exit action
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)

        # Connect tray icon signals
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.messageClicked.connect(self.on_tray_message_clicked)

        # Show tray icon
        self.tray_icon.show()

        # Set tooltip
        self.update_tray_tooltip()

    def _create_tray_icon(self) -> QIcon:
        """Create a simple tray icon"""
        # Create a 64x64 pixmap
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw blue circle
        painter.setBrush(QColor(0, 136, 204))  # Telegram blue
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 56, 56)

        # Draw "T" letter
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setPixelSize(36)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "T")

        painter.end()

        return QIcon(pixmap)

    def update_tray_tooltip(self):
        """Update the tray icon tooltip"""
        url_count = len(self.download_tab.url_list.get_urls())
        monitoring_status = "开启" if self.clipboard_monitoring_enabled else "关闭"
        self.tray_icon.setToolTip(
            f"Telegram Downloader\n"
            f"当前链接数: {url_count}\n"
            f"剪贴板监控: {monitoring_status}"
        )
        # Update menu item
        self.url_count_action.setText(f"📥 当前链接: {url_count}")

    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - show tooltip
            pass

    def on_tray_message_clicked(self):
        """Handle tray notification balloon click"""
        self.show_window()

    def show_window(self):
        """Show and activate the main window"""
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def toggle_clipboard_monitoring(self, checked):
        """Toggle clipboard monitoring on/off (from tray menu)"""
        self.clipboard_monitoring_enabled = checked
        if checked:
            self.start_clipboard_monitoring()
            self.status_bar.showMessage("📋 剪贴板监控已开启")
        else:
            self.stop_clipboard_monitoring()
            self.status_bar.showMessage("📋 剪贴板监控已关闭")
        self.update_tray_tooltip()
        # Sync with download tab checkbox
        self.download_tab.set_clipboard_monitoring(checked)

    @Slot(bool)
    def on_clipboard_monitoring_ui_changed(self, checked):
        """Handle clipboard monitoring toggle from download tab UI"""
        self.clipboard_monitoring_enabled = checked
        if checked:
            self.start_clipboard_monitoring()
            self.status_bar.showMessage("📋 剪贴板监控已开启")
        else:
            self.stop_clipboard_monitoring()
            self.status_bar.showMessage("📋 剪贴板监控已关闭")
        self.update_tray_tooltip()
        # Sync with tray menu checkbox
        self.clipboard_action.setChecked(checked)

    @Slot()
    def on_url_list_changed(self):
        """Handle URL list changes - sync known URLs with clipboard monitor"""
        current_urls = self.download_tab.url_list.get_urls()
        self.clipboard_monitor.sync_known_urls(current_urls)
        # Also update tray tooltip
        self.update_tray_tooltip()

    def start_clipboard_monitoring(self):
        """Start clipboard monitoring"""
        if self.clipboard_monitoring_enabled:
            # Add existing URLs to known set
            existing_urls = self.download_tab.url_list.get_urls()
            self.clipboard_monitor.add_known_urls(existing_urls)
            self.clipboard_monitor.start()

    def stop_clipboard_monitoring(self):
        """Stop clipboard monitoring"""
        self.clipboard_monitor.stop()

    @Slot(list)
    def on_new_urls_detected(self, new_urls: list):
        """Handle newly detected URLs from clipboard"""
        if not self.clipboard_monitoring_enabled:
            return

        added_count = 0
        existing_urls = set(self.download_tab.url_list.get_urls())

        for url in new_urls:
            # Double check it's not already in the list
            if url not in existing_urls:
                # Add to URL list widget
                from PySide6.QtWidgets import QListWidgetItem
                item = QListWidgetItem(url)
                self.download_tab.url_list.url_list.addItem(item)
                added_count += 1
                existing_urls.add(url)

        if added_count > 0:
            # Update status
            self.download_tab.url_list.update_status()
            self.download_tab.url_list.urls_changed.emit()

            # Update tray tooltip
            self.update_tray_tooltip()

            # Get total count
            total_count = len(self.download_tab.url_list.get_urls())

            # Show tray notification balloon
            self.show_tray_notification(added_count, total_count)

            # Update status bar
            self.status_bar.showMessage(f"📋 从剪贴板添加了 {added_count} 个链接，当前共 {total_count} 个")

    def show_tray_notification(self, added_count: int, total_count: int):
        """Show tray notification for new URLs with sound"""
        import threading

        # Build notification message
        if added_count == 1:
            message = f"已添加 1 个新链接，当前共 {total_count} 个链接"
        else:
            message = f"已添加 {added_count} 个新链接，当前共 {total_count} 个链接"

        title = "TDL - 检测到新链接"

        # Update tooltip
        self.tray_icon.setToolTip(
            f"[NEW!] Telegram Downloader\n"
            f"刚添加 {added_count} 个新链接!\n"
            f"当前链接数: {total_count}"
        )

        # Run notification in separate thread to avoid blocking Qt event loop
        def show_notification_thread():
            # Play sound
            self.play_notification_sound()

            # Show notification
            if WINOTIFY_AVAILABLE:
                self._show_winotify_toast(title, message)

        thread = threading.Thread(target=show_notification_thread, daemon=True)
        thread.start()

    def _show_winotify_toast(self, title: str, message: str) -> bool:
        """Show Windows toast notification using winotify library"""
        try:
            toast = Notification(
                app_id="Telegram Downloader",
                title=title,
                msg=message,
                duration="short"
            )
            toast.show()
            return True
        except Exception as e:
            print(f"Winotify notification error: {e}")
            return False

    def play_notification_sound(self):
        """Play a system notification sound"""
        if platform.system() == "Windows":
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception as e:
                print(f"Sound notification error: {e}")

    def setup_floating_panel(self):
        """Setup the floating quick action panel"""
        self.floating_panel = FloatingPanel()

        # Connect floating panel signals
        self.floating_panel.clear_requested.connect(self.on_floating_clear)
        self.floating_panel.generate_requested.connect(self.on_floating_generate)
        self.floating_panel.execute_requested.connect(self.on_floating_execute)
        self.floating_panel.show_main_requested.connect(self.show_window)

        # Connect URL list changes to update floating panel
        self.download_tab.url_list.urls_changed.connect(self.update_floating_panel_count)

        # Sync tray menu checkbox when floating panel visibility changes
        self.floating_panel.close_btn.clicked.connect(
            lambda: self.floating_panel_action.setChecked(False)
        )

        # Initial update
        self.update_floating_panel_count()

        # Show the floating panel
        self.floating_panel.show()

    def setup_keyboard_shortcuts(self):
        """Setup global keyboard shortcuts"""
        from PySide6.QtGui import QShortcut, QKeySequence

        # Ctrl+Shift+F to toggle floating panel
        self.toggle_panel_shortcut = QShortcut(QKeySequence("Ctrl+Shift+F"), self)
        self.toggle_panel_shortcut.activated.connect(self.toggle_floating_panel)

    @Slot()
    def toggle_floating_panel(self):
        """Toggle the floating panel visibility (from keyboard shortcut)"""
        if self.floating_panel.isVisible():
            self.floating_panel.hide()
            self.status_bar.showMessage("Floating panel hidden (Ctrl+Shift+F to show)")
        else:
            self.floating_panel.show()
            self.floating_panel.raise_()
            self.status_bar.showMessage("Floating panel shown")
        # Sync tray menu checkbox
        self.floating_panel_action.setChecked(self.floating_panel.isVisible())

    @Slot(bool)
    def on_tray_toggle_floating_panel(self, checked):
        """Toggle the floating panel visibility (from tray menu)"""
        if checked:
            self.floating_panel.show()
            self.floating_panel.raise_()
            self.status_bar.showMessage("Floating panel shown")
        else:
            self.floating_panel.hide()
            self.status_bar.showMessage("Floating panel hidden (Ctrl+Shift+F to show)")

    @Slot()
    def update_floating_panel_count(self):
        """Update the URL count in the floating panel"""
        count = len(self.download_tab.url_list.get_urls())
        self.floating_panel.update_url_count(count)

    @Slot()
    def on_floating_clear(self):
        """Handle clear request from floating panel"""
        self.download_tab.url_list.clear_urls()
        self.status_bar.showMessage("All URLs cleared")
        self.update_tray_tooltip()

    @Slot()
    def on_floating_generate(self):
        """Handle generate bat request from floating panel"""
        self.generate_batch_file()

    @Slot()
    def on_floating_execute(self):
        """Handle execute request from floating panel - generate and run bat"""
        import subprocess
        import os

        try:
            # Get configuration from tabs
            self.config.session = self.session_tab.get_session_config()
            self.config.download = self.download_tab.get_download_config()

            # Validate configuration
            errors = self.config.validate()
            if errors:
                QMessageBox.critical(
                    self,
                    "Configuration Errors",
                    "Please fix the following configuration errors:\n\n" +
                    "\n".join(f"• {error}" for error in errors)
                )
                return

            # Generate batch file with auto_close=True for quick run
            success, message = self.batch_generator.generate_batch(self.config, auto_close=True)

            if success:
                self.status_bar.showMessage("Batch file generated, executing...")

                # Get the batch file path
                batch_path = self.batch_generator.get_batch_file_path()

                # Execute the batch file in a new console window
                if platform.system() == "Windows":
                    # Use subprocess to open in a new console window
                    subprocess.Popen(
                        ['cmd', '/c', 'start', '', batch_path],
                        shell=True,
                        cwd=os.path.dirname(batch_path)
                    )
                    self.status_bar.showMessage(f"Executing: {batch_path}")
                else:
                    # For non-Windows systems
                    subprocess.Popen(
                        ['bash', batch_path],
                        cwd=os.path.dirname(batch_path)
                    )
                    self.status_bar.showMessage(f"Executing: {batch_path}")

                # Clear URLs after successful execution
                self.download_tab.url_list.clear_urls()
                self.update_tray_tooltip()
            else:
                self.status_bar.showMessage("Failed to generate batch file")
                QMessageBox.critical(
                    self,
                    "Generation Failed",
                    message
                )

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.status_bar.showMessage("Error executing batch file")
            QMessageBox.critical(
                self,
                "Execution Error",
                error_msg
            )

    def quit_application(self):
        """Quit the application completely"""
        # Stop clipboard monitoring
        self.stop_clipboard_monitoring()

        # Hide floating panel
        if hasattr(self, 'floating_panel'):
            self.floating_panel.close()

        # Hide tray icon
        self.tray_icon.hide()

        # Quit application
        from PySide6.QtWidgets import QApplication
        QApplication.quit()

    def closeEvent(self, event):
        """Handle window close event - minimize to tray instead of closing"""
        if self.tray_icon.isVisible():
            # Minimize to tray
            self.hide()
            if QSystemTrayIcon.supportsMessages():
                self.tray_icon.showMessage(
                    "Telegram Downloader",
                    "程序已最小化到系统托盘\n剪贴板监控继续运行中",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
            event.ignore()
        else:
            # If tray is not available, ask for confirmation
            reply = QMessageBox.question(
                self,
                "Exit Confirmation",
                "Are you sure you want to exit the Telegram Downloader?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.quit_application()
                event.accept()
            else:
                event.ignore()