#!/usr/bin/env python3
"""
Test script to run the GUI and verify layout fixes
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Import the main window
from ui.main_window import MainWindow

def test_gui():
    """Run the GUI application to test layout fixes"""

    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Telegram Downloader - Test")
    app.setApplicationVersion("1.0.0-test")
    app.setStyle("Fusion")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Maximize window to better see the layout
    window.showMaximized()

    print("GUI Test Started")
    print("- Window should now be maximized")
    print("- Session Configuration tab should fill the available height")
    print("- Bottom section (Command Preview) should be smaller")
    print("- Check that there is no excessive empty space in Session tab")

    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    test_gui()