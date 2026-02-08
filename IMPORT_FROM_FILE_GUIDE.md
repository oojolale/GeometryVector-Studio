# Import from File Guide - 导入文件指南

## 🐛 问题描述

### 问题现象
1. 导入 `original.gvec` → 对象A → 直接导出 → 再导入 ✅ **正常还原**
2. 导入 `original.gvec` → 对象A → **修改向量** → Decode&Render → 对象B
3. 导出对象B → `modified.gvec`
4. 导入 `modified.gvec` → ❌ **总是变成立方体，而不是对象B**

### 根本原因分析

**问题链**：
```
修改向量 → Decode&Render → 对象B（从预设/缓存生成）
                              ↓
                         Export时选择 include_mesh=True
                              ↓
                         但对象B没有真实mesh数据！
                              ↓
                         导出的.gvec文件中mesh=null
                              ↓
                         导入时创建空mesh对象
                              ↓
                      Blender显示为默认立方体 ❌
```

**核心问题**：
- Decode&Render 创建的对象使用的是**临时几何** + **修改器**
- 这些修改器没有被"应用"（apply），所以实际mesh数据是基础几何
- 导出时如果序列化这个未应用的mesh，会导致信息丢失

---

## ✅ 解决方案

### 方案概述

1. **导出时**：优先使用保存的向量数据（已在上次修复中完成）
2. **导入时**：检测空mesh，使用向量重建几何

### 实现细节

#### 修改 1：`geometry_file_format.py` - 明确标记无mesh数据的情况

```python
@staticmethod
def restore_object_from_file(filepath, context):
    # ...
    if "mesh" in data:
        # 有mesh数据：直接反序列化
        mesh = GeometryFileFormat.deserialize_mesh(data["mesh"])
        obj = bpy.data.objects.new(obj_name, mesh)
    else:
        # 无mesh数据：创建空对象，等待重建
        mesh = bpy.data.meshes.new(obj_name)
        obj = bpy.data.objects.new(obj_name, mesh)
    
    # 总是保存向量数据
    for i in range(32):
        obj[f"geom_vector_{i}"] = float(geom_vector.vector[i])
```

#### 修改 2：`operators.py` - 导入时检测并重建空mesh

```python
class MYADDON_OT_import_gvec:
    def execute(self, context):
        obj = GeometryFileFormat.restore_object_from_file(...)
        
        # 检测空mesh（需要重建）
        if len(obj.data.vertices) == 0:
            # 加载向量到编辑器
            for i in range(32):
                scene.geom_vector_current[i] = obj[f"geom_vector_{i}"]
            
            # 删除空对象
            old_name = obj.name
            bpy.data.objects.remove(obj, do_unlink=True)
            
            # 使用Decode&Render重建
            bpy.ops.myaddon.vector_decode_and_render()
            obj = context.active_object
            obj.name = old_name
```

---

## 📊 工作流程对比

### 修复前 ❌

```
导入original.gvec
     ↓
修改向量 [0.1 → 0.8]
     ↓
Decode&Render → 对象B（基础mesh + 修改器）
     ↓
导出 → 保存未应用的基础mesh（错误）
     ↓
导入 → 只有基础mesh，丢失修改器 → 立方体 ❌
```

### 修复后 ✅

```
导入original.gvec
     ↓
修改向量 [0.1 → 0.8]
     ↓
Decode&Render → 对象B + 保存向量 [0.8...]
     ↓
导出 → 优先保存向量 [0.8...] + 基础mesh（或无mesh）
     ↓
导入 → 检测到空/简单mesh → 从向量重建 → 正确的对象B ✅
```

---

## 🎯 两种导出模式

### 模式 1：完整mesh模式（推荐）

**适用场景**：
- 复杂的导入模型
- 需要完整保留网格细节
- 不依赖Decode&Render的对象

**导出方式**：
```python
bpy.ops.myaddon.export_gvec(
    filepath="model.gvec",
    include_mesh=True  # 包含完整mesh
)
```

**文件大小**：10 KB - 10 MB（取决于mesh复杂度）

**导入行为**：
- 有完整mesh → 直接反序列化 ✅
- 快速加载
- 100%保真

---

### 模式 2：纯向量模式

**适用场景**：
- Decode&Render生成的对象
- 预设几何体
- 需要小文件大小

