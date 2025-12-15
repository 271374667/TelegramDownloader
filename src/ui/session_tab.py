"""
Session configuration tab for Telegram Downloader GUI
Handles all session-related tdl parameters
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QCheckBox, QSpinBox, QLineEdit, QComboBox, QGroupBox,
    QScrollArea, QFrame, QToolTip, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from core.config_manager import SessionConfig


class SessionTab(QWidget):
    """Tab for configuring tdl session parameters"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup the session configuration interface"""
        # Create scroll area for all settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMinimumHeight(400)  # Set minimum height

        # Main container widget
        container = QWidget()
        scroll_area.setWidget(container)

        # Main layout
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(10)  # Reduced spacing
        main_layout.setContentsMargins(5, 5, 5, 5)  # Add some margins

        # Create sections
        main_layout.addWidget(self.create_basic_settings())
        main_layout.addWidget(self.create_network_settings())
        main_layout.addWidget(self.create_storage_settings())
        main_layout.addWidget(self.create_performance_settings())

        # Add stretch to push content to the top and fill available space
        main_layout.addStretch()

        # Main layout for this tab
        tab_layout = QVBoxLayout(self)
        tab_layout.addWidget(scroll_area)
        # Remove the stretch to make the content fill the space

    def create_basic_settings(self):
        """Create basic settings group"""
        group = QGroupBox("🔧 Basic Settings")
        group.setCheckable(True)
        group.setChecked(True)

        layout = QFormLayout(group)

        # Debug mode checkbox
        self.debug_checkbox = QCheckBox("Enable debug mode")
        self.debug_checkbox.setToolTip("Enable debug logging for troubleshooting")
        layout.addRow("", self.debug_checkbox)

        # Delay between tasks
        self.delay_edit = QLineEdit("0s")
        self.delay_edit.setPlaceholderText("e.g., 1s, 30s, 5m")
        self.delay_edit.setToolTip("Delay between each task (s=seconds, m=minutes, h=hours)")
        layout.addRow("Delay between tasks:", self.delay_edit)

        # Concurrent tasks limit
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 50)
        self.limit_spin.setValue(2)
        self.limit_spin.setToolTip("Maximum number of concurrent download tasks")
        layout.addRow("Concurrent tasks limit:", self.limit_spin)

        # Namespace
        self.namespace_edit = QLineEdit("default")
        self.namespace_edit.setToolTip("Namespace for Telegram session")
        layout.addRow("Session namespace:", self.namespace_edit)

        # Store group reference
        self.basic_settings_group = group

        return group

    def create_network_settings(self):
        """Create network settings group"""
        group = QGroupBox("🌐 Network Settings")
        group.setCheckable(True)
        group.setChecked(True)

        layout = QFormLayout(group)

        # NTP server
        self.ntp_edit = QLineEdit()
        self.ntp_edit.setPlaceholderText("Optional: e.g., pool.ntp.org")
        self.ntp_edit.setToolTip("NTP server host (leave empty to use system time)")
        layout.addRow("NTP server:", self.ntp_edit)

        # DC pool size
        self.pool_spin = QSpinBox()
        self.pool_spin.setRange(0, 20)
        self.pool_spin.setValue(8)
        self.pool_spin.setToolTip("Size of the DC pool (0 means infinity)")
        layout.addRow("DC pool size:", self.pool_spin)

        # Proxy settings
        proxy_layout = QHBoxLayout()
        self.proxy_edit = QLineEdit("socks5://127.0.0.1:7897")
        self.proxy_edit.setToolTip("Proxy address format: protocol://[username:password@]host:port")
        proxy_layout.addWidget(self.proxy_edit)

        self.proxy_presets = QComboBox()
        self.proxy_presets.addItems([
            "Custom Proxy",
            "SOCKS5 (127.0.0.1:7897)",
            "SOCKS5 (127.0.0.1:1080)",
            "HTTP (127.0.0.1:8080)",
            "HTTPS (127.0.0.1:8080)"
        ])
        self.proxy_presets.currentTextChanged.connect(self.on_proxy_preset_changed)
        proxy_layout.addWidget(self.proxy_presets)

        layout.addRow("Proxy:", proxy_layout)

        # Reconnect timeout
        self.reconnect_edit = QLineEdit("5m0s")
        self.reconnect_edit.setPlaceholderText("e.g., 30s, 5m, 1h")
        self.reconnect_edit.setToolTip("Telegram client reconnection timeout")
        layout.addRow("Reconnect timeout:", self.reconnect_edit)

        # Store group reference
        self.network_settings_group = group

        return group

    def create_storage_settings(self):
        """Create storage settings group"""
        group = QGroupBox("💾 Storage Settings")
        group.setCheckable(True)
        group.setChecked(False)  # Default unchecked

        layout = QFormLayout(group)

        # Storage type
        self.storage_type_combo = QComboBox()
        self.storage_type_combo.addItems(["bolt", "legacy", "file"])
        self.storage_type_combo.setToolTip("Storage driver type for session data")
        layout.addRow("Storage type:", self.storage_type_combo)

        # Storage path
        self.storage_path_edit = QLineEdit("~/.tdl/data")
        self.storage_path_edit.setToolTip("Storage path for session data")
        layout.addRow("Storage path:", self.storage_path_edit)

        # Store group reference
        self.storage_settings_group = group

        return group

    def create_performance_settings(self):
        """Create performance settings group"""
        group = QGroupBox("⚡ Performance Settings")
        group.setCheckable(True)
        group.setChecked(True)

        layout = QFormLayout(group)

        # Transfer threads
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 32)
        self.threads_spin.setValue(4)
        self.threads_spin.setToolTip("Maximum threads for transferring one item")
        layout.addRow("Transfer threads per item:", self.threads_spin)

        # Performance hints
        hints_label = QLabel("💡 Performance Tips:")
        hints_font = QFont()
        hints_font.setItalic(True)
        hints_label.setFont(hints_font)
        hints_layout = QVBoxLayout()
        hints_layout.addWidget(hints_label)

        tips = [
            "• Higher thread count = faster individual downloads but more resource usage",
            "• Pool size affects connection management to Telegram servers",
            "• Proxy may affect overall speed and reliability",
            "• Adjust based on your network connection and system capabilities"
        ]

        for tip in tips:
            tip_label = QLabel(tip)
            tip_label.setWordWrap(True)
            tip_label.setStyleSheet("color: #666666; margin-left: 10px;")
            hints_layout.addWidget(tip_label)

        layout.addRow("", hints_layout)

        # Store group reference
        self.performance_settings_group = group

        return group

    def on_proxy_preset_changed(self, preset_name):
        """Handle proxy preset selection change"""
        preset_proxies = {
            "Custom Proxy": "",
            "SOCKS5 (127.0.0.1:7897)": "socks5://127.0.0.1:7897",
            "SOCKS5 (127.0.0.1:1080)": "socks5://127.0.0.1:1080",
            "HTTP (127.0.0.1:8080)": "http://127.0.0.1:8080",
            "HTTPS (127.0.0.1:8080)": "https://127.0.0.1:8080"
        }

        if preset_name in preset_proxies:
            self.proxy_edit.setText(preset_proxies[preset_name])
            if preset_name == "Custom Proxy":
                self.proxy_edit.setFocus()
                self.proxy_edit.selectAll()

    def get_session_config(self) -> SessionConfig:
        """Get the current session configuration from UI elements"""
        return SessionConfig(
            # Basic settings
            debug=self.debug_checkbox.isChecked(),
            delay=self.delay_edit.text().strip() or "0s",
            limit=self.limit_spin.value(),
            namespace=self.namespace_edit.text().strip() or "default",

            # Network settings
            ntp_server=self.ntp_edit.text().strip(),
            pool=self.pool_spin.value(),
            proxy=self.proxy_edit.text().strip(),
            reconnect_timeout=self.reconnect_edit.text().strip() or "5m0s",

            # Storage settings
            storage_type=self.storage_type_combo.currentText(),
            storage_path=self.storage_path_edit.text().strip() or "~/.tdl/data",

            # Performance settings
            threads=self.threads_spin.value(),

            # GroupBox enabled states
            basic_settings_enabled=self.basic_settings_group.isChecked(),
            network_settings_enabled=self.network_settings_group.isChecked(),
            storage_settings_enabled=self.storage_settings_group.isChecked(),
            performance_settings_enabled=self.performance_settings_group.isChecked()
        )

    def load_session_config(self, config: SessionConfig):
        """Load session configuration into UI elements"""
        # Basic settings
        self.debug_checkbox.setChecked(config.debug)
        self.delay_edit.setText(config.delay)
        self.limit_spin.setValue(config.limit)
        self.namespace_edit.setText(config.namespace)

        # Network settings
        self.ntp_edit.setText(config.ntp_server)
        self.pool_spin.setValue(config.pool)
        self.proxy_edit.setText(config.proxy)
        self.reconnect_edit.setText(config.reconnect_timeout)

        # Storage settings
        index = self.storage_type_combo.findText(config.storage_type)
        if index >= 0:
            self.storage_type_combo.setCurrentIndex(index)
        self.storage_path_edit.setText(config.storage_path)

        # Performance settings
        self.threads_spin.setValue(config.threads)