# .gvec 格式快速参考

## 文件扩展名

- `.gvec` - 单个对象（向量 ± 网格）
- `.gvec_batch` - 多个对象批量文件

---

## Blender UI操作

### 导出
```
选择对象 → Vector Editor → Export .gvec
- Include Mesh Data: ✅ = 向量+网格  ❌ = 仅向量
```

### 导入
```
Vector Editor → Import .gvec → 选择文件
```

### 批量操作
```
选择多个对象 → Export Batch → 保存 .gvec_batch
Import Batch → 选择 .gvec_batch 文件
```

---

## Python API

### 导出
```python
from geometry_file_format import GeometryFileFormat
from geometry_encoder import GeometryEncoder

encoder = GeometryEncoder()
vec = encoder.encode(obj)

GeometryFileFormat.export_to_file(
    "output.gvec",
    vec,
    obj,  # None = 仅向量
    metadata
)
```

### 导入
```python
vec, data = GeometryFileFormat.import_from_file("input.gvec")
obj = GeometryFileFormat.restore_object_from_file("input.gvec", context)
```

### 批量
```python
from geometry_file_format import GeometryBatchExporter

# 导出
GeometryBatchExporter.export_batch("batch.gvec_batch", objects)

# 导入
objs = GeometryBatchExporter.import_batch("batch.gvec_batch", context)
```

---

## JSON结构

```json
{
  "version": "1.0",
  "type": "geometry_vector",
  "vector": [32 floats],           // 必需
  "metadata": {"name": "..."},     // 必需
  "mesh": {...},                   // 可选
  "materials": {...}               // 可选
}
```

---

## 向量索引速查

| 索引 | 参数 | 范围 |
|------|------|------|
| 0-1 | 形状类型/复杂度 | [0, 1] |
| 2-4 | 缩放 X/Y/Z | > 0 |
| 22-24 | 旋转 X/Y/Z | 弧度 |
| 25-27 | 位置 X/Y/Z | 任意 |
| 28 | 平滑度 | [0, 1] |
| 29 | 边缘锐化 | [0, 1] |
| 30 | 膨胀/收缩 | [-1, 1] |
| 31 | 随机扰动 | [0, 1] |

---

## 使用模式

### 模式1：纯向量（Preset）
- ❌ 不包含网格数据
- ✅ 文件小（1-2 KB）
- ✅ 参数化重建
- ⚠️ 仅适用于简单几何体

### 模式2：混合（Import）
- ✅ 包含完整网格
- ❌ 文件较大（10-500 KB）
- ✅ 精确还原
- ✅ 适用于复杂模型

---

## 常见操作

### 修改向量值
```python
vec.vector[2] = 2.0  # 设置 X 缩放
vec.vector[22] = math.radians(45)  # 旋转 45°
```

### 检查文件
```python
import json
data = json.load(open("file.gvec"))
print(data["metadata"]["source"])  # "preset" 或 "import"
has_mesh = "mesh" in data
```

### 向量插值
```python
morph = vec1.vector * 0.7 + vec2.vector * 0.3
```

---

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 导入失败 | JSON格式错误 | 验证JSON |
| 网格丢失 | 导出时未包含 | 勾选 Include Mesh |
| 形状不对 | 向量值异常 | 使用 Normalize |

---

## 文件大小估算

- **仅向量**：~1-2 KB
- **简单网格**（<1000顶点）：10-50 KB
- **复杂网格**（>5000顶点）：100-500 KB
- **批量文件**：单对象大小 × 数量

---

## 相关命令

### Blender Operators
- `myaddon.export_gvec` - 导出单个
- `myaddon.import_gvec` - 导入单个
- `myaddon.export_gvec_batch` - 批量导出
- `myaddon.import_gvec_batch` - 批量导入

---

**完整文档**: `GVEC_FILE_FORMAT_GUIDE.md`
