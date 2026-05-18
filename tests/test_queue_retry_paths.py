#!/usr/bin/env python3
"""Regression tests for queue retry target directories."""

import sys
import os
import shutil
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.batch_generator import BatchGenerator
from core.config_manager import DownloadConfig, SessionConfig
from core.task_history import TaskRecord


def test_grouped_retry_batch_uses_each_original_target_directory():
    tmp_path = Path.cwd() / "downloads" / f"tdl_queue_retry_test_{uuid.uuid4().hex}"
    tmp_path.mkdir(parents=True, exist_ok=False)
    old_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

        groups = [
            {
                "download_dir": str(tmp_path / "downloads" / "alpha_abcd"),
                "urls": ["https://t.me/tdl/1"],
            },
            {
                "download_dir": str(tmp_path / "downloads" / "beta_ef01"),
                "urls": ["https://t.me/tdl/2"],
            },
        ]
        template = DownloadConfig(
            directory=str(tmp_path / "wrong-root"),
            subfolder="wrong-subfolder",
            subfolder_enabled=True,
            skip_same=True,
        )

        ok, msg = BatchGenerator().generate_grouped_download_batch(
            groups,
            SessionConfig(),
            download_cfg_template=template,
            auto_close=True,
        )

        assert ok, msg
        bat = (tmp_path / "telegram_downloader.bat").read_text(encoding="utf-8")
        assert f'-d {groups[0]["download_dir"]}' in bat or f'-d "{groups[0]["download_dir"]}"' in bat
        assert f'-d {groups[1]["download_dir"]}' in bat or f'-d "{groups[1]["download_dir"]}"' in bat
        assert "wrong-root" not in bat
        assert "wrong-subfolder" not in bat
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(tmp_path)


def test_task_record_persists_download_groups_and_keeps_old_history_compatible():
    groups = [
        {"download_dir": "downloads/alpha_abcd", "urls": ["https://t.me/tdl/1"]},
        {"download_dir": "downloads/beta_ef01", "urls": ["https://t.me/tdl/2"]},
    ]
    task = TaskRecord("task-id", ["https://t.me/tdl/1", "https://t.me/tdl/2"], "downloads", groups)

    restored = TaskRecord.from_dict(task.to_dict())
    old_restored = TaskRecord.from_dict({
        "id": "old-task",
        "urls": ["https://t.me/tdl/3"],
        "download_dir": "downloads",
    })

    assert restored.download_groups == groups
    assert old_restored.download_groups == []
