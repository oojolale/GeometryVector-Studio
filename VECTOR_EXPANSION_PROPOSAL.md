# 向量参数扩展方案

## 目标

在当前32维向量空间中，添加更多**拓扑无关**的参数，使其能够：
1. 同时应用于 Preset 模式和 Import 模式
2. 不依赖具体的网格拓扑结构
3. 通过 Blender 修改器实现
4. 保持数学上的可运算性（加减乘除、插值）

## 当前状态分析

### 已使用的维度 [0-27]

| 索引 | 参数 | Preset | Import | 实现方式 |
|------|------|--------|--------|----------|
| 0-1  | 形状类型/复杂度 | ✅ | ⚠️ 只读 | 统计 |
| 2-4  | Scale | ✅ | ✅ | 变换 |
| 5-7  | 对称性/曲率/拓扑 | ✅ | ⚠️ 只读 | 统计 |
| 8-11 | 比例/拉伸 | ✅ | ⚠️ 只读 | 统计 |
| 12-14| 扭曲/锥化/弯曲 | ✅ | ❌ | Simple Deform |
| 15-18| 波浪/噪声 | ✅ | ❌ | Wave/Displace |
| 19-21| 形状变形 | ✅ | ❌ | Cast |
| 22-27| 旋转/位置 | ✅ | ✅ | 变换 |

### 问题

索引 12-21（变形参数）在 Import 模式中**被禁用**，因为会破坏原始形状。

### 可用空间

- **索引 28-31**：4个维度完全空闲
- **可选**：扩展到64维或128维（需要重大重构）

## 扩展方案：拓扑无关的通用参数

### 方案 A：材质与外观参数 [28-31] ⭐推荐

这些参数不改变几何，但影响渲染外观，**完全拓扑无关**：

#### 索引 28：平滑度 (Smoothness)
```python
IDX_SMOOTHNESS = 28  # 0.0-1.0
```

**实现方式**：
- **Preset 模式**：控制 Subdivision Surface 级别
- **Import 模式**：添加 Subdivision Surface 修改器
- **可逆**：可以安全地添加/移除

**Blender 实现**：
```python
if smoothness > 0.1:
    subsurf = obj.modifiers.new(name="Smooth", type='SUBSURF')
    subsurf.levels = int(smoothness * 3)  # 0-3级细分
    subsurf.render_levels = subsurf.levels
```

#### 索引 29：边缘锐化 (Edge Sharpness)
```python
IDX_EDGE_SHARPNESS = 29  # 0.0-1.0
```

**实现方式**：
- 控制边缘的折痕（Crease）
- 影响细分时的边缘保持

**Blender 实现**：
```python
if edge_sharpness > 0.1:
    # 为所有边设置折痕
    for edge in mesh.edges:
        edge.crease = edge_sharpness
    # 或使用 Edge Split 修改器
    edge_split = obj.modifiers.new(name="EdgeSharp", type='EDGE_SPLIT')
    edge_split.split_angle = math.radians(180 * (1 - edge_sharpness))
```

#### 索引 30：整体膨胀/收缩 (Inflation)
```python
IDX_INFLATION = 30  # -1.0 到 1.0
```

**实现方式**：
- 沿法线方向移动所有顶点
- 不改变拓扑，只改变位置

**Blender 实现**：
```python
if abs(inflation) > 0.01:
    displace = obj.modifiers.new(name="Inflate", type='DISPLACE')
    displace.strength = inflation * 0.5  # 缩放到合理范围
    displace.direction = 'NORMAL'  # 沿法线
    # 不需要纹理，使用默认
```

#### 索引 31：随机扰动强度 (Randomness)
```python
IDX_RANDOMNESS = 31  # 0.0-1.0
```

**实现方式**：
- 轻微的随机位移
- 打破完美对称性

**Blender 实现**：
```python
if randomness > 0.01:
    displace = obj.modifiers.new(name="Random", type='DISPLACE')
    displace.strength = randomness * 0.1
    # 使用噪声纹理
    tex = bpy.data.textures.new("RandomTex", type='CLOUDS')
    tex.noise_scale = 5.0
    displace.texture = tex
```

