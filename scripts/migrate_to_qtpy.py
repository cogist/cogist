#!/usr/bin/env python3
"""
Migrate all PySide6 imports to QtPy imports.

QtPy automatically handles:
- Enum promotion for PyQt6 (unscoped enum access)
- Module aliases (pyqtSignal -> Signal, pyqtSlot -> Slot, etc.)
- API differences between PyQt5/6 and PySide2/6

This script simply replaces import statements:
- from qtpy.QtCore import ... -> from qtpy.QtCore import ...
- from qtpy.QtGui import ... -> from qtpy.QtGui import ...
- from qtpy.QtWidgets import ... -> from qtpy.QtWidgets import ...
"""

import re
from pathlib import Path


def migrate_file(file_path: Path) -> bool:
    """Migrate a single Python file from PySide6 to QtPy."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # Replace PySide6 imports with QtPy imports
        # Pattern 1: from qtpy.QtCore import ...
        content = re.sub(
            r'from PySide6\.QtCore import',
            'from qtpy.QtCore import',
            content
        )

        # Pattern 2: from qtpy.QtGui import ...
        content = re.sub(
            r'from PySide6\.QtGui import',
            'from qtpy.QtGui import',
            content
        )

        # Pattern 3: from qtpy.QtWidgets import ...
        content = re.sub(
            r'from PySide6\.QtWidgets import',
            'from qtpy.QtWidgets import',
            content
        )

        # Pattern 4: from qtpy.QtPrintSupport import ...
        content = re.sub(
            r'from PySide6\.QtPrintSupport import',
            'from qtpy.QtPrintSupport import',
            content
        )

        # Pattern 5: from qtpy.QtSvg import ...
        content = re.sub(
            r'from PySide6\.QtSvg import',
            'from qtpy.QtSvg import',
            content
        )

        # Remove standalone PySide6 imports if any
        content = re.sub(
            r'^import PySide6\s*$',
            '',
            content,
            flags=re.MULTILINE
        )

        # Only write if content changed
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main migration function."""
    project_root = Path(__file__).parent.parent

    # Find all Python files in the project
    python_files = list(project_root.rglob('*.py'))

    # Exclude virtual environment and cache directories
    exclude_dirs = {'.venv', '__pycache__', '.git', 'build', 'dist'}
    python_files = [
        f for f in python_files
        if not any(excluded in f.parts for excluded in exclude_dirs)
    ]

    migrated_count = 0
    for py_file in python_files:
        if migrate_file(py_file):
            print(f"Migrated: {py_file.relative_to(project_root)}")
            migrated_count += 1

    print(f"\nMigration complete! {migrated_count} files modified.")


if __name__ == '__main__':
    main()
