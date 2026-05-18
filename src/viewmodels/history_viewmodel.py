"""QML ViewModel for the task history panel.

Exposed to QML as ``historyVM``.
"""

import json
from typing import List

from PySide6.QtCore import (
    QAbstractListModel, QModelIndex, Qt, Signal, Slot, Property, QObject
)

from core.task_history import TaskHistoryManager, TaskRecord


# ── List Model ────────────────────────────────────────────────────────────────

class HistoryListModel(QAbstractListModel):
    """Flat list model of TaskRecords for use in QML Repeater / ListView."""

    IdRole          = Qt.UserRole + 1
    TitleRole       = Qt.UserRole + 2
    StatusRole      = Qt.UserRole + 3
    StatusLabelRole = Qt.UserRole + 4
    SummaryRole     = Qt.UserRole + 5
    TimeRole        = Qt.UserRole + 6
    HasFailuresRole = Qt.UserRole + 7
    UrlCountRole    = Qt.UserRole + 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks: List[TaskRecord] = []

    def set_tasks(self, tasks: List[TaskRecord]):
        self.beginResetModel()
        self._tasks = list(tasks)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._tasks)

    def roleNames(self):
        return {
            self.IdRole:          b"taskId",
            self.TitleRole:       b"taskTitle",
            self.StatusRole:      b"taskStatus",
            self.StatusLabelRole: b"taskStatusLabel",
            self.SummaryRole:     b"taskSummary",
            self.TimeRole:        b"taskTime",
            self.HasFailuresRole: b"hasFailures",
            self.UrlCountRole:    b"urlCount",
        }

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._tasks):
            return None
        t = self._tasks[index.row()]
        if role == self.IdRole:          return t.id
        if role == self.TitleRole:       return t.title
        if role == self.StatusRole:      return t.status
        if role == self.StatusLabelRole: return t.status_label
        if role == self.SummaryRole:     return t.summary
        if role == self.TimeRole:        return t.display_time
        if role == self.HasFailuresRole: return t.has_failures
        if role == self.UrlCountRole:    return len(t.urls)
        return None


# ── ViewModel ─────────────────────────────────────────────────────────────────

class HistoryViewModel(QObject):
    """Exposed to QML as ``historyVM``."""

    historyChanged     = Signal()
    maxHistoryChanged  = Signal()
    failedCountChanged = Signal()

    # Emitted when user requests a re-download from history
    # args: urls_json (JSON string of URL list), retry_failed_only (bool), task_id
    retryRequested = Signal(str, bool, str)

    def __init__(self, manager: TaskHistoryManager, parent=None):
        super().__init__(parent)
        self._manager = manager
        self._model   = HistoryListModel(parent=self)
        self._refresh_model()

    # ── Internal ──────────────────────────────────────────────────────────

    def _refresh_model(self):
        tasks = self._manager.get_history()
        self._model.set_tasks(tasks)

    def _find_task(self, task_id: str) -> TaskRecord:
        for t in self._manager.get_history():
            if t.id == task_id:
                return t
        return None

    # ── Properties ───────────────────────────────────────────────────────

    def _get_model(self) -> HistoryListModel:
        return self._model

    historyModel = Property(QObject, _get_model, notify=historyChanged)

    def _get_failed_count(self) -> int:
        return sum(1 for t in self._manager.get_history() if t.has_failures)

    failedCount = Property(int, _get_failed_count, notify=failedCountChanged)

    def _get_max_history(self) -> int:
        return self._manager.max_history

    def _set_max_history(self, n: int):
        self._manager.update_max_history(n)
        self._refresh_model()
        self.maxHistoryChanged.emit()
        self.historyChanged.emit()

    maxHistory = Property(int, _get_max_history, _set_max_history, notify=maxHistoryChanged)

    def _get_count(self) -> int:
        return self._model.rowCount()

    count = Property(int, _get_count, notify=historyChanged)

    # ── Slots (called by Python after task completes) ─────────────────────

    @Slot()
    def refresh(self):
        """Reload history from disk and update the model."""
        self._refresh_model()
        self.historyChanged.emit()
        self.failedCountChanged.emit()

    # ── Slots (called from QML) ───────────────────────────────────────────

    @Slot(str)
    def retryFailedItems(self, task_id: str):
        """Emit retryRequested with only the failed URLs from this task."""
        task = self._find_task(task_id)
        if task is None:
            return
        urls = task.retry_urls
        self.retryRequested.emit(json.dumps(urls, ensure_ascii=False), True, task.id)

    @Slot(str)
    def restartTask(self, task_id: str):
        """Emit retryRequested with all URLs from this task (full restart)."""
        task = self._find_task(task_id)
        if task is None:
            return
        self.retryRequested.emit(json.dumps(task.urls, ensure_ascii=False), False, task.id)

    @Slot(str)
    def deleteTask(self, task_id: str):
        """Delete a task from history."""
        self._manager.delete_task(task_id)
        self.refresh()
