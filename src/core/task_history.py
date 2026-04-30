"""Task history management with persist-queue backed crash recovery.

Architecture:
- In-progress task: stored in persistqueue.SQLiteAckQueue so app crashes don't lose it
- Completed history: JSON file (capped at max_history entries, default 20)
"""

import datetime
import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import persistqueue

# ── Status constants ─────────────────────────────────────────────────────────

STATUS_RUNNING   = "running"
STATUS_COMPLETED = "completed"
STATUS_PARTIAL   = "partial"    # some files missing
STATUS_FAILED    = "failed"     # all or most files missing / download error


# ── TaskRecord ───────────────────────────────────────────────────────────────

class TaskRecord:
    """Represents one download task."""

    def __init__(
        self,
        task_id: str,
        urls: List[str],
        download_dir: str,
        created_at: float = None,
    ):
        self.id            = task_id
        self.urls          = list(urls)
        self.download_dir  = download_dir
        self.created_at    = created_at or time.time()
        self.status        = STATUS_RUNNING
        self.expected_count   = 0
        self.downloaded_count = 0
        self.expected_files: List[Dict] = []   # [{id, file, chat, url}, ...]
        self.failed_urls:    List[str]  = []   # URLs whose files are missing
        self.new_files:      List[str]  = []   # relative paths of downloaded files

    # ── Serialization ─────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "urls":             self.urls,
            "download_dir":     self.download_dir,
            "created_at":       self.created_at,
            "status":           self.status,
            "expected_count":   self.expected_count,
            "downloaded_count": self.downloaded_count,
            "expected_files":   self.expected_files,
            "failed_urls":      self.failed_urls,
            "new_files":        self.new_files,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TaskRecord":
        task = cls(
            task_id      = d.get("id", str(uuid.uuid4())),
            urls         = d.get("urls", []),
            download_dir = d.get("download_dir", ""),
            created_at   = d.get("created_at", 0.0),
        )
        task.status           = d.get("status", STATUS_FAILED)
        task.expected_count   = d.get("expected_count", 0)
        task.downloaded_count = d.get("downloaded_count", 0)
        task.expected_files   = d.get("expected_files", [])
        task.failed_urls      = d.get("failed_urls", [])
        task.new_files        = d.get("new_files", [])
        return task

    # ── Display helpers ────────────────────────────────────────────────────

    @property
    def status_label(self) -> str:
        return {
            STATUS_RUNNING:   "下载中",
            STATUS_COMPLETED: "已完成",
            STATUS_PARTIAL:   "部分失败",
            STATUS_FAILED:    "失败",
        }.get(self.status, self.status)

    @property
    def has_failures(self) -> bool:
        return self.status in (STATUS_PARTIAL, STATUS_FAILED)

    @property
    def summary(self) -> str:
        if self.expected_count > 0:
            return f"{self.downloaded_count}/{self.expected_count} 个文件"
        if self.downloaded_count > 0:
            return f"新增 {self.downloaded_count} 个文件"
        return f"共 {len(self.urls)} 条链接"

    @property
    def display_time(self) -> str:
        dt = datetime.datetime.fromtimestamp(self.created_at)
        return dt.strftime("%m-%d %H:%M")

    @property
    def title(self) -> str:
        if not self.urls:
            return "空任务"
        u = self.urls[0]
        m = re.search(r"t\.me/c/(\d+)/", u)
        if m:
            name = f"私有频道 {m.group(1)}"
        else:
            m = re.search(r"t\.me/([^/]+)/", u)
            name = m.group(1) if m else u
        n = len(self.urls)
        suffix = f" 等{n}条" if n > 1 else ""
        return f"{name}{suffix}"

    @property
    def retry_urls(self) -> List[str]:
        """URLs to use when retrying only failed items."""
        return self.failed_urls if self.failed_urls else self.urls


# ── TaskHistoryManager ────────────────────────────────────────────────────────

class TaskHistoryManager:
    """Manages download task history.

    - Uses ``persistqueue.SQLiteAckQueue`` for crash-safe in-progress task storage.
    - Uses a JSON file for completed task history (capped at max_history entries).
    """

    HISTORY_FILE = "tasks_history.json"
    QUEUE_DIR    = "task_queue"

    def __init__(self, data_dir: str, max_history: int = 20):
        self._data_dir     = Path(data_dir)
        self._max_history  = max_history
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._history_path = self._data_dir / self.HISTORY_FILE
        self._history: List[TaskRecord] = self._load_history()

        queue_path = str(self._data_dir / self.QUEUE_DIR)
        self._queue = persistqueue.SQLiteAckQueue(
            path=queue_path,
            name="downloads",
            auto_commit=True,
            multithreading=True,
        )

        # On startup, any unacknowledged tasks from a previous crash → mark failed
        self._recover_crashed_tasks()

    # ── Persistence ────────────────────────────────────────────────────────

    def _load_history(self) -> List[TaskRecord]:
        if not self._history_path.exists():
            return []
        try:
            with open(self._history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [TaskRecord.from_dict(d) for d in data]
        except Exception:
            return []

    def _save_history(self):
        data = [t.to_dict() for t in self._history]
        with open(self._history_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ── Crash recovery ─────────────────────────────────────────────────────

    def _recover_crashed_tasks(self):
        """Mark unacknowledged in-progress tasks from last run as failed."""
        recovered = []
        try:
            while not self._queue.empty():
                item = self._queue.get(block=False)
                task = TaskRecord.from_dict(item)
                task.status = STATUS_FAILED
                recovered.append(task)
                self._queue.ack(item)
        except Exception:
            pass

        for task in recovered:
            self._add_to_history(task)

    # ── Public API ─────────────────────────────────────────────────────────

    def begin_task(self, urls: List[str], download_dir: str) -> TaskRecord:
        """Create a new task and register it in the persistent queue."""
        task = TaskRecord(
            task_id      = str(uuid.uuid4()),
            urls         = urls,
            download_dir = download_dir,
        )
        self._queue.put(task.to_dict())
        return task

    def complete_task(self, task: TaskRecord):
        """Acknowledge the active task from the queue and move it to history."""
        # Drain the queue (should have exactly one item – the current task)
        try:
            while not self._queue.empty():
                item = self._queue.get(block=False)
                self._queue.ack(item)
        except Exception:
            pass
        self._add_to_history(task)

    def _add_to_history(self, task: TaskRecord):
        self._history.insert(0, task)
        self._history = self._history[: self._max_history]
        self._save_history()

    def get_history(self) -> List[TaskRecord]:
        return list(self._history)

    @property
    def max_history(self) -> int:
        return self._max_history

    def update_max_history(self, n: int):
        self._max_history = max(1, n)
        self._history = self._history[: self._max_history]
        self._save_history()
