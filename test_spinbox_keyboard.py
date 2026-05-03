#!/usr/bin/env python3
"""Test QSpinBox keyboard events."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QSpinBox, QVBoxLayout, QWidget


class SpinBoxTest(QWidget):
    """Test QSpinBox keyboard events."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("QSpinBox Keyboard Test")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # QSpinBox with SVG arrows
        label = QLabel("Test QSpinBox with SVG arrows:")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        self.spin = QSpinBox()
        self.spin.setRange(1, 10)
        self.spin.setValue(5)
        self.spin.setAlignment(Qt.AlignLeft)
        self.spin.setFocusPolicy(Qt.StrongFocus)
        self.spin.setKeyboardTracking(True)
        self.spin.setStyleSheet(
            "QSpinBox {"
            "    border: 1px solid #C8C8C8;"
            "    border-radius: 4px;"
            "    padding: 2px 8px;"
            "    background: white;"
            "}"
            "QSpinBox::up-button {"
            "    width: 18px;"
            "    border: none;"
            "    background: transparent;"
            "}"
            "QSpinBox::down-button {"
            "    width: 18px;"
            "    border: none;"
            "    background: transparent;"
            "}"
            "QSpinBox::up-button:hover, QSpinBox::down-button:hover {"
            "    background: #F5F5F5;"
            "}"
            "QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {"
            "    background: #E8E8E8;"
            "}"
            "QSpinBox::up-arrow {"
            "    image: url(assets/icons/arrow-up.svg);"
            "}"
            "QSpinBox::down-arrow {"
            "    image: url(assets/icons/arrow-down.svg);"
            "}"
        )
        self.spin.valueChanged.connect(lambda v: print(f"Value changed to: {v}"))
        layout.addWidget(self.spin)

        info = QLabel("Click on the spinbox and press Up/Down arrow keys")
        info.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(info)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpinBoxTest()
    window.show()
    sys.exit(app.exec())