### 方案 B：高级变形参数（需要慎重）

如果将来扩展到64维，可以添加：

#### [32-35] 局部缩放 (Non-uniform Stretch)
```python
IDX_STRETCH_TOP = 32     # 顶部缩放 0.5-2.0
IDX_STRETCH_BOTTOM = 33  # 底部缩放 0.5-2.0
IDX_STRETCH_CENTER = 34  # 中心缩放 0.5-2.0
IDX_STRETCH_BLEND = 35   # 过渡平滑度 0.0-1.0
```

**实现**：使用 Simple Deform 的 Stretch 模式 + 顶点组

#### [36-38] 对称性破坏 (Asymmetry)
```python
IDX_ASYM_X = 36  # X轴不对称程度
IDX_ASYM_Y = 37  # Y轴不对称程度
IDX_ASYM_Z = 38  # Z轴不对称程度
```

**实现**：Mirror 修改器的偏移

#### [39-41] 表面细节 (Surface Detail)
```python
IDX_DETAIL_SCALE = 39     # 细节大小
IDX_DETAIL_DEPTH = 40     # 细节深度
IDX_DETAIL_ROUGHNESS = 41 # 表面粗糙度
```

**实现**：多层次 Displace 修改器

#### [42-44] 物理属性暗示 (Physics Hints)
```python
IDX_SOFTNESS = 42    # 柔软度（可用于后续物理模拟）
IDX_RIGIDITY = 43    # 刚度
IDX_ELASTICITY = 44  # 弹性
```

**实现**：存储为自定义属性，供物理引擎使用

### 方案 C：上下文感知参数（智能）

#### [32-35] 网格优化参数
```python
IDX_POLYGON_REDUCTION = 32  # 0.0-1.0，多边形简化程度
IDX_REMESH_DENSITY = 33     # 0.0-1.0，重新网格化密度
IDX_TRIANGULATE = 34        # 0.0-1.0，三角化程度
IDX_DECIMATE = 35           # 0.0-1.0，网格精简
```

**实现**：
```python
if polygon_reduction > 0.1:
    decimate = obj.modifiers.new(name="Reduce", type='DECIMATE')
    decimate.ratio = 1.0 - polygon_reduction
    decimate.use_collapse_triangulate = True
```

## 实现计划

### 阶段 1：添加 4 个通用参数 [28-31]

选择**方案 A**中的参数：
1. Smoothness（平滑度）
2. Edge Sharpness（边缘锐化）
3. Inflation（膨胀）
4. Randomness（随机性）

**理由**：
- ✅ 完全拓扑无关
- ✅ 对 Preset 和 Import 都适用
- ✅ 视觉效果明显
- ✅ 可逆操作
- ✅ 数学上可插值

### 阶段 2：更新编码器

修改 `geometry_encoder.py`：

```python
class GeometryVector:
    # ... 现有索引 ...
    IDX_SMOOTHNESS = 28      # 平滑度
    IDX_EDGE_SHARPNESS = 29  # 边缘锐化
    IDX_INFLATION = 30       # 膨胀/收缩
    IDX_RANDOMNESS = 31      # 随机扰动
```

### 阶段 3：更新编码逻辑

```python
@staticmethod
def encode_object(obj) -> GeometryVector:
    vec = GeometryVector()
    # ... 现有编码 ...
    
    # 新增：外观参数编码
    for mod in obj.modifiers:
        if mod.type == 'SUBSURF':
            vec.vector[GeometryVector.IDX_SMOOTHNESS] = mod.levels / 3.0
        elif mod.type == 'EDGE_SPLIT':
            angle = mod.split_angle
            vec.vector[GeometryVector.IDX_EDGE_SHARPNESS] = 1.0 - (angle / math.pi)
        elif mod.type == 'DISPLACE' and mod.direction == 'NORMAL':
            vec.vector[GeometryVector.IDX_INFLATION] = mod.strength / 0.5
    
    # 检测网格的随机性（通过顶点位置方差）
    if len(obj.data.vertices) > 10:
        positions = [v.co for v in obj.data.vertices]
        variance = calculate_position_variance(positions)
        vec.vector[GeometryVector.IDX_RANDOMNESS] = min(1.0, variance * 10)
    
    return vec
```

