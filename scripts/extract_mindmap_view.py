#!/usr/bin/env python3
"""Extract MindMapView class from main.py to independent file."""

import re
from pathlib import Path


def extract_mindmap_view():
    """Extract MindMapView class from main.py."""

    # Read main.py
    main_py = Path("main.py")
    content = main_py.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    # Find MindMapView class definition
    mindmap_start = None
    for i, line in enumerate(lines):
        if re.match(r'^class MindMapView\(QGraphicsView\):', line):
            mindmap_start = i
            break

    if mindmap_start is None:
        print("❌ MindMapView class not found!")
        return False

    print(f"✅ Found MindMapView at line {mindmap_start + 1}")

    # Extract from MindMapView to end of file
    mindmap_lines = lines[mindmap_start:]

    # Create the new file with proper header
    header = '''"""MindMap View - QGraphicsView for mind map visualization.

This module contains the MindMapView class which handles:
- UI rendering of nodes and edges
- User interaction (mouse, keyboard events)
- Layout algorithm invocation
- Node selection and focus management
"""

'''

    # Write to new file
    output_path = Path("cogist/presentation/views/mindmap_view.py")
    output_path.write_text(header + ''.join(mindmap_lines), encoding="utf-8")

    print(f"✅ Created {output_path}")
    print(f"   Lines: {len(mindmap_lines)}")

    # Now remove MindMapView from main.py
    # Keep everything before MindMapView class
    main_content_before = ''.join(lines[:mindmap_start])

    # Add import statement for MindMapView
    import_statement = "\nfrom cogist.presentation.views.mindmap_view import MindMapView\n"

    # Find where to add the import (after other imports)
    main_lines = main_content_before.splitlines(keepends=True)

    # Find the last import line
    last_import_idx = 0
    for i, line in enumerate(main_lines):
        if line.startswith('from ') or line.startswith('import '):
            last_import_idx = i

    # Insert import after last import
    main_lines.insert(last_import_idx + 1, import_statement)

    # Write back to main.py
    main_py.write_text(''.join(main_lines), encoding="utf-8")

    print("✅ Updated main.py")
    print(f"   Removed {len(mindmap_lines)} lines")
    print("   Added import statement")

    return True

if __name__ == "__main__":
    success = extract_mindmap_view()
    if success:
        print("\n✅ Extraction completed successfully!")
    else:
        print("\n❌ Extraction failed!")
        exit(1)
