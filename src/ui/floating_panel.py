"""
Floating quick action panel for Telegram Downloader GUI
A compact, always-on-top widget for quick access to common operations
"""

import subprocess
import os

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont


class FloatingPanel(QWidget):
    """
    A compact, always-on-top floating panel for quick operations.

    Features:
    - Shows current URL count
    - Clear all URLs button
    - Generate BAT file button
    - Execute (generate + run) button
    """

    # Signals for communication with main window
    clear_requested = Signal()
    generate_requested = Signal()
    execute_requested = Signal()
    show_main_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Window flags for always on top, frameless, tool window
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

        # Allow moving the window
        self._drag_pos = None

        self.setup_ui()
        self.setFixedHeight(50)
        self.setMinimumWidth(380)

        # Position at top-right of screen by default
        self._position_default()

    def setup_ui(self):
        """Setup the floating panel UI"""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 4, 8, 4)
        main_layout.setSpacing(6)

        # Container frame with styling
        self.setStyleSheet("""
            FloatingPanel {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton {
                background-color: #444444;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #555555;
                border-color: #888888;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
            QPushButton#clearBtn {
                background-color: #8b4513;
            }
            QPushButton#clearBtn:hover {
                background-color: #a0522d;
            }
            QPushButton#generateBtn {
                background-color: #2e7d32;
            }
            QPushButton#generateBtn:hover {
                background-color: #388e3c;
            }
            QPushButton#executeBtn {
                background-color: #1565c0;
            }
            QPushButton#executeBtn:hover {
                background-color: #1976d2;
            }
            QPushButton#showMainBtn {
                background-color: #6a1b9a;
            }
            QPushButton#showMainBtn:hover {
                background-color: #7b1fa2;
            }
        """)

        # Drag handle / Title area
        drag_label = QLabel("TDL")
        drag_label.setStyleSheet("""
            QLabel {
                color: #0088cc;
                font-size: 14px;
                font-weight: bold;
                padding: 0 4px;
            }
        """)
        drag_label.setCursor(Qt.CursorShape.SizeAllCursor)
        main_layout.addWidget(drag_label)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet("QFrame { color: #555555; }")
        main_layout.addWidget(sep1)

        # URL count label
        self.url_count_label = QLabel("0 links")
        self.url_count_label.setStyleSheet("""
            QLabel {
                color: #4fc3f7;
                font-size: 13px;
                padding: 0 8px;
            }
        """)
        self.url_count_label.setMinimumWidth(80)
        main_layout.addWidget(self.url_count_label)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setStyleSheet("QFrame { color: #555555; }")
        main_layout.addWidget(sep2)

        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("clearBtn")
        self.clear_btn.setToolTip("Clear all URLs")
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        main_layout.addWidget(self.clear_btn)

        # Generate BAT button
        self.generate_btn = QPushButton("BAT")
        self.generate_btn.setObjectName("generateBtn")
        self.generate_btn.setToolTip("Generate batch file")
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        main_layout.addWidget(self.generate_btn)

        # Execute button
        self.execute_btn = QPushButton("Run")
        self.execute_btn.setObjectName("executeBtn")
        self.execute_btn.setToolTip("Generate and execute batch file")
        self.execute_btn.clicked.connect(self._on_execute_clicked)
        main_layout.addWidget(self.execute_btn)

        # Show main window button
        self.show_main_btn = QPushButton("Main")
        self.show_main_btn.setObjectName("showMainBtn")
        self.show_main_btn.setToolTip("Show main window")
        self.show_main_btn.clicked.connect(self._on_show_main_clicked)
        main_layout.addWidget(self.show_main_btn)

        # Close button
        self.close_btn = QPushButton("X")
        self.close_btn.setFixedWidth(28)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #c62828;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)
        self.close_btn.setToolTip("Hide panel (Ctrl+Shift+F to reopen)")
        self.close_btn.clicked.connect(self.hide)
        main_layout.addWidget(self.close_btn)

    def _position_default(self):
        """Position the panel at the top-right of the screen"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = geometry.right() - self.width() - 20
            y = geometry.top() + 20
            self.move(x, y)

    @Slot(int)
    def update_url_count(self, count: int):
        """Update the URL count display"""
        if count == 0:
            self.url_count_label.setText("No links")
            self.url_count_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 13px;
                    padding: 0 8px;
                }
            """)
        elif count == 1:
            self.url_count_label.setText("1 link")
            self.url_count_label.setStyleSheet("""
                QLabel {
                    color: #4fc3f7;
                    font-size: 13px;
                    padding: 0 8px;
                }
            """)
        else:
            self.url_count_label.setText(f"{count} links")
            self.url_count_label.setStyleSheet("""
                QLabel {
                    color: #4fc3f7;
                    font-size: 13px;
                    padding: 0 8px;
                }
            """)

        # Update button states
        has_urls = count > 0
        self.clear_btn.setEnabled(has_urls)
        self.generate_btn.setEnabled(has_urls)
        self.execute_btn.setEnabled(has_urls)

    def _on_clear_clicked(self):
        """Handle clear button click"""
        self.clear_requested.emit()

    def _on_generate_clicked(self):
        """Handle generate button click"""
        self.generate_requested.emit()

    def _on_execute_clicked(self):
        """Handle execute button click"""
        self.execute_requested.emit()

    def _on_show_main_clicked(self):
        """Handle show main window button click"""
        self.show_main_requested.emit()

    # Drag support for frameless window
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release for dragging"""
        self._drag_pos = None
        event.accept()

    def mouseDoubleClickEvent(self, event):
        """Handle double click - show main window"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.show_main_requested.emit()
            event.accept()