### 阶段 4：更新解码逻辑

修改 `operators.py` 的 `_create_geometry_from_vector()`：

```python
def _create_geometry_from_vector(self, context, vec, scene):
    # ... 现有代码：创建/恢复网格 ...
    
    # ========== 通用参数：对所有模式都应用 ==========
    
    # 1. 平滑度
    smoothness = vec.vector[GeometryVector.IDX_SMOOTHNESS]
    if smoothness > 0.1:
        mod = obj.modifiers.new(name="Smoothness", type='SUBSURF')
        mod.levels = max(1, min(3, int(smoothness * 3)))
        mod.render_levels = mod.levels
    
    # 2. 边缘锐化
    edge_sharpness = vec.vector[GeometryVector.IDX_EDGE_SHARPNESS]
    if edge_sharpness > 0.1:
        mod = obj.modifiers.new(name="EdgeSharp", type='EDGE_SPLIT')
        mod.split_angle = math.radians(180 * (1 - edge_sharpness))
        mod.use_edge_angle = True
    
    # 3. 膨胀
    inflation = vec.vector[GeometryVector.IDX_INFLATION]
    if abs(inflation) > 0.01:
        mod = obj.modifiers.new(name="Inflate", type='DISPLACE')
        mod.strength = inflation * 0.5
        mod.direction = 'NORMAL'
    
    # 4. 随机扰动
    randomness = vec.vector[GeometryVector.IDX_RANDOMNESS]
    if randomness > 0.01:
        mod = obj.modifiers.new(name="Random", type='DISPLACE')
        mod.strength = randomness * 0.1
        tex = bpy.data.textures.new(f"RandomTex_{obj.name}", type='CLOUDS')
        tex.noise_scale = 5.0
        mod.texture = tex
    
    # ========== 模式特定参数 ==========
    if not has_source_mesh:
        # Preset 模式：应用变形修改器
        # ... 现有的 twist, taper, bend 等 ...
        pass
```

### 阶段 5：UI 更新

在 `panels.py` 中添加新的参数组：

```python
# 通用外观参数（新增，折叠面板）
box = layout.box()
row = box.row()
row.prop(scene, "show_appearance_params",
        icon='TRIA_DOWN' if scene.show_appearance_params else 'TRIA_RIGHT',
        icon_only=True, emboss=False)
row.label(text="Appearance (Universal)", icon='SHADING_RENDERED')

if scene.show_appearance_params:
    box.label(text="These work on any geometry:", icon='INFO')
    box.prop(scene, "my_appearance_smoothness", slider=True)
    box.prop(scene, "my_appearance_edge_sharpness", slider=True)
    box.prop(scene, "my_appearance_inflation", slider=True)
    box.prop(scene, "my_appearance_randomness", slider=True)
```

### 阶段 6：属性定义

在 `properties.py` 中添加：

```python
# Appearance parameters (universal, topology-agnostic)
bpy.types.Scene.my_appearance_smoothness = bpy.props.FloatProperty(
    name="Smoothness",
    description="Surface smoothness (subdivision level)",
    default=0.0,
    min=0.0,
    max=1.0,
    update=update_shape_callback
)

bpy.types.Scene.my_appearance_edge_sharpness = bpy.props.FloatProperty(
    name="Edge Sharpness",
    description="Sharpness of edges (0=smooth, 1=sharp)",
    default=0.0,
    min=0.0,
    max=1.0,
    update=update_shape_callback
)

bpy.types.Scene.my_appearance_inflation = bpy.props.FloatProperty(
    name="Inflation",
    description="Inflate/deflate along normals",
    default=0.0,
    min=-1.0,
    max=1.0,
    update=update_shape_callback
)

bpy.types.Scene.my_appearance_randomness = bpy.props.FloatProperty(
    name="Randomness",
    description="Random surface displacement",
    default=0.0,
    min=0.0,
    max=1.0,
    update=update_shape_callback
)

bpy.types.Scene.show_appearance_params = bpy.props.BoolProperty(
    name="Show Appearance Parameters",
    default=False
)
```

