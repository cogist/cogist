"""Spacing configuration section widget.

Provides controls for customizing spacing values for parent-child and sibling spacing.
Implements lazy initialization for better performance.
"""

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QGridLayout, QLabel

from .collapsible_panel import CollapsiblePanel
from .spinbox import SpinBox


class SpacingSection(CollapsiblePanel):
    """Spacing configuration settings with lazy initialization.

    Signals:
        spacing_changed(dict): Emitted when spacing configuration changes
    """

    spacing_changed = Signal(dict)

    # UI constants (fallback value, will use parent's LABEL_WIDTH if available)
    LABEL_WIDTH = 90
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Spacing", collapsed=True, parent=parent)

        # Get LABEL_WIDTH from parent (StyleEditorTab) if available, otherwise use class default
        self._label_width = getattr(parent, 'LABEL_WIDTH', self.LABEL_WIDTH) if parent else self.LABEL_WIDTH

        # State - will be initialized from style_config when loaded
        self._initialized = False
        self.current_spacing = {}  # Will be set by set_spacing() before UI is shown

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
        layout.setContentsMargins(self.GROUP_MARGIN, 6, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        row = 0

        # Horizontal spacing (Parent-Child)
        pc_label = QLabel("H-Spacing:")
        pc_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pc_label.setFixedWidth(self._label_width)
        layout.addWidget(pc_label, row, 0)

        self.parent_child_spin = SpinBox()
        self.parent_child_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.parent_child_spin.setRange(0, 100)
        self.parent_child_spin.setValue(int(self.current_spacing["parent_child"]))
        self.parent_child_spin.valueChanged.connect(self._on_spacing_changed)
        layout.addWidget(self.parent_child_spin, row, 1)
        row += 1

        # Vertical spacing (Sibling)
        sib_label = QLabel("V-Spacing:")
        sib_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        sib_label.setFixedWidth(self._label_width)
        layout.addWidget(sib_label, row, 0)

        self.sibling_spin = SpinBox()
        self.sibling_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.sibling_spin.setRange(0, 100)
        self.sibling_spin.setValue(int(self.current_spacing["sibling"]))
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
        """Set spacing configuration programmatically without triggering signals."""
        self.current_spacing = spacing.copy()

        if self._initialized:
            # Block signals to prevent triggering layout refresh when loading data
            self.parent_child_spin.blockSignals(True)
            self.sibling_spin.blockSignals(True)

            try:
                if "parent_child" in spacing:
                    self.parent_child_spin.setValue(int(spacing["parent_child"]))
                if "sibling" in spacing:
                    self.sibling_spin.setValue(int(spacing["sibling"]))
            finally:
                # Restore signal emission
                self.parent_child_spin.blockSignals(False)
                self.sibling_spin.blockSignals(False)

