#!/usr/bin/env python3
"""Test different approaches for QSpinBox arrow rendering."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPolygon
from PySide6.QtWidgets import QApplication, QLabel, QSpinBox, QVBoxLayout, QWidget


def create_triangle_arrow(up: bool, size: int = 10, color: str = "#666666") -> QImage:
    """Create a triangle arrow image."""
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)

    # Parse color
    qcolor = QColor(color)
    painter.setBrush(qcolor)
    painter.setPen(Qt.NoPen)

    # Create triangle polygon
    from PySide6.QtCore import QPoint
    polygon = QPolygon()
    if up:
        # Up arrow: ▲
        polygon.append(QPoint(0, size - 2))      # bottom-left
        polygon.append(QPoint(size // 2, 2))     # top-center
        polygon.append(QPoint(size - 2, size - 2))  # bottom-right
    else:
        # Down arrow: ▼
        polygon.append(QPoint(2, 2))             # top-left
        polygon.append(QPoint(size // 2, size - 2))  # bottom-center
        polygon.append(QPoint(size - 2, 2))      # top-right

    painter.drawPolygon(polygon)
    painter.end()

    return image


class ArrowTest(QWidget):
    """Test different arrow rendering approaches."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("QSpinBox Arrow Test")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # === Test 1: Border technique ===
        test1_label = QLabel("Test 1: Border technique (CSS)")
        test1_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(test1_label)

        self.spin1 = QSpinBox()
        self.spin1.setRange(1, 10)
        self.spin1.setValue(5)
        self.spin1.setStyleSheet(
            "QSpinBox {"
            "    border: 1px solid #C8C8C8;"
            "    border-radius: 4px;"
            "    padding: 2px 8px;"
            "    background: white;"
            "}"
            "QSpinBox::up-button {"
            "    width: 20px;"
            "    border: none;"
            "    border-bottom: 1px solid #E0E0E0;"
            "    background: transparent;"
            "}"
            "QSpinBox::down-button {"
            "    width: 20px;"
            "    border: none;"
            "    background: transparent;"
            "}"
            "QSpinBox::up-arrow {"
            "    image: none;"
            "    width: 0;"
            "    height: 0;"
            "    border-left: 5px solid transparent;"
            "    border-right: 5px solid transparent;"
            "    border-bottom: 8px solid #666666;"
            "}"
            "QSpinBox::down-arrow {"
            "    image: none;"
            "    width: 0;"
            "    height: 0;"
            "    border-left: 5px solid transparent;"
            "    border-right: 5px solid transparent;"
            "    border-top: 8px solid #666666;"
            "}"
        )
        layout.addWidget(self.spin1)

        # === Test 2: Generated images ===
        test2_label = QLabel("Test 2: Generated triangle images")
        test2_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(test2_label)

        # Generate arrow images
        up_arrow = create_triangle_arrow(up=True, size=10, color="#666666")
        down_arrow = create_triangle_arrow(up=False, size=10, color="#666666")

        self.spin2 = QSpinBox()
        self.spin2.setRange(1, 10)
        self.spin2.setValue(5)
        self.spin2.setStyleSheet(
            "QSpinBox {"
            "    border: 1px solid #C8C8C8;"
            "    border-radius: 4px;"
            "    padding: 2px 8px;"
            "    background: white;"
            "}"
            "QSpinBox::up-button {"
            "    width: 18px;"
            "    border: none;"
            "    border-bottom: 1px solid #E0E0E0;"
            "    background: transparent;"
            "}"
            "QSpinBox::down-button {"
            "    width: 18px;"
            "    border: none;"
            "    background: transparent;"
            "}"
            f"QSpinBox::up-arrow {{ image: url(data:image/png;base64,{self._image_to_base64(up_arrow)}); width: 10px; height: 10px; }}"
            f"QSpinBox::down-arrow {{ image: url(data:image/png;base64,{self._image_to_base64(down_arrow)}); width: 10px; height: 10px; }}"
        )
        layout.addWidget(self.spin2)

        layout.addStretch()
        self.setLayout(layout)

    def _image_to_base64(self, image: QImage) -> str:
        """Convert QImage to base64 string."""
        import base64

        from PySide6.QtCore import QBuffer, QIODevice

        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, format=b"PNG")
        return base64.b64encode(buffer.data().data()).decode()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArrowTest()
    window.show()
    sys.exit(app.exec())
