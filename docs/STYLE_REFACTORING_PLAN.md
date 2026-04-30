# Style System Refactoring Plan

**Date**: 2026-04-30  
**Status**: Planning Phase  
**Target Version**: v0.9.0 (Breaking Changes - No Backward Compatibility)

---

## 📋 Executive Summary

This refactoring plan restructures the style system to align with the new architecture defined in the authoritative documentation:

- **MINDMAP_STYLE_DATA_STRUCTURE.md**
- **COLOR_SCHEME_DATA_STRUCTURE.md**
- **CGS_FILE_FORMAT.md**
- **TEMPLATE_DATA_STRUCTURE.md**

### Key Design Decisions

1. **Color Pool Expansion**: `branch_colors` now contains **10 colors** (indices 0-7 for branches, index 8 for canvas background, index 9 for root node background)
2. **Flat RoleStyle Structure**: All style fields at the same level (no nested BackgroundStyle/BorderStyle objects)
3. **Index-Based Color References**: Roles reference colors via `*_color_index` pointing to the color pool
4. **Text Color Auto-Calculation**: Text color automatically calculated based on background luminance (threshold 0.5)
5. **No Compatibility Layer**: Since there are no users yet, we can make breaking changes freely

---

## 🎯 Goals

### Primary Goals

1. ✅ Update data structures to match official design documents
2. ✅ Simplify serialization format (single `style/mindmap_style.json` file in CGS)
3. ✅ Remove deprecated code (`color_theme.py`, nested style objects)
4. ✅ Update UI panels to work with new structure
5. ✅ Ensure all rendering code uses `branch_colors[8]` for canvas background

### Non-Goals

- ❌ Maintain backward compatibility with old `.cgs` files
- ❌ Support both old and new architectures simultaneously
- ❌ Preserve legacy template loading mechanisms

---

## 📊 Current State Analysis

### What Needs to Change

#### 1. Data Structures

**Current Issues:**
- `MindMapStyle` has `canvas_bg_color` as separate field ❌
- `RoleBasedStyle` uses nested objects (`BackgroundStyle`, `BorderStyle`) ❌
- `ColorScheme.branch_colors` only has 8 colors ❌
- `ColorScheme` has extra fields that should be removed ❌

**Target State:**
```python
@dataclass
class MindMapStyle:
    name: str = "Default"
    use_rainbow_branches: bool = False
    branch_colors: list[str]  # 10 colors: [0-7] branches, [8] canvas bg, [9] root node
    role_styles: dict[NodeRole, RoleStyle]  # Flat structure
    
@dataclass
class RoleStyle:
    role: NodeRole
    # Shape
    shape_type: str = "basic"
    basic_shape: str = "rounded_rect"
    border_radius: int = 8
    
    # Background (flat fields)
    bg_enabled: bool = True
    bg_color_index: int = 0
    bg_brightness: float = 1.0
    bg_opacity: int = 255
    
    # Border (flat fields)
    border_enabled: bool = True
    border_width: int = 0
    border_color_index: int = 0
    border_brightness: float = 1.0
    border_opacity: int = 255
    border_style: str = "solid"
    
    # Connector (flat fields)
    connector_shape: str = "bezier"
    connector_color_index: int = 0
    connector_brightness: float = 1.0
    connector_opacity: int = 255
    line_width: float = 2.0
    
    # Text
    text_color: str | None = None  # Auto-calculated if None
    font_size: int = 14
    font_weight: str = "Normal"
    font_family: str = "Arial"
    
    # Shadow
    shadow_enabled: bool = False
    shadow_offset_x: int = 2
    shadow_offset_y: int = 2
    shadow_blur: int = 4
    shadow_color: str | None = None  # Default: none
    
    # Spacing
    parent_child_spacing: float = 80.0
    sibling_spacing: float = 60.0
    
    # Padding
    padding_w: int = 12
    padding_h: int = 8
    max_text_width: int = 250

@dataclass
class ColorScheme:
    name: str
    description: str
    branch_colors: list[str]  # 10 colors (index 8 = canvas bg, index 9 = root node)
    default_use_rainbow_branches: bool | None = None
```

#### 2. Files to Delete

