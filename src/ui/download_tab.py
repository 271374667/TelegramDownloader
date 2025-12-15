"""
Download configuration tab for Telegram Downloader GUI
Handles all download-related tdl parameters
"""

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QCheckBox, QSpinBox, QLineEdit, QGroupBox, QScrollArea,
    QPushButton, QFileDialog, QSplitter, QTextEdit,
    QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from core.config_manager import DownloadConfig
from .widgets.url_list import URLListWidget


class DownloadTab(QWidget):
    """Tab for configuring download parameters"""

    # Signal emitted when clipboard monitoring state changes
    clipboard_monitoring_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup the download configuration interface"""
        # Create scroll area for all settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Main container widget
        container = QWidget()
        scroll_area.setWidget(container)

        # Main layout with splitter
        main_layout = QHBoxLayout(container)

        # Left panel - URLs
        left_panel = self.create_url_panel()

        # Right panel - Settings
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(self.create_basic_settings())
        right_layout.addWidget(self.create_file_filtering_settings())
        right_layout.addWidget(self.create_advanced_settings())
        right_layout.addWidget(self.create_server_settings())

        # Add panels to splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)  # URLs panel
        splitter.setStretchFactor(1, 2)  # Settings panel

        main_layout.addWidget(splitter)

        # Main layout for this tab
        tab_layout = QVBoxLayout(self)
        tab_layout.addWidget(scroll_area)

    def create_url_panel(self):
        """Create the URL management panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # URL list widget (not checkable - URLs are mandatory)
        url_group = QGroupBox("🔗 Download URLs")
        url_layout = QVBoxLayout(url_group)

        self.url_list = URLListWidget()
        url_layout.addWidget(self.url_list)

        # URL import/export buttons
        button_layout = QHBoxLayout()

        import_button = QPushButton("📋 Paste URLs")
        import_button.clicked.connect(self.import_urls)
        import_button.setToolTip("Paste URLs from clipboard")
        button_layout.addWidget(import_button)

        export_button = QPushButton("💾 Copy URLs")
        export_button.clicked.connect(self.export_urls)
        export_button.setToolTip("Copy all URLs to clipboard")
        button_layout.addWidget(export_button)

        url_layout.addLayout(button_layout)

        # Clipboard monitoring checkbox
        clipboard_layout = QHBoxLayout()
        self.clipboard_monitor_checkbox = QCheckBox("📋 Auto-detect URLs from clipboard")
        self.clipboard_monitor_checkbox.setChecked(True)  # Default enabled
        self.clipboard_monitor_checkbox.setToolTip(
            "Automatically detect and add Telegram URLs when copied to clipboard"
        )
        self.clipboard_monitor_checkbox.toggled.connect(self.on_clipboard_monitor_toggled)
        clipboard_layout.addWidget(self.clipboard_monitor_checkbox)
        clipboard_layout.addStretch()

        url_layout.addLayout(clipboard_layout)
        layout.addWidget(url_group)

        return panel

    def create_basic_settings(self):
        """Create basic download settings group"""
        group = QGroupBox("⬇️ Basic Settings")
        group.setCheckable(True)
        group.setChecked(True)

        layout = QFormLayout(group)

        # Download directory
        dir_layout = QHBoxLayout()
        self.directory_edit = QLineEdit(os.path.join(os.getcwd(), "downloads"))
        self.directory_edit.setToolTip("Directory where files will be downloaded")
        dir_layout.addWidget(self.directory_edit)

        self.browse_button = QPushButton("📁 Browse")
        self.browse_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.browse_button)

        layout.addRow("Download directory:", dir_layout)

        # Subfolder setting
        subfolder_layout = QHBoxLayout()
        self.subfolder_checkbox = QCheckBox("Download to subfolder:")
        self.subfolder_checkbox.setToolTip("Download files to a subfolder under the download directory")
        self.subfolder_checkbox.toggled.connect(self.on_subfolder_checkbox_toggled)
        subfolder_layout.addWidget(self.subfolder_checkbox)

        self.subfolder_edit = QLineEdit()
        self.subfolder_edit.setPlaceholderText("e.g., 相册")
        self.subfolder_edit.setToolTip("Subfolder name (e.g., 相册, videos, photos)")
        self.subfolder_edit.setEnabled(False)  # Disabled by default
        subfolder_layout.addWidget(self.subfolder_edit)

        self.subfolder_browse_button = QPushButton("📁")
        self.subfolder_browse_button.setToolTip("Browse for subfolder")
        self.subfolder_browse_button.setMaximumWidth(40)
        self.subfolder_browse_button.setEnabled(False)  # Disabled by default
        self.subfolder_browse_button.clicked.connect(self.browse_subfolder)
        subfolder_layout.addWidget(self.subfolder_browse_button)

        layout.addRow("", subfolder_layout)

        # Download options checkboxes
        self.continue_checkbox = QCheckBox("Continue last download")
        self.continue_checkbox.setToolTip("Resume the interrupted download")
        layout.addRow("", self.continue_checkbox)

        self.restart_checkbox = QCheckBox("Restart last download")
        self.restart_checkbox.setToolTip("Restart the last download from beginning")
        layout.addRow("", self.restart_checkbox)

        self.desc_checkbox = QCheckBox("Download from newest to oldest")
        self.desc_checkbox.setToolTip("Download files in reverse chronological order")
        layout.addRow("", self.desc_checkbox)

        self.group_checkbox = QCheckBox("Auto-detect grouped messages")
        self.group_checkbox.setToolTip("Automatically detect and download grouped messages")
        layout.addRow("", self.group_checkbox)

        self.skip_same_checkbox = QCheckBox("Skip same files")
        self.skip_same_checkbox.setToolTip("Skip files with same name and size")
        self.skip_same_checkbox.setChecked(True)  # Default enabled
        layout.addRow("", self.skip_same_checkbox)

        self.takeout_checkbox = QCheckBox("Use takeout session")
        self.takeout_checkbox.setToolTip("Use takeout sessions for lower flood wait limits")
        layout.addRow("", self.takeout_checkbox)

        self.rewrite_ext_checkbox = QCheckBox("Rewrite file extension")
        self.rewrite_ext_checkbox.setToolTip("Rewrite file extension according to file header MIME")
        layout.addRow("", self.rewrite_ext_checkbox)

        # Store group reference
        self.basic_settings_group = group

        return group

    def create_file_filtering_settings(self):
        """Create file filtering settings group"""
        group = QGroupBox("🎯 File Filtering")
        group.setCheckable(True)
        group.setChecked(False)  # Default unchecked

        layout = QFormLayout(group)

        # Include extensions
        self.include_edit = QLineEdit()
        self.include_edit.setPlaceholderText("e.g., mp4,mp3,jpg (comma-separated)")
        self.include_edit.setToolTip("Include only these file extensions (without dot)")
        layout.addRow("Include extensions:", self.include_edit)

        # Exclude extensions
        self.exclude_edit = QLineEdit()
        self.exclude_edit.setPlaceholderText("e.g., txt,log,tmp (comma-separated)")
        self.exclude_edit.setToolTip("Exclude these file extensions (without dot)")
        layout.addRow("Exclude extensions:", self.exclude_edit)

        # Official files
        self.official_edit = QLineEdit()
        self.official_edit.setPlaceholderText("Path to official client exported files")
        self.official_edit.setToolTip("Official client exported files to process")
        layout.addRow("Official files:", self.official_edit)

        # Filter help
        help_label = QLabel("💡 Filtering Tips:")
        help_font = QFont()
        help_font.setItalic(True)
        help_label.setFont(help_font)
        help_layout = QVBoxLayout()
        help_layout.addWidget(help_label)

        tips = [
            "• Use 'include' to download only specific file types",
            "• Use 'exclude' to skip certain file types",
            "• Cannot use both include and exclude simultaneously",
            "• Extensions should be without the dot (e.g., 'mp4' not '.mp4')"
        ]

        for tip in tips:
            tip_label = QLabel(tip)
            tip_label.setWordWrap(True)
            tip_label.setStyleSheet("color: #666666; margin-left: 10px;")
            help_layout.addWidget(tip_label)

        layout.addRow("", help_layout)

        # Store group reference
        self.file_filtering_group = group

        return group

    def create_advanced_settings(self):
        """Create advanced download settings group"""
        group = QGroupBox("⚙️ Advanced Settings")
        group.setCheckable(True)
        group.setChecked(False)  # Default unchecked

        layout = QFormLayout(group)

        # File name template
        self.template_edit = QLineEdit("{{ .DialogID }}_{{ .MessageID }}_{{ filenamify .FileName }}")
        self.template_edit.setToolTip("Template for downloaded file names")
        layout.addRow("File name template:", self.template_edit)

        # Server mode
        self.serve_checkbox = QCheckBox("Serve as HTTP server")
        self.serve_checkbox.setToolTip("Serve media files as HTTP server instead of downloading")
        layout.addRow("", self.serve_checkbox)

        # Store group reference
        self.advanced_settings_group = group

        return group

    def create_server_settings(self):
        """Create HTTP server settings group"""
        group = QGroupBox("🌐 Server Settings")
        group.setCheckable(True)
        group.setChecked(False)  # Default unchecked

        layout = QFormLayout(group)

        # HTTP server port
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(8080)
        self.port_spin.setToolTip("HTTP server port (when using server mode)")
        layout.addRow("HTTP server port:", self.port_spin)

        # Server info
        info_label = QLabel("📡 Server Mode Info:")
        info_font = QFont()
        info_font.setItalic(True)
        info_label.setFont(info_font)
        info_layout = QVBoxLayout()
        info_layout.addWidget(info_label)

        info_text = [
            "• Server mode serves files via HTTP instead of downloading",
            "• Access files via http://localhost:port",
            "• Useful for streaming or previewing without downloading",
            "• Port must be available and not blocked by firewall"
        ]

        for info in info_text:
            info_item = QLabel(info)
            info_item.setWordWrap(True)
            info_item.setStyleSheet("color: #666666; margin-left: 10px;")
            info_layout.addWidget(info_item)

        layout.addRow("", info_layout)

        # Store group reference
        self.server_settings_group = group

        return group

    def on_clipboard_monitor_toggled(self, checked):
        """Handle clipboard monitoring checkbox toggle"""
        self.clipboard_monitoring_changed.emit(checked)

    def set_clipboard_monitoring(self, enabled: bool):
        """Set clipboard monitoring checkbox state (called from main window)"""
        # Block signals to prevent infinite loop
        self.clipboard_monitor_checkbox.blockSignals(True)
        self.clipboard_monitor_checkbox.setChecked(enabled)
        self.clipboard_monitor_checkbox.blockSignals(False)

    def on_subfolder_checkbox_toggled(self, checked):
        """Handle subfolder checkbox toggle"""
        self.subfolder_edit.setEnabled(checked)
        self.subfolder_browse_button.setEnabled(checked)
        if not checked:
            self.subfolder_edit.clear()

    def browse_subfolder(self):
        """Browse for subfolder directory"""
        # Use download directory as base path
        base_path = self.directory_edit.text().strip()
        if not base_path or not os.path.exists(base_path):
            base_path = os.getcwd()

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Subfolder",
            base_path,
            QFileDialog.ShowDirsOnly
        )

        if directory:
            # Extract just the folder name relative to download directory
            download_dir = self.directory_edit.text().strip()
            if directory.startswith(download_dir):
                # Get relative path
                relative_path = os.path.relpath(directory, download_dir)
                self.subfolder_edit.setText(relative_path)
            else:
                # Just use the folder name
                self.subfolder_edit.setText(os.path.basename(directory))

    def browse_directory(self):
        """Browse for download directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Download Directory",
            self.directory_edit.text(),
            QFileDialog.ShowDirsOnly
        )

        if directory:
            self.directory_edit.setText(directory)

    def import_urls(self):
        """Import URLs from clipboard"""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        text = clipboard.text()

        if text.strip():
            self.url_list.add_urls_from_text(text)
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Clipboard Empty", "No URLs found in clipboard.")

    def export_urls(self):
        """Export URLs to clipboard"""
        urls = self.url_list.get_urls()
        if urls:
            from PySide6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText('\n'.join(urls))
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "URLs Copied", f"{len(urls)} URLs copied to clipboard.")
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "No URLs", "No URLs to copy to clipboard.")

    def get_download_config(self) -> DownloadConfig:
        """Get the current download configuration from UI elements"""
        # Parse extensions from text
        include_exts = [ext.strip() for ext in self.include_edit.text().split(',') if ext.strip()]
        exclude_exts = [ext.strip() for ext in self.exclude_edit.text().split(',') if ext.strip()]
        official_files = [f.strip() for f in self.official_edit.text().split(',') if f.strip()]

        return DownloadConfig(
            # URLs
            urls=self.url_list.get_urls(),

            # Basic settings
            continue_last=self.continue_checkbox.isChecked(),
            desc=self.desc_checkbox.isChecked(),
            directory=self.directory_edit.text().strip() or os.path.join(os.getcwd(), "downloads"),
            subfolder=self.subfolder_edit.text().strip(),
            subfolder_enabled=self.subfolder_checkbox.isChecked(),

            # File filtering
            include_extensions=include_exts,
            exclude_extensions=exclude_exts,
            official_files=official_files,

            # Special features
            group=self.group_checkbox.isChecked(),

            # Server settings
            port=self.port_spin.value(),

            # Download behavior
            restart=self.restart_checkbox.isChecked(),
            rewrite_ext=self.rewrite_ext_checkbox.isChecked(),
            serve=self.serve_checkbox.isChecked(),
            skip_same=self.skip_same_checkbox.isChecked(),
            takeout=self.takeout_checkbox.isChecked(),

            # Template
            template=self.template_edit.text().strip() or "{{ .DialogID }}_{{ .MessageID }}_{{ filenamify .FileName }}",

            # GroupBox enabled states
            basic_settings_enabled=self.basic_settings_group.isChecked(),
            file_filtering_enabled=self.file_filtering_group.isChecked(),
            advanced_settings_enabled=self.advanced_settings_group.isChecked(),
            server_settings_enabled=self.server_settings_group.isChecked()
        )

    def load_download_config(self, config: DownloadConfig):
        """Load download configuration into UI elements"""
        # URLs
        self.url_list.set_urls(config.urls)

        # Basic settings
        self.continue_checkbox.setChecked(config.continue_last)
        self.desc_checkbox.setChecked(config.desc)
        self.directory_edit.setText(config.directory)
        self.subfolder_checkbox.setChecked(config.subfolder_enabled)
        self.subfolder_edit.setText(config.subfolder)
        self.subfolder_edit.setEnabled(config.subfolder_enabled)
        self.subfolder_browse_button.setEnabled(config.subfolder_enabled)

        # File filtering
        self.include_edit.setText(', '.join(config.include_extensions))
        self.exclude_edit.setText(', '.join(config.exclude_extensions))
        self.official_edit.setText(', '.join(config.official_files))

        # Special features
        self.group_checkbox.setChecked(config.group)

        # Server settings
        self.port_spin.setValue(config.port)

        # Download behavior
        self.restart_checkbox.setChecked(config.restart)
        self.rewrite_ext_checkbox.setChecked(config.rewrite_ext)
        self.serve_checkbox.setChecked(config.serve)
        self.skip_same_checkbox.setChecked(config.skip_same)
        self.takeout_checkbox.setChecked(config.takeout)

        # Template
        self.template_edit.setText(config.template)