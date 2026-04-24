"""Reusable visual list popup for graphical option selection.

This is a generic dialog that can be used for any visual option selection
with preview images (connector shapes, node shapes, etc.).
"""

from collections.abc import Callable

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QGraphicsDropShadowEffect,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class VisualListPopup(QDialog):
    """Generic popup widget for visual option selection with preview images.

    Usage:
        popup = VisualListPopup(
            options=[
                ("value1", preview_generator1, QSize(140, 30)),
                ("value2", preview_generator2, QSize(140, 30)),
            ],
            parent=parent_widget
        )
        popup.item_selected.connect(on_item_selected_handler)
        popup.exec()
    """

    item_selected = Signal(str)

    def __init__(
        self,
        options: list[tuple[str, Callable, QSize]],
        parent=None,
    ):
        """Initialize the visual list popup.

        Args:
            options: List of (value, preview_generator, size) tuples
            parent: Parent widget for positioning
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Store options
        self.options = options

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Content widget with background (flat design)
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            background-color: rgb(236, 236, 236);
            border-radius: 6px;
        """)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        content_widget.setGraphicsEffect(shadow)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 4, 0, 4)
        content_layout.setSpacing(2)

        # Create preview options
        self.preview_labels: dict[str, dict] = {}

        for value, preview_gen, preview_size in options:
            item_widget = QWidget()
            item_widget.setProperty("visual_value", value)
            item_widget.setCursor(Qt.PointingHandCursor)

            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 2, 0, 2)
            item_layout.setSpacing(0)

            # Create preview
            pixmap = preview_gen(preview_size, selected=False)
            preview_label = QLabel()
            preview_label.setPixmap(pixmap)
            preview_label.setAlignment(Qt.AlignCenter)
            preview_label.setFixedSize(preview_size)
            preview_label.setStyleSheet("background: transparent;")
            item_layout.addWidget(preview_label, alignment=Qt.AlignCenter)

            self.preview_labels[value] = {
                "widget": item_widget,
                "label": preview_label,
                "generator": preview_gen,
                "size": preview_size,
            }

            # Connect events
            item_widget.mousePressEvent = lambda _, v=value: self._on_item_clicked(v)
            item_widget.enterEvent = lambda _, v=value: self._on_item_hover(v, True)
            item_widget.leaveEvent = lambda _, v=value: self._on_item_hover(v, False)

            content_layout.addWidget(item_widget)

        main_layout.addWidget(content_widget)

    def _on_item_clicked(self, value: str):
        """Handle item click."""
        self.item_selected.emit(value)
        self.close()

    def _on_item_hover(self, value: str, hovered: bool):
        """Update preview on hover."""
        if value in self.preview_labels:
            info = self.preview_labels[value]
            pixmap = info["generator"](info["size"], selected=hovered)
            info["label"].setPixmap(pixmap)

            # Apply blue background on hover (same as QMenu selection)
            if hovered:
                info["widget"].setStyleSheet("""
                    background-color: rgb(84, 143, 255);
                    border-radius: 4px;
                """)
            else:
                info["widget"].setStyleSheet("background: transparent;")

    def show_at(self, position: QPoint):
        """Show popup at specified position.

        Args:
            position: Global position to show the popup
        """
        self.move(position)
        self.show()
