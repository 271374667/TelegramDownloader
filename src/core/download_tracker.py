"""Download tracking utilities.

- Parse Telegram share URLs to extract chat/message IDs
- Run tdl chat export to get expected file list before download
- Take directory snapshots for before/after comparison to detect downloaded files
- Determine which URLs failed to download
"""

import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple


# ── URL parsing ─────────────────────────────────────────────────────────────

_PRIVATE_URL_RE = re.compile(r"https?://t\.me/c/(\d+)/(\d+)")
_PUBLIC_URL_RE  = re.compile(r"https?://t\.me/([A-Za-z0-9_]{4,})/(\d+)")


def parse_url(url: str) -> Optional[Tuple[str, int]]:
    """Parse a Telegram share URL into (chat_id_str, message_id).

    Private channels: chat_id_str = "-100<channel_id>"
    Public  channels: chat_id_str = "<username>"
    Returns None if not parseable.
    """
    url = url.strip()
    m = _PRIVATE_URL_RE.search(url)
    if m:
        return f"-100{m.group(1)}", int(m.group(2))
    m = _PUBLIC_URL_RE.search(url)
    if m:
        return m.group(1), int(m.group(2))
    return None


def group_urls_by_chat(urls: List[str]) -> Dict[str, List[Tuple[int, str]]]:
    """Group (message_id, original_url) pairs by chat identifier."""
    groups: Dict[str, List[Tuple[int, str]]] = {}
    for url in urls:
        result = parse_url(url)
        if result:
            chat_id, msg_id = result
            groups.setdefault(chat_id, []).append((msg_id, url))
    return groups


# ── Directory snapshot ───────────────────────────────────────────────────────

def snapshot_directory(directory: str) -> Dict[str, int]:
    """Return {relative_path: file_size} for all files in directory."""
    result: Dict[str, int] = {}
    base = Path(directory)
    if not base.exists():
        return result
    for p in base.rglob("*"):
        if p.is_file():
            try:
                result[str(p.relative_to(base))] = p.stat().st_size
            except Exception:
                pass
    return result


def get_new_files(before: Dict[str, int], after: Dict[str, int]) -> List[str]:
    """Return relative paths of files that appeared (or grew) after download."""
    new = []
    for path, size in after.items():
        if path not in before:
            new.append(path)
        elif size > before[path]:
            # File size increased – re-downloaded / completed partial file
            new.append(path)
    return new


# ── Chat export ──────────────────────────────────────────────────────────────

def run_chat_export(
    tdl_path: str,
    chat_id: str,
    min_id: int,
    max_id: int,
    session_args: List[str],
    output_path: str,
    timeout: int = 90,
) -> List[Dict]:
    """Run ``tdl chat export -T id -i min_id,max_id`` and return all media records.

    Uses a single range query (min,max) instead of per-ID calls.
    Returns list of dicts with at least {"id": int, "file": str, ...}.
    """
    # Single ID: -i 5485,5485 (range of one)
    id_range = f"{min_id},{max_id}"

    args = [
        tdl_path, "chat", "export",
        "-c", str(chat_id),
        "-T", "id",
        "-i", id_range,
        "-o", output_path,
    ]
    args += session_args

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            return []
        if not os.path.exists(output_path):
            return []
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Keep only records that have a media file
        return [item for item in data if isinstance(item, dict) and item.get("file")]
    except Exception:
        return []


def fetch_expected_files(
    urls: List[str],
    tdl_path: str,
    session_args: List[str],
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> List[Dict]:
    """For all URLs, run chat export and return expected file records.

    Strategy:
      1. Group URLs by chat_id.
      2. For each chat, compute min/max message ID → one ``-T id -i min,max`` call.
      3. Filter returned records to only those whose IDs are in the requested set.
      4. This minimises tdl invocations while keeping all logic in Python.

    Each result record: ``{"id": int, "file": str, "chat": str, "url": str}``
    """
    groups = group_urls_by_chat(urls)
    result: List[Dict] = []
    total = len(groups)
    done = 0

    for chat_id, pairs in groups.items():
        # Build a set of wanted IDs and a url lookup map
        wanted_ids: set = {mid for mid, _ in pairs}
        url_map: Dict[int, str] = {mid: url for mid, url in pairs}

        min_id = min(wanted_ids)
        max_id = max(wanted_ids)

        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w", encoding="utf-8"
        ) as f:
            tmp_path = f.name

        try:
            # Fetch entire [min_id, max_id] range in one call
            all_records = run_chat_export(
                tdl_path, chat_id, min_id, max_id, session_args, tmp_path
            )

            # Keep only the records whose IDs were in our URL list
            for rec in all_records:
                mid = rec.get("id")
                if mid in wanted_ids:
                    result.append({
                        "id":   mid,
                        "file": rec.get("file", ""),
                        "chat": chat_id,
                        "url":  url_map.get(mid, ""),
                    })
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

        done += 1
        if progress_callback:
            progress_callback(done, total)

    return result


# ── Failed URL detection ─────────────────────────────────────────────────────

def find_failed_urls(
    expected_files: List[Dict],
    new_files: List[str],
    all_urls: List[str],
) -> List[str]:
    """Attempt to detect which URLs were NOT successfully downloaded.

    Strategy: match message IDs embedded in downloaded filenames.
    Default template: ``{{ .DialogID }}_{{ .MessageID }}_{{ filenamify .FileName }}``
    If a message's ID cannot be found in any downloaded filename, its URL is failed.

    Falls back to returning all URLs if matching is impossible (e.g. custom template).
    """
    if not expected_files:
        # Could not export – cannot determine failures
        return []

    downloaded_text = "\n".join(new_files)
    failed_urls: List[str] = []

    for rec in expected_files:
        msg_id = rec.get("id")
        url    = rec.get("url", "")
        if not url or msg_id is None:
            continue
        # Check if any downloaded file contains the message ID as a word boundary
        # e.g. "_123_" in the filename
        pattern = re.compile(r"(?:^|_|/)0*" + str(msg_id) + r"(?:_|\.|\Z)", re.MULTILINE)
        if not pattern.search(downloaded_text):
            failed_urls.append(url)

    return failed_urls