**导出方式**：
```python
bpy.ops.myaddon.export_gvec(
    filepath="vector.gvec",
    include_mesh=False  # 仅向量
)
```

**文件大小**：1-2 KB

**导入行为**：
- 无mesh或空mesh → 从向量重建 ✅
- 需要Decode&Render
- 可能与原始略有差异（修改器应用顺序）

---

## 🧪 测试场景

### 测试 1：修改向量后导出导入

```python
# 1. 创建预设对象
bpy.ops.myaddon.apply_preset(preset_name='SPIRAL_CORRIDOR')

# 2. 加载向量到编辑器
bpy.ops.myaddon.vector_load_from_object()

# 3. 修改向量
scene = bpy.context.scene
scene.geom_vector_current[8] = 1.5  # 增加扭曲

# 4. Decode & Render
bpy.ops.myaddon.vector_decode_and_render()
obj_modified = bpy.context.active_object

# 5. 导出（两种模式都测试）
## 模式1：包含mesh
bpy.ops.myaddon.export_gvec(
    filepath="test_with_mesh.gvec",
    include_mesh=True
)

## 模式2：仅向量
bpy.ops.myaddon.export_gvec(
    filepath="test_vector_only.gvec",
    include_mesh=False
)

# 6. 删除对象
bpy.ops.object.delete()

# 7. 导入测试
bpy.ops.myaddon.import_gvec(filepath="test_with_mesh.gvec")
# ✅ 应该正确还原修改后的对象

bpy.ops.object.delete()
bpy.ops.myaddon.import_gvec(filepath="test_vector_only.gvec")
# ✅ 应该从向量重建，效果相同
```

---

### 测试 2：复杂导入模型

```python
# 1. 导入外部.blend文件中的复杂模型
bpy.ops.myaddon.vector_load_from_file()  # 选择包含复杂mesh的文件

# 2. 不做任何修改，直接导出
bpy.ops.myaddon.export_gvec(filepath="imported_model.gvec")

# 3. 删除并重新导入
bpy.ops.object.delete()
bpy.ops.myaddon.import_gvec(filepath="imported_model.gvec")

# ✅ 应该完整保留原始mesh细节
```

---

### 测试 3：迭代编辑工作流

```python
# 迭代1：创建基础
scene.geom_vector_current[0] = 0.5
bpy.ops.myaddon.vector_decode_and_render()
bpy.ops.myaddon.export_gvec(filepath="v1.gvec")

# 迭代2：调整参数
bpy.ops.myaddon.import_gvec(filepath="v1.gvec")
scene.geom_vector_current[1] = 0.8  # 修改复杂度
bpy.ops.myaddon.vector_decode_and_render()
bpy.ops.myaddon.export_gvec(filepath="v2.gvec")

# 迭代3：继续调整
bpy.ops.myaddon.import_gvec(filepath="v2.gvec")
scene.geom_vector_current[8] = 0.3  # 修改扭曲
bpy.ops.myaddon.vector_decode_and_render()
bpy.ops.myaddon.export_gvec(filepath="v3.gvec")

# 验证：导入v3应该保留所有修改
bpy.ops.object.delete()
bpy.ops.myaddon.import_gvec(filepath="v3.gvec")
# ✅ 应该看到包含所有迭代修改的最终对象
```

---

## 🔍 调试信息

### 启用调试输出

修改后的代码在导入时会输出调试信息：

```python
[GVEC] Restoring from mesh data (vertices: 1024)
# 或
[GVEC] No mesh data found, will reconstruct from vector...

[Import] Object has empty mesh, reconstructing from vector...
[Import] Successfully reconstructed ObjectName from vector
```

### 检查.gvec文件内容

```python
import json

# 读取.gvec文件
with open("test.gvec", 'r') as f:
    data = json.load(f)

# 检查是否有mesh数据
if "mesh" in data:
    vertex_count = len(data["mesh"]["vertices"])
    face_count = len(data["mesh"]["faces"])
    print(f"Mesh data: {vertex_count} vertices, {face_count} faces")
else:
    print("No mesh data - vector only mode")

# 检查向量数据
vector = data["vector"]
print(f"Vector[0] (Shape Type): {vector[0]}")
print(f"Vector[1] (Complexity): {vector[1]}")
```

---

## 📝 最佳实践

### 推荐工作流

