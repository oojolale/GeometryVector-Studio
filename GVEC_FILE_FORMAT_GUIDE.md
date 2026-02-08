# .gvec 文件格式使用指南

## 概述

`.gvec` 是一个自定义的JSON格式文件，用于存储3D几何对象的向量表示和网格数据，无需依赖Blender的`.blend`文件格式。

### 特点

✅ **纯向量模式**：仅保存32维向量，适合参数化生成的对象  
✅ **混合模式**：同时保存向量+完整网格数据，适合导入的复杂对象  
✅ **跨平台**：JSON格式，可在任何支持的应用中读取  
✅ **轻量级**：比`.blend`文件更小  
✅ **版本化**：支持向后兼容  

---

## 文件格式规范

### 基本结构

```json
{
  "version": "1.0",
  "type": "geometry_vector",
  "vector": [32 float values],
  "metadata": {
    "name": "object_name",
    "created": "timestamp",
    "source": "preset" | "import"
  },
  "mesh": {  // Optional - only for imported objects
    "vertices": [[x, y, z], ...],
    "edges": [[v1, v2], ...],
    "faces": [[v1, v2, v3, ...], ...],
    "normals": [[nx, ny, nz], ...],
    "uv_coords": [[u, v], ...]
  },
  "materials": {  // Optional
    "name": "material_name",
    "diffuse_color": [r, g, b, a],
    "metallic": 0.0,
    "roughness": 0.5
  }
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `version` | string | ✅ | 文件格式版本号 |
| `type` | string | ✅ | 固定为 "geometry_vector" |
| `vector` | array[32] | ✅ | 32维几何向量 |
| `metadata` | object | ✅ | 元数据信息 |
| `mesh` | object | ❌ | 网格几何数据（可选） |
| `materials` | object | ❌ | 材质信息（可选） |

---

## 使用场景

### 场景1：纯向量模式（Preset对象）

**适用于**：参数化生成的简单几何体（立方体、球体、圆柱等）

**操作流程**：
1. 选择由Preset生成的对象
2. 点击 **Export .gvec**
3. 取消勾选 "Include Mesh Data"
4. 保存文件

**文件大小**：约 1-2 KB

**还原方式**：
- 导入时自动识别为Preset模式
- 使用参数化方法重新生成几何体
- 应用向量中的所有变换和修改器

---

### 场景2：混合模式（Import对象）

**适用于**：从外部文件导入的复杂网格

**操作流程**：
1. 选择导入的复杂对象
2. 点击 **Export .gvec**
3. 保持勾选 "Include Mesh Data"
4. 保存文件

**文件大小**：取决于网格复杂度（通常10-500 KB）

**还原方式**：
- 导入时直接还原原始网格
- 应用向量中的基础变换（位置、旋转、缩放）
- 应用拓扑无关的通用参数（平滑度、锐化等）

---

## Blender操作指南

### 导出单个对象

1. **选择对象**：在3D视口中选择要导出的网格对象
2. **打开向量编辑器**：在侧边栏找到"Vector Editor"面板
3. **点击导出按钮**：
   - **Export .gvec**：导出当前选中的对象
4. **配置选项**：
   - **Include Mesh Data**：勾选则保存完整网格，取消则仅保存向量
5. **选择文件路径**：保存为 `.gvec` 文件

### 导入单个对象

1. **打开向量编辑器**
2. **点击导入按钮**：
   - **Import .gvec**：导入单个对象
3. **选择文件**：浏览并选择 `.gvec` 文件
4. **确认导入**：对象将自动添加到场景中

### 批量导出

1. **选择多个对象**：按住 Shift 多选网格对象
2. **点击批量导出**：
   - **Export Batch**：导出所有选中对象
3. **保存为**：`.gvec_batch` 文件

### 批量导入

1. **点击批量导入**：
   - **Import Batch**：导入多个对象
2. **选择批量文件**：浏览并选择 `.gvec_batch` 文件
3. **确认导入**：所有对象将保持原始位置和变换

---

## 向量索引参考

### 向量维度分配（32维）

| 索引范围 | 参数类型 | 说明 |
|---------|---------|------|
| 0-1 | 形状类型 | Shape Type, Complexity |
| 2-4 | 全局缩放 | Scale X/Y/Z |
| 5-10 | 拓扑特征 | Symmetry, Curvature, Genus, Aspect Ratios |
| 11-14 | 变形参数 | Elongation, Twist, Taper, Bend |
| 15-18 | 波浪/噪声 | Wave Freq/Amp, Noise Scale/Strength |
| 19-21 | 形态融合 | Sphericity, Cubicity, Cylindricity |
| 22-24 | 旋转角度 | Rotation X/Y/Z (弧度) |
| 25-27 | 位置坐标 | Location X/Y/Z |
| 28-31 | 通用参数 | Smoothness, Edge Sharpness, Inflation, Randomness |

---

## 代码示例

### Python API 使用

```python
from geometry_file_format import GeometryFileFormat
from geometry_encoder import GeometryEncoder

