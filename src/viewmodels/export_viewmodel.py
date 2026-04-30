"""Export configuration ViewModel for QML binding."""

import os
from PySide6.QtCore import QObject, Signal, Slot, Property
from core.config_manager import ExportConfig


class ExportViewModel(QObject):
    """Exposes ExportConfig fields as QML-bindable properties (exportVM)."""

    # ── Signals ─────────────────────────────────────────────────────
    chatChanged = Signal()
    outputChanged = Signal()
    topicEnabledChanged = Signal()
    topicIdChanged = Signal()
    replyEnabledChanged = Signal()
    replyPostIdChanged = Signal()
    rangeEnabledChanged = Signal()
    rangeTypeChanged = Signal()
    rangeStartChanged = Signal()
    rangeEndChanged = Signal()
    filterEnabledChanged = Signal()
    filterExprChanged = Signal()
    withContentChanged = Signal()
    rawChanged = Signal()
    allMessagesChanged = Signal()

    configChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._chat = ""
        self._output = "tdl-export.json"
        self._topicEnabled = False
        self._topicId = 0
        self._replyEnabled = False
        self._replyPostId = 0
        self._rangeEnabled = False
        self._rangeType = "time"   # "time" | "id" | "last"
        self._rangeStart = ""
        self._rangeEnd = ""
        self._filterEnabled = False
        self._filterExpr = ""
        self._withContent = False
        self._raw = False
        self._allMessages = False

    def _set(self, attr, value, signal):
        if getattr(self, attr) != value:
            setattr(self, attr, value)
            signal.emit()
            self.configChanged.emit()

    def get_config(self) -> ExportConfig:
        return ExportConfig(
            chat=self._chat,
            output=self._output,
            topic_enabled=self._topicEnabled,
            topic_id=self._topicId,
            reply_enabled=self._replyEnabled,
            reply_post_id=self._replyPostId,
            range_enabled=self._rangeEnabled,
            range_type=self._rangeType,
            range_start=self._rangeStart,
            range_end=self._rangeEnd,
            filter_enabled=self._filterEnabled,
            filter_expr=self._filterExpr,
            with_content=self._withContent,
            raw=self._raw,
            all_messages=self._allMessages,
        )

    # ── Properties ───────────────────────────────────────────────────

    def _get_chat(self): return self._chat
    def _set_chat(self, v): self._set("_chat", v, self.chatChanged)
    chat = Property(str, _get_chat, _set_chat, notify=chatChanged)

    def _get_output(self): return self._output
    def _set_output(self, v): self._set("_output", v, self.outputChanged)
    output = Property(str, _get_output, _set_output, notify=outputChanged)

    def _get_topicEnabled(self): return self._topicEnabled
    def _set_topicEnabled(self, v): self._set("_topicEnabled", v, self.topicEnabledChanged)
    topicEnabled = Property(bool, _get_topicEnabled, _set_topicEnabled, notify=topicEnabledChanged)

    def _get_topicId(self): return self._topicId
    def _set_topicId(self, v): self._set("_topicId", int(v), self.topicIdChanged)
    topicId = Property(int, _get_topicId, _set_topicId, notify=topicIdChanged)

    def _get_replyEnabled(self): return self._replyEnabled
    def _set_replyEnabled(self, v): self._set("_replyEnabled", v, self.replyEnabledChanged)
    replyEnabled = Property(bool, _get_replyEnabled, _set_replyEnabled, notify=replyEnabledChanged)

    def _get_replyPostId(self): return self._replyPostId
    def _set_replyPostId(self, v): self._set("_replyPostId", int(v), self.replyPostIdChanged)
    replyPostId = Property(int, _get_replyPostId, _set_replyPostId, notify=replyPostIdChanged)

    def _get_rangeEnabled(self): return self._rangeEnabled
    def _set_rangeEnabled(self, v): self._set("_rangeEnabled", v, self.rangeEnabledChanged)
    rangeEnabled = Property(bool, _get_rangeEnabled, _set_rangeEnabled, notify=rangeEnabledChanged)

    def _get_rangeType(self): return self._rangeType
    def _set_rangeType(self, v): self._set("_rangeType", v, self.rangeTypeChanged)
    rangeType = Property(str, _get_rangeType, _set_rangeType, notify=rangeTypeChanged)

    def _get_rangeStart(self): return self._rangeStart
    def _set_rangeStart(self, v): self._set("_rangeStart", v, self.rangeStartChanged)
    rangeStart = Property(str, _get_rangeStart, _set_rangeStart, notify=rangeStartChanged)

    def _get_rangeEnd(self): return self._rangeEnd
    def _set_rangeEnd(self, v): self._set("_rangeEnd", v, self.rangeEndChanged)
    rangeEnd = Property(str, _get_rangeEnd, _set_rangeEnd, notify=rangeEndChanged)

    def _get_filterEnabled(self): return self._filterEnabled
    def _set_filterEnabled(self, v): self._set("_filterEnabled", v, self.filterEnabledChanged)
    filterEnabled = Property(bool, _get_filterEnabled, _set_filterEnabled, notify=filterEnabledChanged)

    def _get_filterExpr(self): return self._filterExpr
    def _set_filterExpr(self, v): self._set("_filterExpr", v, self.filterExprChanged)
    filterExpr = Property(str, _get_filterExpr, _set_filterExpr, notify=filterExprChanged)

    def _get_withContent(self): return self._withContent
    def _set_withContent(self, v): self._set("_withContent", v, self.withContentChanged)
    withContent = Property(bool, _get_withContent, _set_withContent, notify=withContentChanged)

    def _get_raw(self): return self._raw
    def _set_raw(self, v): self._set("_raw", v, self.rawChanged)
    raw = Property(bool, _get_raw, _set_raw, notify=rawChanged)

    def _get_allMessages(self): return self._allMessages
    def _set_allMessages(self, v): self._set("_allMessages", v, self.allMessagesChanged)
    allMessages = Property(bool, _get_allMessages, _set_allMessages, notify=allMessagesChanged)

    # ── Convenience slots ────────────────────────────────────────────

    @Slot()
    def resetDefaults(self):
        cfg = ExportConfig()
        self._set("_chat", cfg.chat, self.chatChanged)
        self._set("_output", cfg.output, self.outputChanged)
        self._set("_topicEnabled", cfg.topic_enabled, self.topicEnabledChanged)
        self._set("_topicId", cfg.topic_id, self.topicIdChanged)
        self._set("_replyEnabled", cfg.reply_enabled, self.replyEnabledChanged)
        self._set("_replyPostId", cfg.reply_post_id, self.replyPostIdChanged)
        self._set("_rangeEnabled", cfg.range_enabled, self.rangeEnabledChanged)
        self._set("_rangeType", cfg.range_type, self.rangeTypeChanged)
        self._set("_rangeStart", cfg.range_start, self.rangeStartChanged)
        self._set("_rangeEnd", cfg.range_end, self.rangeEndChanged)
        self._set("_filterEnabled", cfg.filter_enabled, self.filterEnabledChanged)
        self._set("_filterExpr", cfg.filter_expr, self.filterExprChanged)
        self._set("_withContent", cfg.with_content, self.withContentChanged)
        self._set("_raw", cfg.raw, self.rawChanged)
        self._set("_allMessages", cfg.all_messages, self.allMessagesChanged)
