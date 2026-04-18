"""Tests for ColorTheme"""

import pytest
from cogist.domain.colors import (
    ColorTheme,
    COLOR_THEMES,
    BLUE_THEME,
    DARK_THEME,
)


class TestColorTheme:
    """Test suite for ColorTheme"""
    
    def test_create_theme(self):
        """Test creating a color theme"""
        theme = ColorTheme(
            name="test",
            canvas_bg="#FFFFFF",
            edge_color="#000000",
            text_color="#333333",
        )
        
        assert theme.name == "test"
        assert theme.canvas_bg == "#FFFFFF"
        assert theme.edge_color == "#000000"
        assert theme.text_color == "#333333"
    
    def test_default_values(self):
        """Test default theme values"""
        theme = ColorTheme(name="default")
        
        assert theme.canvas_bg == "#FFFFFF"
        assert theme.edge_color == "#666666"
        assert theme.text_color == "#333333"
        assert len(theme.node_colors) > 0
        assert len(theme.priority_colors) > 0
    
    def test_get_node_color_by_depth(self):
        """Test getting node color for specific depth"""
        theme = ColorTheme(
            name="test",
            node_colors={
                0: "#FF0000",
                1: "#00FF00",
                2: "#0000FF",
            }
        )
        
        assert theme.get_node_color(0) == "#FF0000"
        assert theme.get_node_color(1) == "#00FF00"
        assert theme.get_node_color(2) == "#0000FF"
    
    def test_get_node_color_cycle(self):
        """Test color cycling for deep levels"""
        theme = ColorTheme(
            name="test",
            node_colors={
                0: "#FF0000",
                1: "#00FF00",
            }
        )
        
        # Level 2 should cycle back to level 0
        color_2 = theme.get_node_color(2)
        color_0 = theme.get_node_color(0)
        
        assert color_2 == color_0
        
        # Level 3 should cycle to level 1
        color_3 = theme.get_node_color(3)
        color_1 = theme.get_node_color(1)
        
        assert color_3 == color_1
    
    def test_get_priority_color_override(self):
        """Test priority color override"""
        theme = ColorTheme(
            name="test",
            priority_colors={
                "critical": "#FF0000",
                "low": "#999999",
            }
        )
        
        assert theme.get_priority_color("critical") == "#FF0000"
        assert theme.get_priority_color("low") == "#999999"
    
    def test_get_priority_color_none_uses_base(self):
        """Test that None priority color uses base color"""
        theme = ColorTheme(
            name="test",
            priority_colors={
                "normal": None,
            }
        )
        
        base_color = "#123456"
        result = theme.get_priority_color("normal", base_color)
        
        assert result == base_color
    
    def test_get_priority_color_fallback(self):
        """Test fallback when no base color provided"""
        theme = ColorTheme(
            name="test",
            priority_colors={
                "normal": None,
            }
        )
        
        # Should fall back to root node color
        result = theme.get_priority_color("normal")
        expected = theme.get_node_color(0)
        
        assert result == expected


class TestPresetThemes:
    """Test suite for preset themes"""
    
    def test_themes_registry(self):
        """Test that all preset themes are registered"""
        assert len(COLOR_THEMES) == 4
        assert "blue" in COLOR_THEMES
        assert "dark" in COLOR_THEMES
        assert "warm" in COLOR_THEMES
        assert "cool" in COLOR_THEMES
    
    def test_blue_theme(self):
        """Test blue theme properties"""
        assert BLUE_THEME.name == "blue"
        assert BLUE_THEME.canvas_bg == "#FFFFFF"
        assert BLUE_THEME.get_node_color(0) == "#2196F3"
        assert BLUE_THEME.get_node_color(1) == "#4CAF50"
    
    def test_dark_theme(self):
        """Test dark theme properties"""
        assert DARK_THEME.name == "dark"
        assert DARK_THEME.canvas_bg == "#1E1E1E"
        assert DARK_THEME.text_color == "#E0E0E0"
    
    def test_warm_theme(self):
        """Test warm theme properties"""
        warm = COLOR_THEMES["warm"]
        
        assert warm.name == "warm"
        assert warm.canvas_bg == "#FFF8E1"
    
    def test_cool_theme(self):
        """Test cool theme properties"""
        cool = COLOR_THEMES["cool"]
        
        assert cool.name == "cool"
        assert cool.canvas_bg == "#E3F2FD"
    
    def test_theme_priority_colors(self):
        """Test that themes have priority colors defined"""
        for theme_name, theme in COLOR_THEMES.items():
            assert "critical" in theme.priority_colors
            assert "normal" in theme.priority_colors
            assert "low" in theme.priority_colors
    
    def test_theme_node_colors_by_depth(self):
        """Test that themes have node colors for multiple depths"""
        for theme_name, theme in COLOR_THEMES.items():
            # Should have at least root color
            assert 0 in theme.node_colors
            
            # Test color retrieval for various depths
            for depth in range(6):
                color = theme.get_node_color(depth)
                assert color is not None
                assert color.startswith("#")
    
    def test_blue_theme_critical_color(self):
        """Test blue theme critical priority color"""
        critical_color = BLUE_THEME.get_priority_color("critical")
        
        assert critical_color == "#D32F2F"
        assert critical_color != BLUE_THEME.get_node_color(0)
    
    def test_theme_edge_and_text_colors(self):
        """Test that themes have edge and text colors"""
        for theme_name, theme in COLOR_THEMES.items():
            assert theme.edge_color.startswith("#")
            assert theme.text_color.startswith("#")
