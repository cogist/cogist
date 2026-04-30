"""Color scheme section widget.

Simplified to only manage color pool and rainbow branch mode.
Background, border, brightness, opacity controls moved to their respective panels.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from cogist.presentation.widgets import ToggleSwitch

from .collapsible_panel import CollapsiblePanel


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
        super().__init__("Color Scheme", collapsed=True, parent=parent)

        # Get LABEL_WIDTH from parent if available
        self._label_width = getattr(parent, 'LABEL_WIDTH', self.LABEL_WIDTH) if parent else self.LABEL_WIDTH

        self._initialized = False
        self._rainbow_visible = False

        # Default rainbow colors
        self._default_rainbow = [
            "#FFFF6B6B",
            "#FF4ECDC4",
            "#FF45B7D1",
            "#FFFFA07A",
            "#FF98D8C8",
            "#FFF7DC6F",
            "#FFBB8FCE",
            "#FF85C1E2",
            "#FFF8B739",
            "#FF52B788",
        ]

        # Rainbow controls
        self.rainbow_check: ToggleSwitch | None = None
        self.rainbow_buttons: list[QPushButton] = []
        self.rainbow_colors: list[str] = []
        self.rainbow_pool_widget: QWidget | None = None

        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, expanded: bool):
        """Handle panel expand/collapse."""
        if expanded and not self._initialized:
            self._initialized = True
            self._init_content()

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
        self.rainbow_check.toggled.connect(self._on_rainbow_changed)
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
        self.rainbow_colors = self._default_rainbow.copy()

        for row_idx in range(2):
            btn_row_layout = QHBoxLayout()
            btn_row_layout.setSpacing(0)
            btn_row_layout.setContentsMargins(0, 0, 0, 0)

            for col_idx in range(5):  # 5 columns x 2 rows = 10 colors
                i = row_idx * 5 + col_idx
                btn = QPushButton()
                btn.setFixedSize(32, 32)
                btn.setToolTip(f"Branch {i + 1} color")
                color = self.rainbow_colors[i] if i < len(self.rainbow_colors) else "#FFCCCCCC"
                btn.setStyleSheet(
                    f"background-color: {color}; "
                    "border: none; border-radius: 4px;"
                )
                btn.clicked.connect(lambda _, idx=i: self._edit_rainbow_color(idx))
                self.rainbow_buttons.append(btn)
                btn_row_layout.addWidget(btn)

                if col_idx < 4:
                    btn_row_layout.addStretch()

            buttons_layout.addLayout(btn_row_layout)

        buttons_container.setLayout(buttons_layout)
        layout.addWidget(buttons_container, row, 1)
        row += 1

        self.setLayout(layout)

        # Initially hide color pool if rainbow is disabled
        self.rainbow_pool_widget = buttons_container
        self.rainbow_pool_widget.setVisible(self._rainbow_visible)
        if self.rainbow_check:
            self.rainbow_check.blockSignals(False)

    def _on_rainbow_changed(self, checked: bool):
        """Handle rainbow branch mode toggle."""
        self._rainbow_visible = checked

        # Show/hide color pool
        if hasattr(self, 'rainbow_pool_widget') and self.rainbow_pool_widget:
            self.rainbow_pool_widget.setVisible(checked)

        # Emit change
        self.color_changed.emit({"use_rainbow_branches": checked})

    def _edit_rainbow_color(self, index: int):
        """Handle rainbow color button click."""
        # TODO: Implement color picker dialog
        pass

    def get_style(self) -> dict:
        """Get current color scheme style."""
        return {
            "use_rainbow_branches": self._rainbow_visible,
            "branch_colors": self.rainbow_colors.copy(),
        }

    def set_style(self, style: dict):
        """Set color scheme style programmatically."""
        if "use_rainbow_branches" in style:
            self._rainbow_visible = style["use_rainbow_branches"]
            if self.rainbow_check:
                self.rainbow_check.setChecked(self._rainbow_visible)

        if "branch_colors" in style:
            self.rainbow_colors = style["branch_colors"].copy()
            # Update button colors
            for i, btn in enumerate(self.rainbow_buttons):
                if i < len(self.rainbow_colors):
                    color = self.rainbow_colors[i]
                    btn.setStyleSheet(
                        f"background-color: {color}; "
                        "border: none; border-radius: 4px;"
                    )
