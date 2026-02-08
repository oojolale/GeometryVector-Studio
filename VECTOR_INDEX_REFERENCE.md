# GeometryVector 索引参考

## 向量维度定义

`GeometryVector` 类定义了32维向量空间，每个维度对应特定的几何参数。

### 完整索引列表

```python
# geometry_encoder.py - GeometryVector类

VECTOR_DIM = 32  # 总维度

# 索引常量
IDX_SHAPE_TYPE = 0          # 形状类型（连续编码）
IDX_COMPLEXITY = 1          # 几何复杂度度量
IDX_SCALE_X = 2             # X轴缩放
IDX_SCALE_Y = 3             # Y轴缩放
IDX_SCALE_Z = 4             # Z轴缩放
IDX_SYMMETRY = 5            # 对称性度量
IDX_CURVATURE = 6           # 整体曲率
IDX_TOPOLOGY_GENUS = 7      # 拓扑亏格（孔的数量）
IDX_ASPECT_RATIO_XY = 8     # XY平面比例
IDX_ASPECT_RATIO_XZ = 9     # XZ平面比例
IDX_ASPECT_RATIO_YZ = 10    # YZ平面比例
IDX_ELONGATION = 11         # 拉伸因子
IDX_TWIST = 12              # 扭曲量
IDX_TAPER = 13              # 锥化因子
IDX_BEND = 14               # 弯曲
IDX_WAVE_FREQ = 15          # 波浪频率
IDX_WAVE_AMP = 16           # 波浪幅度
IDX_NOISE_SCALE = 17        # 噪声缩放
IDX_NOISE_STRENGTH = 18     # 噪声强度
IDX_SPHERICITY = 19         # 球形化（形状变形）
IDX_CUBICITY = 20           # 立方化
IDX_CYLINDRICITY = 21       # 圆柱化
IDX_ROT_X = 22              # X轴旋转（弧度）
IDX_ROT_Y = 23              # Y轴旋转（弧度）
IDX_ROT_Z = 24              # Z轴旋转（弧度）
IDX_LOC_X = 25              # X轴位置
IDX_LOC_Y = 26              # Y轴位置
IDX_LOC_Z = 27              # Z轴位置
IDX_SMOOTHNESS = 28         # 平滑度（细分级别）
IDX_EDGE_SHARPNESS = 29     # 边缘锐化程度
IDX_INFLATION = 30          # 膨胀/收缩（沿法线）
IDX_RANDOMNESS = 31         # 随机表面扰动
```

## 向量参数分组

### Group 1: Shape & Topology [0-7]
- **[0] IDX_SHAPE_TYPE**: 形状类型编码
- **[1] IDX_COMPLEXITY**: 顶点数量、面数等复杂度
- **[2-4] IDX_SCALE_X/Y/Z**: 对象缩放系数（obj.scale，不是dimensions）
- **[5] IDX_SYMMETRY**: 对称性分析
- **[6] IDX_CURVATURE**: 曲率（影响细分级别）
- **[7] IDX_TOPOLOGY_GENUS**: 拓扑特征

### Group 2: Aspect & Deformation [8-14]
- **[8-10] IDX_ASPECT_RATIO_XY/XZ/YZ**: 各轴比例关系
- **[11] IDX_ELONGATION**: 拉伸程度
- **[12] IDX_TWIST**: 扭曲角度（单位：2π倍数）
- **[13] IDX_TAPER**: 锥化系数
- **[14] IDX_BEND**: 弯曲角度（单位：2π倍数）

### Group 3: Wave & Noise [15-18]
- **[15] IDX_WAVE_FREQ**: 波浪频率参数
- **[16] IDX_WAVE_AMP**: 波浪幅度
- **[17] IDX_NOISE_SCALE**: 噪声纹理缩放
- **[18] IDX_NOISE_STRENGTH**: 噪声位移强度

### Group 4: Shape Morphing [19-21]
- **[19] IDX_SPHERICITY**: 向球体变形程度 (0-1)
- **[20] IDX_CUBICITY**: 向立方体变形程度 (0-1)
- **[21] IDX_CYLINDRICITY**: 向圆柱体变形程度 (0-1)

