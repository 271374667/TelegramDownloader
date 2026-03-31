#!/usr/bin/env python3
"""
TDL – Telegram Downloader GUI  (QML / MVVM edition)
Entry point: bootstraps QML engine, creates ViewModels, loads Main.qml
"""

import sys
import os
from pathlib import Path

# Ensure src/ is on the path
sys.path.insert(0, str(Path(__file__).parent))

# Set Universal dark style early, before QApplication
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QDir, QUrl
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QFontDatabase

from viewmodels import (
    AppViewModel,
    SessionViewModel,
    DownloadViewModel,
    UrlListModel,
)


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("TDL - Telegram Downloader")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("TDL")

    # Set application-wide CJK font so QML never falls back to 宋体
    # Load bundled Source Han Sans SC fonts
    fonts_dir = Path(__file__).parent / "qml" / "Fonts"
    for font_file in fonts_dir.glob("*.otf"):
        font_id = QFontDatabase.addApplicationFont(str(font_file))
        if font_id < 0:
            print(f"WARNING: Failed to load font: {font_file.name}", file=sys.stderr)
    app_font = QFont("Source Han Sans SC")
    app_font.setStyleHint(QFont.SansSerif)
    app.setFont(app_font)

    # Icon
    icon_path = Path(__file__).parent / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    else:
        # Generate a simple blue "T" icon
        pix = QPixmap(64, 64)
        pix.fill(QColor("#0078D4"))
        painter = QPainter(pix)
        painter.setPen(QColor("#FFFFFF"))
        f = QFont("Segoe UI", 36, QFont.Bold)
        painter.setFont(f)
        painter.drawText(pix.rect(), 0x0084, "T")  # AlignCenter
        painter.end()
        app.setWindowIcon(QIcon(pix))

    # Working directory → project root (parent of src/)
    project_root = Path(__file__).parent.parent.absolute()
    QDir.setCurrent(str(project_root))

    # ── ViewModels ──────────────────────────────────────────────────
    # Parent to app so PySide6 prevents Python-side garbage collection
    url_model = UrlListModel(parent=app)
    session_vm = SessionViewModel(parent=app)
    download_vm = DownloadViewModel(parent=app)
    app_vm = AppViewModel(session_vm, download_vm, url_model, parent=app)

    # ── QML Engine ──────────────────────────────────────────────────
    engine = QQmlApplicationEngine()

    # Keep explicit Python references to prevent GC
    engine._vm_refs = [app_vm, session_vm, download_vm, url_model]

    # Add QML import paths
    qml_dir = Path(__file__).parent / "qml"
    engine.addImportPath(str(qml_dir))

    # Expose ViewModels to QML
    ctx = engine.rootContext()
    ctx.setContextProperty("appVM", app_vm)
    ctx.setContextProperty("sessionVM", session_vm)
    ctx.setContextProperty("downloadVM", download_vm)
    ctx.setContextProperty("urlModel", url_model)

    # Load main QML
    qml_path = qml_dir / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))

    if not engine.rootObjects():
        print("ERROR: Failed to load QML. Check console for errors.", file=sys.stderr)
        sys.exit(1)

    # Initial preview
    app_vm.schedulePreviewUpdate()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
