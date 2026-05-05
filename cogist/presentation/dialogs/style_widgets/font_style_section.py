"""Font style section widget.

Provides controls for customizing font properties including:
- Font family
- Font size
- Font weight
- Font styles (Italic, Underline, Strikeout)
- Font shadow

Implements lazy initialization for better performance.
"""

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QGridLayout,
    QLabel,
    QMenu,
    QPushButton,
)

from cogist.presentation.widgets import ToggleSwitch

from .collapsible_panel import CollapsiblePanel
from .spinbox import SpinBox


class FontStyleSection(CollapsiblePanel):
    """Font style settings with lazy initialization.

    Signals:
        style_changed(dict): Emitted when any font style property changes
        shadow_enabled_changed(bool): Emitted when shadow enabled state changes
    """

    style_changed = Signal(dict)
    shadow_enabled_changed = Signal(bool)

    # UI constants (fallback value, will use parent's LABEL_WIDTH if available)
    LABEL_WIDTH = 90
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Font Style", collapsed=True, parent=parent)

        # Get LABEL_WIDTH from parent (AdvancedStyleTab) if available, otherwise use class default
        self._label_width = getattr(parent, 'LABEL_WIDTH', self.LABEL_WIDTH) if parent else self.LABEL_WIDTH

        # State
        self._initialized = False
        self.current_style = self._get_default_style()
        self.last_emitted_style = None  # Track last emitted style to detect changes
        self._font_data_cache: tuple[list[tuple[str, str, str]], dict[str, str]] | None = None
        self._font_dialog = None
        self._font_loader = None
        self._load_fonts()  # Pre-load fonts on initialization

        # Connect toggle signal for lazy initialization
        self.toggled.connect(self._on_toggled)

    def _get_default_style(self) -> dict:
        """Get default font style - used only during initialization before real data is loaded."""
        # This should be overwritten by set_style() before any UI interaction
        return {
            "font_family": "Arial",
            "font_size": 14,
            "font_weight": "Normal",
            "font_italic": False,
            "font_underline": False,
            "font_strikeout": False,
            "shadow_enabled": False,
        }

    def _load_fonts(self):
        """Pre-load all available fonts in background thread on initialization."""
        from qtpy.QtCore import QThread, Signal
        from qtpy.QtGui import QFontDatabase

        class FontLoaderThread(QThread):
            """Background thread for loading fonts."""
            fonts_loaded = Signal(object)

            def run(self):
                """Load and process fonts."""
                # Qt6: QFontDatabase constructor is deprecated, use static methods
                families = QFontDatabase.families()

                # Filter out bitmap/system fonts
                filtered_families = []
                for family in families:
                    if family.startswith('.'):
                        continue
                    if any(keyword in family.lower() for keyword in ['bitmap', 'dingbats', 'symbol', 'icon']):
                        continue
                    if not QFontDatabase.styles(family):
                        continue
                    filtered_families.append(family)

                # Return raw family names (localization done in main thread)
                self.fonts_loaded.emit(filtered_families)

        def on_fonts_loaded(filtered_families):
            """Cache the loaded font data."""
            # Process fonts in main thread (for localization)
            font_name_map = {}
            seen_base_names = set()
            items_data = []

            for family in filtered_families:
                # Get localized name
                localized_name = self._get_localized_font_name(family)

                # Normalize for deduplication
                base_name = family.split('(')[0].strip().lower()

                is_duplicate = False
                for seen_base in seen_base_names:
                    if base_name in seen_base or seen_base in base_name:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    seen_base_names.add(base_name)
                    font_name_map[localized_name] = family
                    items_data.append((localized_name, family, family))

            self._font_data_cache = (items_data, font_name_map)

        # Start background loader
        self._font_loader = FontLoaderThread()
        self._font_loader.fonts_loaded.connect(on_fonts_loaded)
        self._font_loader.start()

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

        # Font family
        font_family_label = QLabel("Font:")
        font_family_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_family_label.setFixedWidth(self._label_width)
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
        font_size_label.setFixedWidth(self._label_width)
        layout.addWidget(font_size_label, row, 0)

        self.font_size_spin = SpinBox()
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
        font_weight_label.setFixedWidth(self._label_width)
        layout.addWidget(font_weight_label, row, 0)

        self.font_weight_menu = QMenu()
        self.font_weight_menu.aboutToShow.connect(
            lambda: self._update_font_weight_options()
        )

        # Initial weight options (will be updated dynamically)
        weight_options = ["Light", "Normal", "Bold", "ExtraBold"]
        for option in weight_options:
            action = self.font_weight_menu.addAction(option)
            action.triggered.connect(lambda _, opt=option: self._set_font_weight(opt))

        # Use reusable MenuButton instead of QPushButton
        from .menu_button import MenuButton
        self.font_weight_combo = MenuButton(self.current_style["font_weight"], self.WIDGET_HEIGHT)
        self.font_weight_combo.setStyleSheet(self._button_style())
        self.font_weight_combo.set_menu(self.font_weight_menu)
        layout.addWidget(self.font_weight_combo, row, 1)
        row += 1

        # Italic toggle
        italic_label = QLabel("Italic:")
        italic_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        italic_label.setFixedWidth(self._label_width)
        layout.addWidget(italic_label, row, 0)

        self.font_italic_check = ToggleSwitch()
        self.font_italic_check.setChecked(self.current_style["font_italic"])
        self.font_italic_check.toggled.connect(self._on_font_style_changed)
        layout.addWidget(self.font_italic_check, row, 1, alignment=Qt.AlignRight)
        row += 1

        # Underline toggle
        underline_label = QLabel("Underline:")
        underline_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        underline_label.setFixedWidth(self._label_width)
        layout.addWidget(underline_label, row, 0)

        self.font_underline_check = ToggleSwitch()
        self.font_underline_check.setChecked(self.current_style["font_underline"])
        self.font_underline_check.toggled.connect(self._on_font_style_changed)
        layout.addWidget(self.font_underline_check, row, 1, alignment=Qt.AlignRight)
        row += 1

        # Strikeout toggle
        strikeout_label = QLabel("Strikeout:")
        strikeout_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        strikeout_label.setFixedWidth(self._label_width)
        layout.addWidget(strikeout_label, row, 0)

        self.font_strikeout_check = ToggleSwitch()
        self.font_strikeout_check.setChecked(self.current_style["font_strikeout"])
        self.font_strikeout_check.toggled.connect(self._on_font_style_changed)
        layout.addWidget(self.font_strikeout_check, row, 1, alignment=Qt.AlignRight)
        row += 1

        # Shadow toggle
        shadow_label = QLabel("Shadow:")
        shadow_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        shadow_label.setFixedWidth(self._label_width)
        layout.addWidget(shadow_label, row, 0)

        self.font_shadow_check = ToggleSwitch()
        self.font_shadow_check.setChecked(self.current_style.get("shadow_enabled", False))
        self.font_shadow_check.toggled.connect(self._on_font_shadow_toggled)
        layout.addWidget(self.font_shadow_check, row, 1, alignment=Qt.AlignRight)

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
            QPushButton::menu-indicator {
                image: none;
                width: 0;
                height: 0;
            }
        """

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
        """Show font family selection popup with localized names.

        Uses a frameless dialog with single-click selection for better UX.
        Uses pre-loaded font cache for instant display.
        """
        from qtpy.QtCore import Qt
        from qtpy.QtGui import QFont
        from qtpy.QtWidgets import (
            QDialog,
            QListWidget,
            QVBoxLayout,
        )

        # Reuse existing dialog if available
        if hasattr(self, '_font_dialog') and self._font_dialog is not None:
            # Dialog already created, just show it
            self._font_dialog.show()
            self._font_dialog.raise_()
            self._font_dialog.activateWindow()
            self._font_dialog.setFocus()
            return

        # Store default button style to restore later
        self._default_font_button_style = self.font_family_combo.styleSheet()

        # Set button background to match dialog while open
        self.font_family_combo.setStyleSheet("""
            QPushButton {
                background-color: rgb(236, 236, 236);
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 24px 4px 12px;
                font-size: 13px;
                text-align: left;
            }
        """)

        # Create frameless dialog with rounded corners
        dialog = QDialog(self)
        dialog.setWindowFlags(
            Qt.Dialog | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        )
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.setFixedSize(300, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: rgb(236, 236, 236);
                border: 1px solid #C8C8C8;
                border-radius: 8px;
            }
        """)

        # Store reference to prevent multiple dialogs
        self._font_dialog = dialog

        # Layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Font list with custom styling
        font_list = QListWidget()
        font_list.setFont(QFont("Arial", 14))
        font_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        font_list.setFrameShape(QListWidget.NoFrame)
        font_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: transparent;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QListWidget::item:hover {
                background-color: rgb(84, 143, 255);
                color: white;
            }
            QListWidget::item:selected {
                background-color: rgb(84, 143, 255);
                color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.5);
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 0, 0, 0.7);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        layout.addWidget(font_list)

        # Show dialog immediately
        button_pos = self.font_family_combo.mapToGlobal(
            self.font_family_combo.rect().bottomLeft()
        )
        dialog_x = button_pos.x()
        dialog_y = button_pos.y() + 2  # 2px gap below button

        dialog.show()
        dialog.move(dialog_x, dialog_y)
        dialog.raise_()
        dialog.activateWindow()
        dialog.setFocus()

        # Populate fonts from cache (instant!)
        self._populate_fonts_from_cache(font_list, dialog)

    def _populate_fonts_from_cache(self, font_list, dialog):
        """Populate font list from pre-loaded cache."""
        from qtpy.QtGui import QFont
        from qtpy.QtWidgets import QListWidget, QListWidgetItem

        # Check if cache is ready
        if self._font_data_cache is None:
            # Cache not ready yet, wait for it
            return

        items_data, font_name_map = self._font_data_cache
        current_family = self.current_style.get("font_family", "Arial")

        # Track last hovered item to avoid redundant updates
        last_hovered_item = [None]

        # Hover to set focus (with deduplication)
        def on_item_entered(item):
            if item != last_hovered_item[0]:
                font_list.setCurrentItem(item)
                last_hovered_item[0] = item

        font_list.itemEntered.connect(on_item_entered)
        font_list.setMouseTracking(True)

        # Single-click to select
        def on_item_clicked(item):
            display_name = item.text()
            actual_family = font_name_map.get(display_name, display_name)
            self._set_font_family(actual_family)
            # Restore button style immediately before closing
            self.font_family_combo.setStyleSheet(self._button_style())
            self._font_dialog = None
            dialog.accept()

        font_list.itemClicked.connect(on_item_clicked)

        # ESC to close
        def on_key_press(event):
            if event.key() == Qt.Key_Escape:
                # Restore button style
                self.font_family_combo.setStyleSheet(self._button_style())
                self._font_dialog = None
                dialog.reject()
            else:
                # Call base class implementation
                type(dialog).keyPressEvent(dialog, event)

        dialog.keyPressEvent = on_key_press

        # Close dialog when clicking outside
        def on_mouse_press_outside(event):
            if event.button() == Qt.LeftButton:
                # Restore button style
                self.font_family_combo.setStyleSheet(self._button_style())
                self._font_dialog = None
                dialog.reject()

        dialog.mousePressEvent = on_mouse_press_outside

        # Cleanup when dialog closes
        def cleanup_on_close():
            self.font_family_combo.setStyleSheet(self._button_style())
            self._font_dialog = None

        dialog.finished.connect(cleanup_on_close)

        # Populate the list from cache
        font_list.clear()
        current_item = None
        for display_name, actual_family, render_family in items_data:
            item = QListWidgetItem(display_name)
            item.setFont(QFont(render_family))
            font_list.addItem(item)

            if actual_family == current_family:
                font_list.setCurrentItem(item)
                current_item = item

        # Scroll to current font at the top of the view
        if current_item:
            font_list.scrollToItem(current_item, QListWidget.PositionAtTop)

        dialog.keyPressEvent = on_key_press

        # Close dialog when clicking outside
        def on_mouse_press(event):
            if event.button() == Qt.LeftButton:
                # Restore button style
                self.font_family_combo.setStyleSheet(self._button_style())
                self._font_dialog = None
                dialog.reject()

        dialog.mousePressEvent = on_mouse_press

        # Cleanup when dialog closes (handles ESC, focus loss, and click)
        def cleanup_and_restore():
            # Restore button style using the original method
            self.font_family_combo.setStyleSheet(self._button_style())
            self._font_dialog = None

        # Connect to both accepted and rejected to handle all close scenarios
        dialog.finished.connect(cleanup_and_restore)

        # Position dialog below the font button (like QMenu)
        button_pos = self.font_family_combo.mapToGlobal(
            self.font_family_combo.rect().bottomLeft()
        )
        dialog_x = button_pos.x()
        dialog_y = button_pos.y() + 2  # 2px gap below button

        # Show dialog first, then move it
        dialog.show()
        dialog.move(dialog_x, dialog_y)
        dialog.raise_()
        dialog.activateWindow()
        dialog.setFocus()

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
        from qtpy.QtGui import QFontDatabase

        font_family = self.current_style.get("font_family", "Arial")
        # Qt6: styles() is a static method, no need to create instance
        styles = QFontDatabase.styles(font_family)

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
            # Qt6: weight() is a static method
            weight_value = QFontDatabase.weight(font_family, style)

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
            # Qt6: weight() is a static method
            weight_value = QFontDatabase.weight(font_family, style)
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
        """Emit style changed signal with only changed fields."""
        # If last_emitted_style is None, this means we haven't emitted anything yet
        # Initialize it with current state so future changes can be detected
        if self.last_emitted_style is None:
            self.last_emitted_style = dict(self.current_style)
            return  # Don't emit on initialization

        # Calculate which fields have changed
        changed_fields = {}
        for key, value in self.current_style.items():
            if key not in self.last_emitted_style or self.last_emitted_style[key] != value:
                changed_fields[key] = value

        # Update last emitted style
        self.last_emitted_style = dict(self.current_style)

        # Only emit if there are changes
        if changed_fields:
            self.style_changed.emit(changed_fields)

    def get_style(self) -> dict:
        """Get current font style."""
        return self.current_style.copy()

    def set_style(self, style: dict):
        """Set font style programmatically.

        Args:
            style: Dictionary containing font style properties
        """
        self.current_style.update(style)

        # Update last_emitted_style to match current state
        # This ensures the next change will only emit the actually changed fields
        self.last_emitted_style = dict(self.current_style)

        # Update UI if initialized
        if self._initialized:
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
