# Cogist Documentation Index

📚 **Complete Documentation Navigation for Cogist Project**

---

## 🎯 Quick Start

| Document | Description | For |
|----------|-------------|-----|
| [README.md](../README.md) | Project introduction and quick start | Everyone |
| [QUICKSTART.md](../QUICKSTART.md) | 5-minute hands-on experience | New users |
| [CHANGELOG.md](../CHANGELOG.md) | Version history and updates | All users |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines | Contributors |

---

## 📖 Core Documentation

### For Contributors

| Document | Description | When to read |
|----------|-------------|--------------|
| [CONTRIBUTING.md](CONTRIBUTING.md) | **Contribution guidelines** | Before contributing |
| [DOCUMENT_CHECKLIST.md](DOCUMENT_CHECKLIST.md) | **Documentation checklist** | Before submitting PR |
| [DOCUMENT_GOVERNANCE.md](DOCUMENT_GOVERNANCE.md) | **Documentation standards** | Understanding project norms |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | **Current status and tasks** | See what's being worked on |

**Recommended reading order:**
1. CONTRIBUTING.md → Learn how to contribute
2. DOCUMENT_CHECKLIST.md → Understand quality standards
3. PROJECT_STATUS.md → Find tasks to work on

---

### Architecture & Design

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | **Detailed architecture design** |
| [TECHNICAL_IMPLEMENTATION.md](TECHNICAL_IMPLEMENTATION.md) | **Technical implementation details** |

**Architecture overview:**
- Four-layer architecture (DDD pattern)
- Domain-driven design
- Plugin-friendly structure

---

### Features & Requirements

| Document | Description |
|----------|-------------|
| [FEATURES_SUMMARY.md](FEATURES_SUMMARY.md) | **Feature roadmap summary** |
| [FEATURES.md](FEATURES.md) | **Detailed feature specifications** |
| [LAYOUT_COMPARISON.md](LAYOUT_COMPARISON.md) | **Layout algorithms comparison** |
| [XMIND_LAYOUT_GUIDE.md](XMIND_LAYOUT_GUIDE.md) | **Default-style layout guide** |

---

### Product & Strategy

| Document | Description | Audience |
|----------|-------------|----------|
| [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md) | **Product strategy and positioning** | Internal reference |

---

### Legal & Compliance

| Document | Description |
|----------|-------------|
| [LICENSE_GUIDE.md](LICENSE_GUIDE.md) | **License compliance guide** |

**Main licenses:**
- **Cogist code**: MIT License
- **PySide6 dependency**: LGPL-3.0

---

## 🔧 Development & Build

| File | Description |
|------|-------------|
| [pyproject.toml](../pyproject.toml) | Project configuration and dependencies |
| [pyrightconfig.json](../pyrightconfig.json) | Type checking configuration |
| [.python-version](../.python-version) | Python version requirement (3.13+) |

**Setup environment:**
```bash
# Install uv (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install dependencies
git clone <repo-url>
cd cogist
uv install

# Run demo
uv run python main.py
```

---

## 📁 Documentation Structure

```
docs/
├── INDEX.md                    # 📚 This file - Documentation index
│
├── CONTRIBUTING.md             # 👥 Contribution guidelines
├── DOCUMENT_CHECKLIST.md       # ✅ Quality checklist
├── DOCUMENT_GOVERNANCE.md      # 📋 Governance standards
│
├── ARCHITECTURE.md             # 🏗️ Architecture design
├── TECHNICAL_IMPLEMENTATION.md # 🔧 Technical details
│
├── FEATURES_SUMMARY.md         # 📋 Feature summary
├── FEATURES.md                 # 📝 Detailed features
├── LAYOUT_COMPARISON.md        # 📊 Layout comparison
├── XMIND_LAYOUT_GUIDE.md       # 🎨 Default layout guide
│
├── PROJECT_STATUS.md           # 📊 Current project status
├── PRODUCT_STRATEGY.md         # 🎯 Product strategy (internal)
│
└── LICENSE_GUIDE.md            # ⚖️ License guide
```

**Chinese documentation:**
- [zh-CN/](zh-CN/) - Chinese translated versions

---

## 🌍 Internationalization

This project supports multiple languages:

| Language | Documentation |
|----------|---------------|
| 🇬🇧 English | Main documentation (this directory) |
| 🇨🇳 简体中文 | [zh-CN/INDEX.md](zh-CN/INDEX.md) |

**Want to help translate?** Check out [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📞 Need Help?

- 📖 Browse this documentation index
- 💬 Open an issue on GitHub
- ✉️ Contact the maintainers

---

*Last updated: 2026-04-03*  
*Maintained by: Cogist Team*