- ❌ `cogist/domain/colors/color_theme.py` (obsolete, replaced by ColorScheme)
- ❌ Nested classes in `extended_styles.py`:
  - `BackgroundStyle` (merge into flat `RoleStyle`)
  - `BorderStyle` (merge into flat `RoleStyle`)
  - `NodeShape` (merge into flat `RoleStyle`)
  - `EdgeStyle` (merge into flat `RoleStyle`)
  - `EdgeConfig` (not needed)
  - `NodeColorConfig` (deprecated)

#### 3. Serialization Changes

**Old Format (Multi-file):**
```
style/
├── config.json          # MindMapStyle basic config
├── template.json        # Template with role styles
└── color_scheme.json    # ColorScheme with colors
```

**New Format (Single-file):**
```
style/
└── mindmap_style.json   # Complete MindMapStyle (self-contained)
```

**New JSON Structure:**
```json
{
  "version": "1.0",
  "style": {
    "name": "My Custom Style",
    "use_rainbow_branches": false,
    "branch_colors": [
      "#FFFF6B6B", "#FF4ECDC4", "#FF45B7D1", "#FFFFA07A",
      "#FF98D8C8", "#FFF7DC6F", "#FFBB8FCE", "#FF85C1E2",
      "#FFFFFFFF"  // [8] Canvas Background
    ],
    "role_styles": {
      "root": {
        "role": "root",
        "shape_type": "basic",
        "basic_shape": "rounded_rect",
        "border_radius": 12,
        "bg_enabled": true,
        "bg_color_index": 0,
        "bg_brightness": 1.0,
        "bg_opacity": 255,
        "border_enabled": true,
        "border_width": 3,
        "border_color_index": 0,
        "border_brightness": 1.0,
        "border_opacity": 255,
        "border_style": "solid",
        "connector_shape": "bezier",
        "connector_color_index": 0,
        "connector_brightness": 1.0,
        "connector_opacity": 255,
        "line_width": 2.0,
        "text_color": null,
        "font_size": 22,
        "font_weight": "Bold",
        "font_family": "Arial",
        "shadow_enabled": false,
        "shadow_offset_x": 2,
        "shadow_offset_y": 2,
        "shadow_blur": 4,
        "shadow_color": null,
        "parent_child_spacing": 80.0,
        "sibling_spacing": 60.0,
        "padding_w": 20,
        "padding_h": 16,
        "max_text_width": 300
      },
      // ... other roles
    }
  }
}
```

---

## 🔧 Implementation Plan

### Phase 1: Update Core Data Structures (Priority: HIGH)

#### Task 1.1: Redefine `RoleStyle` as Flat Structure

**File**: `cogist/domain/styles/extended_styles.py`

**Actions:**
1. Create new `RoleStyle` dataclass with all fields flattened
2. Mark old nested classes as deprecated (add deprecation warnings)
3. Keep old classes temporarily for migration (will be deleted in Phase 3)

**Code Example:**
```python
@dataclass
class RoleStyle:
    """Flat role-based style configuration (new architecture)."""
    
    role: NodeRole
    
    # === Shape ===
    shape_type: str = "basic"
    basic_shape: str = "rounded_rect"
    border_radius: int = 8
    
    # === Background (flat) ===
    bg_enabled: bool = True
    bg_color_index: int = 0  # Index into branch_colors
    bg_brightness: float = 1.0  # 0.5-1.5
    bg_opacity: int = 255  # 0-255
    
    # === Border (flat) ===
    border_enabled: bool = True
    border_width: int = 0
    border_color_index: int = 0  # Index into branch_colors
    border_brightness: float = 1.0
    border_opacity: int = 255
    border_style: str = "solid"
    
    # === Connector (flat) ===
    connector_shape: str = "bezier"
    connector_color_index: int = 0  # Index into branch_colors
    connector_brightness: float = 1.0
    connector_opacity: int = 255
    line_width: float = 2.0
    
    # === Text ===
    text_color: str | None = None  # Auto-calculated if None
    font_size: int = 14
    font_weight: str = "Normal"
    font_italic: bool = False
    font_family: str = "Arial"
    font_underline: bool = False
    font_strikeout: bool = False
    
    # === Shadow ===
    shadow_enabled: bool = False
    shadow_offset_x: int = 2
    shadow_offset_y: int = 2
    shadow_blur: int = 4
    shadow_color: str | None = None  # Default: none (black semi-transparent if enabled)
    
    # === Spacing ===
    parent_child_spacing: float = 80.0
    sibling_spacing: float = 60.0
    
    # === Padding ===
    padding_w: int = 12
    padding_h: int = 8
    max_text_width: int = 250
```

