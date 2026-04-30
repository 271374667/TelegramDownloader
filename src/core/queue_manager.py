"""Queue management for deferred download batches.

A "queue" is a named JSON file that stores a list of Telegram URLs for later
bulk download.  The file is saved as  ``{queues_dir}/{safe_name}.json``.
"""

import json
import os
import re
import uuid
from datetime import datetime
from typing import List, Tuple

QUEUES_DEFAULT_DIR = "queues"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_queue(
    name: str,
    urls: List[str],
    queues_dir: str = QUEUES_DEFAULT_DIR,
) -> Tuple[bool, str]:
    """Persist a named queue to disk.

    Returns (True, success_msg) on success or (False, error_msg) on failure.
    UUID format: xxxxxxxx-xxxx-XXXX-xxxx-xxxxxxxxxxxx
    The folder suffix uses the **3rd dash-separated group** (the 2nd 4-char group),
    e.g. ``71f7b3a8-b75d-4c3f-b0b3-…`` → suffix ``4c3f``.
    """
    os.makedirs(queues_dir, exist_ok=True)
    fname = _safe_filename(name)
    path = os.path.join(queues_dir, f"{fname}.json")
    if os.path.exists(path):
        return False, f"队列「{name}」已存在，请换一个名称"
    uid = str(uuid.uuid4())
    seg = uid.split("-")[2]          # 3rd group → 2nd 4-char group
    data = {
        "name": name,
        "uuid_segment": seg,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "urls": urls,
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        return False, f"写入失败: {exc}"
    return True, f"已保存队列「{name}」（{len(urls)} 个链接）"


def list_queues(queues_dir: str = QUEUES_DEFAULT_DIR) -> List[dict]:
    """Return all valid queue dicts from *queues_dir*, sorted by filename."""
    if not os.path.isdir(queues_dir):
        return []
    result: List[dict] = []
    for fname in sorted(os.listdir(queues_dir)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(queues_dir, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "name" in data and "urls" in data:
                data.setdefault("uuid_segment", "0000")
                data.setdefault("created_at", "")
                result.append(data)
        except Exception:
            pass
    return result


def queue_name_exists(name: str, queues_dir: str = QUEUES_DEFAULT_DIR) -> bool:
    fname = _safe_filename(name)
    return os.path.exists(os.path.join(queues_dir, f"{fname}.json"))


def delete_queue(name: str, queues_dir: str = QUEUES_DEFAULT_DIR) -> bool:
    fname = _safe_filename(name)
    path = os.path.join(queues_dir, f"{fname}.json")
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _safe_filename(name: str) -> str:
    """Strip filesystem-unsafe characters; keep letters, digits, CJK, spaces → underscore."""
    safe = re.sub(r'[\\/:*?"<>|]', "_", name).strip()
    return safe or "unnamed"
