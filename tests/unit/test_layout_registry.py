"""Tests for LayoutRegistry"""

import pytest

from cogist.domain.layout import (
    DEFAULT_LAYOUT_CONFIG,
    DefaultLayout,
    LayoutRegistry,
)


class TestLayoutRegistry:
    """Test suite for LayoutRegistry"""

    def setup_method(self):
        """Create a fresh registry for each test"""
        self.registry = LayoutRegistry()

    def test_register_layout(self):
        """Test registering a layout algorithm"""
        self.registry.register("default", DefaultLayout)

        assert self.registry.has_layout("default")
        assert "default" in self.registry.get_available_layouts()

    def test_register_duplicate_raises_error(self):
        """Test that registering duplicate layout raises ValueError"""
        self.registry.register("default", DefaultLayout)

        with pytest.raises(ValueError, match="already registered"):
            self.registry.register("default", DefaultLayout)

    def test_get_layout_creates_instance(self):
        """Test that get_layout creates a new instance"""
        self.registry.register("default", DefaultLayout)

        layout = self.registry.get_layout("default", DEFAULT_LAYOUT_CONFIG)

        assert isinstance(layout, DefaultLayout)
        assert layout.config == DEFAULT_LAYOUT_CONFIG

    def test_get_layout_with_none_config(self):
        """Test that get_layout uses default config when None provided"""
        self.registry.register("default", DefaultLayout)

        layout = self.registry.get_layout("default", None)

        assert isinstance(layout, DefaultLayout)
        assert layout.config is not None

    def test_get_unknown_layout_raises_error(self):
        """Test that getting unknown layout raises ValueError"""
        with pytest.raises(ValueError, match="Unknown layout"):
            self.registry.get_layout("nonexistent")

    def test_get_available_layouts(self):
        """Test getting list of available layouts"""
        self.registry.register("default", DefaultLayout)

        layouts = self.registry.get_available_layouts()

        assert isinstance(layouts, list)
        assert "default" in layouts
        assert len(layouts) == 1

    def test_unregister_layout(self):
        """Test unregistering a layout"""
        self.registry.register("default", DefaultLayout)
        assert self.registry.has_layout("default")

        self.registry.unregister("default")

        assert not self.registry.has_layout("default")
        assert len(self.registry.get_available_layouts()) == 0

    def test_unregister_unknown_raises_error(self):
        """Test that unregistering unknown layout raises KeyError"""
        with pytest.raises(KeyError, match="not registered"):
            self.registry.unregister("nonexistent")

    def test_clear_registry(self):
        """Test clearing all layouts from registry"""
        self.registry.register("default", DefaultLayout)

        self.registry.clear()

        assert len(self.registry.get_available_layouts()) == 0

    def test_multiple_registrations(self):
        """Test registering multiple layouts"""
        self.registry.register("default", DefaultLayout)
        # In future, add more layouts here

        layouts = self.registry.get_available_layouts()
        assert len(layouts) >= 1
        assert "default" in layouts
