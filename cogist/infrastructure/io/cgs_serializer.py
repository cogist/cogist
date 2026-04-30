"""CGS File Serializer - Handles .cgs file format (ZIP container).

This module implements the Cogist Save (.cgs) file format using ZIP containers.
Supports structured data, binary resources, and future extensibility.
"""

import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cogist.domain.styles import MindMapStyle, serialize_style


class CGSSerializer:
    """Serializer for .cgs file format (ZIP container).

    The .cgs format structure:
    mindmap.cgs (ZIP)
    ├── manifest.json          # File manifest and metadata
    ├── data/
    │   ├── nodes.json         # Node tree structure
    │   └── positions.json     # Node positions (optional)
    ├── style/
    │   └── mindmap_style.json # Complete MindMapStyle (self-contained)
    └── assets/                # Resource files (optional)
        ├── images/
        ├── vectors/
        └── fonts/
    """

    FORMAT_VERSION = 1
    APPLICATION = "Cogist v0.3.0"

    @classmethod
    def serialize(cls, root_node_data: dict[str, Any],
                  style_config: MindMapStyle | None = None,
                  assets: dict[str, bytes] | None = None,
                  viewport_state: dict[str, float] | None = None) -> bytes:
        """Serialize mind map to .cgs format (ZIP bytes).

        Node order is preserved by the order of children list in the serialized data.

        Args:
            root_node_data: Serialized node tree dictionary
            style_config: Optional MindMapStyle configuration
            assets: Optional dictionary of asset files {path: content}
            viewport_state: Optional viewport state {center_x, center_y, zoom_level}

        Returns:
            ZIP file content as bytes
        """
        import io

        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 1. Write node data
            zf.writestr('data/nodes.json', json.dumps(root_node_data, indent=2, ensure_ascii=False))

            # 2. Write style configuration
            if style_config:
                cls._write_style_config(zf, style_config)

            # 3. Write assets
            if assets:
                for asset_path, content in assets.items():
                    zf.writestr(f'assets/{asset_path}', content)

            # 4. Generate and write manifest
            manifest = cls._create_manifest(root_node_data, style_config, assets, viewport_state)
            zf.writestr('manifest.json', json.dumps(manifest, indent=2, ensure_ascii=False))

        return buffer.getvalue()

    @classmethod
    def deserialize(cls, cgs_bytes: bytes) -> dict[str, Any]:
        """Deserialize .cgs format to mind map data.

        Args:
            cgs_bytes: ZIP file content as bytes

        Returns:
            Dictionary containing:
            - nodes: Node tree data
            - style: MindMapStyle (if present)
            - assets: Dictionary of asset files {path: content}
            - manifest: File manifest

        Raises:
            ValueError: If format is invalid or unsupported
        """
        import io

        buffer = io.BytesIO(cgs_bytes)

        try:
            with zipfile.ZipFile(buffer, 'r') as zf:
                # 1. Read and validate manifest
                manifest_data = json.loads(zf.read('manifest.json'))
                cls._validate_manifest(manifest_data)

                # 2. Read node data
                nodes_data = json.loads(zf.read('data/nodes.json'))

                # 3. Read style configuration (if present)
                style_config = None
                if 'style/mindmap_style.json' in zf.namelist():
                    style_config = cls._read_style_config(zf)

                # 4. Read assets
                assets = cls._read_assets(zf)

                # 5. Extract viewport state from manifest (if present)
                viewport_state = manifest_data.get('viewport')

                return {
                    'nodes': nodes_data,
                    'style': style_config,
                    'assets': assets,
                    'manifest': manifest_data,
                    'viewport': viewport_state,  # May be None
                }

        except KeyError as e:
            raise ValueError(f"Invalid .cgs file: missing required file {e}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in .cgs file: {e}") from e

    @classmethod
    def save_to_file(cls, file_path: str | Path,
                     root_node_data: dict[str, Any],
                     style_config: MindMapStyle | None = None,
                     assets: dict[str, bytes] | None = None,
                     viewport_state: dict[str, float] | None = None) -> Path:
        """Serialize and save mind map to .cgs file.

        Args:
            file_path: Path to save the file
            root_node_data: Serialized node tree dictionary
            style_config: Optional MindMapStyle configuration
            assets: Optional dictionary of asset files
            viewport_state: Optional viewport state {center_x, center_y, zoom_level}

        Returns:
            Path to the saved file
        """
        path = Path(file_path)

        # Ensure correct extension
        if path.suffix != '.cgs':
            path = path.with_suffix('.cgs')

        # Serialize
        cgs_bytes = cls.serialize(root_node_data, style_config, assets, viewport_state)

        # Write to file
        path.write_bytes(cgs_bytes)

        return path

    @classmethod
    def load_from_file(cls, file_path: str | Path) -> dict[str, Any]:
        """Load and deserialize mind map from .cgs file.

        Args:
            file_path: Path to the .cgs file

        Returns:
            Dictionary containing nodes, style, assets, and manifest

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Read file
        cgs_bytes = path.read_bytes()

        # Deserialize
        return cls.deserialize(cgs_bytes)

    @classmethod
    def _write_style_config(cls, zf: zipfile.ZipFile, style_config: MindMapStyle) -> None:
        """Write complete MindMapStyle to single file (NEW FORMAT)."""
        style_data = serialize_style(style_config)
        zf.writestr(
            'style/mindmap_style.json',
            json.dumps(style_data, indent=2, ensure_ascii=False)
        )

    @classmethod
    def _read_style_config(cls, zf: zipfile.ZipFile) -> MindMapStyle | None:
        """Read complete MindMapStyle from single file (NEW FORMAT)."""
        from cogist.domain.styles import deserialize_style

        # Read the single self-contained style file
        style_data = json.loads(zf.read('style/mindmap_style.json'))
        return deserialize_style(style_data)

    @classmethod
    def _read_assets(cls, zf: zipfile.ZipFile) -> dict[str, bytes]:
        """Read all asset files from ZIP archive."""
        assets = {}

        for name in zf.namelist():
            if name.startswith('assets/'):
                assets[name] = zf.read(name)

        return assets

    @classmethod
    def _create_manifest(cls, root_node_data: dict[str, Any],
                         style_config: MindMapStyle | None,
                         assets: dict[str, bytes] | None,
                         viewport_state: dict[str, float] | None = None) -> dict[str, Any]:
        """Create manifest.json content."""
        now = datetime.now(UTC).isoformat()

        # Count nodes
        node_count = cls._count_nodes(root_node_data.get('root', {}))
        max_depth = cls._calculate_max_depth(root_node_data.get('root', {}))

        manifest = {
            'version': cls.APPLICATION,
            'format_version': cls.FORMAT_VERSION,
            'created_at': now,
            'modified_at': now,
            'application': cls.APPLICATION,

            'files': {
                'nodes': 'data/nodes.json',
            },

            'metadata': {
                'node_count': node_count,
                'max_depth': max_depth,
            },
        }

        # Add viewport state if present
        if viewport_state:
            manifest['viewport'] = viewport_state

        # Add style files if present
        if style_config:
            manifest['files']['style_config'] = 'style/config.json'
            if style_config.resolved_template:
                manifest['files']['template'] = 'style/template.json'
            if style_config.resolved_color_scheme:
                manifest['files']['color_scheme'] = 'style/color_scheme.json'

        # Add asset files if present
        if assets:
            manifest['files']['assets'] = list(assets.keys())

        return manifest

    @classmethod
    def _validate_manifest(cls, manifest: dict[str, Any]) -> None:
        """Validate manifest format version."""
        format_version = manifest.get('format_version', 0)

        if format_version > cls.FORMAT_VERSION:
            raise ValueError(
                f"File requires newer version (format {format_version}). "
                f"This version supports up to format {cls.FORMAT_VERSION}."
            )

        if format_version < 1:
            raise ValueError(f"Unsupported old format version: {format_version}")

    @classmethod
    def _count_nodes(cls, node_data: dict[str, Any]) -> int:
        """Count total number of nodes in tree."""
        if not node_data:
            return 0

        count = 1  # Current node
        children = node_data.get('children', [])

        for child in children:
            count += cls._count_nodes(child)

        return count

    @classmethod
    def _calculate_max_depth(cls, node_data: dict[str, Any], current_depth: int = 0) -> int:
        """Calculate maximum depth of node tree."""
        if not node_data:
            return current_depth

        children = node_data.get('children', [])

        if not children:
            return current_depth

        max_child_depth = current_depth
        for child in children:
            child_depth = cls._calculate_max_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth
