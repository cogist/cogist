"""Reusable visual preview button with popup selection dialog.

This component combines a preview button and a popup dialog for visual option
selection (connector shapes, node shapes, etc.).
"""

from collections.abc import Callable

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from .visual_list_popup import VisualListPopup


class VisualPreviewButton(QWidget):
    """A button that shows a preview image and opens a popup for selection.

    Usage:
        button = VisualPreviewButton(
            options=[
                ("value1", preview_generator1, QSize(140, 50)),
                ("value2", preview_generator2, QSize(140, 50)),
            ],
            initial_value="value1",
            preview_size=QSize(140, 50),
            parent=parent_widget
        )
        button.value_changed.connect(lambda value: print(f"Selected: {value}"))
        layout.addWidget(button)

        # Update value programmatically
        button.set_value("value2")
    """

    value_changed = Signal(str)

    def __init__(
        self,
        options: list[tuple[str, Callable, QSize]],
        initial_value: str,
        preview_size: QSize,
        button_height: int = 32,
        parent: QWidget | None = None,
    ):
        """Initialize the visual preview button.

        Args:
            options: List of (value, preview_generator, size) tuples
            initial_value: Initial selected value
            preview_size: Size of the preview image in popup dialog
            button_height: Fixed button height (default 32)
            parent: Parent widget
        """
        super().__init__(parent)

        self.options = options
        self.popup_preview_size = preview_size
        self.current_value = initial_value

        # Button layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create button with button style
        self.button = QPushButton()
        self.button.setFixedHeight(button_height)
        # Button width will be set by parent layout (auto-fill)
        self.button.setStyleSheet(self._button_style())

        # Button internal layout
        btn_layout = QHBoxLayout(self.button)
        btn_layout.setContentsMargins(4, 2, 4, 2)
        btn_layout.setSpacing(0)

        btn_layout.addStretch()

        # Preview label - will auto-expand to fill button width
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background: transparent;")
        self.preview_label.setMinimumHeight(button_height - 4)  # Leave 2px margin top/bottom
        btn_layout.addWidget(self.preview_label)

        btn_layout.addStretch()

        layout.addWidget(self.button)

        # Create popup dialog
        self.popup = VisualListPopup(
            options=self.options,
            parent=self,
        )

        # Connect signals
        self.button.clicked.connect(self._show_popup)
        self.popup.item_selected.connect(self._on_value_selected)

        # Set initial preview using popup_preview_size as fallback
        self._update_preview()

    def resizeEvent(self, event):
        """Handle resize event to update preview."""
        super().resizeEvent(event)
        # Update preview when button size changes
        if event.size() != event.oldSize():
            self._update_preview()

    def _button_style(self) -> str:
        """Get standard button stylesheet."""
        return """
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #A0A0A0;
            }
        """

    def _show_popup(self):
        """Show popup dialog below the button."""
        # Position popup below the button with same width
        btn_width = self.button.width()
        self.popup.setFixedWidth(btn_width)

        # Position popup below the button
        button_pos = self.button.mapToGlobal(QPoint(0, self.button.height()))
        self.popup.show_at(button_pos)

    def _on_value_selected(self, value: str):
        """Handle value selection from popup."""
        self.current_value = value
        self._update_preview()
        self.value_changed.emit(value)

    def _update_preview(self):
        """Update the preview image based on current value."""
        for value, generator, _size in self.options:
            if value == self.current_value:
                # Always use popup_preview_size for consistent appearance
                pixmap = generator(self.popup_preview_size, selected=False)
                self.preview_label.setPixmap(pixmap)
                break

    def set_value(self, value: str):
        """Set the current value programmatically.

        Args:
            value: The value to set
        """
        self.current_value = value
        self._update_preview()

    def get_value(self) -> str:
        """Get the current value.

        Returns:
            Current selected value
        """
        return self.current_value
