# Cogist v0.3.2

## 🎯 核心改进

### 键盘导航优化

实现了基于视觉坐标的键盘导航系统，确保上下箭头在**同一侧、同一层级**内移动。

#### 主要特性

- ✅ **同侧导航保证** - 严格限制在左侧或右侧分支内
- ✅ **同层级导航** - 只在相同深度（depth）的节点间移动
- ✅ **视觉相邻性** - 基于实际渲染的 Y 坐标判断上下关系
- ✅ **智能循环** - 到达边界时自动循环到同一侧同一层级的另一端

#### 技术实现

新增 `_find_visually_adjacent_node()` 方法，通过三个维度严格过滤：
1. **同侧检查**：`is_right_side` 属性确保不跨越左右分支
2. **同层检查**：`depth` 属性确保不跨越层级
3. **视觉相邻**：基于 `scenePos().y()` 的实际渲染坐标

代码从 30+ 行简化到 5 行，逻辑更清晰、更易维护。

## 📊 变更统计

- **修改文件**: 4 个
- **新增代码**: 296 行
- **删除代码**: 22 行
- **净增加**: 274 行

## 🔧 技术细节

### 核心方法

```python
def _find_visually_adjacent_node(self, direction: str):
    """Find the visually adjacent node on the same side and same depth."""
    
    # 1. Get current node info
    current_y = current_item.scenePos().y()
    is_right_side = current_item.is_right_side
    current_depth = current_node.depth
    
    # 2. Collect candidates with strict filtering
    for node_id, item in self.node_items.items():
        if item.is_right_side != is_right_side:
            continue  # Filter 1: Same side
        if domain_node.depth != current_depth:
            continue  # Filter 2: Same depth
        candidates.append((domain_node, item.scenePos().y()))
    
    # 3. Find closest node based on Y coordinate
    if direction == "up":
        above_nodes = [(node, y) for node, y in candidates if y < current_y]
        return max(above_nodes, key=lambda x: x[1])[0]
    else:
        below_nodes = [(node, y) for node, y in candidates if y > current_y]
        return min(below_nodes, key=lambda x: x[1])[0]
```

## 📝 完整变更日志

详见 [CHANGELOG.md](https://github.com/cogist/cogist/blob/main/CHANGELOG.md)

## 📚 文档

- [VERSION_v0.3.2.md](https://github.com/cogist/cogist/blob/main/docs/zh-CN/VERSION_v0.3.2.md) - 详细版本说明
- [DESIGN_PHILOSOPHY.md](https://github.com/cogist/cogist/blob/main/docs/zh-CN/DESIGN_PHILOSOPHY.md) - 设计理念

---

**发布日期**: 2026-04-23  
**维护者**: Cogist Team  
**许可证**: MIT License
