#!/usr/bin/env python3
"""
Telegram Downloader GUI Application
Main entry point for the PySide6-based GUI application
"""

import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QDir
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow


def setup_application():
    """Configure application settings and properties"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Telegram Downloader")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("TDL GUI")

    # Set application icon if available
    icon_path = Path(__file__).parent / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Set style
    app.setStyle("Fusion")

    return app


def main():
    """Main application entry point"""
    # Create QApplication
    app = setup_application()

    # Set working directory to project root (parent of src/)
    project_root = Path(__file__).parent.parent.absolute()
    QDir.setCurrent(str(project_root))

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()