#### Task 1.2: Update `MindMapStyle` Structure

**File**: `cogist/domain/styles/style_config.py`

**Changes:**
```python
@dataclass
class MindMapStyle:
    """Complete mind map style configuration (new architecture)."""
    
    name: str = "Default"
    
    # === Global settings ===
    use_rainbow_branches: bool = False
    branch_colors: list[str] = field(default_factory=lambda: [
        "#FFFF6B6B", "#FF4ECDC4", "#FF45B7D1", "#FFFFA07A",
        "#FF98D8C8", "#FFF7DC6F", "#FFBB8FCE", "#FF85C1E2",
        "#FFFFFFFF",  # [8] Canvas Background
    ])
    
    # === Role configurations (flat structure) ===
    role_styles: dict[NodeRole, RoleStyle] = field(default_factory=dict)
```

**Remove:**
- ❌ `canvas_bg_color` field (now `branch_colors[8]`)
- ❌ `resolved_template` field (no longer needed)
- ❌ `resolved_color_scheme` field (no longer needed)

#### Task 1.3: Update `ColorScheme` Structure

**File**: `cogist/domain/styles/extended_styles.py`

**Changes:**
```python
@dataclass
class ColorScheme:
    """Color scheme (pure color pool only)."""
    
    name: str
    description: str
    
    # Branch color pool (10 colors)
    branch_colors: list[str] = field(default_factory=lambda: [
        "#FFFF6B6B",  # [0] Red
        "#FF4ECDC4",  # [1] Teal
        "#FF45B7D1",  # [2] Light Blue
        "#FFFFA07A",  # [3] Light Salmon
        "#FF98D8C8",  # [4] Mint
        "#FFF7DC6F",  # [5] Yellow
        "#FFBB8FCE",  # [6] Purple
        "#FF85C1E2",  # [7] Sky Blue
        "#FFFFFFFF",  # [8] Canvas Background (White)
    ])
    
    # Optional defaults
    default_use_rainbow_branches: bool | None = None
```

**Remove:**
- ❌ `role_configs` field
- ❌ `canvas_bg_color` field (now index 8 in branch_colors)
- ❌ `edge_color` field (use `branch_colors[0]` by default)
- ❌ `use_rainbow_branches` field (moved to MindMapStyle)

---

### Phase 2: Update Serialization Logic (Priority: HIGH)

#### Task 2.1: Rewrite `serialize_style()` and `deserialize_style()`

**File**: `cogist/domain/styles/style_resolver.py`

**New Serialization:**
```python
def serialize_style(style: MindMapStyle) -> dict:
    """Serialize complete MindMapStyle to JSON."""
    return {
        "name": style.name,
        "use_rainbow_branches": style.use_rainbow_branches,
        "branch_colors": style.branch_colors,
        "role_styles": {
            role.value: _serialize_role_style(role_style)
            for role, role_style in style.role_styles.items()
        },
    }

def deserialize_style(data: dict) -> MindMapStyle:
    """Deserialize MindMapStyle from JSON."""
    style = MindMapStyle(
        name=data.get("name", "Default"),
        use_rainbow_branches=data.get("use_rainbow_branches", False),
        branch_colors=data.get("branch_colors", DEFAULT_BRANCH_COLORS),
    )
    
    # Deserialize role styles
    if "role_styles" in data:
        for role_str, role_data in data["role_styles"].items():
            role = NodeRole(role_str)
            style.role_styles[role] = _deserialize_role_style(role_data)
    
    return style
```

