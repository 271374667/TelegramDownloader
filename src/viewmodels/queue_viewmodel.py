"""Queue ViewModel – exposes download-queue state to QML as ``queueVM``."""

import os

from PySide6.QtCore import QObject, Signal, Slot, Property


class QueueViewModel(QObject):
    """Manages the list of queued download batches and related folder paths."""

    queueDirChanged = Signal()
    outputDirChanged = Signal()
    queueListChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._queue_dir = os.path.join(os.getcwd(), "queues")
        self._output_dir = os.path.join(os.getcwd(), "downloads")
        self._queue_list: list[dict] = []
        self._refresh()

    # ── Internal ────────────────────────────────────────────────────

    def _refresh(self):
        from core.queue_manager import list_queues
        self._queue_list = list_queues(self._queue_dir)
        self.queueListChanged.emit()

    def _set(self, attr, value, signal):
        if getattr(self, attr) != value:
            setattr(self, attr, value)
            signal.emit()

    # ── Slots ────────────────────────────────────────────────────────

    @Slot()
    def refreshQueues(self):
        self._refresh()

    @Slot(str, result=bool)
    def nameExists(self, name: str) -> bool:
        from core.queue_manager import queue_name_exists
        return queue_name_exists(name.strip(), self._queue_dir)

    @Slot(str)
    def deleteQueue(self, name: str):
        from core.queue_manager import delete_queue
        delete_queue(name.strip(), self._queue_dir)
        self._refresh()

    # ── Properties ──────────────────────────────────────────────────

    def _get_queueDir(self): return self._queue_dir
    def _set_queueDir(self, v):
        if self._queue_dir != v:
            self._queue_dir = v
            self.queueDirChanged.emit()
            self._refresh()
    queueDir = Property(str, _get_queueDir, _set_queueDir, notify=queueDirChanged)

    def _get_outputDir(self): return self._output_dir
    def _set_outputDir(self, v): self._set("_output_dir", v, self.outputDirChanged)
    outputDir = Property(str, _get_outputDir, _set_outputDir, notify=outputDirChanged)

    def _get_queueCount(self): return len(self._queue_list)
    queueCount = Property(int, _get_queueCount, notify=queueListChanged)

    def _get_queueList(self):
        return [
            {
                "name": q["name"],
                "urlCount": len(q["urls"]),
                "createdAt": q.get("created_at", ""),
                "uuidSegment": q.get("uuid_segment", ""),
            }
            for q in self._queue_list
        ]
    queueList = Property("QVariantList", _get_queueList, notify=queueListChanged)
