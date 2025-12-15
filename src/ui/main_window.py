"""
Main window for the Telegram Downloader GUI application
Contains the tabbed interface for session and download configuration
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QTextEdit, QLabel, QMessageBox, QSplitter,
    QGroupBox, QStatusBar
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont

from .session_tab import SessionTab
from .download_tab import DownloadTab
from core.config_manager import FullConfig
from core.batch_generator import BatchGenerator


class MainWindow(QMainWindow):
    """Main application window with tabbed interface"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telegram Downloader - TDL GUI")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize configuration and generator
        self.config = FullConfig()
        self.batch_generator = BatchGenerator()

        # Setup UI
        self.setup_ui()
        self.setup_status_bar()

        # Check for tdl.exe
        self.check_tdl_executable()

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

    def closeEvent(self, event):
        """Handle window close event"""
        # Ask for confirmation if there are unsaved changes
        reply = QMessageBox.question(
            self,
            "Exit Confirmation",
            "Are you sure you want to exit the Telegram Downloader?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()