# GVEC Mesh Detection System

## 概述

本系统自动检测对象是否被手动修改，智能选择导出模式（纯向量 vs 向量+mesh），确保数据不丢失。

## 核心机制

### 1. Mesh Fingerprint（网格指纹）

当对象通过 `Decode & Render` 创建时，系统会保存：
```python
obj["geometry_vector_mesh_verts"] = len(obj.data.vertices)  # 顶点数
obj["geometry_vector_mesh_faces"] = len(obj.data.polygons)  # 面数
```

### 2. 四层检测机制

导出时会进行四层检测：

#### 检测1：网格拓扑变化
```python
original_verts = obj.get("geometry_vector_mesh_verts", -1)
current_verts = len(obj.data.vertices)

if original_verts != current_verts:
    # 顶点数改变 → 已被手动编辑
    mesh_manually_edited = True
```

**触发场景**：
- 手动添加/删除顶点
- 使用 Join 合并多个对象
- 使用 Boolean 操作
- 挤出（Extrude）、倒角（Bevel）等编辑操作

#### 检测2：共享网格数据
```python
mesh_is_shared = obj.data.users > 1
```

**触发场景**：
- 对象被复制且使用链接数据（Linked Duplicate）
- 多个对象共享同一个 mesh 数据块

#### 检测3：顶点组
```python
has_vertex_groups = len(obj.vertex_groups) > 0
```

**触发场景**：
- 添加了顶点组（用于权重绘制、骨骼绑定等）
- 使用粒子系统
- 手动编辑权重

#### 检测4：形态键
```python
has_shape_keys = obj.data.shape_keys is not None
```

**触发场景**：
- 添加了 Shape Keys（用于面部动画、变形动画等）
- 使用了 Blend Shapes

## 工作流程示例

### 场景A：纯向量对象（未修改）
```
1. Decode & Render → 创建对象
   - source = "decode_render"
   - mesh_verts = 24 (cube)
   - mesh_faces = 6
   
2. 导出 → 检测
   - 拓扑未变 ✓
   - 无共享 ✓
   - 无顶点组 ✓
   - 无形态键 ✓
   → 使用纯向量模式 (1.5KB)

3. 导入 → 自动重建 ✓
```

### 场景B：手动编辑顶点
```
1. Decode & Render → 创建对象
   - mesh_verts = 24
   - 带有修改器：Subdivision, Twist, Bend等
   
2. 进入编辑模式 → 挤出面 (E键) → 添加了12个顶点
   - mesh_verts = 36 (变化!)

3. 导出 → 检测
   - 拓扑变化：24 → 36 ✗
   → **应用所有修改器**到mesh
   → 导出完整几何体 (mesh+vector 模式)
   → 更新 source = "manual_edit"

4. 导入 → 使用导入的完整mesh
   - ✓ 挤出效果保留
   - ✓ 向量修改效果保留（已烘焙到mesh）
   - 如果再次 Decode & Render，会覆盖手动编辑
```

### 场景C：合并对象
```
1. 对象A (纯向量球体，带修改器) + 对象B (手动建模立方体)

2. 选中两个对象 → Join (Ctrl+J)
   - 合并后的对象C
   - mesh_verts = A的顶点数 + B的顶点数 (变化!)

3. 导出对象C → 检测
   - 拓扑变化 ✗
   → **应用所有修改器**
   → 导出包含完整几何体的mesh+vector ✓
   - 对象A的向量效果已烘焙到mesh
   - 对象B的手动建模保留
```

## 关键特性：修改器应用

### 自动修改器烘焙

当检测到对象被手动编辑时，导出过程会：

1. **创建临时评估对象**
   ```python
   depsgraph = context.evaluated_depsgraph_get()
   obj_eval = obj.evaluated_get(depsgraph)
   ```

2. **应用所有修改器**
   ```python
   temp_mesh = bpy.data.meshes.new_from_object(obj_eval)
   ```
   
3. **导出完整几何体**
   - 包含向量修改器的效果（subdivision, twist, bend等）
   - 包含手动编辑的效果（挤出、布尔运算等）
   - 完整的最终mesh

4. **清理临时数据**
   ```python
   bpy.data.meshes.remove(temp_mesh)
   ```

### 为什么需要应用修改器？

**问题场景**：
```
Decode & Render创建对象
  ↓
应用向量参数（通过修改器：Subdivision, Twist等）
  ↓
进入编辑模式 → E键挤出顶点（手动编辑）
  ↓
导出 → 如果不应用修改器
  ↓
导出的mesh = 基础mesh + 手动挤出（❌ 缺少修改器效果）
  ↓
导入 → 看到挤出效果，但向量修改效果消失 ❌
```

