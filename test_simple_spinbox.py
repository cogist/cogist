#!/usr/bin/env python3
"""Simple test for QSpinBox with default arrows."""

import sys

from PySide6.QtWidgets import QApplication, QLabel, QSpinBox, QVBoxLayout, QWidget


class SimpleTest(QWidget):
    """Test QSpinBox with minimal styling."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple QSpinBox Test")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # === Test 1: No custom style ===
        test1_label = QLabel("Test 1: No custom style (platform default)")
        test1_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(test1_label)

        self.spin1 = QSpinBox()
        self.spin1.setRange(1, 10)
        self.spin1.setValue(5)
        layout.addWidget(self.spin1)

        # === Test 2: Only main widget style ===
        test2_label = QLabel("Test 2: Only QSpinBox style (no button customization)")
        test2_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(test2_label)

        self.spin2 = QSpinBox()
        self.spin2.setRange(1, 10)
        self.spin2.setValue(5)
        self.spin2.setStyleSheet(
            "QSpinBox {"
            "    border: 1px solid #C8C8C8;"
            "    border-radius: 4px;"
            "    padding: 4px 8px;"
            "    background: white;"
            "}"
        )
        layout.addWidget(self.spin2)

        layout.addStretch()
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleTest()
    window.show()
    sys.exit(app.exec())
