#!/usr/bin/env python3
"""
Version bump utility for TDL-GUI.

直接运行本脚本即可将所有涉及版本号的文件统一修改为 TARGET_VERSION。
也可被其他模块导入后调用具体函数。
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ===========================================================================
# ★ 修改这里即可：直接运行脚本时使用的目标版本号
# ===========================================================================
TARGET_VERSION = "1.12.8"
# ===========================================================================

PROJECT_ROOT = Path(__file__).parent.parent

# Semver validation pattern
_SEMVER_RE = re.compile(r'^\d+\.\d+\.\d+$')


@dataclass
class VersionTarget:
    """描述一个版本号所在位置及其替换规则。"""
    file: str         # 相对于项目根目录的路径
    pattern: str      # 匹配当前版本值的正则（含上下文）
    replace: str      # 替换模板，{ver} 会被新版本号替换
    description: str  # 可读标签


# 所有需要同步的版本号位置
TARGETS: list[VersionTarget] = [
    VersionTarget(
        file="scripts/build.py",
        pattern=r'(APP_VERSION\s*=\s*")[^"]+(")',
        replace=r'\g<1>{ver}\g<2>',
        description="scripts/build.py  →  APP_VERSION",
    ),
    VersionTarget(
        file="src/ui/__init__.py",
        pattern=r'(__version__\s*=\s*")[^"]+(")',
        replace=r'\g<1>{ver}\g<2>',
        description="src/ui/__init__.py  →  __version__",
    ),
    VersionTarget(
        file="src/main.py",
        pattern=r'(setApplicationVersion\(")[^"]+("\))',
        replace=r'\g<1>{ver}\g<2>',
        description="src/main.py  →  setApplicationVersion",
    ),
    VersionTarget(
        file="src/main_widget.py",
        pattern=r'(setApplicationVersion\(")[^"]+("\))',
        replace=r'\g<1>{ver}\g<2>',
        description="src/main_widget.py  →  setApplicationVersion",
    ),
]


# ---------------------------------------------------------------------------
# Public API（供其他模块调用）
# ---------------------------------------------------------------------------

def validate_version(version: str) -> bool:
    """检查是否为合法的 X.Y.Z 语义化版本号。"""
    return bool(_SEMVER_RE.match(version))


def get_current_version(target: VersionTarget) -> str | None:
    """读取某个 VersionTarget 当前的版本号字符串，未找到则返回 None。"""
    path = PROJECT_ROOT / target.file
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    m = re.search(target.pattern, text)
    if not m:
        return None
    ver_m = re.search(r'\d+\.\d+\.\d+', m.group(0))
    return ver_m.group(0) if ver_m else None


def set_version_in_target(target: VersionTarget, new_ver: str) -> tuple[bool, str]:
    """
    将单个 VersionTarget 中的版本号更新为 new_ver。

    Returns:
        (changed, message)
        changed  — True 表示文件被修改
        message  — 描述结果的字符串
    """
    path = PROJECT_ROOT / target.file
    if not path.exists():
        return False, "文件不存在"

    original = path.read_text(encoding="utf-8")
    repl = target.replace.replace("{ver}", new_ver)
    updated = re.sub(target.pattern, repl, original)

    if updated == original:
        return False, "未匹配到目标模式，或版本号已是最新"

    path.write_text(updated, encoding="utf-8")
    return True, "已更新"


def set_all_versions(new_ver: str) -> dict[str, tuple[bool, str]]:
    """
    将所有 TARGETS 中的版本号统一更新为 new_ver。

    Args:
        new_ver: 目标版本号，必须符合 X.Y.Z 格式。

    Returns:
        以 target.description 为键，(changed, message) 为值的字典。

    Raises:
        ValueError: new_ver 不是合法的语义化版本号。
    """
    if not validate_version(new_ver):
        raise ValueError(f"无效的版本号 '{new_ver}'，格式应为 X.Y.Z")

    results: dict[str, tuple[bool, str]] = {}
    for t in TARGETS:
        results[t.description] = set_version_in_target(t, new_ver)
    return results


def check_all_versions() -> dict[str, str | None]:
    """
    返回所有 TARGETS 当前的版本号。

    Returns:
        以 target.description 为键，当前版本字符串（或 None）为值的字典。
    """
    return {t.description: get_current_version(t) for t in TARGETS}


# ---------------------------------------------------------------------------
# 直接运行入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    version = TARGET_VERSION

    print(f"目标版本: {version}\n")

    try:
        results = set_all_versions(version)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    changed_count = 0
    for desc, (changed, msg) in results.items():
        icon = "✓" if changed else "–"
        print(f"  {icon}  {desc:<50}  {msg}")
        if changed:
            changed_count += 1

    print(f"\n共更新 {changed_count}/{len(TARGETS)} 个文件。")
