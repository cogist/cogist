"""Tests for NodeTemplate"""

import pytest
from cogist.domain.templates import (
    NodeTemplate,
    NodeShape,
    PriorityRule,
    NODE_TEMPLATES,
    MODERN_TEMPLATE,
)


class TestNodeShape:
    """Test suite for NodeShape enum"""
    
    def test_shape_values(self):
        """Test that all shape values are correct"""
        assert NodeShape.ROUNDED_RECT.value == "rounded_rect"
        assert NodeShape.CIRCLE.value == "circle"
        assert NodeShape.RECTANGLE.value == "rectangle"
        assert NodeShape.NONE.value == "none"


class TestPriorityRule:
    """Test suite for PriorityRule"""
    
    def test_default_values(self):
        """Test default priority rule values"""
        rule = PriorityRule()
        
        assert rule.border_width_override is None
        assert rule.border_width_delta == 0
        assert rule.font_weight_override is None
        assert rule.font_size_delta == 0
        assert rule.icon is None
        assert rule.badge is None
        assert rule.brightness_delta == 0.0
    
    def test_custom_values(self):
        """Test custom priority rule values"""
        rule = PriorityRule(
            border_width_override=4,
            font_weight_override="bold",
            icon="⚠️",
            badge="P1",
        )
        
        assert rule.border_width_override == 4
        assert rule.font_weight_override == "bold"
        assert rule.icon == "⚠️"
        assert rule.badge == "P1"


class TestNodeTemplate:
    """Test suite for NodeTemplate"""
    
    def test_create_template(self):
        """Test creating a node template"""
        template = NodeTemplate(
            name="test",
            shape=NodeShape.ROUNDED_RECT,
            corner_radius=10,
            border_width=3,
            padding=15,
        )
        
        assert template.name == "test"
        assert template.shape == NodeShape.ROUNDED_RECT
        assert template.corner_radius == 10
        assert template.border_width == 3
        assert template.padding == 15
    
    def test_default_values(self):
        """Test default template values"""
        template = NodeTemplate(name="default")
        
        assert template.shape == NodeShape.ROUNDED_RECT
        assert template.corner_radius == 8
        assert template.border_width == 2
        assert template.padding == 12
        assert template.min_width == 60
        assert template.min_height == 30
        assert template.recommended_layouts == []
        assert template.priority_rules == {}
    
    def test_get_priority_rule_exists(self):
        """Test getting existing priority rule"""
        rule = PriorityRule(border_width_delta=2)
        template = NodeTemplate(
            name="test",
            priority_rules={"critical": rule}
        )
        
        result = template.get_priority_rule("critical")
        
        assert result is not None
        assert result.border_width_delta == 2
    
    def test_get_priority_rule_not_exists(self):
        """Test getting non-existent priority rule"""
        template = NodeTemplate(name="test")
        
        result = template.get_priority_rule("critical")
        
        assert result is None


class TestPresetTemplates:
    """Test suite for preset templates"""
    
    def test_templates_registry(self):
        """Test that all preset templates are registered"""
        assert len(NODE_TEMPLATES) == 4
        assert "modern" in NODE_TEMPLATES
        assert "minimal" in NODE_TEMPLATES
        assert "colorful" in NODE_TEMPLATES
        assert "professional" in NODE_TEMPLATES
    
    def test_modern_template(self):
        """Test modern template properties"""
        assert MODERN_TEMPLATE.name == "modern"
        assert MODERN_TEMPLATE.shape == NodeShape.ROUNDED_RECT
        assert MODERN_TEMPLATE.corner_radius == 8
        assert MODERN_TEMPLATE.border_width == 2
        assert len(MODERN_TEMPLATE.recommended_layouts) > 0
    
    def test_modern_template_priority_rules(self):
        """Test modern template has priority rules"""
        critical_rule = MODERN_TEMPLATE.get_priority_rule("critical")
        
        assert critical_rule is not None
        assert critical_rule.border_width_delta == 2
        assert critical_rule.font_weight_override == "bold"
        assert critical_rule.icon == "⚠️"
    
    def test_minimal_template(self):
        """Test minimal template properties"""
        minimal = NODE_TEMPLATES["minimal"]
        
        assert minimal.name == "minimal"
        assert minimal.border_width == 1
        assert minimal.corner_radius == 4
    
    def test_colorful_template(self):
        """Test colorful template properties"""
        colorful = NODE_TEMPLATES["colorful"]
        
        assert colorful.name == "colorful"
        assert colorful.shape == NodeShape.CIRCLE
        assert colorful.border_width == 3
    
    def test_professional_template(self):
        """Test professional template properties"""
        professional = NODE_TEMPLATES["professional"]
        
        assert professional.name == "professional"
        assert professional.shape == NodeShape.RECTANGLE
        assert professional.min_width == 80
