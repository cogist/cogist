"""Reusable color pool popup for selecting colors from a predefined palette.

This is a generic dialog that displays color swatches from the color pool
and allows users to select one by clicking.
"""

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ColorPoolPopup(QDialog):
    """Popup widget for color pool selection with visual swatches.

    Usage:
        popup = ColorPoolPopup(
            color_pool=["#FFEE3848", "#FFF48333", ...],
            parent=parent_widget
        )
        popup.color_selected.connect(on_color_selected_handler)
        popup.show_at(trigger_position)
    """

    color_selected = Signal(int)  # Emits selected color index (0-7)

    def __init__(
        self,
        color_pool: list[str],
        parent=None,
    ):
        """Initialize the color pool popup.

        Args:
            color_pool: List of color hex strings (should have 8 colors)
            parent: Parent widget for positioning
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Store color pool
        self.color_pool = color_pool

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
        content_layout.setContentsMargins(4, 4, 4, 4)  # Reduced padding on all sides
        content_layout.setSpacing(6)  # Row spacing

        # Create color buttons (2 rows x 4 columns) with centered alignment
        self.color_buttons: list[QPushButton] = []

        for row in range(2):
            # Create a horizontal layout for each row
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)  # Reduced spacing between buttons

            # Add stretch on both sides for centering
            row_layout.addStretch()

            # Add 4 color buttons for this row
            for col in range(4):
                i = row * 4 + col
                if i >= len(color_pool):
                    break

                # Create button for this color
                btn = QPushButton()
                btn.setFixedSize(30, 30)  # Smaller square buttons

                color = color_pool[i] if i < len(color_pool) else "#FFCCCCCC"
                btn.setStyleSheet(
                    f"background-color: {color}; "
                    "border: none; "
                    "border-radius: 4px;"
                )
                btn.setToolTip(f"Color Index {i}")

                # Store index for callback
                btn.setProperty("color_index", i)
                btn.clicked.connect(lambda _, idx=i: self._on_color_clicked(idx))
                btn.enterEvent = lambda _, b=btn: self._on_button_hover(b, True)
                btn.leaveEvent = lambda _, b=btn: self._on_button_hover(b, False)

                row_layout.addWidget(btn)
                self.color_buttons.append(btn)

            # Add stretch on the right side for centering
            row_layout.addStretch()

            content_layout.addWidget(row_widget)
        main_layout.addWidget(content_widget)

    def _on_color_clicked(self, color_index: int):
        """Handle color selection."""
        self.color_selected.emit(color_index)
        self.close()

    def _on_button_hover(self, button: QPushButton, hovered: bool):
        """Update button appearance on hover."""
        if hovered:
            # Add highlight border
            current_style = button.styleSheet()
            button.setStyleSheet(
                current_style.replace("border: 2px solid #C8C8C8", "border: 3px solid rgb(84, 143, 255)")
            )
        else:
            # Restore original border
            color_index = button.property("color_index")
            color = self.color_pool[color_index] if color_index < len(self.color_pool) else "#FFCCCCCC"
            button.setStyleSheet(
                f"background-color: {color}; "
                "border: none; "
                "border-radius: 4px;"
            )

    def show_at(self, position: QPoint, trigger_width: int = 0):
        """Show popup at specified position with smart boundary detection.

        Automatically adjusts position to ensure popup stays within screen bounds.
        If popup would extend below screen, it shows above the trigger position.

        Args:
            position: Global position to show the popup (typically below trigger button)
            trigger_width: Width of the trigger button (popup will match this width)
        """
        from PySide6.QtWidgets import QApplication

        # Set popup width to match trigger button if provided
        # But ensure minimum width for 4 color buttons (4 * 30 + 3 * 6 = 138px)
        if trigger_width > 0:
            min_width = 140  # Minimum width to fit 4 color buttons comfortably
            actual_width = max(trigger_width, min_width)
            self.setFixedWidth(actual_width)

        # Get screen geometry
        screen = QApplication.screenAt(position)
        if not screen:
            screen = QApplication.primaryScreen()

        screen_geometry = screen.availableGeometry()

        # Calculate popup size
        popup_width = self.width()
        popup_height = self.height()

        # Calculate ideal position (below trigger)
        x = position.x()
        y = position.y()

        # Check if popup would extend below screen
        if y + popup_height > screen_geometry.bottom():
            # Show above the trigger position instead
            y = position.y() - popup_height - 4  # 4px gap

        # Ensure popup doesn't go above screen top
        if y < screen_geometry.top():
            y = screen_geometry.top() + 10  # 10px margin from top

        # Ensure popup doesn't extend beyond right edge
        if x + popup_width > screen_geometry.right():
            x = screen_geometry.right() - popup_width - 10  # 10px margin

        # Ensure popup doesn't go beyond left edge
        if x < screen_geometry.left():
            x = screen_geometry.left() + 10  # 10px margin

        # Move and show
        self.move(int(x), int(y))
        self.show()
