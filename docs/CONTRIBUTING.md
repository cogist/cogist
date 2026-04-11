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

This is the **golden rule** for Cogist documentation. All documentation work must follow this principle.

---

### Documentation Categories

Cogist has three tiers of documentation, each with a clear purpose:

#### 1️⃣ **Root Level** - For Everyone

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| `README.md` | Project introduction | Low (stable after launch) |
| `CHANGELOG.md` | Version changelog | Medium (each release) |
| `LICENSE` | Legal license | Very low |
| `QUICKSTART.md` | 5-minute quick start | Low |

**Key:** These are the first documents users see. Must be concise and clear.

---

#### 2️⃣ **docs/ Core** - For Developers

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| `INDEX.md` | Documentation index | When adding new docs |
| `PROJECT_STATUS.md` | **Current status & tasks** | High (each commit) |
| `FEATURES_SUMMARY.md` | Feature roadmap | Medium (phase completion) |
| `TECHNICAL_IMPLEMENTATION.md` | Technical details | Low (after design stable) |
| `ARCHITECTURE.md` | Architecture design | Low (after architecture stable) |

**Key:** PROJECT_STATUS.md is the most active document. Must stay current.

---

#### 3️⃣ **docs/ Reference** - Specialized Topics

| Document | Purpose | When to update |
|----------|---------|----------------|
| `PRODUCT_STRATEGY.md` | Product strategy | When strategy changes |
| `LAYOUT_COMPARISON.md` | Layout algorithms | When adding new algorithms |
| `XMIND_LAYOUT_GUIDE.md` | Default layout guide | When optimizing algorithms |
| `LICENSE_GUIDE.md` | License details | When dependencies change |

**Key:** These are reference documents. Don't need frequent updates.

---

### 🚫 Common Mistakes

#### ❌ Mistake 1: Writing detailed history in PROJECT_STATUS.md

```markdown
# ❌ DON'T do this

## Completed

### 2026-04-01 - Node entity completed
Today I completed the Node entity class, implemented UUID, parent-child...

### 2026-04-02 - Architecture setup
Set up four-layer architecture, created all directories...
```

**Problem:** This is Changelog's job, not current status.

---

#### ✅ Correct: Only write current state in PROJECT_STATUS.md

```markdown
# ✅ DO this

## Completed

### 1. Directory Structure Created ✅
(List directory structure)

### 2. Node Entity Implemented ✅
(List features)

**See recent updates**: [CHANGELOG.md](../CHANGELOG.md)
```

---

#### ❌ Mistake 2: Writing technical details in CHANGELOG.md

```markdown
# ❌ DON'T do this

## [Unreleased]

### Changed
- Refactored traverse method in Node class to use generator pattern...
- Improved layout algorithm complexity from O(n²) to O(n log n)...
```

**Problem:** Users don't care about implementation details. That's for Git commits or technical docs.

---

#### ✅ Correct: Write user-visible changes in CHANGELOG.md

```markdown
# ✅ DO this

## [Unreleased]

### Added
- Node entity class with parent-child relationship management
- Four-layer DDD architecture for better extensibility

### Changed
- Performance improvement: 50% faster layout for large node counts
```

---

### 📋 Documentation Maintenance Checklist

#### Before Each Commit

- [ ] Is the document purpose clear?
- [ ] Is there any content overlap?
- [ ] Are links correct (relative paths)?
- [ ] Is language concise?
- [ ] Format consistent with other docs?

#### When Adding New Documents

- [ ] Is this document really necessary?
- [ ] Does it overlap with existing docs?
- [ ] Who is the target reader?
- [ ] Should it be in root or docs/?
- [ ] Is INDEX.md updated?

---

### 🔗 Link Maintenance

When referencing related content, **use links, not copy-paste**:

```markdown
# ✅ Good practice

For details, see [Architecture Design](ARCHITECTURE.md).

# ❌ Bad practice

Architecture design is as follows:
(Paste 500 lines from ARCHITECTURE.md here)
```

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