### Group 5: Rotation [22-24]
- **[22] IDX_ROT_X**: X轴旋转角度（弧度）
- **[23] IDX_ROT_Y**: Y轴旋转角度（弧度）
- **[24] IDX_ROT_Z**: Z轴旋转角度（弧度）

### Group 6: Location [25-27]
- **[25] IDX_LOC_X**: X轴位置（世界坐标）
- **[26] IDX_LOC_Y**: Y轴位置（世界坐标）
- **[27] IDX_LOC_Z**: Z轴位置（世界坐标）

### Group 7: Universal Appearance [28-31] ⭐新增
**这些参数拓扑无关，同时适用于Preset和Import模式**

- **[28] IDX_SMOOTHNESS**: 平滑度 (0-1)
  - 控制细分曲面级别
  - 0 = 无细分，1 = 最高细分（3级）
  - 实现：Subdivision Surface修改器
  
- **[29] IDX_EDGE_SHARPNESS**: 边缘锐化 (0-1)
  - 控制边缘的清晰程度
  - 0 = 完全平滑，1 = 完全锐利
  - 实现：Edge Split修改器
  
- **[30] IDX_INFLATION**: 膨胀/收缩 (-1 到 1)
  - 沿法线方向位移所有顶点
  - 负值 = 收缩，正值 = 膨胀
  - 实现：Displace修改器（NORMAL方向）
  
- **[31] IDX_RANDOMNESS**: 随机扰动 (0-1)
  - 添加微小的随机位移
  - 打破完美对称性
  - 实现：Displace修改器 + Clouds纹理

## 使用注意事项

### ⚠️ 常见错误

1. **错误的索引名称**
   ```python
   # ❌ 错误 - 不存在的索引
   shear = vec.vector[GeometryVector.IDX_SHEAR]
   wave = vec.vector[GeometryVector.IDX_WAVE_AMPLITUDE]
   
   # ✅ 正确
   elongation = vec.vector[GeometryVector.IDX_ELONGATION]
   wave = vec.vector[GeometryVector.IDX_WAVE_AMP]
   ```

2. **索引名称不一致**
   - 使用 `IDX_WAVE_AMP` 而不是 `IDX_WAVE_AMPLITUDE`
   - 使用 `IDX_WAVE_FREQ` 而不是 `IDX_WAVE_FREQUENCY`
   - 没有 `IDX_SHEAR`，应使用 `IDX_ELONGATION` 或其他变形参数

3. **⚠️ Scale vs Dimensions 重要区别**
   - `IDX_SCALE_X/Y/Z` 存储的是 **obj.scale**（缩放系数），而不是 **obj.dimensions**（最终尺寸）
   - 对于从文件导入的对象，这样可以正确保存原始缩放值
   - 例如：如果原对象 scale=(1.0, 1.0, 1.0)，解码后也会是 scale=(1.0, 1.0, 1.0)
   - 如果错误地存储dimensions，会导致双重缩放问题

### ✅ 正确用法示例

```python
from geometry_encoder import GeometryVector

# 创建向量
vec = GeometryVector()

# 设置缩放
vec.vector[GeometryVector.IDX_SCALE_X] = 2.0
vec.vector[GeometryVector.IDX_SCALE_Y] = 1.5
vec.vector[GeometryVector.IDX_SCALE_Z] = 3.0

# 设置变形
vec.vector[GeometryVector.IDX_TWIST] = 0.5  # 扭曲半圈
vec.vector[GeometryVector.IDX_TAPER] = 0.3  # 锥化
vec.vector[GeometryVector.IDX_SPHERICITY] = 0.4  # 40%球形化

# 设置波浪
vec.vector[GeometryVector.IDX_WAVE_AMP] = 0.2
vec.vector[GeometryVector.IDX_WAVE_FREQ] = 1.5

# 读取参数
scale_x = vec.vector[GeometryVector.IDX_SCALE_X]
twist = vec.vector[GeometryVector.IDX_TWIST]
```

## 修改器映射关系

在解码渲染时，向量参数映射到Blender修改器：

