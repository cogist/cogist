"""Spacing configuration section widget.

Provides controls for customizing spacing values for parent-child and sibling spacing.
Implements lazy initialization for better performance.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QSpinBox

from .collapsible_panel import CollapsiblePanel


class SpacingSection(CollapsiblePanel):
    """Spacing configuration settings with lazy initialization.

    Signals:
        spacing_changed(dict): Emitted when spacing configuration changes
    """

    spacing_changed = Signal(dict)

    # UI constants
    LABEL_WIDTH = 75
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Spacing", collapsed=True, parent=parent)

        # State
        self._initialized = False
        self.current_spacing = self._get_default_spacing()

        # Connect toggle signal for lazy initialization
        self.toggled.connect(self._on_toggled)

    def _get_default_spacing(self) -> dict:
        """Get default spacing configuration."""
        return {
            "parent_child": 20,
            "sibling": 15,
        }

    def _on_toggled(self, checked: bool):
        """Handle expand/collapse events."""
        if checked and not self._initialized:
            self._init_content()
            self._initialized = True

    def _init_content(self):
        """Initialize content on first expand (lazy initialization)."""
        layout = QGridLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(self.GROUP_MARGIN, 16, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        row = 0

        # Parent-child spacing
        pc_label = QLabel("Parent-Child:")
        pc_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pc_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(pc_label, row, 0)

        self.parent_child_spin = QSpinBox()
        self.parent_child_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.parent_child_spin.setRange(0, 100)
        self.parent_child_spin.setValue(self.current_spacing["parent_child"])
        self.parent_child_spin.valueChanged.connect(self._on_spacing_changed)
        layout.addWidget(self.parent_child_spin, row, 1)
        row += 1

        # Sibling spacing
        sib_label = QLabel("Sibling:")
        sib_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        sib_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(sib_label, row, 0)

        self.sibling_spin = QSpinBox()
        self.sibling_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.sibling_spin.setRange(0, 100)
        self.sibling_spin.setValue(self.current_spacing["sibling"])
        self.sibling_spin.valueChanged.connect(self._on_spacing_changed)
        layout.addWidget(self.sibling_spin, row, 1)

        self.setLayout(layout)

    def _on_spacing_changed(self):
        """Handle spacing spin box changes."""
        if not hasattr(self, 'parent_child_spin') or not hasattr(self, 'sibling_spin'):
            return

        self.current_spacing["parent_child"] = self.parent_child_spin.value()
        self.current_spacing["sibling"] = self.sibling_spin.value()
        self._emit_spacing_changed()

    def _emit_spacing_changed(self):
        """Emit spacing changed signal."""
        self.spacing_changed.emit(self.current_spacing.copy())

    def get_spacing(self) -> dict:
        """Get current spacing configuration."""
        return self.current_spacing.copy()

    def set_spacing(self, spacing: dict):
        """Set spacing configuration programmatically."""
        self.current_spacing.update(spacing)

        if self._initialized:
            if "parent_child" in spacing:
                self.parent_child_spin.setValue(spacing["parent_child"])

            if "sibling" in spacing:
                self.sibling_spin.setValue(spacing["sibling"])
