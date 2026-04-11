# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-11

### Added
- **Initial Release**: Cogist - A Beautiful Mind Mapping Tool
- **Domain Layer**: Node entity with UUID, parent-child relationships, tree traversal
- **Architecture**: Four-layer DDD architecture (Domain/Application/Infrastructure/Presentation)
- **Layout Algorithm**: Intelligent auto-layout with depth-based spacing and styling
- **Node Editing**: Inline text editing with Space key
- **File Operations**: Save/Load mind maps in `.mwd` format (JSON-based)
- **Keyboard Shortcuts**: Full keyboard navigation (Cmd/Ctrl key mappings for macOS)
- **Undo/Redo**: Command pattern implementation for all operations
- **Documentation**: Complete documentation system

### Technical Stack
- Python 3.13+
- PySide6 6.8+ (Qt for Python)
- Built with uv package manager

### Project Information
- **Name**: Cogist (formerly MindWeave, renamed 2026-04-11)
- **License**: MIT License for project code + LGPL-3.0 compliance for PySide6 dependency

---

*Last updated: 2026-04-11*
