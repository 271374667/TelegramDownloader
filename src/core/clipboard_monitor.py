"""
Clipboard monitor for Telegram Downloader GUI
Monitors clipboard for new Telegram URLs and notifies the application
"""

import re
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication


class ClipboardMonitor(QObject):
    """
    Monitors the system clipboard for new Telegram URLs.

    Signals:
        new_urls_detected(list): Emitted when new valid URLs are found in clipboard
    """

    new_urls_detected = Signal(list)  # List of new URLs detected

    # Regex pattern for Telegram URLs
    # Supports formats:
    # - https://t.me/telegram/193
    # - https://t.me/c/1697797156/151
    # - https://t.me/iFreeKnow/45662/55005
    # - https://t.me/c/1492447836/251015/251021
    # - https://t.me/opencfdchannel/4434?comment=360409
    # - https://t.me/myhostloc/1485524?thread=1485523
    URL_PATTERN = re.compile(
        r'https?://t\.me/'
        r'(?:c/\d+|\w[\w-]*)'  # Channel: c/123456 or username
        r'/\d+'                 # First message ID
        r'(?:/\d+)*'           # Optional additional message IDs
        r'(?:\?(?:comment|thread)=\d+)?',  # Optional query params
        re.IGNORECASE
    )

    def __init__(self, check_interval_ms: int = 1000, parent=None):
        """
        Initialize the clipboard monitor.

        Args:
            check_interval_ms: Interval in milliseconds to check clipboard (default: 1000ms)
            parent: Parent QObject
        """
        super().__init__(parent)

        self.check_interval = check_interval_ms
        self.is_monitoring = False
        self.known_urls = set()  # URLs we've already seen
        self.last_clipboard_text = ""

        # Timer for periodic clipboard checking
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_clipboard)

    def start(self):
        """Start monitoring the clipboard."""
        if not self.is_monitoring:
            self.is_monitoring = True
            # Initialize with current clipboard content to avoid immediate detection
            self._initialize_clipboard_state()
            self.timer.start(self.check_interval)

    def stop(self):
        """Stop monitoring the clipboard."""
        if self.is_monitoring:
            self.is_monitoring = False
            self.timer.stop()

    def is_running(self) -> bool:
        """Check if the monitor is currently running."""
        return self.is_monitoring

    def add_known_urls(self, urls: list):
        """
        Add URLs to the known set (won't be detected again).

        Args:
            urls: List of URLs to mark as known
        """
        for url in urls:
            normalized = self._normalize_url(url)
            if normalized:
                self.known_urls.add(normalized)

    def clear_known_urls(self):
        """Clear all known URLs."""
        self.known_urls.clear()

    def sync_known_urls(self, current_urls: list):
        """
        Sync known URLs with the current URL list.
        This removes URLs from known_urls that are no longer in the list,
        allowing them to be detected again if copied.

        Args:
            current_urls: List of URLs currently in the URL list
        """
        # Normalize current URLs
        normalized_current = set()
        for url in current_urls:
            normalized = self._normalize_url(url)
            if normalized:
                normalized_current.add(normalized)

        # Keep only URLs that are still in the current list
        self.known_urls = normalized_current.copy()

    def set_check_interval(self, interval_ms: int):
        """
        Set the clipboard check interval.

        Args:
            interval_ms: Interval in milliseconds
        """
        self.check_interval = interval_ms
        if self.is_monitoring:
            self.timer.setInterval(interval_ms)

    def _initialize_clipboard_state(self):
        """Initialize the clipboard state to avoid detecting existing content."""
        clipboard = QApplication.clipboard()
        self.last_clipboard_text = clipboard.text()

        # Extract and mark existing URLs as known
        existing_urls = self._extract_urls(self.last_clipboard_text)
        for url in existing_urls:
            self.known_urls.add(url)

    def _check_clipboard(self):
        """Check clipboard for new Telegram URLs."""
        if not self.is_monitoring:
            return

        clipboard = QApplication.clipboard()
        current_text = clipboard.text()

        # Only process if clipboard content changed
        if current_text == self.last_clipboard_text:
            return

        self.last_clipboard_text = current_text

        # Extract URLs from clipboard
        found_urls = self._extract_urls(current_text)

        # Filter out already known URLs
        new_urls = []
        for url in found_urls:
            if url not in self.known_urls:
                new_urls.append(url)
                self.known_urls.add(url)

        # Emit signal if new URLs found
        if new_urls:
            self.new_urls_detected.emit(new_urls)

    def _extract_urls(self, text: str) -> list:
        """
        Extract Telegram URLs from text.

        Args:
            text: Text to search for URLs

        Returns:
            List of found URLs (normalized)
        """
        if not text:
            return []

        matches = self.URL_PATTERN.findall(text)

        # Normalize and deduplicate
        urls = []
        seen = set()
        for url in matches:
            normalized = self._normalize_url(url)
            if normalized and normalized not in seen:
                urls.append(normalized)
                seen.add(normalized)

        return urls

    def _normalize_url(self, url: str) -> str:
        """
        Normalize a URL for consistent comparison.

        Args:
            url: URL to normalize

        Returns:
            Normalized URL or empty string if invalid
        """
        if not url:
            return ""

        url = url.strip()

        # Ensure https://
        if url.startswith("http://t.me/"):
            url = "https://t.me/" + url[12:]
        elif not url.startswith("https://t.me/"):
            return ""

        return url

    @staticmethod
    def validate_telegram_url(url: str) -> bool:
        """
        Validate if a string is a valid Telegram URL.

        Args:
            url: URL to validate

        Returns:
            True if valid, False otherwise
        """
        if not url:
            return False

        url = url.strip()

        # Must start with https://t.me/
        if not url.startswith("https://t.me/"):
            # Try http
            if url.startswith("http://t.me/"):
                url = "https://t.me/" + url[12:]
            else:
                return False

        return bool(ClipboardMonitor.URL_PATTERN.match(url))
