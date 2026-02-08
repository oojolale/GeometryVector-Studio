# .gvec 法线处理说明

## 问题说明

在导入 `.gvec` 文件时，可能遇到错误：
```
bpy_struct: attribute "normal" from "MeshVertex" is read-only
```

## 原因

在Blender中，**顶点法线（vertex normals）是只读属性**，不能直接赋值。法线通常由Blender根据面的几何形状自动计算。

## 解决方案

### 当前实现（推荐）

```python
mesh.from_pydata(vertices, edges, faces)
mesh.update()
# Blender会自动计算法线，对于大多数情况已足够
```

**优点**：
- ✅ 简单可靠
- ✅ 法线基于几何自动计算，保证正确
- ✅ 适用于99%的使用场景

### 如需自定义法线（高级）

如果确实需要保存和恢复自定义法线：

```python
# 导出时 - 获取循环法线（loop normals）
mesh.calc_normals_split()
loop_normals = []
for loop in mesh.loops:
    loop_normals.append(list(loop.normal))

# 导入时 - 设置自定义法线
import mathutils
mesh.use_auto_smooth = True
mesh.create_normals_split()

# 为每个循环设置法线
custom_normals = [mathutils.Vector(n) for n in loop_normals]
mesh.normals_split_custom_set(custom_normals)

mesh.update()
```

## 当前版本行为

### 导出（序列化）
- ✅ 保存顶点法线到JSON（用于调试/可视化）
- ⚠️ 这些法线不会在导入时应用

### 导入（反序列化）
- ✅ 从顶点和面重建网格
- ✅ Blender自动计算法线
- ✅ 法线通常与原始一致（基于相同几何）

## 何时需要自定义法线

自定义法线主要用于：
- 🎨 硬表面建模（Hard Surface）
- 🔧 游戏资产（优化着色）
- 🎬 特殊视觉效果

对于大多数用途，**自动法线已足够**。

## 测试对比

```python
# 原始对象
original_mesh.calc_normals_split()
original_normals = [v.normal for v in original_mesh.vertices]

# 导入后对象
imported_mesh.calc_normals_split()
imported_normals = [v.normal for v in imported_mesh.vertices]

# 比较（通常差异很小）
import numpy as np
diff = np.array(original_normals) - np.array(imported_normals)
max_diff = np.max(np.abs(diff))
print(f"Max normal difference: {max_diff:.6f}")
# 通常 < 0.001 (可忽略)
```

## 未来增强（可选）

如果需要完整的自定义法线支持，可在 Phase 2 中添加：

### 文件格式扩展
```json
{
  "mesh": {
    "vertices": [...],
    "faces": [...],
    "loop_normals": [[nx, ny, nz], ...],  // 新增
    "has_custom_normals": true             // 新增
  }
}
```

### 代码修改
```python
# geometry_file_format.py
if mesh_data.get("has_custom_normals"):
    # 应用自定义法线
    apply_custom_normals(mesh, mesh_data["loop_normals"])
else:
    # 使用自动法线（当前行为）
    pass
```

## 推荐

对于 v1.0：
- ✅ **保持当前实现**（自动法线）
- ✅ 简单可靠，满足绝大多数需求
- ✅ 如有特殊需求，用户可手动调整法线

对于 v2.0：
- 考虑添加自定义法线支持（可选功能）

---

**结论**：当前实现已修复，法线由Blender自动计算，无需手动设置。
