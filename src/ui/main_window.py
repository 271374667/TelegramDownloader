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

# Windows sound support
if platform.system() == "Windows":
    import winsound

from .session_tab import SessionTab
from .download_tab import DownloadTab
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
        """Show tray notification balloon for new URLs with sound"""
        # Play notification sound on Windows
        self.play_notification_sound()

        # Build notification message
        if added_count == 1:
            message = f"已添加 1 个新链接\n当前共 {total_count} 个链接"
        else:
            message = f"已添加 {added_count} 个新链接\n当前共 {total_count} 个链接"

        # Use plain text title
        title = "TDL - 检测到新链接"

        # Update tooltip first
        self.tray_icon.setToolTip(
            f"[NEW!] Telegram Downloader\n"
            f"刚添加 {added_count} 个新链接!\n"
            f"当前链接数: {total_count}"
        )

        # Store notification data for delayed display
        self._pending_notification = (title, message)

        # Use delayed notification to ensure tray icon is ready
        QTimer.singleShot(100, self._show_delayed_notification)

    def _show_delayed_notification(self):
        """Show the pending notification after a short delay"""
        if not hasattr(self, '_pending_notification') or not self._pending_notification:
            return

        title, message = self._pending_notification
        self._pending_notification = None

        # Try Qt tray notification first
        try:
            if self.tray_icon.isVisible() and QSystemTrayIcon.supportsMessages():
                self.tray_icon.showMessage(
                    title,
                    message,
                    QSystemTrayIcon.MessageIcon.Information,
                    5000
                )
        except Exception as e:
            print(f"Qt tray notification error: {e}")

        # Also try Windows native toast notification as backup
        if platform.system() == "Windows":
            self._show_windows_toast(title, message)

    def _show_windows_toast(self, title: str, message: str):
        """Show Windows toast notification using PowerShell"""
        try:
            import subprocess
            # Use PowerShell to show a toast notification
            ps_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
            $template = @"
            <toast>
                <visual>
                    <binding template="ToastText02">
                        <text id="1">{title}</text>
                        <text id="2">{message.replace(chr(10), " ")}</text>
                    </binding>
                </visual>
                <audio src="ms-winsoundevent:Notification.Default"/>
            </toast>
"@
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("TDL").Show($toast)
            '''
            # Run in background without waiting
            subprocess.Popen(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            # Silently fail - the sound notification is the main feedback
            pass

    def play_notification_sound(self):
        """Play a system notification sound"""
        try:
            if platform.system() == "Windows":
                # Play Windows default notification sound
                # MB_ICONASTERISK = Information sound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception as e:
            print(f"Sound notification error: {e}")

    def quit_application(self):
        """Quit the application completely"""
        # Stop clipboard monitoring
        self.stop_clipboard_monitoring()

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