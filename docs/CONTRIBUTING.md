# Contributing to Cogist

🤝 **Welcome! We're excited that you're interested in contributing to Cogist!**

This document provides guidelines and instructions for contributing.

---

## 📚 Table of Contents

1. [Code Contributions](#code-contributions)
2. [Documentation](#documentation)
3. [Development Environment](#development-environment)
4. [Submission Process](#submission-process)

---

## 💻 Code Contributions

### Development Workflow

1. **Fork the project**
2. **Create a branch** (`git checkout -b feature/amazing-feature`)
3. **Write code** (follow existing code style)
4. **Run tests** (ensure all tests pass)
5. **Commit changes** (use semantic commit messages)
6. **Open a Pull Request**

### Code Style

- Follow PEP 8 style guidelines
- Add type annotations where appropriate
- Write clear docstrings
- Keep functions focused (single responsibility)
- Avoid long functions (recommended < 50 lines)

---

## 📖 Documentation

### Core Principles

> **"Clear responsibilities, no overlap, each document does one thing well"**

This is the **golden rule** for Cogist documentation.

---

### Documentation Structure

Cogist maintains two types of documentation:

#### 1️⃣ **Public Documentation** (English)

| Document | Purpose |
|----------|---------|
| `README.md` | Project introduction and quick start |
| `CHANGELOG.md` | Version history and updates |
| `docs/INDEX.md` | Documentation index |
| `docs/CONTRIBUTING.md` | Contribution guidelines |

These documents are included in public releases and should be kept up-to-date.

---

#### 2️⃣ **Internal Documentation** (Chinese)

Detailed design documents, architecture decisions, and development plans are maintained in Chinese in the `docs/zh-CN/` directory. These are for internal development use only and are not included in public releases.

---

### Keeping Documentation Current

When making changes:

- ✅ Update CHANGELOG.md with user-visible changes
- ✅ Update INDEX.md if adding/removing public documents
- ✅ Keep README.md accurate for new users
- ❌ Don't modify internal Chinese docs unless you're part of the core team

---

## 🛠️ Development Environment

### Prerequisites

- Python 3.13+
- uv package manager
- Git

### Installation Steps

```bash
# Clone the project
git clone https://github.com/YOUR_USERNAME/cogist.git
cd cogist

# Install dependencies
uv install

# Run demo
uv run python main.py
```

---

## 📤 Submission Process

### Commit Message Convention

Follow semantic versioning for commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation update
- `style`: Code formatting (no functional change)
- `refactor`: Refactoring
- `test`: Test-related
- `chore`: Build/tool configuration

**Example:**
```
feat(domain): add Node entity class

- Implement UUID unique identifier
- Add parent-child relationship management
- Support tree traversal methods

Closes #12
```

---

## 📞 Need Help?

- 📖 Check [Documentation Index](INDEX.md)
- 💬 Join discussions (GitHub Issues)
- ✉️ Contact maintainers

---

**Thank you for your contribution!** 🎉