**Helper Functions:**
```python
def _serialize_role_style(role_style: RoleStyle) -> dict:
    """Serialize a single RoleStyle to dict."""
    return {
        "role": role_style.role.value,
        "shape_type": role_style.shape_type,
        "basic_shape": role_style.basic_shape,
        "border_radius": role_style.border_radius,
        "bg_enabled": role_style.bg_enabled,
        "bg_color_index": role_style.bg_color_index,
        "bg_brightness": role_style.bg_brightness,
        "bg_opacity": role_style.bg_opacity,
        # ... all other fields
    }

def _deserialize_role_style(data: dict) -> RoleStyle:
    """Deserialize RoleStyle from dict."""
    return RoleStyle(
        role=NodeRole(data["role"]),
        shape_type=data.get("shape_type", "basic"),
        basic_shape=data.get("basic_shape", "rounded_rect"),
        border_radius=data.get("border_radius", 8),
        bg_enabled=data.get("bg_enabled", True),
        bg_color_index=data.get("bg_color_index", 0),
        bg_brightness=data.get("bg_brightness", 1.0),
        bg_opacity=data.get("bg_opacity", 255),
        # ... all other fields
    )
```

#### Task 2.2: Update CGS Serializer

**File**: `cogist/infrastructure/io/cgs_serializer.py`

**Changes:**

1. **Update `_write_style_config()`**:
```python
@classmethod
def _write_style_config(cls, zf: zipfile.ZipFile, style_config: MindMapStyle) -> None:
    """Write complete MindMapStyle to single file."""
    from cogist.domain.styles import serialize_style
    
    style_data = serialize_style(style_config)
    zf.writestr(
        'style/mindmap_style.json',
        json.dumps(style_data, indent=2, ensure_ascii=False)
    )
```

2. **Update `_read_style_config()`**:
```python
@classmethod
def _read_style_config(cls, zf: zipfile.ZipFile) -> MindMapStyle | None:
    """Read complete MindMapStyle from single file."""
    from cogist.domain.styles import deserialize_style
    
    if 'style/mindmap_style.json' not in zf.namelist():
        return None
    
    style_data = json.loads(zf.read('style/mindmap_style.json'))
    return deserialize_style(style_data)
```

3. **Remove Old Code**:
- ❌ Delete references to `style/config.json`
- ❌ Delete references to `style/template.json`
- ❌ Delete references to `style/color_scheme.json`
- ❌ Remove sync logic for `canvas_bg_color` and `use_rainbow_branches`

#### Task 2.3: Update Template Deserializer

**File**: `cogist/infrastructure/utils/resources/template_deserializer.py`

**Changes:**
```python
def deserialize_complete_template(data: dict[str, Any]) -> MindMapStyle:
    """Deserialize template from single JSON structure."""
    from cogist.domain.styles import deserialize_style
    
    # The entire data is now a MindMapStyle
    return deserialize_style(data)
```

---

### Phase 3: Update Rendering Code (Priority: HIGH)

#### Task 3.1: Update Canvas Background Rendering

**File**: `cogist/presentation/views/mindmap_view.py`

**Find and Replace:**
```python
# OLD (lines ~383, ~393):
canvas_color = self.style_config.canvas_bg_color or "#FFFFFF"

# NEW:
if self.style_config.branch_colors and len(self.style_config.branch_colors) > 8:
    canvas_color = self.style_config.branch_colors[8]
else:
    canvas_color = "#FFFFFFFF"  # Default white
```

#### Task 3.2: Update Node Item Rendering

**File**: `cogist/presentation/items/node_item.py`

**Key Changes:**

1. **Get Background Color**:
```python
# OLD:
bg_color = role_config.background.color  # From nested object

# NEW:
color_index = role_style.bg_color_index
base_color = self.mindmap_style.branch_colors[color_index]
adjusted_color = adjust_brightness(base_color, role_style.bg_brightness)
bg_color = apply_opacity(adjusted_color, role_style.bg_opacity)
```

2. **Get Border Color**:
```python
# OLD:
border_color = role_config.border.color

# NEW:
color_index = role_style.border_color_index
base_color = self.mindmap_style.branch_colors[color_index]
adjusted_color = adjust_brightness(base_color, role_style.border_brightness)
border_color = apply_opacity(adjusted_color, role_style.border_opacity)
```

3. **Get Connector Color**:
```python
# OLD:
connector_color = role_config.connector_color

# NEW:
color_index = role_style.connector_color_index
base_color = self.mindmap_style.branch_colors[color_index]
adjusted_color = adjust_brightness(base_color, role_style.connector_brightness)
connector_color = apply_opacity(adjusted_color, role_style.connector_opacity)
```