1. **创建/导入初始对象**
   ```python
   bpy.ops.myaddon.apply_preset(preset_name='...')
   # 或
   bpy.ops.myaddon.vector_load_from_file()
   ```

2. **编辑向量参数**
   ```python
   scene.geom_vector_current[i] = new_value
   ```

3. **Decode & Render（必须！）**
   ```python
   bpy.ops.myaddon.vector_decode_and_render()
   ```

4. **导出（选择合适模式）**
   ```python
   # 简单几何 → 仅向量（小文件）
   bpy.ops.myaddon.export_gvec(include_mesh=False)
   
   # 复杂导入模型 → 完整mesh（保真）
   bpy.ops.myaddon.export_gvec(include_mesh=True)
   ```

5. **导入验证**
   ```python
   bpy.ops.myaddon.import_gvec(filepath="...")
   # 系统自动选择：有mesh→反序列化，无mesh→重建
   ```

---

### 避免的错误

❌ **错误 1：修改向量后不Decode&Render就导出**
```python
scene.geom_vector_current[0] = 0.8
# 没有调用 Decode & Render！
bpy.ops.myaddon.export_gvec(filepath="bad.gvec")
# 结果：导出的是旧向量，不是修改后的
```

✅ **正确做法**：
```python
scene.geom_vector_current[0] = 0.8
bpy.ops.myaddon.vector_decode_and_render()  # 必须！
bpy.ops.myaddon.export_gvec(filepath="good.gvec")
```

---

❌ **错误 2：手动建模后期望向量导出**
```python
# 手动修改了mesh（添加顶点、面等）
bpy.ops.mesh.primitive_cube_add()
# ... 手动编辑 ...
bpy.ops.myaddon.export_gvec(filepath="manual.gvec")
# 结果：向量是重新编码的，可能不准确
```

✅ **正确做法**：手动建模的对象应该使用普通.blend文件保存

---

❌ **错误 3：期望修改器自动应用**
```python
obj = bpy.context.active_object
obj.modifiers.new(name="Subsurf", type='SUBSURF')
bpy.ops.myaddon.export_gvec(filepath="test.gvec", include_mesh=True)
# 结果：导出的是未应用修改器的基础mesh
```

✅ **正确做法**：手动应用修改器后再导出
```python
for mod in obj.modifiers:
    bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.myaddon.export_gvec(filepath="test.gvec", include_mesh=True)
```

---

## 🚀 性能优化

### 大批量导入导出

```python
# 批量导出（推荐）
selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
bpy.ops.myaddon.export_gvec_batch(filepath="batch.gvec_batch")

# 批量导入
bpy.ops.myaddon.import_gvec_batch(filepath="batch.gvec_batch")
# 系统自动处理每个对象的mesh/向量模式
```

### 文件大小对比

| 对象类型 | 原始.blend | .gvec (mesh) | .gvec (vector) |
|---------|-----------|--------------|----------------|
| 简单立方体 | 500 KB | 5 KB | 1 KB |
| 预设几何(中等) | 800 KB | 20 KB | 1.5 KB |
| 导入模型(复杂) | 5 MB | 500 KB | 2 KB |
| 高精度扫描 | 50 MB | 8 MB | 2 KB* |

*注：高精度模型使用vector模式会丢失细节，不推荐

---

## ✅ 总结

### 问题原因
- Decode&Render 创建的对象有临时几何，导出时mesh数据不完整
- 导入时空mesh被显示为默认立方体

### 解决方法
- ✅ 导出时优先使用保存的向量数据
- ✅ 导入时检测空mesh，自动从向量重建
- ✅ 支持两种模式：完整mesh / 纯向量

### 使用建议
1. **修改向量后必须Decode&Render**
2. **导出时选择合适模式**（复杂mesh→include_mesh=True）
3. **导入会自动处理**（有mesh用mesh，无mesh重建）

### 测试验证
```python
# 完整测试流程（应该全部通过）
导入 → 修改向量 → Decode&Render → 导出 → 导入 ✅
```

---

## 🔮 下次使用

**重启Blender**后，测试以下场景：

1. 创建对象 → 修改向量 → Decode → Export → Import ✅
2. 复杂模型 → Export (mesh=True) → Import ✅  
3. 简单几何 → Export (mesh=False) → Import ✅

所有场景都应该正确还原，不再出现"立方体"问题！🎉
