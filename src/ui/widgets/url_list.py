"""
Custom URL list widget for Telegram Downloader GUI
Provides an interface for managing multiple download URLs
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QMessageBox, QInputDialog, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon


class URLListWidget(QWidget):
    """Custom widget for managing Telegram message URLs"""

    urls_changed = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup the URL list interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # URL input section
        input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Telegram message URL (e.g., https://t.me/channel/123)")
        self.url_input.returnPressed.connect(self.add_url)
        input_layout.addWidget(self.url_input)

        self.add_button = QPushButton("➕ Add")
        self.add_button.clicked.connect(self.add_url)
        self.add_button.setToolTip("Add URL to the download list")
        input_layout.addWidget(self.add_button)

        layout.addLayout(input_layout)

        # URL list section
        self.url_list = QListWidget()
        self.url_list.setMaximumHeight(200)
        self.url_list.setFont(QFont("Consolas", 9))
        self.url_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(self.url_list)

        # URL management buttons
        button_layout = QHBoxLayout()

        self.remove_button = QPushButton("🗑️ Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected_url)
        self.remove_button.setEnabled(False)
        button_layout.addWidget(self.remove_button)

        self.edit_button = QPushButton("✏️ Edit Selected")
        self.edit_button.clicked.connect(self.edit_selected_url)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)

        self.clear_button = QPushButton("🧹 Clear All")
        self.clear_button.clicked.connect(self.clear_all_urls)
        self.clear_button.setEnabled(False)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        # URL validation label
        self.status_label = QLabel("📝 Add Telegram message URLs to download")
        self.status_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.status_label)

        # Connect signals
        self.url_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.url_list.itemDoubleClicked.connect(self.edit_selected_url)

    def add_url(self):
        """Add URL from input field to the list"""
        url = self.url_input.text().strip()

        if not url:
            return

        if not self.validate_url(url):
            QMessageBox.warning(
                self,
                "Invalid URL",
                "Please enter a valid Telegram message URL.\n\n"
                "Valid format: https://t.me/channel/123\n"
                "or: https://t.me/c/123/456"
            )
            return

        # Check for duplicates
        for i in range(self.url_list.count()):
            if self.url_list.item(i).text() == url:
                QMessageBox.information(
                    self,
                    "Duplicate URL",
                    "This URL is already in the list."
                )
                return

        # Add URL to list
        item = QListWidgetItem(url)
        self.url_list.addItem(item)

        # Clear input and update status
        self.url_input.clear()
        self.update_status()
        self.urls_changed.emit()

    def remove_selected_url(self):
        """Remove the selected URL from the list"""
        current_row = self.url_list.currentRow()
        if current_row >= 0:
            item = self.url_list.takeItem(current_row)
            del item
            self.update_status()
            self.urls_changed.emit()

    def edit_selected_url(self):
        """Edit the selected URL"""
        current_row = self.url_list.currentRow()
        if current_row >= 0:
            item = self.url_list.item(current_row)
            old_url = item.text()

            new_url, ok = QInputDialog.getText(
                self,
                "Edit URL",
                "Telegram message URL:",
                text=old_url
            )

            if ok and new_url.strip():
                if self.validate_url(new_url.strip()):
                    item.setText(new_url.strip())
                    self.urls_changed.emit()
                else:
                    QMessageBox.warning(
                        self,
                        "Invalid URL",
                        "Please enter a valid Telegram message URL."
                    )

    def clear_all_urls(self):
        """Clear all URLs from the list (with confirmation)"""
        reply = QMessageBox.question(
            self,
            "Clear All URLs",
            "Are you sure you want to remove all URLs from the list?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.clear_urls()

    def clear_urls(self):
        """Clear all URLs from the list (without confirmation) - used by floating panel"""
        self.url_list.clear()
        self.update_status()
        self.urls_changed.emit()

    def on_selection_changed(self):
        """Handle URL list selection change"""
        has_selection = self.url_list.currentItem() is not None
        self.remove_button.setEnabled(has_selection)
        self.edit_button.setEnabled(has_selection)

    def validate_url(self, url: str) -> bool:
        """
        Validate if the URL is a valid Telegram message URL.

        Supported formats:
        - https://t.me/telegram/193
        - https://t.me/c/1697797156/151
        - https://t.me/iFreeKnow/45662/55005
        - https://t.me/c/1492447836/251015/251021
        - https://t.me/opencfdchannel/4434?comment=360409
        - https://t.me/myhostloc/1485524?thread=1485523
        """
        import re

        url = url.strip()

        # Basic format validation
        if not url.startswith("https://t.me/") and not url.startswith("http://t.me/"):
            return False

        # Regex pattern for Telegram URLs
        pattern = re.compile(
            r'^https?://t\.me/'
            r'(?:c/\d+|[a-zA-Z][\w-]*)'  # Channel: c/123456 or username (must start with letter)
            r'/\d+'                       # First message ID
            r'(?:/\d+)*'                 # Optional additional message IDs
            r'(?:\?(?:comment|thread)=\d+)?$',  # Optional query params
            re.IGNORECASE
        )

        return bool(pattern.match(url))

    def get_urls(self) -> list[str]:
        """Get all URLs from the list"""
        urls = []
        for i in range(self.url_list.count()):
            urls.append(self.url_list.item(i).text())
        return urls

    def set_urls(self, urls: list[str]):
        """Set URLs in the list"""
        self.url_list.clear()
        for url in urls:
            if url.strip():
                item = QListWidgetItem(url.strip())
                self.url_list.addItem(item)
        self.update_status()

    def update_status(self):
        """Update the status label based on current URLs"""
        count = self.url_list.count()
        if count == 0:
            self.status_label.setText("📝 Add Telegram message URLs to download")
            self.clear_button.setEnabled(False)
        elif count == 1:
            self.status_label.setText(f"📥 1 URL ready for download")
            self.clear_button.setEnabled(True)
        else:
            self.status_label.setText(f"📥 {count} URLs ready for download")
            self.clear_button.setEnabled(True)

    def add_urls_from_text(self, text: str):
        """Add URLs from pasted text"""
        urls = [line.strip() for line in text.split('\n') if line.strip()]
        valid_urls = []
        invalid_urls = []

        for url in urls:
            if self.validate_url(url):
                # Check for duplicates
                if not any(self.url_list.item(i).text() == url for i in range(self.url_list.count())):
                    valid_urls.append(url)
            else:
                invalid_urls.append(url)

        # Add valid URLs
        for url in valid_urls:
            item = QListWidgetItem(url)
            self.url_list.addItem(item)

        # Show results
        if valid_urls:
            self.urls_changed.emit()

        if invalid_urls:
            QMessageBox.warning(
                self,
                "Some URLs were invalid",
                f"The following URLs were not added:\n\n" +
                "\n".join(invalid_urls[:5]) +
                ("\n..." if len(invalid_urls) > 5 else "")
            )

        self.update_status()

    def focus_to_input(self):
        """Set focus to the URL input field"""
        self.url_input.setFocus()
        self.url_input.selectAll()