**解决方案**：
```
检测到手动编辑
  ↓
应用所有修改器到mesh
  ↓
导出的mesh = 完整最终几何体（✓ 包含所有效果）
  ↓
导入 → 挤出效果 ✓ + 向量修改效果 ✓
```

### 场景D：添加顶点组
```
1. Decode & Render → 创建角色对象

2. 权重绘制模式 → 添加顶点组 "arm", "leg"
   - vertex_groups.count > 0

3. 导出 → 检测
   - 有顶点组 ✗
   → 使用 mesh+vector 模式 ✓
```

### 场景E：添加形态键
```
1. Decode & Render → 创建面部对象

2. 添加 Shape Keys → "Smile", "Blink"
   - shape_keys存在

3. 导出 → 检测
   - 有形态键 ✗
   → 使用 mesh+vector 模式 ✓
```

## 安全策略

### 原则："宁可多存，不可丢失"

如果检测到任何手动编辑的迹象，系统会：
1. 强制使用 mesh+vector 模式
2. 更新 source 标记为 "manual_edit"
3. 保留完整的网格数据

### Fallback机制

```python
# 如果对象状态不明确，默认保存mesh
if source == "decode_render" and 有任何疑问:
    self.report({'INFO'}, "Using mesh+vector mode (safety fallback)")
```

## 对象来源标记

系统使用以下标记追踪对象来源：

| Source | 含义 | 导出模式 |
|--------|------|----------|
| `decode_render` | Decode & Render创建，未修改 | 纯向量 |
| `manual_edit` | 原为decode_render，但已手动编辑 | mesh+vector |
| `preset` | 从预设导入 | mesh+vector |
| `import` | 从文件导入 | mesh+vector |
| `unknown` | 未知来源（手动建模） | mesh+vector |

## 性能对比

### 纯向量模式
- 文件大小：~1.5KB
- 导入速度：需要重建（慢）
- 适用场景：未修改的参数化对象

### Mesh+Vector模式
- 文件大小：20KB - 几MB（取决于复杂度）
- 导入速度：直接加载（快）
- 适用场景：手动编辑、复杂模型、合并对象

## 最佳实践

1. **参数化设计流程**：保持对象为纯向量，享受小文件、完美重建
2. **手动编辑后立即导出**：系统会自动应用修改器并切换到mesh+vector模式
3. **定期检查对象来源**：查看 `obj["geometry_vector_source"]`
4. **合并前考虑**：合并操作会触发mesh模式，文件会变大

## 重要注意事项

### ⚠️ 手动编辑后的向量参数

一旦对象被手动编辑（挤出顶点、合并对象等），导出时修改器会被**烘焙**到mesh中：

```
原始：基础mesh + 修改器（可调整）
  ↓ 手动编辑
烘焙：完整mesh（修改器效果固化）
```

**重要**：导入后，如果你再次点击"Decode & Render"：
- ✅ 会应用当前的向量参数
- ❌ **会丢失手动编辑的部分**（挤出的顶点等）

**推荐工作流**：
1. **先完成参数调整** → 使用向量编辑器调整参数
2. **再进行手动编辑** → 进入编辑模式细化模型
3. **导出保存** → 系统自动烘焙所有效果
4. **导入使用** → 不要再点击Decode & Render

如果需要继续调整向量参数，应该：
- 从原始纯向量对象开始
- 或者重新Decode & Render一个新对象
- 保持手动编辑和向量编辑分开

## 技术细节

### 属性存储

每个对象会携带以下自定义属性：

```python
obj["geom_vector_0"] ... obj["geom_vector_31"]  # 向量数据(32维)
obj["geometry_vector_source"]                    # 来源标记
obj["geometry_vector_version"]                   # 版本号
obj["geometry_vector_mesh_verts"]                # 原始顶点数
obj["geometry_vector_mesh_faces"]                # 原始面数
obj["geometry_vector_source_mesh"]               # 导入mesh名称（如有）
```

### 检测代码位置

- **Fingerprint保存**：`operators.py` 行2040-2044（`_create_geometry_from_vector`）
- **检测逻辑**：`operators.py` 行2309-2369（`MYADDON_OT_export_gvec.execute`）
- **导入判断**：`operators.py` 行2422-2465（`MYADDON_OT_import_gvec.execute`）

## 总结

这个系统通过四层检测机制，自动识别对象是否被手动修改，智能选择最合适的导出模式：
- ✅ 纯向量对象 → 纯向量模式（小文件）
- ✅ 手动编辑对象 → mesh+vector模式（完整数据）
- ✅ 合并对象 → 自动检测并保存完整mesh
- ✅ 复杂编辑（顶点组、形态键）→ 自动保护数据

**核心理念**：让用户放心使用，系统会自动做正确的事情！