4. **Text Color Auto-Calculation** (already implemented):
```python
# Already exists in node_item.py line 261:
text_color = role_config.text_color if role_config.text_color else self._auto_contrast(bg_color)
```

**Keep this logic unchanged!** It already implements auto-contrast correctly.

#### Task 3.3: Add Helper Functions for Color Adjustment

**File**: `cogist/presentation/items/node_item.py` (or create new utility module)

```python
def adjust_brightness(hex_color: str, brightness: float) -> str:
    """Adjust color brightness.
    
    Args:
        hex_color: Color in #AARRGGBB format
        brightness: Brightness factor (0.5-1.5, where 1.0 = no change)
    
    Returns:
        Adjusted color in #AARRGGBB format
    """
    # Parse color
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 8:
        alpha = hex_color[:2]
        rgb = hex_color[2:]
    else:
        alpha = "FF"
        rgb = hex_color
    
    r = int(rgb[0:2], 16)
    g = int(rgb[2:4], 16)
    b = int(rgb[4:6], 16)
    
    # Apply brightness
    r = min(255, int(r * brightness))
    g = min(255, int(g * brightness))
    b = min(255, int(b * brightness))
    
    return f"#{alpha}{r:02X}{g:02X}{b:02X}"


def apply_opacity(hex_color: str, opacity: int) -> str:
    """Apply opacity to color.
    
    Args:
        hex_color: Color in #RRGGBB or #AARRGGBB format
        opacity: Opacity value (0-255)
    
    Returns:
        Color with opacity in #AARRGGBB format
    """
    hex_color = hex_color.lstrip("#")
    
    if len(hex_color) == 6:
        rgb = hex_color
    elif len(hex_color) == 8:
        rgb = hex_color[2:]
    else:
        return hex_color
    
    return f"#{opacity:02X}{rgb}"
```

---

### Phase 4: Update UI Panels (Priority: MEDIUM)

#### Task 4.1: Update Color Scheme Section

**File**: `cogist/presentation/dialogs/style_widgets/color_scheme_section.py`

**Key Changes:**

1. **Canvas Background Picker**:
   - Keep existing UI control
   - Map selected color to `branch_colors[8]` instead of `canvas_bg_color`
   
```python
# OLD (line ~559):
self.style_config.canvas_bg_color = colors["canvas_bg"]

# NEW:
if len(self.style_config.branch_colors) >= 9:
    self.style_config.branch_colors[8] = colors["canvas_bg"]
```

2. **Border/Background/Connector Color Pickers**:
   - Change from direct color selection to **color pool index selection**
   - Add dropdown/combo box to select from `branch_colors[0-7]`
   - Keep brightness and opacity sliders (already exist)

**UI Layout Changes:**
```
Background Color:
  [Dropdown: Color 1 ▼] [Brightness: ━━━━━━●━━] [Opacity: ━━━━━━━━●]

Border Color:
  [Dropdown: Color 1 ▼] [Brightness: ━━━━━━●━━] [Opacity: ━━━━━━━━●]

Connector Color:
  [Dropdown: Color 1 ▼] [Brightness: ━━━━━━●━━] [Opacity: ━━━━━━━━●]

Text Color:
  [Auto (Recommended)] [Custom: #FFFFFF]  ← Keep both options
  
Shadow Color:
  [None] [Custom: #80000000]  ← Keep existing
```

3. **Rainbow Mode Controls**:
   - Keep rainbow color pool editor (8 buttons for indices 0-7)
   - When rainbow mode is ON, ignore per-role color selections
   - When rainbow mode is OFF, use per-role color index selections

#### Task 4.2: Update Border Section

**File**: `cogist/presentation/dialogs/style_widgets/border_section.py`

**Changes:**
- Remove direct color picker
- Add color index dropdown (selecting from `branch_colors[0-7]`)
- Keep width, style, radius controls

#### Task 4.3: Update Connector Section

**File**: `cogist/presentation/dialogs/style_widgets/connector_section.py`

**Changes:**
- Remove direct color picker
- Add color index dropdown (selecting from `branch_colors[0-7]`)
- Keep shape, width, style controls

#### Task 4.4: Update Shadow Section

