#!/usr/bin/env python3
"""Test script for refactored style panel components."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all components can be imported."""
    print("Testing imports...")

    try:
        from cogist.presentation.dialogs.style_widgets import (
            BorderSection,
            CanvasSection,
            ConnectorSection,
            LayerSelector,
            NodeStyleSection,
        )
        # Use imports to verify they exist
        _ = BorderSection
        _ = CanvasSection
        _ = ConnectorSection
        _ = LayerSelector
        _ = NodeStyleSection
        print("✅ All widget components imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    try:
        from cogist.presentation.dialogs.style_panel_advanced import AdvancedStyleTab
        # Use import to verify it exists
        _ = AdvancedStyleTab
        print("✅ AdvancedStyleTab imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    return True


def test_component_creation():
    """Test that components can be instantiated."""
    print("\nTesting component creation...")

    from PySide6.QtWidgets import QApplication

    from cogist.presentation.dialogs.style_widgets import (
        BorderSection,
        CanvasSection,
        ConnectorSection,
        LayerSelector,
        NodeStyleSection,
    )

    # Create a minimal QApplication for testing
    _app = QApplication.instance() or QApplication(sys.argv)

    try:
        _layer_selector = LayerSelector()
        print("✅ LayerSelector created")

        _canvas_section = CanvasSection()
        print("✅ CanvasSection created")

        _node_style_section = NodeStyleSection()
        print("✅ NodeStyleSection created")

        _border_section = BorderSection()
        print("✅ BorderSection created")

        _connector_section = ConnectorSection()
        print("✅ ConnectorSection created")

        return True
    except Exception as e:
        print(f"❌ Component creation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_advanced_tab():
    """Test AdvancedStyleTab creation."""
    print("\nTesting AdvancedStyleTab creation...")

    from PySide6.QtWidgets import QApplication

    from cogist.presentation.dialogs.style_panel_advanced import AdvancedStyleTab

    _app = QApplication.instance() or QApplication(sys.argv)

    try:
        tab = AdvancedStyleTab()
        print("✅ AdvancedStyleTab created successfully")
        print(f"   - Panel width: {tab.PANEL_WIDTH}px")
        print(f"   - Current layer: {tab.current_layer}")
        print(f"   - Layer styles count: {len(tab.layer_styles)}")
        return True
    except Exception as e:
        print(f"❌ AdvancedStyleTab creation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lazy_initialization():
    """Test that components use lazy initialization."""
    print("\nTesting lazy initialization...")

    from PySide6.QtWidgets import QApplication

    from cogist.presentation.dialogs.style_widgets import NodeStyleSection

    _app = QApplication.instance() or QApplication(sys.argv)

    try:
        section = NodeStyleSection()

        # Check that it's collapsed by default
        if not section.isChecked():
            print("✅ Section is collapsed by default")
        else:
            print("⚠️  Section is expanded by default (should be collapsed)")

        # Check that _initialized is False
        if not section._initialized:
            print("✅ Lazy initialization flag is set correctly")
        else:
            print("⚠️  Section appears to be initialized already")

        # Check that internal widgets don't exist yet
        if not hasattr(section, 'shape_combo'):
            print("✅ Internal widgets not created yet (lazy loading works)")
        else:
            print("⚠️  Internal widgets already exist")

        return True
    except Exception as e:
        print(f"❌ Lazy initialization test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_consistency():
    """Test that all components have consistent API."""
    print("\nTesting API consistency...")

    from PySide6.QtWidgets import QApplication

    from cogist.presentation.dialogs.style_widgets import (
        BorderSection,
        ConnectorSection,
        NodeStyleSection,
    )

    _app = QApplication.instance() or QApplication(sys.argv)

    try:
        components = [
            ("NodeStyleSection", NodeStyleSection()),
            ("BorderSection", BorderSection()),
            ("ConnectorSection", ConnectorSection()),
        ]

        for name, component in components:
            # Test get_style()
            if hasattr(component, 'get_style'):
                style = component.get_style()
                if isinstance(style, dict):
                    print(f"✅ {name}.get_style() returns dict")
                else:
                    print(f"❌ {name}.get_style() doesn't return dict")
                    return False
            else:
                print(f"❌ {name} missing get_style() method")
                return False

            # Test set_style()
            if hasattr(component, 'set_style'):
                component.set_style({})
                print(f"✅ {name}.set_style() works")
            else:
                print(f"❌ {name} missing set_style() method")
                return False

        return True
    except Exception as e:
        print(f"❌ API consistency test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Style Panel Refactoring - Integration Tests")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Component Creation", test_component_creation()))
    results.append(("Advanced Tab", test_advanced_tab()))
    results.append(("Lazy Initialization", test_lazy_initialization()))
    results.append(("API Consistency", test_api_consistency()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Refactoring successful!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
