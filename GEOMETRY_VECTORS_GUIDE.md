# Geometry Vectors - Unified Latent Space Representation

## 概述

这个系统将所有几何体（立方体、螺旋、飞机、人物等）统一表示为**32维向量空间**中的点，实现了类似于深度学习中**潜在空间（Latent Space）**的概念。

## 核心概念

### 1. 统一向量表示 (GeometryVector)

每个几何体被编码为一个32维向量：

```
Vector = [shape_type, complexity, scale_x, scale_y, scale_z, symmetry, 
          curvature, topology, aspect_ratios..., deformations..., ...]
```

**关键维度：**
- **0**: Shape Type (0-1连续编码)
- **1**: Complexity (几何复杂度)
- **2-4**: Scale (X, Y, Z缩放)
- **5**: Symmetry (对称性度量)
- **6**: Curvature (曲率)
- **7**: Topology Genus (拓扑孔洞数)
- **8-10**: Aspect Ratios (长宽比)
- **11-14**: Deformations (拉伸、扭曲、锥化、弯曲)
- **15-18**: Wave & Noise (波浪和噪声参数)
- **19-21**: Shape Morphing (球形度、立方度、圆柱度)

### 2. 编码器 (GeometryEncoder)

将几何体转换为向量：

```python
# 编码预设
vec = GeometryEncoder.encode_preset("FIGHTER_JET", scene)

# 编码Blender对象
vec = GeometryEncoder.encode_object(obj)

# 编码场景参数
vec = GeometryEncoder.encode_scene_parameters(scene)
```

### 3. 解码器 (GeometryDecoder)

将向量还原为几何参数：

```python
# 解码到场景参数
params = GeometryDecoder.decode_to_scene(vec, scene)

# 查找最近的预设
nearest = GeometryDecoder.find_nearest_preset(vec, scene)
```

### 4. 潜在空间操作 (GeometryLatentSpace)

在向量空间中进行数学运算：

```python
latent_space = get_latent_space()

# 插值路径
path = latent_space.interpolate_path("start", "end", steps=10)

# 混合多个几何体
blended = latent_space.blend_geometries(
    names=["JET", "BOMBER", "HELICOPTER"],
    weights=[0.5, 0.3, 0.2]
)

# 查找邻居
neighbors = latent_space.get_neighbors(vec, k=5)
```

## 使用场景

### 场景1：几何体插值（变形动画）

**目标**：从螺旋走廊平滑变形到战斗机

```python
# 在UI中：Geometry Vectors面板 → Interpolate Presets
# 设置：
#   Preset A: Spiral Corridor
#   Preset B: Fighter Jet
#   t = 0.0 → 1.0 (动画)
```

**原理**：
```
vec(t) = (1-t) * vec_spiral + t * vec_jet
```

在t=0.5时，得到一个"介于螺旋和飞机之间"的几何体。

### 场景2：几何体混合

**目标**：创建混合了战斗机、轰炸机和直升机特征的新飞机

```python
# 在UI中：Geometry Vectors面板 → Blend Multiple
# 设置：
#   Preset 1: Fighter Jet (weight: 0.5)
#   Preset 2: Bomber (weight: 0.3)
#   Preset 3: Helicopter (weight: 0.2)
```

**原理**：
```
vec_blend = 0.5*vec_jet + 0.3*vec_bomber + 0.2*vec_heli
           ────────────────────────────────────────────
                         总权重 = 1.0
```

### 场景3：相似度搜索

**目标**：找到与当前几何体最相似的预设

```python
# 在UI中：Geometry Vectors面板 → Find Similar
# 返回：5个最近邻居及其距离
```

**距离计算**：
```
distance = ||vec_current - vec_preset||₂ (欧几里得距离)
```

### 场景4：向量运算

**目标**：几何体的"向量代数"

```python
# 概念类比（类似Word2Vec）：
# "King - Man + Woman = Queen"
# 
# 几何体例子：
# "Fighter - Wings + Rotor = Helicopter"

vec_fighter = encode("FIGHTER_JET")
vec_wings = encode_component("wings")
vec_rotor = encode_component("rotor")

vec_result = vec_fighter - vec_wings + vec_rotor
# 解码后接近直升机
```

## 数学原理

### 向量空间性质

1. **距离度量**：欧几里得距离
   ```
   d(v₁, v₂) = √Σᵢ(v₁ᵢ - v₂ᵢ)²
   ```

2. **线性插值**：LERP
   ```
   lerp(v₁, v₂, t) = (1-t)v₁ + tv₂
   ```

3. **加权平均**：凸组合
   ```
   blend(v₁...vₙ, w₁...wₙ) = Σᵢ(wᵢvᵢ) / Σᵢwᵢ
   ```

4. **归一化**：单位向量
   ```
   normalize(v) = v / ||v||
   ```

