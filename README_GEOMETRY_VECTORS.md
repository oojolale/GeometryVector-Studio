# Blender几何体统一向量表示系统

## 🎯 核心创新

将**所有几何体**（立方体、螺旋、飞机、人物、楼梯等）统一表示为**32维潜在空间**中的向量，实现了类似于深度学习中的**Latent Space**概念。

```
任意几何体 → [32维向量] → 数学运算 → 新几何体
```

## 🌟 主要特性

### 1. 统一编码系统
- **32维向量空间**：所有几何体共享相同的表示
- **参数化编码**：形状类型、复杂度、尺度、对称性、拓扑、变形等
- **双向转换**：几何体 ↔ 向量

### 2. 向量空间操作
- **插值（Interpolation）**：平滑变形动画
- **混合（Blending）**：多几何体加权组合
- **相似度搜索**：查找最近邻
- **向量运算**：加法、减法、归一化

### 3. 支持的几何体类型
- ✅ 基础形状（立方体、球体、圆柱）
- ✅ 螺旋结构（走廊、DNA、弹簧）
- ✅ 复杂机械（战斗机、轰炸机、直升机）
- ✅ 建筑结构（直线楼梯、螺旋楼梯、L型楼梯）
- ✅ 人物模型（男/女、儿童/青少年/成人/老年）

## 📊 向量维度定义

| 索引 | 参数 | 说明 |
|------|------|------|
| 0 | Shape Type | 形状类型（连续编码） |
| 1 | Complexity | 几何复杂度 |
| 2-4 | Scale X/Y/Z | 三维尺度 |
| 5 | Symmetry | 对称性度量 |
| 6 | Curvature | 整体曲率 |
| 7 | Topology Genus | 拓扑孔洞数 |
| 8-10 | Aspect Ratios | 长宽比 |
| 11-14 | Deformations | 拉伸/扭曲/锥化/弯曲 |
| 15-18 | Wave & Noise | 波浪和噪声参数 |
| 19-21 | Shape Morphing | 球形度/立方度/圆柱度 |
| 22-31 | Reserved | 保留扩展维度 |

## 🚀 快速开始

### 安装
1. 将整个文件夹复制到Blender插件目录
2. 在Blender中启用插件"Simple Panel Demo"

### 基础使用

#### 1. 创建几何体
```
My Addon → Shape Transformer
→ 选择Preset（如Fighter Jet）
→ Update Shape
```

#### 2. 向量操作
```
My Addon → Geometry Vectors
→ 选择操作类型
```

### UI面板说明

**Shape Transformer面板**：
- Quick Presets：预设选择
- Basic Properties：基础属性
- 各类参数：螺旋、拓扑变换、波浪、噪声等
- Update Shape / Split Shape：生成和拆分

**Geometry Vectors面板**：
- Encode Current Geometry：编码当前几何体
- Interpolate Presets：两个预设之间插值
- Blend Multiple：混合多个预设
- Find Similar：相似度搜索
- Morph Animation：变形动画

## 💡 使用示例

### 示例1：创建混合飞机
```python
# 目标：60%战斗机 + 40%轰炸机
Geometry Vectors → Blend Multiple
  Preset 1: Fighter Jet (weight: 0.6)
  Preset 2: Bomber (weight: 0.4)
→ OK → Update Shape
```

结果：获得介于战斗机和轰炸机之间的新设计

### 示例2：形状变形动画
```python
# 目标：螺旋走廊→人物 (120帧动画)
Geometry Vectors → Interpolate Presets
  From: Spiral Corridor
  To: Character
  t: 0.0 → 1.0 (animate)
```

结果：120帧的平滑变形动画

### 示例3：探索几何空间
```python
# Blender Python Console
import sys
sys.path.insert(0, r"d:\Users\PC\PycharmProjects\blenderUI")

from geometry_encoder import *

# 编码所有预设
scene = bpy.context.scene
space = get_latent_space()

for preset in ["FIGHTER_JET", "BOMBER", "HELICOPTER"]:
    vec = GeometryEncoder.encode_preset(preset, scene)
    space.add_geometry(preset, vec)

# 查找邻居
vec_query = space.vectors["FIGHTER_JET"]
neighbors = space.get_neighbors(vec_query, k=3)
print(neighbors)
```

## 🧮 数学原理

