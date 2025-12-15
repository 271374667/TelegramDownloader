#!/usr/bin/env python3
"""
Test script to run the GUI and verify GroupBox checkboxes appear correctly
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
    """Run the GUI application to test GroupBox checkboxes"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Telegram Downloader - Test Checkboxes")
    app.setStyle("Fusion")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Show message to user
    from PySide6.QtWidgets import QMessageBox
    QMessageBox.information(
        window,
        "Group Box Checkboxes Test",
        "请验证以下内容：\n\n"
        "1. 每个 GroupBox 前面都有一个勾选框\n"
        "2. 取消勾选后，GroupBox 内的内容仍然可用（不会被禁用）\n"
        "3. 生成的命令只包含勾选的 GroupBox 的参数\n"
        "4. Download URLs 没有勾选框（因为是必须的）\n\n"
        "请测试各种勾选组合！"
    )

    print("GUI Test Started")
    print("- All GroupBoxes should have checkboxes in front")
    print("- GroupBox content should remain enabled even when unchecked")
    print("- Command preview should only include checked parameters")
    print("- Download URLs group has no checkbox (mandatory)")

    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    test_gui()