"""
JSON Serializer - Infrastructure Layer

Handles serialization and deserialization of mind maps to/from JSON format.
"""

import json
from typing import Any


class JSONSerializer:
    """
    Serializer for converting mind map data to and from JSON format.

    This class handles the conversion of node trees to JSON-serializable
    dictionaries and vice versa.
    """

    VERSION = "1.0"
    FORMAT_VERSION = 1

    @classmethod
    def serialize(cls, root_node: dict[str, Any], style_config: Any = None) -> str:
        """
        Serialize a mind map to JSON string.

        Args:
            root_node: Root node dictionary with full tree structure
            style_config: Optional MindMapStyle configuration

        Returns:
            JSON string representation of the mind map

        Example:
            mind_map_data = {
                "root": {...},
                "metadata": {...}
            }
            json_string = JSONSerializer.serialize(mind_map_data, style_config)
        """
        data = {
            "version": cls.VERSION,
            "format_version": cls.FORMAT_VERSION,
            "mind_map": root_node,
        }

        # Add style configuration if provided
        if style_config is not None:
            from cogist.domain.styles import serialize_style
            data["style"] = serialize_style(style_config)

        return json.dumps(data, indent=2, ensure_ascii=False)

    @classmethod
    def deserialize(cls, json_string: str) -> dict[str, Any]:
        """
        Deserialize a JSON string to mind map data.

        Args:
            json_string: JSON string to parse

        Returns:
            Dictionary containing mind map data with optional style config

        Raises:
            ValueError: If JSON is invalid or version is unsupported
        """
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}") from e

        # Validate version
        version = data.get("version", "unknown")
        if version != cls.VERSION:
            raise ValueError(
                f"Unsupported format version: {version}. Expected version {cls.VERSION}"
            )

        # Validate structure
        if "mind_map" not in data:
            raise ValueError("Invalid mind map format: missing 'mind_map' field")

        result = {
            "root": data["mind_map"].get("root"),
        }

        # Extract style configuration if present
        if "style" in data:
            from cogist.domain.styles import deserialize_style
            result["style"] = deserialize_style(data["style"])

        return result

    @staticmethod
    def node_to_dict(node: Any) -> dict[str, Any]:
        """
        Convert a Node entity to a dictionary.

        Args:
            node: Node entity to convert

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        result = {
            "id": node.id,
            "text": node.text,
            "width": node.width,
            "height": node.height,
            "position": {"x": node.position[0], "y": node.position[1]},
            "color": node.color,
            "is_root": node.is_root,
            "depth": node.depth,  # Save depth for proper style resolution
            "rainbow_branch_index": node.rainbow_branch_index,  # Fixed color index for rainbow mode
            "children": [JSONSerializer.node_to_dict(child) for child in node.children],
        }

        return result

    @staticmethod
    def dict_to_node(data: dict[str, Any], parent: Any = None) -> Any:
        """
        Convert a dictionary to a Node entity.

        Args:
            data: Dictionary containing node data
            parent: Parent node reference (optional)

        Returns:
            Node entity instance
        """
        from cogist.domain.entities.node import Node

        # Create node
        node = Node(
            id=data["id"],
            text=data["text"],
            width=data.get("width", 0.0),  # Must be calculated based on text
            height=data.get("height", 0.0),  # Must be calculated based on text
            position=(
                data.get("position", {}).get("x", 0.0),
                data.get("position", {}).get("y", 0.0),
            ),
            color=data.get("color", "#FF2196F3"),
            is_root=data.get("is_root", False),
            depth=data.get("depth", 0),  # Restore depth from saved data
            rainbow_branch_index=data.get("rainbow_branch_index"),  # Restore rainbow branch index
        )

        # Set parent reference
        if parent is not None:
            node.parent = parent

        # Recursively process children
        if "children" in data:
            for child_data in data["children"]:
                child_node = JSONSerializer.dict_to_node(child_data, parent=node)
                node.add_child(child_node)

        return node
