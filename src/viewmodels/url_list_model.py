"""URL list model for QML ListView - MVVM Model layer"""

import re
from PySide6.QtCore import (
    QAbstractListModel, QModelIndex, Qt, Signal, Slot, Property
)


class UrlListModel(QAbstractListModel):
    """QAbstractListModel exposing Telegram URLs to QML."""

    UrlRole = Qt.UserRole + 1

    countChanged = Signal()
    urlsChanged = Signal()
    statusTextChanged = Signal()

    _URL_VALIDATE = re.compile(
        r'^https://t\.me/'
        r'(?:c/\d+|\w[\w-]*)'
        r'/\d+'
        r'(?:/\d+)*'
        r'(?:\?(?:comment|thread)=\d+)?$',
        re.IGNORECASE,
    )

    _URL_EXTRACT = re.compile(
        r'https?://t\.me/'
        r'(?:c/\d+|[\w][\w-]*)'
        r'/\d+'
        r'(?:/\d+)*'
        r'(?:\?(?:comment|thread)=\d+)?',
        re.IGNORECASE,
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self._urls: list[str] = []

    # ── Qt model interface ──────────────────────────────────────────

    def roleNames(self):
        return {self.UrlRole: b"url", Qt.DisplayRole: b"display"}

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._urls)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._urls):
            return None
        if role in (self.UrlRole, Qt.DisplayRole):
            return self._urls[index.row()]
        return None

    # ── Slots for QML ───────────────────────────────────────────────

    @Slot(str, result=bool)
    def addUrl(self, url: str) -> bool:
        url = url.strip()
        if not url or not self._URL_VALIDATE.match(url) or url in self._urls:
            return False
        pos = len(self._urls)
        self.beginInsertRows(QModelIndex(), pos, pos)
        self._urls.append(url)
        self.endInsertRows()
        self._notify()
        return True

    @Slot(int)
    def removeUrl(self, index: int):
        if 0 <= index < len(self._urls):
            self.beginRemoveRows(QModelIndex(), index, index)
            self._urls.pop(index)
            self.endRemoveRows()
            self._notify()

    @Slot(int, str, result=bool)
    def editUrl(self, index: int, new_url: str) -> bool:
        new_url = new_url.strip()
        if not (0 <= index < len(self._urls)):
            return False
        if not self._URL_VALIDATE.match(new_url):
            return False
        if new_url in self._urls and self._urls[index] != new_url:
            return False
        self._urls[index] = new_url
        mi = self.index(index)
        self.dataChanged.emit(mi, mi, [self.UrlRole])
        self._notify()
        return True

    @Slot()
    def clear(self):
        if not self._urls:
            return
        self.beginResetModel()
        self._urls.clear()
        self.endResetModel()
        self._notify()

    @Slot(str, result=int)
    def addUrlsFromText(self, text: str) -> int:
        urls = self._URL_EXTRACT.findall(text)
        added = 0
        for url in urls:
            normalized = url.strip()
            if normalized.startswith("http://"):
                normalized = "https://" + normalized[7:]
            if self.addUrl(normalized):
                added += 1
        return added

    _PRIVATE_RE = re.compile(r'https?://t\.me/c/(\d+)/(\d+)', re.IGNORECASE)
    _PUBLIC_RE  = re.compile(r'https?://t\.me/([A-Za-z0-9_]{4,})/(\d+)', re.IGNORECASE)

    @Slot(str, str, result=str)
    def addRange(self, start_url: str, end_url: str) -> str:
        """Generate all URLs between start and end (inclusive) and add them.

        Both URLs must be from the same chat.
        Returns a result message string (success or error).
        """
        start_url = start_url.strip()
        end_url   = end_url.strip()

        def _parse(url):
            m = self._PRIVATE_RE.search(url)
            if m:
                return ("c/" + m.group(1), int(m.group(2)), f"https://t.me/c/{m.group(1)}/{{id}}")
            m = self._PUBLIC_RE.search(url)
            if m:
                return (m.group(1), int(m.group(2)), f"https://t.me/{m.group(1)}/{{id}}")
            return None

        r1 = _parse(start_url)
        r2 = _parse(end_url)

        if r1 is None or r2 is None:
            return "无法解析链接，请检查格式"
        if r1[0] != r2[0]:
            return "两个链接必须来自同一个频道"

        chat_key, id1, tmpl = r1
        _, id2, _           = r2

        min_id, max_id = min(id1, id2), max(id1, id2)
        if max_id - min_id > 5000:
            return f"范围过大（{max_id - min_id + 1} 条），最多支持 5000 条"

        added = 0
        for mid in range(min_id, max_id + 1):
            url = tmpl.format(id=mid)
            if self.addUrl(url):
                added += 1

        skipped = (max_id - min_id + 1) - added
        msg = f"已添加 {added} 个链接（共 {max_id - min_id + 1} 条"
        if skipped:
            msg += f"，{skipped} 条已存在跳过"
        return msg + "）"

    @Slot(result=str)
    def exportToText(self) -> str:
        return "\n".join(self._urls)

    @Slot(str, result=bool)
    def validateUrl(self, url: str) -> bool:
        return bool(self._URL_VALIDATE.match(url.strip()))

    # ── Python helpers ──────────────────────────────────────────────

    def get_urls(self) -> list[str]:
        return list(self._urls)

    def set_urls(self, urls: list[str]):
        self.beginResetModel()
        self._urls = list(urls)
        self.endResetModel()
        self._notify()

    def _notify(self):
        self.countChanged.emit()
        self.urlsChanged.emit()
        self.statusTextChanged.emit()

    # ── QML Properties ──────────────────────────────────────────────

    def _get_count(self):
        return len(self._urls)

    count = Property(int, _get_count, notify=countChanged)

    def _get_status_text(self):
        n = len(self._urls)
        return f"{n} 个链接" if n else "暂无链接"

    statusText = Property(str, _get_status_text, notify=statusTextChanged)