## 测试用例

### 用例 1：Preset 对象 + 新参数
```python
# 创建螺旋楼梯
vec = encode_preset("STAIRCASE")
vec[IDX_SMOOTHNESS] = 0.6      # 添加平滑
vec[IDX_INFLATION] = 0.2        # 轻微膨胀
vec[IDX_RANDOMNESS] = 0.1       # 轻微随机化

decode_and_render(vec)
# 结果：平滑的、略微膨胀的、带有细微不规则的楼梯
```

### 用例 2：Import 对象 + 新参数
```python
# 导入外部模型
vec = load_from_file("character.blend")
vec[IDX_SMOOTHNESS] = 0.8      # 高平滑度
vec[IDX_EDGE_SHARPNESS] = 0.3  # 保持一些边缘
vec[IDX_INFLATION] = -0.1       # 轻微收缩

decode_and_render(vec)
# 结果：更平滑、有轮廓感、略微收缩的角色模型
```

### 用例 3：向量插值
```python
# 在两个状态间插值
vec_A = load_from_file("model_A.blend")
vec_A[IDX_SMOOTHNESS] = 0.0

vec_B = vec_A.copy()
vec_B[IDX_SMOOTHNESS] = 1.0
vec_B[IDX_INFLATION] = 0.5

# 创建动画
for t in range(0, 100):
    vec_t = lerp(vec_A, vec_B, t/100)
    decode_and_render(vec_t)
    render_frame(t)

# 结果：从粗糙到平滑、从正常到膨胀的变形动画
```

## 优势

1. **完全拓扑无关** ✅
   - 不关心顶点数量
   - 不关心面的连接方式
   - 适用于任何网格

2. **视觉效果明显** ✅
   - 平滑度：显著改变外观
   - 膨胀：创造有趣的变体
   - 随机性：打破机械感

3. **可逆性** ✅
   - 所有修改器都可以移除
   - 不破坏原始网格数据
   - 参数值为0时无影响

4. **数学兼容** ✅
   - 支持插值：`lerp(v1, v2, t)`
   - 支持运算：`v1 + v2`
   - 支持缩放：`v * 2`

5. **实现简单** ✅
   - 使用标准 Blender 修改器
   - 不需要复杂算法
   - 性能开销小

## 潜在问题与解决方案

### 问题 1：修改器顺序
不同修改器的顺序会影响结果。

**解决**：定义标准顺序
```python
MODIFIER_ORDER = [
    'Smoothness',      # 首先平滑
    'EdgeSharp',       # 然后定义边缘
    'Inflate',         # 膨胀/收缩
    'Random',          # 最后添加随机性
    'Twist',           # Preset特定的变形
    'Taper',
    # ...
]
```

### 问题 2：参数冲突
例如：Smoothness 和 Curvature 都影响细分。

**解决**：清晰定义语义
- `IDX_CURVATURE` [6]：几何固有的曲率（只读统计）
- `IDX_SMOOTHNESS` [28]：人为添加的平滑（可写参数）

### 问题 3：性能
多个修改器可能降低性能。

**解决**：
- 提供"烘焙"选项
- 在编辑时使用低级别
- 渲染时使用高级别

## 总结

通过添加索引 28-31 的**外观参数**：
- ✅ 扩展了系统能力
- ✅ 保持了拓扑独立性
- ✅ 同时支持两种模式
- ✅ 不增加系统复杂度

这是在32维限制下的**最佳实用扩展**。

## 下一步行动

1. ✅ 定义索引 28-31
2. ✅ 实现编码器更新
3. ✅ 实现解码器更新
4. ✅ 添加UI控件
5. ✅ 测试两种模式
6. ✅ 更新文档

预计工作量：2-3小时开发 + 1小时测试
