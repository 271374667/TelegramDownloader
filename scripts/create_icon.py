#!/usr/bin/env python3
"""
Generate app_icon.ico for TDL-GUI.
Uses PySide6 to render each size then packs them into an ICO
(Vista+ format: PNG data embedded inside ICO container).

Run once from the project root:
    python scripts/create_icon.py
"""

import io
import struct
import sys
from pathlib import Path

# ── Resolve project paths ──────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
ICON_OUTPUT = ASSETS_DIR / "app_icon.ico"

SIZES = [256, 128, 64, 48, 32, 16]


def render_png_bytes(size: int) -> bytes:
    """Render one icon frame at *size*×*size* and return raw PNG bytes."""
    from PySide6.QtCore import Qt, QRect
    from PySide6.QtGui import (
        QBrush, QColor, QFont, QFontMetrics, QImage, QPainter, QPen,
    )

    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # ── Background: rounded square, blue gradient ───────────────────────
    from PySide6.QtGui import QLinearGradient
    grad = QLinearGradient(0, 0, 0, size)
    grad.setColorAt(0.0, QColor("#2979FF"))  # bright blue
    grad.setColorAt(1.0, QColor("#1565C0"))  # deeper blue

    radius = size * 0.20
    painter.setBrush(QBrush(grad))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(0, 0, size, size, radius, radius)

    # ── Download arrow ──────────────────────────────────────────────────
    arrow_color = QColor("white")
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(arrow_color))

    # Shaft
    sw = max(1, size // 8)          # shaft width
    sh = max(1, size * 2 // 5)      # shaft height
    sx = (size - sw) // 2
    sy = size // 6
    painter.drawRect(sx, sy, sw, sh)

    # Arrow head (filled triangle pointing down)
    ah = max(2, size // 4)          # arrowhead height
    aw = max(3, size // 2)          # arrowhead width
    ax = (size - aw) // 2
    ay = sy + sh - 1

    from PySide6.QtGui import QPolygon
    from PySide6.QtCore import QPoint
    triangle = QPolygon([
        QPoint(ax, ay),
        QPoint(ax + aw, ay),
        QPoint(ax + aw // 2, ay + ah),
    ])
    painter.drawPolygon(triangle)

    # Baseline bar
    bh = max(1, size // 12)
    bw = size * 2 // 3
    bx = (size - bw) // 2
    by = ay + ah + max(1, size // 16)
    painter.drawRect(bx, by, bw, bh)

    painter.end()

    # Encode to PNG in-memory
    buf = io.BytesIO()
    # QImage.save to a QBuffer, then read back
    from PySide6.QtCore import QByteArray, QBuffer, QIODevice
    qa = QByteArray()
    qbuf = QBuffer(qa)
    qbuf.open(QIODevice.OpenModeFlag.WriteOnly)
    img.save(qbuf, "PNG")
    qbuf.close()
    return bytes(qa)


def build_ico(png_frames: list[tuple[int, bytes]]) -> bytes:
    """Pack (size, png_bytes) pairs into ICO file bytes (Vista+ PNG-in-ICO)."""
    count = len(png_frames)
    # ICO header: reserved(2) + type(2) + count(2)
    header = struct.pack("<HHH", 0, 1, count)

    # Each directory entry is 16 bytes
    dir_offset = 6 + count * 16
    entries = b""
    images = b""

    for size, png in png_frames:
        w = 0 if size >= 256 else size   # 0 means 256 in ICO spec
        h = 0 if size >= 256 else size
        data_size = len(png)
        entries += struct.pack(
            "<BBBBHHII",
            w, h,         # width, height
            0,            # color count (0 = no palette)
            0,            # reserved
            1,            # planes
            32,           # bit count
            data_size,    # size of image data
            dir_offset + len(images),  # offset to image data
        )
        images += png

    return header + entries + images


def main() -> None:
    ASSETS_DIR.mkdir(exist_ok=True)

    # QApplication is needed for PySide6 rendering
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    print(f"Generating icon sizes: {SIZES}")
    frames: list[tuple[int, bytes]] = []
    for size in SIZES:
        png = render_png_bytes(size)
        frames.append((size, png))
        print(f"  Rendered {size}x{size} ({len(png)} bytes PNG)")

    ico_data = build_ico(frames)
    ICON_OUTPUT.write_bytes(ico_data)
    print(f"\nSaved: {ICON_OUTPUT} ({len(ico_data)} bytes)")


if __name__ == "__main__":
    main()
