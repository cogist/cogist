#!/bin/bash
# Architecture Compliance Check Script
# Usage: bash scripts/check_architecture.sh

set -e

echo "🔍 检查架构合规性..."
echo ""

ERRORS=0

# 1. Domain Layer 纯净性
echo "1️⃣ 检查 Domain Layer 纯净性..."
qt_deps=$(find cogist/domain -name "*.py" -exec grep -l "from PySide6\|import PySide6" {} \; 2>/dev/null || true)
if [ -z "$qt_deps" ]; then
    echo "   ✅ Domain Layer 无 Qt 依赖"
else
    echo "   ❌ Domain Layer 发现 Qt 依赖："
    echo "$qt_deps" | sed 's/^/      /'
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 2. Application Layer 检查
echo "2️⃣ 检查 Application Layer..."
app_qt_deps=$(find cogist/application -name "*.py" -exec grep -l "from PySide6\|import PySide6" {} \; 2>/dev/null || true)
if [ -z "$app_qt_deps" ]; then
    echo "   ✅ Application Layer 无 Qt 依赖"
else
    echo "   ⚠️  Application Layer 发现 Qt 依赖（可能需要审查）："
    echo "$app_qt_deps" | sed 's/^/      /'
fi
echo ""

# 3. Infrastructure Layer 检查
echo "3️⃣ 检查 Infrastructure Layer..."
infra_qt_deps=$(find cogist/infrastructure -name "*.py" -exec grep -l "from PySide6\|import PySide6" {} \; 2>/dev/null || true)
if [ -z "$infra_qt_deps" ]; then
    echo "   ✅ Infrastructure Layer 无 Qt 依赖"
else
    echo "   ⚠️  Infrastructure Layer 发现 Qt 依赖（可能需要审查）："
    echo "$infra_qt_deps" | sed 's/^/      /'
fi
echo ""

# 4. 文件位置检查
echo "4️⃣ 检查文件位置..."

# Connectors
if [ -d "cogist/presentation/connectors" ] && [ "$(ls -A cogist/presentation/connectors/*.py 2>/dev/null)" ]; then
    echo "   ✅ Connectors 在 Presentation Layer"
else
    echo "   ❌ Connectors 不在正确位置"
    ERRORS=$((ERRORS + 1))
fi

if [ -d "cogist/domain/connectors" ]; then
    echo "   ❌ Connectors 错误地在 Domain Layer"
    ERRORS=$((ERRORS + 1))
fi

# Borders
if [ -d "cogist/presentation/borders" ] && [ "$(ls -A cogist/presentation/borders/*.py 2>/dev/null)" ]; then
    echo "   ✅ Borders 在 Presentation Layer"
else
    echo "   ❌ Borders 不在正确位置"
    ERRORS=$((ERRORS + 1))
fi

if [ -d "cogist/domain/borders" ]; then
    echo "   ❌ Borders 错误地在 Domain Layer"
    ERRORS=$((ERRORS + 1))
fi

# MindMapView
if [ -f "cogist/presentation/views/mindmap_view.py" ]; then
    echo "   ✅ MindMapView 在独立文件中"
else
    echo "   ❌ MindMapView 未在独立文件中"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 5. 导入语句检查
echo "5️⃣ 检查导入语句..."
wrong_connectors=$(grep -r "from cogist\.domain\.connectors" --include="*.py" . 2>/dev/null || true)
if [ -z "$wrong_connectors" ]; then
    echo "   ✅ 没有错误的 connectors 导入"
else
    echo "   ❌ 发现错误的 connectors 导入："
    echo "$wrong_connectors" | sed 's/^/      /'
    ERRORS=$((ERRORS + 1))
fi

wrong_borders=$(grep -r "from cogist\.domain\.borders" --include="*.py" . 2>/dev/null || true)
if [ -z "$wrong_borders" ]; then
    echo "   ✅ 没有错误的 borders 导入"
else
    echo "   ❌ 发现错误的 borders 导入："
    echo "$wrong_borders" | sed 's/^/      /'
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 6. 代码质量检查
echo "6️⃣ 运行代码质量检查..."

if command -v uv &> /dev/null; then
    echo "   运行 Ruff..."
    if uv run ruff check . --quiet 2>&1; then
        echo "   ✅ Ruff 检查通过"
    else
        echo "   ❌ Ruff 检查失败"
        ERRORS=$((ERRORS + 1))
    fi
    
    echo "   运行 Pyright..."
    if uv run pyright 2>&1 | grep -q "0 errors"; then
        echo "   ✅ Pyright 检查通过"
    else
        echo "   ⚠️  Pyright 发现类型问题（请手动检查）"
    fi
else
    echo "   ⚠️  uv 未安装，跳过代码质量检查"
fi
echo ""

# 总结
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo "✅ 架构合规性检查通过！"
    exit 0
else
    echo "❌ 发现 $ERRORS 个架构违规问题"
    echo ""
    echo "📖 请参考文档："
    echo "   - docs/zh-CN/ARCHITECTURE.md"
    echo "   - docs/zh-CN/MINDMAP_VIEW_REFACTOR_PLAN.md"
    echo "   - .lingma/rules/architecture_constraints.md"
    exit 1
fi
