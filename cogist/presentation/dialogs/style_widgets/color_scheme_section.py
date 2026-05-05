"""Color scheme section widget.

Simplified to only manage color pool and rainbow branch mode.
Background, border, brightness, opacity controls moved to their respective panels.
"""
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from cogist.presentation.widgets import ToggleSwitch

from .collapsible_panel import CollapsiblePanel
from .color_picker import ColorPicker, create_color_picker
from .dialog_utils import position_color_dialog


class ColorSchemeSection(CollapsiblePanel):
    """Color scheme settings section.

    Simplified to only manage:
    - Rainbow branch mode switch
    - Color pool (10 colors)

    Signals:
        color_changed(dict): Emitted when color properties change
    """

    color_changed = Signal(dict)

    # UI constants
    LABEL_WIDTH = 90
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Color Scheme", collapsed=False, parent=parent)

        # Get LABEL_WIDTH from parent if available
        self._label_width = getattr(parent, 'LABEL_WIDTH', self.LABEL_WIDTH) if parent else self.LABEL_WIDTH

        self._initialized = False
        self._rainbow_visible = False

        # No hardcoded colors - will be set by set_style()
        self._default_rainbow = []

        # Rainbow controls
        self.rainbow_check: ToggleSwitch | None = None
        self.rainbow_buttons: list[QPushButton] = []
        self.rainbow_colors: list[str] = []
        self.rainbow_pool_widget: QWidget | None = None

        # Color picker (shared for all buttons)
        self._color_picker: ColorPicker | None = None
        self._current_color_button: QPushButton | None = None

        self.toggled.connect(self._on_toggled)

        # If panel is expanded by default, initialize content immediately
        if not self.isCollapsed():
            self._on_toggled(True)

    def _on_toggled(self, expanded: bool):
        """Handle panel expand/collapse."""
        if expanded and not self._initialized:
            self._initialized = True
            self._init_content()
            # After creating buttons, apply pending style if available
            if hasattr(self, '_pending_style'):
                self.set_style(self._pending_style)
                del self._pending_style

    def _init_content(self):
        """Initialize content on first expand."""
        layout = QGridLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(self.GROUP_MARGIN, 6, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        row = 0

        # === Rainbow Branch Switch ===
        switch_row = QHBoxLayout()
        switch_row.setContentsMargins(0, 0, 0, 0)
        switch_row.setSpacing(0)

        rainbow_label = QLabel("Branch-based:")
        rainbow_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        rainbow_label.setFixedWidth(self._label_width)
        switch_row.addWidget(rainbow_label)

        switch_row.addStretch()

        self.rainbow_check = ToggleSwitch()
        self.rainbow_check.toggled.connect(self._on_rainbow_toggled)
        switch_row.addWidget(self.rainbow_check)

        layout.addLayout(switch_row, row, 0, 1, 2)
        row += 1

        # === Rainbow Color Pool ===
        pool_label = QLabel("Color Pool:")
        pool_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pool_label.setFixedWidth(self._label_width)
        layout.addWidget(pool_label, row, 0)

        # Color buttons container - 2 rows
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(4)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.rainbow_buttons = []
        # Will be populated by set_style() before panel expansion
        self.rainbow_colors = []

        for row_idx in range(2):
            btn_row_layout = QHBoxLayout()
            btn_row_layout.setSpacing(0)
            btn_row_layout.setContentsMargins(0, 0, 0, 0)

            for col_idx in range(4):  # 4 columns x 2 rows = 8 colors
                i = row_idx * 4 + col_idx
                btn = QPushButton()
                btn.setFixedSize(32, 32)
                btn.setToolTip(f"Color {i + 1}")
                # Use placeholder color (will be updated by set_style)
                color = self.rainbow_colors[i] if i < len(self.rainbow_colors) else "#FFCCCCCC"
                btn.setStyleSheet(
                    f"background-color: {color}; "
                    "border: none; border-radius: 4px;"
                )
                btn.clicked.connect(lambda _, idx=i: self._edit_rainbow_color(idx))
                self.rainbow_buttons.append(btn)
                btn_row_layout.addWidget(btn)

                if col_idx < 3:
                    btn_row_layout.addStretch()

            buttons_layout.addLayout(btn_row_layout)

        buttons_container.setLayout(buttons_layout)
        layout.addWidget(buttons_container, row, 1)
        row += 1

        self.setLayout(layout)

        # Always show color pool (no hiding)
        self.rainbow_pool_widget = buttons_container
        # self.rainbow_pool_widget.setVisible(self._rainbow_visible)  # Removed: always visible
        if self.rainbow_check:
            self.rainbow_check.blockSignals(False)

        # CRITICAL: After creating buttons, update them with current colors
        # This ensures colors are applied even if set_style was called before panel expansion
        for i, btn in enumerate(self.rainbow_buttons):
            if i < len(self.rainbow_colors):
                color = self.rainbow_colors[i]
                btn.setStyleSheet(
                    f"background-color: {color}; "
                    "border: none; border-radius: 4px;"
                )

    def _on_rainbow_toggled(self, checked: bool):
        """Handle rainbow branch mode toggle."""
        self._rainbow_visible = checked

        # Note: Color pool is always visible (no show/hide)
        # Rainbow switch now only controls whether branches use rainbow colors

        # Emit change
        # Note: Rainbow switch is now global, emitted signal will be handled by parent
        self.color_changed.emit({"use_rainbow_branches": checked})

    def _edit_rainbow_color(self, index: int):
        """Handle rainbow color button click."""
        if self._color_picker is None:
            self._color_picker = create_color_picker(self)
            self._color_picker.color_selected.connect(
                lambda color: self._on_rainbow_color_selected(index, color)
            )

        # Use current color or placeholder
        current_color = self.rainbow_colors[index] if index < len(self.rainbow_colors) else "#FFCCCCCC"
        self._color_picker.set_current_color(current_color)

        # Store current button reference
        self._current_color_button = self.rainbow_buttons[index]

        # Show color picker
        self._color_picker.show()
        self._color_picker.raise_()
        self._color_picker.activateWindow()

        # Position dialog
        if self._current_color_button:
            position_color_dialog(self._color_picker, self._current_color_button)

    def _on_rainbow_color_selected(self, index: int, hex_color: str):
        """Handle color selection from picker."""
        if index < len(self.rainbow_colors):
            self.rainbow_colors[index] = hex_color

            # Update button color
            if index < len(self.rainbow_buttons):
                btn = self.rainbow_buttons[index]
                btn.setStyleSheet(
                    f"background-color: {hex_color}; "
                    "border: none; border-radius: 4px;"
                )

            # Emit change
            self.color_changed.emit({"color_pool": self.rainbow_colors.copy()})

    def get_style(self) -> dict:
        """Get current color scheme style."""
        return {
            "use_rainbow_branches": self._rainbow_visible,
            "color_pool": self.rainbow_colors.copy(),
        }

    def set_style(self, style: dict):
        """Set color scheme style programmatically."""
        # If buttons not created yet, save as pending
        if not self._initialized:
            self._pending_style = style
            return

        # Block signals to prevent creating new commands during undo/redo
        was_blocked = self.rainbow_check.blockSignals(True) if self.rainbow_check else False

        if "use_rainbow_branches" in style:
            self._rainbow_visible = style["use_rainbow_branches"]
            if self.rainbow_check:
                self.rainbow_check.setChecked(self._rainbow_visible)

        # Restore signal blocking state
        if self.rainbow_check:
            self.rainbow_check.blockSignals(was_blocked)

        if "color_pool" in style:
            self.rainbow_colors = style["color_pool"].copy()
            # Update button colors
            for i, btn in enumerate(self.rainbow_buttons):
                if i < len(self.rainbow_colors):
                    color = self.rainbow_colors[i]
                    btn.setStyleSheet(
                        f"background-color: {color}; "
                        "border: none; border-radius: 4px;"
                    )
