"""Node style section widget.

Provides controls for customizing node appearance including shape, colors,
padding, and font properties. Implements lazy initialization for better performance.
"""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSpinBox,
    QWidget,
)

from cogist.presentation.widgets import VisualPreviewButton
from cogist.presentation.widgets.node_shape_previews import (
    generate_bottom_line_preview,
    generate_circle_preview,
    generate_left_line_preview,
    generate_rounded_rect_preview,
)

from .collapsible_panel import CollapsiblePanel


class NodeStyleSection(CollapsiblePanel):
    """Node style settings with lazy initialization.

    Signals:
        style_changed(dict): Emitted when any node style property changes
        shadow_enabled_changed(bool): Emitted when shadow enabled state changes
    """

    style_changed = Signal(dict)
    shadow_enabled_changed = Signal(bool)

    # UI constants
    LABEL_WIDTH = 75
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Node Style", collapsed=True, parent=parent)

        # State
        self._initialized = False
        self.current_style = self._get_default_style()

        # Connect toggle signal for lazy initialization
        self.toggled.connect(self._on_toggled)

    def _get_default_style(self) -> dict:
        """Get default node style - used only during initialization before real data is loaded."""
        # This should be overwritten by set_style() before any UI interaction
        return {
            "shape": "rounded_rect",
            "radius": 10,
            "bg_color": "#2196F3",
            "text_color": "#FFFFFF",
            "padding_w": 20,
            "padding_h": 16,
            "font_family": "Arial",
            "font_size": 14,
            "font_weight": "Normal",
            "font_italic": False,
            "font_underline": False,
            "font_strikeout": False,
            "shadow_enabled": False,
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

        # Style selector - using reusable VisualPreviewButton
        style_label = QLabel("Style:")
        style_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        style_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(style_label, row, 0)

        # Create visual options for popup
        style_options = [
            ("rounded_rect", generate_rounded_rect_preview, QSize(140, 50)),
            ("circle", generate_circle_preview, QSize(140, 50)),
            ("bottom_line", generate_bottom_line_preview, QSize(140, 50)),
            ("left_line", generate_left_line_preview, QSize(140, 50)),
        ]

        # Create reusable visual preview button
        self.style_btn = VisualPreviewButton(
            options=style_options,
            initial_value=self.current_style.get("shape", "rounded_rect"),
            preview_size=QSize(140, 50),
            button_height=self.WIDGET_HEIGHT,
        )
        self.style_btn.value_changed.connect(self._on_shape_changed)
        layout.addWidget(self.style_btn, row, 1)
        row += 1

        # Corner radius
        radius_label = QLabel("Radius:")
        radius_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        radius_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(radius_label, row, 0)

        self.radius_spin = QSpinBox()
        self.radius_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.radius_spin.setRange(0, 30)
        self.radius_spin.setValue(self.current_style["radius"])
        self.radius_spin.setAlignment(Qt.AlignLeft)
        self.radius_spin.valueChanged.connect(self._on_radius_changed)

        # Set initial enabled state based on current shape
        container_shapes = ["rounded_rect", "rect", "circle", "ellipse"]
        current_shape = self.current_style.get("shape", "rounded_rect")
        self.radius_spin.setEnabled(current_shape in container_shapes)

        layout.addWidget(self.radius_spin, row, 1)
        row += 1

        # Background color
        bg_label = QLabel("Background:")
        bg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bg_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(bg_label, row, 0)

        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.bg_color_btn.setStyleSheet(
            f"background-color: {self.current_style['bg_color']}; "
            "border: 1px solid #ccc; border-radius: 6px;"
        )
        self.bg_color_btn.clicked.connect(lambda: self._pick_color("bg_color"))
        layout.addWidget(self.bg_color_btn, row, 1)
        row += 1

        # Text color
        text_label = QLabel("Text Color:")
        text_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        text_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(text_label, row, 0)

        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.text_color_btn.setStyleSheet(
            f"background-color: {self.current_style['text_color']}; "
            "border: 1px solid #ccc; border-radius: 6px;"
        )
        self.text_color_btn.clicked.connect(lambda: self._pick_color("text_color"))
        layout.addWidget(self.text_color_btn, row, 1)
        row += 1

        # Padding W
        padding_w_label = QLabel("Padding W:")
        padding_w_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        padding_w_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(padding_w_label, row, 0)

        self.padding_w_spin = QSpinBox()
        self.padding_w_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.padding_w_spin.setRange(0, 50)
        self.padding_w_spin.setValue(self.current_style["padding_w"])
        self.padding_w_spin.setAlignment(Qt.AlignLeft)
        self.padding_w_spin.valueChanged.connect(self._on_padding_changed)
        layout.addWidget(self.padding_w_spin, row, 1)
        row += 1

        # Padding H
        padding_h_label = QLabel("Padding H:")
        padding_h_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        padding_h_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(padding_h_label, row, 0)

        self.padding_h_spin = QSpinBox()
        self.padding_h_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.padding_h_spin.setRange(0, 50)
        self.padding_h_spin.setValue(self.current_style["padding_h"])
        self.padding_h_spin.setAlignment(Qt.AlignLeft)
        self.padding_h_spin.valueChanged.connect(self._on_padding_changed)
        layout.addWidget(self.padding_h_spin, row, 1)
        row += 1

        # Font family
        font_family_label = QLabel("Font:")
        font_family_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_family_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(font_family_label, row, 0)

        self.font_family_combo = QPushButton(self.current_style["font_family"])
        self.font_family_combo.setFixedHeight(self.WIDGET_HEIGHT)
        self.font_family_combo.setStyleSheet(self._button_style())
        self.font_family_combo.clicked.connect(self._show_font_menu)
        layout.addWidget(self.font_family_combo, row, 1)
        row += 1

        # Font size
        font_size_label = QLabel("Font Size:")
        font_size_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_size_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(font_size_label, row, 0)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(self.current_style["font_size"])
        self.font_size_spin.setAlignment(Qt.AlignLeft)
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        layout.addWidget(self.font_size_spin, row, 1)
        row += 1

        # Font weight
        font_weight_label = QLabel("Weight:")
        font_weight_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_weight_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(font_weight_label, row, 0)

        self.font_weight_combo = QPushButton(self.current_style["font_weight"])
        self.font_weight_combo.setFixedHeight(self.WIDGET_HEIGHT)
        self.font_weight_combo.setStyleSheet(self._button_style())

        self.font_weight_menu = QMenu()
        self.font_weight_menu.aboutToShow.connect(
            lambda: self._update_font_weight_options()
        )

        # Initial weight options (will be updated dynamically)
        weight_options = ["Light", "Normal", "Bold", "ExtraBold"]
        for option in weight_options:
            action = self.font_weight_menu.addAction(option)
            action.triggered.connect(lambda _, opt=option: self._set_font_weight(opt))

        self.font_weight_combo.setMenu(self.font_weight_menu)
        layout.addWidget(self.font_weight_combo, row, 1)
        row += 1

        # Font style checkboxes - 2x2 grid layout
        font_style_label = QLabel("Font Style:")
        font_style_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_style_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(font_style_label, row, 0)

        # Container for 2x2 checkbox grid
        style_container = QWidget()
        style_layout = QGridLayout(style_container)
        style_layout.setSpacing(6)
        style_layout.setContentsMargins(0, 0, 0, 4)

        self.font_italic_check = QCheckBox("Italic")
        self.font_italic_check.setChecked(self.current_style["font_italic"])
        self.font_italic_check.setStyleSheet("QCheckBox { background: transparent; }")
        self.font_italic_check.toggled.connect(self._on_font_style_changed)
        style_layout.addWidget(self.font_italic_check, 0, 0)

        self.font_underline_check = QCheckBox("Underline")
        self.font_underline_check.setChecked(self.current_style["font_underline"])
        self.font_underline_check.setStyleSheet("QCheckBox { background: transparent; }")
        self.font_underline_check.toggled.connect(self._on_font_style_changed)
        style_layout.addWidget(self.font_underline_check, 0, 1)

        self.font_strikeout_check = QCheckBox("Strikeout")
        self.font_strikeout_check.setChecked(self.current_style["font_strikeout"])
        self.font_strikeout_check.setStyleSheet("QCheckBox { background: transparent; }")
        self.font_strikeout_check.toggled.connect(self._on_font_style_changed)
        style_layout.addWidget(self.font_strikeout_check, 1, 0)

        self.font_shadow_check = QCheckBox("Shadow")
        self.font_shadow_check.setChecked(self.current_style.get("shadow_enabled", False))
        self.font_shadow_check.setStyleSheet("QCheckBox { background: transparent; }")
        self.font_shadow_check.toggled.connect(self._on_font_shadow_toggled)
        style_layout.addWidget(self.font_shadow_check, 1, 1)

        layout.addWidget(style_container, row, 1)

        self.setLayout(layout)

    def _button_style(self) -> str:
        """Get standard button stylesheet."""
        return """
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
        """

    def _on_shape_changed(self, shape_name: str):
        """Handle shape selection change."""
        self.current_style["shape"] = shape_name

        # Show/hide radius control based on shape type
        container_shapes = ["rounded_rect", "rect", "circle", "ellipse"]
        show_radius = shape_name in container_shapes

        if hasattr(self, 'radius_spin'):
            self.radius_spin.setEnabled(show_radius)

        self._emit_style_changed()

    def _on_radius_changed(self, value: int):
        """Handle radius change."""
        self.current_style["radius"] = value
        self._emit_style_changed()

    def _pick_color(self, color_type: str):
        """Open color picker dialog."""
        from PySide6.QtWidgets import QColorDialog

        current_color = self.current_style.get(f"{color_type}", "#FFFFFF")
        current = QColor(current_color)

        # Determine which button was clicked
        if color_type == "bg_color":
            button = self.bg_color_btn
        elif color_type == "text_color":
            button = self.text_color_btn
        else:
            return

        color = QColorDialog.getColor(current, self, f"Select {color_type.replace('_', ' ').title()} Color", QColorDialog.ShowAlphaChannel)

        if color.isValid():
            # Use name(QColor.HexArgb) to preserve alpha channel
            color_name = color.name(QColor.HexArgb)
            self.current_style[color_type] = color_name

            # Update button appearance
            button.setStyleSheet(
                f"background-color: {color_name}; border: 1px solid #ccc; border-radius: 6px;"
            )

            self._emit_style_changed()

    def _on_padding_changed(self):
        """Handle padding changes."""
        self.current_style["padding_w"] = self.padding_w_spin.value()
        self.current_style["padding_h"] = self.padding_h_spin.value()
        self._emit_style_changed()

    def _get_localized_font_name(self, font_family: str) -> str:
        """Get localized font name for display.

        Uses platform-specific APIs to get the localized font name:
        - macOS: Core Text via PyObjC
        - Windows: ctypes with GDI
        - Linux: fontconfig
        Falls back to English name if localized name not available.
        """
        import platform
        system = platform.system()

        try:
            if system == "Darwin":  # macOS
                # Try to use Core Text via PyObjC
                try:
                    from CoreText import (  # type: ignore
                        CTFontCopyDisplayName,
                        CTFontCreateWithName,
                    )

                    # Create a CTFontRef
                    ct_font = CTFontCreateWithName(font_family, 12.0, None)
                    if ct_font:
                        # Get display name (localized)
                        display_name = CTFontCopyDisplayName(ct_font)
                        if display_name:
                            return str(display_name)
                except Exception:
                    pass  # Fall through to default

            elif system == "Windows":
                # Try to use ctypes with GDI (simplified)
                try:
                    import ctypes
                    from ctypes import wintypes

                    gdi32 = ctypes.windll.gdi32
                    hdc = gdi32.CreateDCW("DISPLAY", None, None, None)

                    class LOGFONTW(ctypes.Structure):
                        _fields_ = [
                            ("lfHeight", wintypes.LONG),
                            ("lfWidth", wintypes.LONG),
                            ("lfEscapement", wintypes.LONG),
                            ("lfOrientation", wintypes.LONG),
                            ("lfWeight", wintypes.LONG),
                            ("lfItalic", wintypes.BYTE),
                            ("lfUnderline", wintypes.BYTE),
                            ("lfStrikeOut", wintypes.BYTE),
                            ("lfCharSet", wintypes.BYTE),
                            ("lfOutPrecision", wintypes.BYTE),
                            ("lfClipPrecision", wintypes.BYTE),
                            ("lfQuality", wintypes.BYTE),
                            ("lfPitchAndFamily", wintypes.BYTE),
                            ("lfFaceName", wintypes.WCHAR * 32),
                        ]

                    logfont = LOGFONTW()
                    logfont.lfHeight = 0
                    logfont.lfFaceName = font_family

                    hfont = gdi32.CreateFontIndirectW(ctypes.byref(logfont))
                    old_font = gdi32.SelectObject(hdc, hfont)
                    gdi32.SelectObject(hdc, old_font)
                    gdi32.DeleteObject(hfont)
                    gdi32.DeleteDC(hdc)
                except Exception:
                    pass

            elif system == "Linux":
                # Try to use fontconfig
                try:
                    import subprocess
                    result = subprocess.run(
                        ["fc-match", "-f", "%{family}", font_family],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        return result.stdout.strip()
                except Exception:
                    pass

        except Exception:
            pass

        # Fallback: return the original font family name
        return font_family

    def _show_font_menu(self):
        """Show font family selection dialog with localized names."""
        from PySide6.QtGui import QFont, QFontDatabase
        from PySide6.QtWidgets import QDialog, QListWidget, QVBoxLayout

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Font")
        dialog.setFixedSize(350, 450)

        # Layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Font list
        font_list = QListWidget()
        font_list.setFont(QFont("Arial", 15))
        layout.addWidget(font_list)

        # Get all available fonts
        font_db = QFontDatabase()
        families = font_db.families()

        # Filter out bitmap/system fonts that cause warnings
        filtered_families = []
        for family in families:
            # Skip system internal fonts (start with '.')
            if family.startswith('.'):
                continue
            # Skip bitmap fonts and system fonts
            if any(keyword in family.lower() for keyword in ['bitmap', 'dingbats', 'symbol', 'icon']):
                continue
            # Skip if font has no styles
            if not font_db.styles(family):
                continue
            filtered_families.append(family)

        families = filtered_families

        current_family = self.current_style.get("font_family", "Arial")

        # Build font list with localized names and deduplication
        font_name_map = {}  # Maps display name -> actual font family
        seen_base_names = set()  # Track base font names for deduplication

        for family in families:
            # Get localized name first
            localized_name = self._get_localized_font_name(family)

            # Normalize for deduplication: remove common suffixes to get base font name
            base_name = family.split('(')[0].strip().lower()

            # Check if we've seen this base font name before
            is_duplicate = False
            for seen_base in seen_base_names:
                # If one contains the other, they're likely variants of the same font
                if base_name in seen_base or seen_base in base_name:
                    is_duplicate = True
                    break

            if not is_duplicate:
                seen_base_names.add(base_name)
                font_name_map[localized_name] = family

                from PySide6.QtWidgets import QListWidgetItem
                item = QListWidgetItem(localized_name)
                item.setFont(QFont(family))  # Use actual font for rendering
                font_list.addItem(item)

                if family == current_family:
                    font_list.setCurrentItem(item)

        # Double-click to select
        def on_item_double_clicked(item):
            display_name = item.text()
            actual_family = font_name_map.get(display_name, display_name)
            self._set_font_family(actual_family)
            dialog.accept()

        font_list.itemDoubleClicked.connect(on_item_double_clicked)

        # Position dialog to the right of the font button
        button_pos = self.font_family_combo.mapToGlobal(self.font_family_combo.rect().topLeft())
        button_width = self.font_family_combo.width()
        dialog_x = button_pos.x() + button_width + 4  # 4px gap to the right
        dialog_y = button_pos.y()  # Align top edges

        # Show dialog first, then move it (to avoid Qt's automatic positioning)
        dialog.show()
        dialog.move(dialog_x, dialog_y)
        dialog.raise_()
        dialog.activateWindow()

        # Click outside to close
        dialog.setMouseTracking(True)
        def on_mouse_press(event):
            if event.button() == Qt.LeftButton:
                dialog.reject()
        dialog.mousePressEvent = on_mouse_press

        # ESC to close
        dialog.keyPressEvent = lambda event: dialog.reject() if event.key() == Qt.Key_Escape else QDialog.keyPressEvent(dialog, event)

        # Show dialog
        dialog.exec()

    def _set_font_family(self, family: str):
        """Set font family."""
        # Get localized name for display
        localized_name = self._get_localized_font_name(family)
        self.font_family_combo.setText(localized_name)
        self.current_style["font_family"] = family

        # Update font weight options based on new font
        self._update_font_weight_options()

        self._emit_style_changed()

    def _on_font_size_changed(self, value: int):
        """Handle font size change."""
        self.current_style["font_size"] = value
        self._emit_style_changed()

    def _update_font_weight_options(self):
        """Update font weight menu based on available weights for the current font.

        Filters out italic/oblique styles and sorts by weight priority.
        Detects and removes duplicate weights (e.g., Normal/Regular may be the same).
        """
        from PySide6.QtGui import QFontDatabase

        font_family = self.current_style.get("font_family", "Arial")
        font_db = QFontDatabase()
        styles = font_db.styles(font_family)

        if not styles:
            # Fallback to default weights if no styles found
            styles = ["Thin", "ExtraLight", "Light", "Regular", "Normal", "Medium", "Bold", "ExtraBold", "Black"]

        # Filter out italic/oblique styles - these are not weights
        weight_styles = [s for s in styles if "italic" not in s.lower() and "oblique" not in s.lower()]

        # Define weight priority for sorting
        weight_priority = {
            "Thin": 1,
            "Hairline": 1,
            "ExtraLight": 2,
            "UltraLight": 2,
            "Light": 3,
            "Regular": 4,
            "Normal": 4,
            "Medium": 5,
            "Semi Bold": 6,
            "SemiBold": 6,
            "Demi Bold": 6,
            "DemiBold": 6,
            "Bold": 7,
            "Extra Bold": 8,
            "ExtraBold": 8,
            "Ultra Bold": 8,
            "UltraBold": 8,
            "Black": 9,
            "Heavy": 9,
        }

        # Sort styles by weight priority
        sorted_styles = sorted(
            weight_styles,
            key=lambda s: weight_priority.get(s, 100)
        )

        # Detect and remove duplicate weights
        # When two styles have the same weight value, prefer the more common name
        # Priority: Regular > Normal, Light > ExtraLight, etc.
        weight_name_priority = {
            "Regular": 1,
            "Normal": 2,
            "Light": 1,
            "ExtraLight": 2,
            "UltraLight": 3,
            "Medium": 1,
            "SemiBold": 1,
            "Semi Bold": 2,
            "DemiBold": 3,
            "Demi Bold": 4,
            "Bold": 1,
            "ExtraBold": 1,
            "Extra Bold": 2,
            "UltraBold": 3,
            "Ultra Bold": 4,
            "Black": 1,
            "Heavy": 2,
            "Thin": 1,
            "Hairline": 2,
        }

        unique_styles = []
        seen_weights = {}  # Maps weight_value -> (style_name, priority)

        for style in sorted_styles:
            # Get the weight value for this style using QFontDatabase
            weight_value = font_db.weight(font_family, style)

            # Get priority for this style name (lower is better)
            priority = weight_name_priority.get(style, 100)

            # If we haven't seen this weight value, or this style has higher priority
            if weight_value not in seen_weights:
                seen_weights[weight_value] = (style, priority)
            else:
                existing_style, existing_priority = seen_weights[weight_value]
                if priority < existing_priority:
                    # Replace with higher priority style
                    seen_weights[weight_value] = (style, priority)

        # Build final list maintaining sort order
        seen_in_final = set()
        for style in sorted_styles:
            weight_value = font_db.weight(font_family, style)
            if weight_value in seen_weights:
                best_style, _ = seen_weights[weight_value]
                if best_style == style and style not in seen_in_final:
                    unique_styles.append(style)
                    seen_in_final.add(style)

        # Rebuild the menu with unique styles
        self.font_weight_menu.clear()
        for style in unique_styles:
            action = self.font_weight_menu.addAction(style)
            action.triggered.connect(lambda _, opt=style: self._set_font_weight(opt))

        # Update current selection if it's still valid
        current_weight = self.current_style.get("font_weight", "Normal")
        if current_weight not in unique_styles:
            # Select first available weight or closest match
            current_weight = unique_styles[0] if unique_styles else "Normal"
            self.current_style["font_weight"] = current_weight

        self.font_weight_combo.setText(current_weight)

    def _set_font_weight(self, value: str):
        """Set font weight."""
        self.font_weight_combo.setText(value)
        self.current_style["font_weight"] = value
        self._emit_style_changed()

    def _on_font_style_changed(self):
        """Handle font style checkbox changes."""
        self.current_style["font_italic"] = self.font_italic_check.isChecked()
        self.current_style["font_underline"] = self.font_underline_check.isChecked()
        self.current_style["font_strikeout"] = self.font_strikeout_check.isChecked()
        self._emit_style_changed()

    def _on_font_shadow_toggled(self, checked: bool):
        """Handle font shadow checkbox toggle."""
        self.current_style["shadow_enabled"] = checked
        self.shadow_enabled_changed.emit(checked)
        self._emit_style_changed()

    def _emit_style_changed(self):
        """Emit style changed signal with only node-style fields."""
        # Only emit fields managed by NodeStyleSection to avoid overwriting other sections' data
        node_only_style = {
            "shape": self.current_style["shape"],
            "radius": self.current_style["radius"],
            "bg_color": self.current_style["bg_color"],
            "text_color": self.current_style["text_color"],
            "padding_w": self.current_style["padding_w"],
            "padding_h": self.current_style["padding_h"],
            "font_family": self.current_style["font_family"],
            "font_size": self.current_style["font_size"],
            "font_weight": self.current_style["font_weight"],
            "font_italic": self.current_style["font_italic"],
            "font_underline": self.current_style["font_underline"],
            "font_strikeout": self.current_style["font_strikeout"],
            "shadow_enabled": self.current_style["shadow_enabled"],
        }
        self.style_changed.emit(node_only_style)

    def get_style(self) -> dict:
        """Get current node style."""
        return self.current_style.copy()

    def set_style(self, style: dict):
        """Set node style programmatically.

        Args:
            style: Dictionary containing node style properties
        """
        self.current_style.update(style)

        # Update UI if initialized
        if self._initialized:
            if "shape" in style:
                # Update preview button
                self.shape_btn.set_value(style["shape"])

                # Update radius enabled state
                container_shapes = ["rounded_rect", "rect", "circle", "ellipse"]
                if hasattr(self, 'radius_spin'):
                    self.radius_spin.setEnabled(style["shape"] in container_shapes)

            if "radius" in style:
                self.radius_spin.setValue(style["radius"])

            if "bg_color" in style:
                self.bg_color_btn.setStyleSheet(
                    f"background-color: {style['bg_color']}; border: 1px solid #ccc; border-radius: 6px;"
                )

            if "text_color" in style:
                self.text_color_btn.setStyleSheet(
                    f"background-color: {style['text_color']}; border: 1px solid #ccc; border-radius: 6px;"
                )

            if "padding_w" in style:
                self.padding_w_spin.setValue(style["padding_w"])
            if "padding_h" in style:
                self.padding_h_spin.setValue(style["padding_h"])

            if "font_family" in style:
                localized_name = self._get_localized_font_name(style["font_family"])
                self.font_family_combo.setText(localized_name)
            if "font_size" in style:
                self.font_size_spin.setValue(style["font_size"])
            if "font_weight" in style:
                self.font_weight_combo.setText(style["font_weight"])

            if "font_italic" in style:
                self.font_italic_check.setChecked(style["font_italic"])
            if "font_underline" in style:
                self.font_underline_check.setChecked(style["font_underline"])
            if "font_strikeout" in style:
                self.font_strikeout_check.setChecked(style["font_strikeout"])
            if "shadow_enabled" in style:
                self.font_shadow_check.setChecked(style["shadow_enabled"])