**File**: `cogist/presentation/dialogs/style_widgets/shadow_section.py`

**Changes:**
- Keep shadow color picker (shadow color is NOT from color pool)
- Keep offset X/Y, blur controls
- Default shadow color when enabled: `#80000000` (50% black)

---

### Phase 5: Update Template Creation (Priority: MEDIUM)

#### Task 5.1: Update `create_default_template()`

**File**: `cogist/domain/styles/templates.py`

**Changes:**
```python
def create_default_template() -> MindMapStyle:
    """Create default MindMapStyle with flat RoleStyle structure."""
    
    style = MindMapStyle(
        name="Default",
        use_rainbow_branches=False,
        branch_colors=[
            "#FFFF6B6B", "#FF4ECDC4", "#FF45B7D1", "#FFFFA07A",
            "#FF98D8C8", "#FFF7DC6F", "#FFBB8FCE", "#FF85C1E2",
            "#FFFFFFFF",  # [8] Canvas Background
        ],
    )
    
    # Create role styles with flat structure
    style.role_styles[NodeRole.ROOT] = RoleStyle(
        role=NodeRole.ROOT,
        shape_type="basic",
        basic_shape="rounded_rect",
        border_radius=12,
        bg_enabled=True,
        bg_color_index=0,  # Use branch_colors[0]
        bg_brightness=1.0,
        bg_opacity=255,
        border_enabled=True,
        border_width=3,
        border_color_index=0,
        border_brightness=1.0,
        border_opacity=255,
        border_style="solid",
        connector_shape="bezier",
        connector_color_index=0,
        connector_brightness=1.0,
        connector_opacity=255,
        line_width=2.0,
        text_color=None,  # Auto-calculated
        font_size=22,
        font_weight="Bold",
        font_family="Arial",
        shadow_enabled=False,
        shadow_offset_x=2,
        shadow_offset_y=2,
        shadow_blur=4,
        shadow_color=None,
        parent_child_spacing=80.0,
        sibling_spacing=60.0,
        padding_w=20,
        padding_h=16,
        max_text_width=300,
    )
    
    # Similar for PRIMARY, SECONDARY, TERTIARY...
    
    return style
```

---

### Phase 6: Cleanup and Testing (Priority: LOW)

#### Task 6.1: Delete Obsolete Files

- ❌ `cogist/domain/colors/color_theme.py`
- ❌ Old nested classes in `extended_styles.py` (after migration period)

#### Task 6.2: Update Asset Files

**Files:**
- `assets/color_schemes/default.json`
- `assets/color_schemes/vibrant.json`
- `assets/color_schemes/pastel.json`

**Changes:**
- Update to new 9-color format
- Remove obsolete fields

**Example:**
```json
{
  "name": "default",
  "description": "Default balanced color scheme",
  "branch_colors": [
    "#FFFF6B6B",
    "#FF4ECDC4",
    "#FF45B7D1",
    "#FFFFA07A",
    "#FF98D8C8",
    "#FFF7DC6F",
    "#FFBB8FCE",
    "#FF85C1E2",
    "#FFFFFFFF"
  ]
}
```

#### Task 6.3: Run Tests

```bash
# Type checking
uv run pyright

# Linting
uv run ruff check .

# Unit tests
uv run pytest tests/unit/test_cgs_serializer.py -v
uv run pytest tests/unit/test_serialization_improvements.py -v

# Manual testing
uv run python main.py
```

**Test Scenarios:**
1. ✅ Create new mind map
2. ✅ Save and load `.cgs` file
3. ✅ Switch rainbow mode ON/OFF
4. ✅ Change individual role colors
5. ✅ Adjust brightness and opacity
6. ✅ Verify canvas background updates
7. ✅ Verify text auto-contrast works
8. ✅ Export and import templates

---

## 📝 Migration Checklist

### Before Starting

- [ ] Backup current code (create feature branch)
- [ ] Review all 4 authoritative documents one more time
- [ ] Confirm no users need backward compatibility

### During Implementation

- [ ] Complete Phase 1 (Data Structures)
- [ ] Complete Phase 2 (Serialization)
- [ ] Complete Phase 3 (Rendering)
- [ ] Complete Phase 4 (UI Panels)
- [ ] Complete Phase 5 (Templates)
- [ ] Complete Phase 6 (Cleanup & Testing)

