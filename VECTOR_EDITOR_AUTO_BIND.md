# Vector Editor Auto-Bind System

## 概述
向量编辑器现在支持**自动绑定到选中对象**，实现实时响应选择变化的动态编辑体验。

## 功能特性

### 1. 自动对象绑定
当你选中一个包含向量数据的对象时，向量编辑器会自动加载该对象的向量参数到编辑器中。

**工作流程：**
```
用户选中对象A → 编辑器自动加载A的向量
用户选中对象B → 编辑器自动加载B的向量
用户选中普通mesh → 编辑器保持当前状态
```

### 2. 可切换的自动绑定
在Geometry Vectors面板顶部有一个开关：
- ✅ **Auto-Bind to Selected Object** - 启用自动绑定（默认）
- ⬜ 禁用后，需要手动点击"From Object"按钮加载对象向量

### 3. 预设创建时的绑定清除
在Shape Transformer面板中创建预设时，系统会自动清除向量编辑器的绑定，防止两个工作流产生冲突。

**两种工作流：**
- **Shape Transformer工作流** - 直接创建3D模型（详细几何体）
- **Geometry Vectors工作流** - 从向量参数重建（参数化+修改器）

## 技术实现

### Handler监听机制
```python
@persistent
def on_depsgraph_update(scene, depsgraph):
    """监听场景图更新，检测对象选择变化"""
    # 当active_object变化时
    if active_obj != _last_selected:
        if active_obj has vector data:
            load vector to editor
            update source info
```

### 对象识别
系统通过以下属性识别向量对象：
```python
has_vector_data = all(f"geom_vector_{i}" in obj for i in range(32))
geometry_vector_source = obj.get("geometry_vector_source")  # preset/decode_render/import/manual_edit
```

### 预设识别
当对象source为"preset"时，系统尝试反向匹配向量到预设名称：
```python
# 计算当前向量与所有预设向量的欧几里得距离
distance = ||current_vec - preset_vec||₂
# 如果distance < 0.1，识别为该预设
```

## 使用示例

### 场景1：多对象编辑
1. 创建直升机A：Load from Preset → HELICOPTER → Decode & Render
2. 修改向量参数（scale, twist等）
3. 创建直升机B：再次Decode & Render
4. 现在可以来回选中A/B，编辑器自动切换到对应向量

### 场景2：导入多个.gvec文件
1. Import Batch导入10个.gvec文件（创建10个对象）
2. 依次选中这些对象，编辑器自动显示各自的向量
3. 修改向量后Decode & Render更新对象
4. Export Batch批量导出修改后的向量

### 场景3：禁用自动绑定
1. 关闭"Auto-Bind to Selected Object"
2. 选中不同对象不会影响编辑器
3. 手动点击"From Object"按钮加载所需对象
4. 适用于需要保持编辑器参数稳定的情况

## 注意事项

### 性能考虑
- Handler在每次depsgraph更新时调用（高频率）
- 通过缓存`_last_selected`避免重复处理
- 仅在`vector_editor_auto_bind=True`时执行检测
- 向量加载操作非常轻量（32个float复制）

### 兼容性
- 与手动"From Object"按钮完全兼容
- 不影响现有导入/导出工作流
- 向下兼容旧版本创建的对象

### 工作流分离
| 面板 | 创建方式 | 适用场景 |
|------|---------|---------|
| Shape Transformer | 直接3D建模 | 需要精确控制几何细节 |
| Geometry Vectors | 向量参数化 | 需要向量运算、插值、批处理 |

**重要**：两种方式创建的同名预设（如HELICOPTER）几何体可能不同：
- Shape Transformer → 多部件组合（机身+旋翼+尾桨+起落架）
- Geometry Vectors → 参数化基础形状+修改器

## 调试信息

启用后会在Console输出日志：
```
[VectorEditor] Auto-bound to object: Helicopter.001
[VectorEditor] Failed to auto-bind: KeyError 'geom_vector_0'
```

## API参考

### 属性
```python
bpy.context.scene.vector_editor_auto_bind: BoolProperty
    # 控制自动绑定开关
    
bpy.context.scene.geom_vector_current[0:32]: FloatVectorProperty
    # 当前编辑的向量值
    
bpy.context.scene.vector_source_preset: StringProperty
    # 当前向量的来源预设名称
```

### Handler
```python
handlers.on_depsgraph_update(scene, depsgraph)
    # 注册到 bpy.app.handlers.depsgraph_update_post
```

## 更新日志

### v1.1 (2026-02-08)
- ✅ 添加自动对象绑定功能
- ✅ 添加UI开关控制
- ✅ 修复预设创建时的向量绑定冲突
- ✅ 统一Shape Transformer和Geometry Vectors的预设创建逻辑
- ✅ 添加预设识别系统