### 高维投影概念

```
原始几何体 ──encode──→ 32维向量 ──操作──→ 新向量 ──decode──→ 新几何体
    (3D空间)           (潜在空间)          (参数空间)       (3D空间)

例如：
立方体 → [0, 0.1, 2, 2, 2, 1, 0, 0, ...] → 向量运算 → [...] → 新形状
```

## 实际应用示例

### 示例1：创建"混合飞机"

1. 打开Blender
2. 进入"My Addon" → "Geometry Vectors"面板
3. 点击"Blend Multiple"
4. 设置：
   - Fighter Jet: weight 0.6
   - Bomber: weight 0.4
5. 点击OK
6. 点击"Update Shape"

结果：获得一个介于战斗机和轰炸机之间的飞机模型

### 示例2：形状变形动画

1. 点击"Morph Animation"
2. 设置：
   - Start: Spiral Corridor
   - End: Character
   - Frames: 120
3. 点击OK

结果：创建一个120帧的动画，螺旋走廊逐渐变形为人物

### 示例3：探索几何空间

```python
# Python控制台
from geometry_encoder import *

# 编码所有预设
presets = ["SPIRAL_CORRIDOR", "FIGHTER_JET", "CHARACTER", ...]
latent_space = get_latent_space()

for preset in presets:
    vec = GeometryEncoder.encode_preset(preset, bpy.context.scene)
    latent_space.add_geometry(preset, vec)

# 可视化距离矩阵
import numpy as np
names = list(latent_space.vectors.keys())
distances = np.zeros((len(names), len(names)))

for i, name1 in enumerate(names):
    for j, name2 in enumerate(names):
        vec1 = latent_space.vectors[name1]
        vec2 = latent_space.vectors[name2]
        distances[i,j] = vec1.distance_to(vec2)

print(distances)
```

## 技术对比

### 类比：图像的潜在空间

| 概念 | 图像领域 | 几何体领域 |
|------|---------|-----------|
| 原始数据 | 像素矩阵 (HxWxC) | 顶点/面/修改器 |
| 编码器 | CNN Encoder | GeometryEncoder |
| 潜在向量 | 512D/1024D | 32D |
| 解码器 | CNN Decoder | GeometryDecoder |
| 插值 | 图像变形 | 几何体变形 |
| 应用 | StyleGAN, VAE | 本系统 |

### 与传统参数化的区别

**传统方法**：
```python
# 每个预设有不同的参数
fighter_jet(fuselage_length=12, wing_span=10, ...)
staircase(steps=10, width=2, ...)
character(height=1.75, gender="male", ...)
# → 参数不兼容，无法插值
```

**向量方法**：
```python
# 所有几何体共享统一的32维表示
vec_jet = [0.5, 0.75, 12, 10, 3, ...]
vec_stair = [0.7, 0.4, 2, 3, 2, ...]
vec_char = [0.8, 0.9, 0.6, 0.4, 1.75, ...]
# → 可以插值、混合、计算距离
vec_hybrid = 0.5*vec_jet + 0.5*vec_stair  # 有意义！
```

## 未来扩展

1. **学习型编码器**：使用神经网络学习更好的编码
2. **非线性插值**：球面插值（SLERP）、样条插值
3. **约束优化**：在潜在空间中优化特定目标
4. **聚类分析**：自动发现几何体类别
5. **降维可视化**：t-SNE/UMAP可视化32D空间

## API参考

### GeometryVector类

```python
vec = GeometryVector()  # 创建零向量
vec = GeometryVector(np.array([...]))  # 从数组创建

# 方法
vec.to_dict()  # 转换为字典
vec.distance_to(other)  # 计算距离
vec.interpolate(other, t)  # 插值
vec.add(other, weight)  # 加权加法
vec.normalize()  # 归一化
```

### GeometryEncoder类

```python
GeometryEncoder.encode_preset(name, scene)
GeometryEncoder.encode_object(obj)
GeometryEncoder.encode_scene_parameters(scene)
```

### GeometryDecoder类

```python
GeometryDecoder.decode_to_scene(vec, scene)
GeometryDecoder.find_nearest_preset(vec, scene)
```

### GeometryLatentSpace类

```python
space = get_latent_space()
space.add_geometry(name, vec)
space.interpolate_path(start, end, steps)
space.blend_geometries(names, weights)
space.get_neighbors(vec, k)
```

## 总结

这个系统实现了：
- ✅ 统一的几何表示（32维向量）
- ✅ 编码/解码机制
- ✅ 向量空间操作（插值、混合、距离）
- ✅ 直观的UI界面
- ✅ 数学严谨性（线性代数基础）

通过这种方式，所有的几何体都被"投射"到同一个高维空间中，可以进行各种数学运算，就像处理向量一样！
