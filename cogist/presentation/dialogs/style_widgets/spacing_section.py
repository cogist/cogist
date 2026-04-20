"""Spacing configuration section widget.

Provides controls for customizing spacing levels (Compact/Normal/Relaxed/Spacious)
for parent-child and sibling spacing. Implements lazy initialization for better performance.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QRadioButton, QVBoxLayout

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
            "parent_child": "normal",
            "sibling": "normal",
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

        # Parent-child spacing
        pc_label = QLabel("Parent-Child:")
        pc_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pc_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(pc_label, 0, 0)

        pc_radio_layout = QHBoxLayout()
        pc_radio_layout.setSpacing(12)
        self.pc_compact_radio = QRadioButton("Compact")
        self.pc_normal_radio = QRadioButton("Normal")
        self.pc_relaxed_radio = QRadioButton("Relaxed")
        self.pc_normal_radio.setChecked(True)
        self.pc_compact_radio.toggled.connect(self._on_spacing_changed)
        self.pc_normal_radio.toggled.connect(self._on_spacing_changed)
        self.pc_relaxed_radio.toggled.connect(self._on_spacing_changed)
        pc_radio_layout.addWidget(self.pc_compact_radio)
        pc_radio_layout.addWidget(self.pc_normal_radio)
        pc_radio_layout.addWidget(self.pc_relaxed_radio)
        pc_radio_layout.addStretch()
        layout.addLayout(pc_radio_layout, 0, 1)

        # Sibling spacing
        sib_label = QLabel("Sibling:")
        sib_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        sib_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(sib_label, 1, 0)

        sib_radio_layout = QHBoxLayout()
        sib_radio_layout.setSpacing(12)
        self.sib_compact_radio = QRadioButton("Compact")
        self.sib_normal_radio = QRadioButton("Normal")
        self.sib_relaxed_radio = QRadioButton("Relaxed")
        self.sib_normal_radio.setChecked(True)
        self.sib_compact_radio.toggled.connect(self._on_spacing_changed)
        self.sib_normal_radio.toggled.connect(self._on_spacing_changed)
        self.sib_relaxed_radio.toggled.connect(self._on_spacing_changed)
        sib_radio_layout.addWidget(self.sib_compact_radio)
        sib_radio_layout.addWidget(self.sib_normal_radio)
        sib_radio_layout.addWidget(self.sib_relaxed_radio)
        sib_radio_layout.addStretch()
        layout.addLayout(sib_radio_layout, 1, 1)

        self.setLayout(layout)

    def _on_spacing_changed(self):
        """Handle spacing radio button changes."""
        # Update state based on which radio buttons are checked
        if self.pc_compact_radio.isChecked():
            self.current_spacing["parent_child"] = "compact"
        elif self.pc_relaxed_radio.isChecked():
            self.current_spacing["parent_child"] = "relaxed"
        else:
            self.current_spacing["parent_child"] = "normal"

        if self.sib_compact_radio.isChecked():
            self.current_spacing["sibling"] = "compact"
        elif self.sib_relaxed_radio.isChecked():
            self.current_spacing["sibling"] = "relaxed"
        else:
            self.current_spacing["sibling"] = "normal"

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
                value = spacing["parent_child"]
                if value == "compact":
                    self.pc_compact_radio.setChecked(True)
                elif value == "relaxed":
                    self.pc_relaxed_radio.setChecked(True)
                else:
                    self.pc_normal_radio.setChecked(True)

            if "sibling" in spacing:
                value = spacing["sibling"]
                if value == "compact":
                    self.sib_compact_radio.setChecked(True)
                elif value == "relaxed":
                    self.sib_relaxed_radio.setChecked(True)
                else:
                    self.sib_normal_radio.setChecked(True)