### 距离度量
```python
distance = sqrt(Σ(v1[i] - v2[i])²)  # 欧几里得距离
```

### 线性插值
```python
lerp(v1, v2, t) = (1-t)*v1 + t*v2
```

### 加权混合
```python
blend = Σ(wi * vi) / Σwi  # 加权平均
```

## 📁 文件结构

```
blenderUI/
├── __init__.py                     # 插件入口
├── properties.py                   # 属性定义
├── operators.py                    # 操作符实现
├── panels.py                       # UI面板
├── ui_lists.py                     # UIList组件
├── handlers.py                     # 事件处理
├── geometry_encoder.py             # ⭐ 几何编码系统
├── demo_geometry_vectors.py        # 演示脚本
├── GEOMETRY_VECTORS_GUIDE.md       # 详细指南
└── README_GEOMETRY_VECTORS.md      # 本文档
```

## 🔬 技术细节

### 编码器架构
```
GeometryEncoder
├── encode_preset()        # 预设 → 向量
├── encode_object()        # Blender对象 → 向量
└── encode_scene_parameters()  # 场景参数 → 向量
```

### 解码器架构
```
GeometryDecoder
├── decode_to_scene()      # 向量 → 场景参数
└── find_nearest_preset()  # 向量 → 最近预设
```

### 潜在空间管理
```
GeometryLatentSpace
├── add_geometry()         # 添加向量
├── interpolate_path()     # 生成插值路径
├── blend_geometries()     # 混合多个向量
└── get_neighbors()        # K近邻搜索
```

## 🎨 应用场景

### 1. 游戏开发
- 程序化生成多样化资产
- 基于参数的资产库
- 运行时形状变形

### 2. 动画制作
- 平滑的形状变形动画
- 关键帧之间的自动插值
- 创意探索工具

### 3. 设计探索
- 参数空间导航
- 自动生成设计变体
- 相似设计检索

### 4. 研究与教学
- 几何拓扑学可视化
- 形状空间理论演示
- 计算几何实验

## 🔮 未来扩展

### 短期（已计划）
- [ ] 增强的插值方法（球面插值SLERP）
- [ ] 更多几何体类型（车辆、家具、植物）
- [ ] 实时预览系统

### 中期（研究中）
- [ ] 基于GAN的生成式模型
- [ ] 物理约束优化
- [ ] 多分辨率表示（LOD）

### 长期（愿景）
- [ ] 深度学习编码器
- [ ] 自动特征学习
- [ ] 跨模态转换（2D→3D）

## 📚 相关概念

### 深度学习类比
| 计算机视觉 | 本系统 |
|-----------|--------|
| 图像 | 几何体 |
| CNN Encoder | GeometryEncoder |
| Latent Vector (512D) | GeometryVector (32D) |
| CNN Decoder | GeometryDecoder |
| Image Interpolation | Geometry Morphing |
| StyleGAN | 本系统概念 |

### 理论基础
- 流形学习（Manifold Learning）
- 降维技术（Dimensionality Reduction）
- 向量空间嵌入（Vector Space Embedding）
- 表示学习（Representation Learning）

## 🛠️ 故障排除

### 问题：插值结果不理想
**原因**：向量维度权重不平衡
**解决**：调整特定维度的权重或使用非线性插值

### 问题：找不到相似几何体
**原因**：潜在空间未初始化
**解决**：先运行`Encode Current Geometry`

### 问题：混合结果异常
**原因**：权重设置不合理
**解决**：确保权重总和>0，归一化会自动处理

## 📖 文档索引

- **快速入门**：本文档
- **详细指南**：`GEOMETRY_VECTORS_GUIDE.md`
- **API文档**：`geometry_encoder.py`中的docstrings
- **演示脚本**：`demo_geometry_vectors.py`

## 🤝 贡献

欢迎贡献代码、报告问题或提出新想法！

关键改进方向：
1. 新的几何体类型编码
2. 改进的距离度量
3. 更好的插值算法
4. 可视化工具

## 📄 许可证

MIT License

## 👨‍💻 作者

Blender UI Plugin Team

## 🙏 致谢

灵感来源：
- StyleGAN（图像潜在空间）
- Word2Vec（词向量表示）
- VAE（变分自动编码器）
- 流形学习理论

---

**Happy Geometry Hacking! 🚀✨**