| 向量参数 | Blender修改器 | 修改器属性 |
|---------|--------------|-----------|
| IDX_SPHERICITY | Cast Modifier | factor, cast_type='SPHERE' |
| IDX_TAPER | Simple Deform | deform_method='TAPER' |
| IDX_TWIST | Simple Deform | deform_method='TWIST', angle |
| IDX_BEND | Simple Deform | deform_method='BEND', angle |
| IDX_ELONGATION | Simple Deform | deform_method='STRETCH' |
| IDX_WAVE_AMP | Wave Modifier | height |
| IDX_WAVE_FREQ | Wave Modifier | width |
| IDX_NOISE_STRENGTH | Displace Modifier | strength |
| IDX_NOISE_SCALE | Texture (Clouds) | noise_scale |
| IDX_CURVATURE | Subdivision Surface | levels |

## 编码器提取的参数

`GeometryEncoder.encode_object()` 从Blender对象提取以下参数：

```python
# 基础测量
dimensions → [IDX_SCALE_X, IDX_SCALE_Y, IDX_SCALE_Z]
vertex_count → IDX_COMPLEXITY
aspect_ratios → [IDX_ASPECT_RATIO_XY, IDX_ASPECT_RATIO_XZ, IDX_ASPECT_RATIO_YZ]
max_dim / sum(dims) → IDX_ELONGATION

# 修改器分析
SUBSURF → IDX_CURVATURE
CAST → IDX_SPHERICITY
SIMPLE_DEFORM (TAPER) → IDX_TAPER
SIMPLE_DEFORM (TWIST) → IDX_TWIST
SIMPLE_DEFORM (BEND) → IDX_BEND
WAVE → IDX_WAVE_AMP, IDX_WAVE_FREQ
DISPLACE → IDX_NOISE_STRENGTH, IDX_NOISE_SCALE
```

## 解码器生成的几何体

`_create_geometry_from_vector()` 使用向量参数生成几何体：

```python
# 1. 创建基础立方体（细分2次）
bmesh.ops.create_cube()
bmesh.ops.subdivide_edges(cuts=2)

# 2. 应用缩放
obj.scale = (scale_x, scale_y, scale_z)

# 3. 添加修改器（按顺序）
if sphericity > 0.01: 添加 Cast Modifier
if taper > 0.01: 添加 Simple Deform (Taper)
if twist > 0.01: 添加 Simple Deform (Twist)
if bend > 0.01: 添加 Simple Deform (Bend)
if elongation != 0.33: 添加 Simple Deform (Stretch)
if wave_amp > 0.01: 添加 Wave Modifier
if noise_strength > 0.01: 添加 Displace Modifier
if curvature > 0.1: 添加 Subdivision Surface
```

## 值域范围

| 参数 | 典型范围 | 单位 | 说明 |
|-----|---------|------|------|
| SCALE_X/Y/Z | 0.1 - 10.0 | 米 | 绝对尺寸 |
| COMPLEXITY | 0.0 - 1.0 | 归一化 | 0=简单, 1=复杂 |
| SPHERICITY | 0.0 - 1.0 | 比例 | 0=无变形, 1=完全球形 |
| TWIST | -1.0 - 1.0 | 2π倍数 | ±1 = ±360° |
| BEND | -1.0 - 1.0 | 2π倍数 | ±1 = ±360° |
| TAPER | -1.0 - 1.0 | 系数 | 负值=倒锥 |
| ELONGATION | 0.1 - 0.8 | 比例 | 0.33=均匀 |
| WAVE_AMP | 0.0 - 2.0 | 米 | 波浪高度 |
| WAVE_FREQ | 0.1 - 5.0 | 周期 | 波浪密度 |
| NOISE_STRENGTH | 0.0 - 2.0 | 米 | 位移强度 |
| CURVATURE | 0.0 - 1.0 | 级别 | 影响细分数 |

## 更新历史

- **2024-02**: 初始32维向量空间定义
- **2024-02**: 修复 `IDX_SHEAR` 错误，使用 `IDX_ELONGATION` 替代
- **2024-02**: 统一波浪参数命名为 `IDX_WAVE_AMP` 和 `IDX_WAVE_FREQ`
