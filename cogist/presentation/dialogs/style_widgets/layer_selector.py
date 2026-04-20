"""Layer selector widget for advanced style panel.

Provides a dropdown menu to select different layers (Canvas, Root, Level 1-3+, etc.)
with collapsible behavior and lazy initialization.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QMenu, QPushButton, QWidget


class LayerSelector(QGroupBox):
    """Layer selection widget with collapsible behavior.
    
    Signals:
        layer_changed(str): Emitted when user selects a different layer
    """
    
    layer_changed = Signal(str)
    
    # UI constants
    LABEL_WIDTH = 75
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10
    
    def __init__(self, parent=None):
        super().__init__("Layer Selection", parent)
        
        # Make it collapsible
        self.setCheckable(True)
        self.setChecked(True)  # Default expanded
        
        # Current layer
        self.current_layer = "canvas"
        
        # Initialize UI
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QGridLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(self.GROUP_MARGIN, 16, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        
        # Layer label
        layer_label = QLabel("Layer:")
        layer_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layer_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(layer_label, 0, 0)
        
        # Layer combo button
        self.layer_combo = QPushButton("Canvas")
        self.layer_combo.setFixedHeight(self.WIDGET_HEIGHT)
        self.layer_combo.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 24px 4px 12px;
                font-size: 13px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #A0A0A0;
            }
        """)
        
        # Create menu
        self.layer_menu = QMenu()
        self.layer_menu.aboutToShow.connect(self._adjust_menu_width)
        
        # Add layer options
        layer_options = [
            "Canvas",
            "---",
            "Root",
            "Level 1",
            "Level 2",
            "Level 3+",
            "---",
            "Critical",
            "Minor",
        ]
        
        for option in layer_options:
            if option == "---":
                self.layer_menu.addSeparator()
            else:
                action = self.layer_menu.addAction(option)
                action.triggered.connect(lambda _, opt=option: self._on_layer_selected(opt))
        
        self.layer_combo.setMenu(self.layer_menu)
        layout.addWidget(self.layer_combo, 0, 1)
        
        self.setLayout(layout)
    
    def _adjust_menu_width(self):
        """Adjust the menu width to match the button width."""
        self.layer_menu.setFixedWidth(self.layer_combo.width())
    
    def _on_layer_selected(self, value: str):
        """Handle layer selection."""
        # Update button text
        self.layer_combo.setText(value)
        
        # Map display name to internal name
        layer_map = {
            "Canvas": "canvas",
            "Root": "root",
            "Level 1": "level_1",
            "Level 2": "level_2",
            "Level 3+": "level_3_plus",
            "Critical": "critical",
            "Minor": "minor",
        }
        
        self.current_layer = layer_map.get(value, "canvas")
        
        # Emit signal
        self.layer_changed.emit(self.current_layer)
    
    def get_current_layer(self) -> str:
        """Get the current selected layer."""
        return self.current_layer
    
    def set_layer(self, layer_name: str):
        """Set the current layer programmatically.
        
        Args:
            layer_name: Internal layer name (canvas, root, level_1, etc.)
        """
        # Map internal name to display name
        display_map = {
            "canvas": "Canvas",
            "root": "Root",
            "level_1": "Level 1",
            "level_2": "Level 2",
            "level_3_plus": "Level 3+",
            "critical": "Critical",
            "minor": "Minor",
        }
        
        display_name = display_map.get(layer_name, "Canvas")
        self.layer_combo.setText(display_name)
        self.current_layer = layer_name
