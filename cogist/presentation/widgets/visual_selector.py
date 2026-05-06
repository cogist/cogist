"""Visual selector widget for graphical option selection.

Provides a reusable component for selecting options with visual previews,
supporting both dynamically drawn graphics and bitmap images.
"""

from collections.abc import Callable

from qtpy.QtCore import QSize, Qt, Signal
from qtpy.QtGui import QColor, QPainter, QPen, QPixmap
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget


class VisualOption:
    """Represents a single selectable option with visual preview."""

    def __init__(
        self,
        value: str,
        preview_generator: Callable[[QSize], QPixmap],
        tooltip: str = "",
    ):
        """Initialize visual option.

        Args:
            value: The value identifier (e.g., "bezier", "straight")
            preview_generator: Function that generates preview pixmap given size
            tooltip: Optional tooltip text
        """
        self.value = value
        self.preview_generator = preview_generator
        self.tooltip = tooltip
        self._pixmap_cache: dict[QSize, QPixmap] = {}

    def get_preview(self, size: QSize) -> QPixmap:
        """Get cached or generate new preview pixmap.

        Args:
            size: Desired preview size

        Returns:
            QPixmap of the preview
        """
        # Use tuple as cache key since QSize is not hashable
        cache_key = (size.width(), size.height())
        if cache_key in self._pixmap_cache:
            return self._pixmap_cache[cache_key]

        pixmap = self.preview_generator(size)
        self._pixmap_cache[cache_key] = pixmap
        return pixmap

    def clear_cache(self):
        """Clear pixmap cache."""
        self._pixmap_cache.clear()


class VisualOptionButton(QWidget):
    """Clickable button widget for a single visual option."""

    clicked = Signal(str)  # Emits the option value when clicked

    def __init__(
        self,
        option: VisualOption,
        preview_size: QSize | None = None,
        show_label: bool = True,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.option = option
        self.preview_size = preview_size if preview_size is not None else QSize(60, 40)
        self.show_label = show_label
        self.is_selected = False

        # Set fixed size based on preview and label
        height = self.preview_size.height() + (24 if show_label else 8)
        self.setFixedSize(self.preview_size.width() + 16, height)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(option.tooltip)

    def set_selected(self, selected: bool):
        """Set selection state."""
        self.is_selected = selected
        self.update()

    def paintEvent(self, _event):
        """Paint the option button with preview and selection indicator."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        if self.is_selected:
            painter.fillRect(self.rect(), QColor("#E3F2FD"))  # Light blue highlight
            border_color = QColor("#2196F3")  # Blue border
            border_width = 2
        else:
            painter.fillRect(self.rect(), QColor("#FAFAFA"))  # Light gray
            border_color = QColor("#E0E0E0")  # Gray border
            border_width = 1

        # Draw border
        pen = QPen(border_color, border_width)
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 4, 4)

        # Draw preview pixmap centered
        pixmap = self.option.get_preview(self.preview_size)
        x = (self.width() - pixmap.width()) // 2
        y = 4  # Top padding
        painter.drawPixmap(x, y, pixmap)

        # Draw label below preview if enabled
        if self.show_label:
            painter.setPen(QColor("#424242"))
            font = painter.font()
            font.setPointSize(9)
            painter.setFont(font)
            label_rect = self.rect().adjusted(0, y + pixmap.height() + 2, 0, 0)
            painter.drawText(label_rect, Qt.AlignHCenter | Qt.AlignTop, self.option.value.capitalize())

    def mousePressEvent(self, event):
        """Handle click event."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.option.value)
        super().mousePressEvent(event)


class VisualSelector(QWidget):
    """Container widget for visual option selection.

    Displays multiple VisualOptionButtons in a horizontal or vertical layout
    and manages selection state.
    """

    selection_changed = Signal(str)  # Emits the selected option value

    def __init__(
        self,
        options: list[VisualOption],
        orientation: Qt.Orientation = Qt.Horizontal,
        preview_size: QSize | None = None,
        spacing: int = 8,
        parent: QWidget | None = None,
    ):
        """Initialize visual selector.

        Args:
            options: List of VisualOption instances
            orientation: Horizontal or Vertical layout
            preview_size: Size for each option's preview
            spacing: Spacing between options
            parent: Parent widget
        """
        super().__init__(parent)
        self.options = {opt.value: opt for opt in options}
        self.orientation = orientation
        self.preview_size = preview_size if preview_size is not None else QSize(60, 40)
        self.selected_value: str | None = None

        # Create layout
        if orientation == Qt.Horizontal:
            self.layout = QHBoxLayout(self)
        else:
            self.layout = QVBoxLayout(self)

        self.layout.setSpacing(spacing)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create option buttons
        self.buttons: dict[str, VisualOptionButton] = {}
        for option in options:
            button = VisualOptionButton(option, preview_size)
            button.clicked.connect(self._on_option_clicked)
            self.buttons[option.value] = button
            self.layout.addWidget(button)

        # Add stretch to prevent buttons from expanding
        if orientation == Qt.Horizontal:
            self.layout.addStretch()
        else:
            self.layout.addStretch()

    def set_selection(self, value: str):
        """Set the selected option programmatically.

        Args:
            value: The option value to select
        """
        if value not in self.buttons:
            return

        # Deselect previous
        if self.selected_value and self.selected_value in self.buttons:
            self.buttons[self.selected_value].set_selected(False)

        # Select new
        self.selected_value = value
        self.buttons[value].set_selected(True)

    def _on_option_clicked(self, value: str):
        """Handle option button click."""
        if value == self.selected_value:
            return  # Already selected

        self.set_selection(value)
        self.selection_changed.emit(value)

    def clear_cache(self):
        """Clear all preview caches (useful when style changes)."""
        for option in self.options.values():
            option.clear_cache()
        self.update()
