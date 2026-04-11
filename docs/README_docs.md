# Documentation Structure

📚 **Cogist Documentation Organization**

---

## 🌍 Internationalization Strategy

Cogist supports multiple languages to serve our global community:

### Language Tiers

| Tier | Languages | Location | Priority |
|------|-----------|----------|----------|
| **Tier 1** | 🇬🇧 English | `docs/` (root) | Primary - All users |
| **Tier 2** | 🇨🇳 简体中文 | `docs/zh-CN/` | Secondary - Chinese users |

---

## 📁 Directory Structure

```
docs/
├── INDEX.md                    # 📚 Main documentation index (English)
│
├── CONTRIBUTING.md             # 👥 Contribution guidelines (English)
├── DOCUMENT_CHECKLIST.md       # ✅ Documentation quality checklist
├── DOCUMENT_GOVERNANCE.md      # 📋 Governance standards
│
├── ARCHITECTURE.md             # 🏗️ Architecture design (English)
├── TECHNICAL_IMPLEMENTATION.md # 🔧 Technical details (English)
│
├── FEATURES_SUMMARY.md         # 📋 Feature roadmap summary (English)
├── PROJECT_STATUS.md           # 📊 Current project status (English)
│
├── LICENSE_GUIDE.md            # ⚖️ License compliance guide (English)
│
└── zh-CN/                      # 🇨🇳 Chinese translations
    ├── INDEX.md                # 中文文档索引
    ├── CONTRIBUTING.md         # 贡献指南
    ├── ARCHITECTURE.md         # 架构设计
    └── ...                     # Other Chinese documents
```

---

## 🎯 Document Categories

### Root Level (User-Facing)

Located in project root (`../`):

- **README.md** - Project introduction (everyone)
- **CHANGELOG.md** - Version history (all users)
- **QUICKSTART.md** - Quick start guide (new users)
- **LICENSE** - Legal license

**Characteristics:** Stable, concise, for everyone

---

### docs/ Core (Developer-Focused)

**Primary language:** 🇬🇧 English

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| INDEX.md | Documentation index | When adding new docs |
| CONTRIBUTING.md | Contribution guidelines | Process improvements |
| PROJECT_STATUS.md | Current status & tasks | Each commit |
| FEATURES_SUMMARY.md | Feature roadmap | Phase completion |
| ARCHITECTURE.md | Architecture design | Architecture changes |
| TECHNICAL_IMPLEMENTATION.md | Technical details | Implementation updates |

**Characteristics:** Active, practical, for contributors

---

### docs/ Reference (Specialized)

**Primary language:** 🇬🇧 English

| Document | Purpose | Audience |
|----------|---------|----------|
| PRODUCT_STRATEGY.md | Product strategy | Internal reference |
| LAYOUT_COMPARISON.md | Layout algorithms | Developers |
| XMIND_LAYOUT_GUIDE.md | Default layout guide | Algorithm implementers |
| LICENSE_GUIDE.md | License details | Legal compliance |

**Characteristics:** Professional, deep knowledge, low-frequency updates

---

### zh-CN/ Chinese Documentation

Chinese translations for Chinese-speaking users:

| Document | Status |
|----------|--------|
| INDEX.md | ✅ Available |
| CONTRIBUTING.md | ✅ Available |
| ARCHITECTURE.md | ✅ Available |
| FEATURES*.md | ✅ Available |
| Others | ✅ Available |

**Note:** English versions are the primary source. Chinese versions may lag behind updates.

---

## 📝 Documentation Principles

All Cogist documentation follows three core principles:

### 1️⃣ Single Responsibility
> Each document has one clear purpose

**Example:**
- ✅ CHANGELOG.md records version changes only
- ✅ PROJECT_STATUS.md tracks current progress only
- ❌ Don't mix detailed history in PROJECT_STATUS.md

---

### 2️⃣ No Duplication
> Same content doesn't appear in multiple documents

**Implementation:**
- Explain once, in the right place
- Use links instead of copy-paste
- Prefer navigation over duplication

---

### 3️⃣ Links First
> Related content is linked, not duplicated

**Benefits:**
- ✅ Avoids inconsistency
- ✅ Reduces maintenance
- ✅ Keeps documents concise

---

## 🔗 Cross-Reference Guide

### For New Contributors

```
Start here:
1. ../README.md → Learn about the project
2. CONTRIBUTING.md → How to contribute
3. PROJECT_STATUS.md → Find tasks
4. DOCUMENT_CHECKLIST.md → Quality standards
```

---

### For Developers

```
Technical docs:
1. ARCHITECTURE.md → System design
2. TECHNICAL_IMPLEMENTATION.md → Implementation details
3. FEATURES.md → Requirements
4. Source code → Actual implementation
```

---

### For Users

```
User docs:
1. ../README.md → What is this?
2. ../QUICKSTART.md → Get started
3. ../CHANGELOG.md → What's new?
```

---

## 🌐 Translation Guidelines

### Want to help translate?

1. **Check existing translations**
   - See `zh-CN/` for current Chinese docs
   - Check if your language exists

2. **Create new translation**
   - Copy English version
   - Add language suffix: `.zh-CN.md`
   - Update INDEX.md with link

3. **Maintain translations**
   - Keep up to date with English original
   - Mark outdated translations

---

## 📊 Current Status

### English Documentation

| Category | Documents | Status |
|----------|-----------|--------|
| Core | 6 | ✅ Complete |
| Technical | 3 | ✅ Complete |
| Reference | 4 | ✅ Complete |
| **Total** | **13** | **✅ All in English** |

### Chinese Documentation

| Category | Documents | Status |
|----------|-----------|--------|
| Translated | 12 | ✅ Available in zh-CN/ |
| Pending | 0 | - |

---

## 🛠️ Maintenance

### Regular Tasks

- **Weekly**: Update PROJECT_STATUS.md
- **Per release**: Update CHANGELOG.md
- **Per feature**: Update technical docs
- **Quarterly**: Review all documentation

### Quality Checks

Before merging PRs:
- [ ] Documentation updated if needed
- [ ] No duplicate content
- [ ] Links are correct
- [ ] Language is clear and concise

---

## 📞 Need Help?

- 📖 Browse [INDEX.md](INDEX.md)
- 💬 Ask in GitHub Issues
- ✉️ Contact maintainers

---

*Last updated: 2026-04-03*  
*Maintained by: Cogist Team*
