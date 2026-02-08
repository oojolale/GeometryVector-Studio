# 插件安装和重新加载指南

## 问题诊断

错误信息：
```
RuntimeError: Error: module 'blenderUI.handlers' has no attribute 'on_depsgraph_update'
```

**原因**：这是因为旧版本的handlers.py被缓存在内存中，而新版本的`__init__.py`尝试访问新函数。

## 解决方案

### 方法1：完全重启Blender（推荐）

1. **关闭Blender**
2. **重新打开Blender**
3. **安装/启用插件**

这是最干净的方法，确保没有缓存问题。

### 方法2：强制重新加载

如果不想重启Blender，在Scripting工作区执行：

```python
import sys
import importlib

# 清除所有blenderUI相关的缓存模块
modules_to_remove = [key for key in sys.modules.keys() if key.startswith('blenderUI')]
for mod in modules_to_remove:
    del sys.modules[mod]
    print(f"Removed: {mod}")

print("Cache cleared! Now reinstall the addon.")
```

### 方法3：使用调试版本（已实现）

新版本的`__init__.py`已经添加了完整的错误处理：

```python
# 检查函数是否存在
if hasattr(handlers, 'on_depsgraph_update'):
    # 安全注册
    bpy.app.handlers.depsgraph_update_post.append(handlers.on_depsgraph_update)
```

现在即使旧版本handlers.py还在缓存中，也不会导致崩溃。

## 验证安装

安装成功后，在Blender Console中应该看到：

```
[Addon] Registered on_load_post handler
[Addon] Registered on_depsgraph_update handler
```

如果看到错误消息：
```
[Addon] ERROR: handlers.on_depsgraph_update not found!
[Addon] Available in handlers module: ['init_scene_items', 'on_load_post', ...]
```

说明handlers.py文件没有正确加载。

## 测试自动绑定功能

1. **打开Geometry Vectors面板**
2. **创建一个预设对象**：
   ```
   Load from Preset → HELICOPTER
   Decode & Render
   ```
3. **修改向量参数**（例如修改scale）
4. **再次Decode & Render**创建第二个对象
5. **来回选中两个对象**，观察向量编辑器是否自动更新

**预期行为**：
- 选中Helicopter.001 → 编辑器显示其向量值
- 选中Helicopter.002 → 编辑器自动切换到其向量值
- Console输出：`[VectorEditor] Auto-bound to object: Helicopter.001`

## 调试日志

启用后会在Console输出详细日志：

```python
# 注册时
[Addon] Registered on_load_post handler
[Addon] Registered on_depsgraph_update handler

# 选择对象时
[VectorEditor] Auto-bound to object: MyShapeObject

# 失败时
[VectorEditor] Failed to auto-bind: KeyError 'geom_vector_0'
```

## 常见问题

### Q: 自动绑定不工作？
**A**: 检查Geometry Vectors面板中的"Auto-Bind to Selected Object"是否勾选。

### Q: 性能下降？
**A**: 关闭"Auto-Bind"开关，depsgraph_update_post是高频事件。

### Q: 仍然报错找不到on_depsgraph_update？
**A**: 
1. 确认handlers.py文件存在且包含该函数
2. 完全重启Blender清除缓存
3. 检查addon文件夹路径是否正确

## 文件清单

确保所有文件都已更新：

- ✅ `handlers.py` - 包含on_depsgraph_update函数
- ✅ `__init__.py` - 安全的注册/注销逻辑
- ✅ `properties.py` - 包含vector_editor_auto_bind属性
- ✅ `panels.py` - UI中显示Auto-Bind开关
- ✅ `operators.py` - Decode & Render使用统一创建逻辑

## 手动验证

在Blender Python Console执行：

```python
import blenderUI.handlers as h
print("Functions:", [x for x in dir(h) if not x.startswith('_')])
print("on_depsgraph_update exists:", hasattr(h, 'on_depsgraph_update'))
```

预期输出：
```
Functions: ['init_scene_items', 'on_depsgraph_update', 'on_load_post']
on_depsgraph_update exists: True
```