# 导出对象
obj = bpy.context.active_object
encoder = GeometryEncoder()
geom_vec = encoder.encode(obj)

metadata = {"name": obj.name, "source": "custom"}
GeometryFileFormat.export_to_file(
    "my_geometry.gvec",
    geom_vec,
    obj,  # 包含网格数据
    metadata
)

# 导入对象
geom_vec, data = GeometryFileFormat.import_from_file("my_geometry.gvec")
restored_obj = GeometryFileFormat.restore_object_from_file(
    "my_geometry.gvec",
    bpy.context
)
```

### 直接读取JSON（其他应用）

```python
import json
import numpy as np

# 读取文件
with open("my_geometry.gvec", 'r') as f:
    data = json.load(f)

# 提取向量
vector = np.array(data["vector"], dtype=np.float32)
print(f"Vector shape: {vector.shape}")  # (32,)

# 提取网格数据
if "mesh" in data:
    vertices = data["mesh"]["vertices"]
    faces = data["mesh"]["faces"]
    print(f"Vertices: {len(vertices)}, Faces: {len(faces)}")
```

---

## 优势对比

### vs Blender .blend 文件

| 特性 | .gvec | .blend |
|------|-------|--------|
| 文件大小 | ✅ 小（1-500KB） | ❌ 大（5-50MB） |
| 可读性 | ✅ JSON文本 | ❌ 二进制 |
| 跨平台 | ✅ 通用格式 | ❌ Blender专有 |
| 向量编辑 | ✅ 直接修改 | ❌ 需要插件 |
| 完整场景 | ❌ 仅单对象 | ✅ 完整场景 |

### vs OBJ/FBX 文件

| 特性 | .gvec | OBJ/FBX |
|------|-------|---------|
| 向量数据 | ✅ 包含 | ❌ 无 |
| 参数化 | ✅ 支持 | ❌ 静态网格 |
| 文件大小 | ✅ 更小 | ❌ 较大 |
| 动画支持 | ❌ 无 | ✅ 有（FBX） |

---

## 注意事项

⚠️ **版本兼容性**
- 当前版本：1.0
- 未来版本会保持向后兼容
- 导入旧版本文件时会显示警告

⚠️ **网格精度**
- 顶点坐标保留6位小数
- 法线向量归一化
- UV坐标范围 [0, 1]

⚠️ **材质限制**
- 仅保存第一个材质
- 仅支持基础PBR参数（颜色、金属度、粗糙度）
- 不保存纹理贴图

⚠️ **文件命名**
- 建议使用小写字母和下划线
- 避免特殊字符
- 扩展名自动添加

---

## 故障排查

### 导入失败

**问题**：文件无法导入  
**原因**：JSON格式错误或版本不兼容  
**解决**：
1. 使用JSON验证工具检查文件
2. 查看Blender控制台错误信息
3. 确认文件扩展名正确

### 网格丢失

**问题**：导入后只有变换没有网格  
**原因**：导出时未包含网格数据  
**解决**：
1. 重新导出时勾选 "Include Mesh Data"
2. 或者将对象设置为Preset模式

### 向量不匹配

**问题**：解码后形状不正确  
**原因**：向量值超出有效范围  
**解决**：
1. 使用 "Normalize" 功能归一化向量
2. 检查索引22-31的值是否合理

---

## 扩展应用

### 机器学习训练数据

`.gvec` 格式非常适合作为几何生成模型的训练数据：

```python
# 批量导出训练集
for obj in training_objects:
    encoder.encode(obj)
    GeometryFileFormat.export_to_file(f"train/{obj.name}.gvec", vec, obj)

# 加载数据集
import glob
vectors = []
for file in glob.glob("train/*.gvec"):
    vec, _ = GeometryFileFormat.import_from_file(file)
    vectors.append(vec.vector)

X = np.array(vectors)  # Shape: (N, 32)
```

### 程序化生成管线

```python
# 随机生成向量
random_vec = GeometryVector(np.random.randn(32) * 0.5)
GeometryFileFormat.export_to_file("random.gvec", random_vec, None)

# 批量生成
for i in range(100):
    vec = generate_random_vector()
    GeometryFileFormat.export_to_file(f"generated_{i}.gvec", vec)
```

---

## 更新日志

### Version 1.0 (2026-02-08)
- ✅ 初始版本发布
- ✅ 支持向量和网格混合存储
- ✅ 支持批量导入导出
- ✅ 支持基础材质保存

---

## 相关文档

- [向量系统设计](VECTOR_SYSTEM_DESIGN.md)
- [向量索引参考](VECTOR_INDEX_REFERENCE.md)
- [网格缓存系统](MESH_CACHE_SYSTEM.md)
- [向量编辑器指南](VECTOR_EDITOR_GUIDE.md)

---

**技术支持**：如有问题请参考故障排查章节或查看控制台日志