### After Completion

- [ ] All unit tests pass
- [ ] Manual testing completed
- [ ] Code review performed
- [ ] Documentation updated
- [ ] Commit with clear message
- [ ] Merge to main branch

---

## ⚠️ Risk Assessment

### High Risk Areas

1. **Serialization Compatibility**
   - **Risk**: Old `.cgs` files won't load
   - **Mitigation**: Acceptable since no users yet
   - **Action**: Document breaking change in CHANGELOG

2. **UI Panel Complexity**
   - **Risk**: Color index dropdowns may confuse users
   - **Mitigation**: Show color swatches in dropdown, not just numbers
   - **Action**: Test UX thoroughly

3. **Rendering Performance**
   - **Risk**: Color adjustment calculations on every render
   - **Mitigation**: Cache adjusted colors, only recalculate on change
   - **Action**: Profile performance after implementation

### Low Risk Areas

- Data structure changes (isolated impact)
- Template creation (only affects new files)
- Asset file updates (simple JSON edits)

---

## 🎨 UI/UX Considerations

### Color Selection Workflow

**For Rainbow Mode:**
1. User enables "Branch-based" toggle
2. Edit 8 colors in the color pool (2x4 grid)
3. Nodes automatically cycle through colors

**For Single Color Mode:**
1. User disables "Branch-based" toggle
2. For each role (Root, Level 1, etc.):
   - Select base color from dropdown (shows color swatches)
   - Adjust brightness slider (0.5x - 1.5x)
   - Adjust opacity slider (0 - 255)
3. Canvas background: Direct color picker (maps to index 8)

### Visual Feedback

- Show live preview of color adjustments
- Display final computed color next to sliders
- Indicate when text color is auto-calculated vs manual

---

## 📚 Documentation Updates Needed

After refactoring, update these docs:

1. **VERSION_v0.9.0.md** - Document breaking changes
2. **CHANGELOG.md** - List all changes
3. **README.md** - Update architecture diagram if needed
4. **docs/zh-CN/** - Ensure consistency with new design

---

## 🔄 Rollback Plan

If critical issues are found:

1. **Immediate Action**: Revert to previous commit
2. **Analysis**: Identify root cause
3. **Fix**: Address issue in isolated branch
4. **Retry**: Re-attempt refactoring with fixes

**Git Commands:**
```bash
git stash
git checkout main
git branch -D refactor-style-system
git checkout -b refactor-style-system-v2
```

---

## ✅ Success Criteria

The refactoring is successful when:

1. ✅ All data structures match authoritative documents
2. ✅ CGS files use single `style/mindmap_style.json` format
3. ✅ Canvas background uses `branch_colors[8]`
4. ✅ Non-rainbow mode defaults to `branch_colors[0]` for borders/background/connectors
5. ✅ Text color auto-calculation works correctly
6. ✅ UI panels allow selecting color index + brightness + opacity
7. ✅ All tests pass
8. ✅ No regression in functionality
9. ✅ Code is cleaner and more maintainable

---

## 📅 Timeline Estimate

| Phase | Estimated Time | Dependencies |
|-------|---------------|--------------|
| Phase 1: Data Structures | 2 hours | None |
| Phase 2: Serialization | 3 hours | Phase 1 |
| Phase 3: Rendering | 4 hours | Phase 1, 2 |
| Phase 4: UI Panels | 6 hours | Phase 1, 2, 3 |
| Phase 5: Templates | 2 hours | Phase 1, 2 |
| Phase 6: Cleanup & Testing | 3 hours | All phases |
| **Total** | **~20 hours** | |

**Note**: This is a conservative estimate. Actual time may vary based on complexity discovered during implementation.

---

## 🚀 Next Steps

1. **Review this plan** with stakeholders
2. **Create feature branch**: `git checkout -b refactor-style-system`
3. **Start with Phase 1**: Update core data structures
4. **Commit frequently**: Small, atomic commits for easy rollback
5. **Test continuously**: Run tests after each phase

---

**Remember**: 
- No backward compatibility needed!
- Follow authoritative documents strictly!
- Keep commits atomic and well-documented!
- Test thoroughly before merging!
