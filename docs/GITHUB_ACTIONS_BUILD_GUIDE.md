# GitHub Actions 自动打包指南

## 概述

本项目配置了 GitHub Actions 工作流，可以自动为三个平台（Linux、Windows、macOS）打包可执行程序，并在创建 Git Tag 时自动发布到 GitHub Releases。

## 工作流程

### 触发条件

1. **自动触发**：当推送版本标签时（如 `v0.5.0`）
2. **手动触发**：在 GitHub Actions 页面手动运行工作流

### 构建过程

工作流会在三个平台上并行执行：

1. **Ubuntu Linux** → 生成 `Cogist-Linux`（可执行文件）
2. **Windows** → 生成 `Cogist-Windows.zip`（压缩包）
3. **macOS** → 生成 `Cogist-macOS`（可执行文件）

### 打包工具

使用 **PyInstaller** 进行打包：
- ✅ 配置简单，易于维护
- ✅ 对 PySide6 支持良好
- ✅ 社区成熟，文档丰富
- ✅ 编译速度快（5-10分钟）

## 使用方法

### 方法 1：通过 Git Tag 自动发布（推荐）

```bash
# 1. 确保所有修改已提交
git add -A
git commit -m "chore: prepare v0.5.0 release"

# 2. 创建 Git Tag
git tag -a v0.5.0 -m "Release v0.5.0: UI improvements and bug fixes"

# 3. 推送到远程（包括 tags）
git push origin main --tags
```

推送后，GitHub Actions 会自动：
1. 在三个平台上构建可执行文件
2. 创建 GitHub Release
3. 上传打包文件到 Release

### 方法 2：手动触发

1. 进入 GitHub 仓库的 **Actions** 标签页
2. 选择 **Build and Release** 工作流
3. 点击 **Run workflow** 按钮
4. 选择分支（通常是 `main`）
5. 点击 **Run workflow**

## 本地测试打包

在推送之前，建议在本地测试打包：

### macOS

```bash
# 安装依赖
uv pip install pyinstaller pillow

# 打包（目录模式，快速测试）
uv run pyinstaller --name=Cogist --onedir --windowed \
  --add-data="assets:assets" \
  --icon=assets/icons/cogist.png \
  main.py

# 运行测试
open dist/Cogist.app
```

### Windows

```powershell
# 安装依赖
uv pip install pyinstaller pillow

# 打包
uv run pyinstaller --name=Cogist --onedir --windowed `
  --add-data="assets;assets" `
  --icon=assets/icons/cogist.png `
  main.py

# 运行测试
.\dist\Cogist\Cogist.exe
```

### Linux

```bash
# 安装依赖
uv pip install pyinstaller pillow

# 打包
uv run pyinstaller --name=Cogist --onedir --windowed \
  --add-data="assets:assets" \
  --icon=assets/icons/cogist.png \
  main.py

# 运行测试
./dist/Cogist/Cogist
```

## 注意事项

### 图标文件

- 必须提供 `assets/icons/cogist.png`（建议 512x512 或更大）
- PyInstaller 会自动转换为各平台所需格式（.icns, .ico）
- 需要安装 Pillow 库进行转换

### 资源文件

- 所有资源文件放在 `assets/` 目录下
- PyInstaller 会通过 `--add-data` 参数包含这些文件
- 代码中使用相对路径访问资源

### 文件大小

- **单文件模式**（`--onefile`）：生成单个可执行文件，但启动较慢
- **目录模式**（`--onedir`）：生成文件夹，启动较快

当前配置使用 **目录模式**，如果需要单文件模式，修改工作流中的 `--onedir` 为 `--onefile`。

## 故障排除

### 问题 1：打包失败，提示缺少模块

**解决**：在 `.spec` 文件中添加 `hiddenimports`：

```python
hiddenimports=['module_name'],
```

### 问题 2：运行时找不到资源文件

**解决**：确保使用了正确的路径获取方式：

```python
import sys
import os

def get_resource_path(relative_path):
    """Get absolute path to resource"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
```

### 问题 3：macOS 提示"应用已损坏"

**解决**：这是 Gatekeeper 的安全提示，因为应用未签名。用户可以：
1. 右键点击应用 → 打开 → 仍然打开
2. 或在系统设置中允许运行

未来可以考虑购买 Apple Developer ID 进行代码签名。

## 后续优化

### Phase 2: 添加安装程序

- **Windows**: 使用 Inno Setup 创建 `.exe` 安装程序
- **macOS**: 创建 `.dmg` 磁盘镜像
- **Linux**: 创建 `.AppImage` 或 `.deb` 包

### Phase 3: 代码签名

- Windows: EV 证书（避免安全警告）
- macOS: Apple Developer ID（$99/年）
- Linux: 通常不需要

### Phase 4: 自动更新

- 集成自动更新检查
- 提示用户下载新版本
