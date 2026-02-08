# .gvec 文件格式系统架构

## 系统概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      Blender 插件系统                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │   UI Panel  │ ←→ │  Operators   │ ←→ │  File Format    │   │
│  │  (panels.py)│    │(operators.py)│    │   (new file)    │   │
│  └─────────────┘    └──────────────┘    └─────────────────┘   │
│         ↓                   ↓                      ↓            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │          Geometry Encoder/Decoder System                │   │
│  │            (geometry_encoder.py)                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               ↓
                    ┌──────────────────────┐
                    │   .gvec File Format   │
                    │     (JSON Storage)    │
                    └──────────────────────┘
```

---

## 核心模块关系

### 1. 数据流：导出 (Export)

```
Blender Object
    ↓
[GeometryEncoder]
    ↓
GeometryVector (32D numpy array)
    ↓
[GeometryFileFormat.serialize_mesh()]  ← Optional
    ↓
Mesh Data (Dict)
    ↓
[json.dump()]
    ↓
.gvec file (JSON)
```

### 2. 数据流：导入 (Import)

```
.gvec file (JSON)
    ↓
[json.load()]
    ↓
Python Dict
    ↓
[GeometryFileFormat.import_from_file()]
    ↓
GeometryVector + Mesh Data
    ↓
[GeometryFileFormat.deserialize_mesh()]
    ↓
Blender Mesh
    ↓
Blender Object
```

---

## 类层次结构

```
geometry_file_format.py
│
├── GeometryFileFormat (静态方法类)
│   ├── serialize_mesh()      : Object → Dict
│   ├── deserialize_mesh()    : Dict → Mesh
│   ├── serialize_material()  : Object → Dict
│   ├── export_to_file()      : (Vector, Object) → File
│   ├── import_from_file()    : File → (Vector, Dict)
│   └── restore_object_from_file() : File → Object
│
└── GeometryBatchExporter (静态方法类)
    ├── export_batch()        : Objects → .gvec_batch
    └── import_batch()        : .gvec_batch → Objects
```

---

## 操作符调用链

### Export Single Object

```
UI Button Click
    ↓
MYADDON_OT_export_gvec.invoke()
    ↓
MYADDON_OT_export_gvec.execute()
    ↓
GeometryEncoder.encode(obj)
    ↓
GeometryFileFormat.export_to_file(filepath, vec, obj, metadata)
    ↓
    ├── GeometryFileFormat.serialize_mesh(obj)
    ├── GeometryFileFormat.serialize_material(obj)
    └── json.dump(data, file)
```

### Import Single Object

```
UI Button Click
    ↓
MYADDON_OT_import_gvec.invoke()
    ↓
MYADDON_OT_import_gvec.execute()
    ↓
GeometryFileFormat.restore_object_from_file(filepath, context)
    ↓
    ├── GeometryFileFormat.import_from_file(filepath)
    │   └── json.load(file)
    ├── GeometryFileFormat.deserialize_mesh(mesh_data)
    │   └── mesh.from_pydata(vertices, edges, faces)
    └── context.collection.objects.link(obj)
```

---

## 数据格式层次

```
.gvec File (JSON)
│
├── version: "1.0"                    [String]
├── type: "geometry_vector"           [String]
├── vector: [...]                     [Array[32]]
│   └── float values (32D)
│
├── metadata: {...}                   [Object]
│   ├── name                          [String]
│   ├── source: "preset"|"import"     [String]
│   └── created                       [String, Optional]
│
├── mesh: {...}                       [Object, Optional]
│   ├── vertices: [[x,y,z], ...]      [Array[Array[3]]]
│   ├── edges: [[v1,v2], ...]         [Array[Array[2]]]
│   ├── faces: [[v1,v2,...], ...]     [Array[Array[N]]]
│   ├── normals: [[nx,ny,nz], ...]    [Array[Array[3]]]
│   ├── uv_coords: [[u,v], ...]       [Array[Array[2]]]
│   ├── vertex_count                  [Integer]
│   └── face_count                    [Integer]
│
└── materials: {...}                  [Object, Optional]
    ├── name                          [String]
    ├── diffuse_color: [r,g,b,a]      [Array[4]]
    ├── metallic                      [Float]
    └── roughness                     [Float]
```

---

## 向量编码映射

```
Blender Object Properties
    ↓
┌─────────────────────────────────────┐
│    32-Dimensional Vector Space      │
├─────────────────────────────────────┤
│ [0-1]   Shape Type & Complexity     │
│ [2-4]   Scale (X, Y, Z)             │
│ [5-10]  Topology Features           │
│ [11-14] Deformations                │
│ [15-18] Wave & Noise                │
│ [19-21] Shape Morphing              │
│ [22-24] Rotation (X, Y, Z)          │
│ [25-27] Location (X, Y, Z)          │
│ [28-31] Universal Parameters        │
└─────────────────────────────────────┘
    ↓
JSON Array
```

---

## 模式选择决策树

```
Start: Export Object
    ↓
┌───────────────────────┐
│ Is complex imported   │
│ mesh?                 │
└───────────────────────┘
    ├─ Yes ──→ [Mixed Mode]
    │           ├─ Save Vector (32D)
    │           └─ Save Mesh (Full)
    │              └─→ .gvec (10-500 KB)
    │
    └─ No ───→ [Vector-Only Mode]
                ├─ Save Vector (32D)
                └─ No Mesh Data
                   └─→ .gvec (1-2 KB)
```

---

## 还原流程决策

```
Start: Import .gvec
    ↓
┌───────────────────────┐
│ "mesh" field exists?  │
└───────────────────────┘
    ├─ Yes ──→ [Import Mode]
    │           ├─ Load mesh directly
    │           ├─ Apply transforms
    │           └─ Apply universal params
    │              └─→ Exact restoration
    │
    └─ No ───→ [Preset Mode]
                ├─ Generate base geometry
                ├─ Apply all modifiers
                └─ Apply vector params
                   └─→ Parametric rebuild
```

---

## 批量操作架构

```
.gvec_batch File
│
├── version: "1.0"
├── type: "geometry_batch"
├── count: N
└── objects: [...]
    ├── Object 1
    │   ├── name
    │   ├── vector: [32D]
    │   ├── mesh: {...}
    │   └── transform: {location, rotation, scale}
    ├── Object 2
    │   ├── ...
    └── Object N
        └── ...
```

### 批量导出流程

```
Selected Objects (N objects)
    ↓
For each object:
    ├── Encode to vector
    ├── Serialize mesh
    └── Extract transform
        ↓
    Collect to array
        ↓
Write batch JSON
    ↓
.gvec_batch file
```

---

## 依赖关系图

```
geometry_file_format.py
    │
    ├── bpy (Blender API)
    │   ├── bpy.types.Object
    │   ├── bpy.types.Mesh
    │   └── bpy.data.meshes
    │
    ├── json (Python stdlib)
    │   ├── json.dump()
    │   └── json.load()
    │
    ├── numpy
    │   └── np.array()
    │
    └── geometry_encoder.py
        └── GeometryVector
            └── GeometryEncoder
```

---

## 错误处理流程

```
Operation Start
    ↓
Try:
    ├── Validate Input
    │   ├── Check file extension
    │   ├── Check object type
    │   └── Check permissions
    │
    ├── Execute Operation
    │   ├── Encode/Decode
    │   ├── Read/Write File
    │   └── Create/Restore Object
    │
    └── Success
        └── Report to User
            ↓
        Return {'FINISHED'}

Except:
    ├── Catch Exception
    ├── Log Error
    └── Report to User
        ↓
    Return {'CANCELLED'}
```

---

## UI集成架构

```
panels.py (VIEW3D_PT_my_panel)
│
└── Vector Editor Section
    │
    ├── Load Vector
    │   ├── From Preset
    │   ├── From Object
    │   └── From Blender File
    │
    ├── Custom Format (.gvec) ← NEW
    │   ├── Import .gvec
    │   └── Export .gvec
    │
    ├── Batch Operations ← NEW
    │   ├── Import Batch
    │   └── Export Batch
    │
    └── Vector Values Display
        └── [0-31] parameter sliders
```

---

## 文件系统布局

```
Project Directory
│
├── geometry_encoder.py          (已有)
│   └── GeometryVector, GeometryEncoder
│
├── geometry_file_format.py      (新增)
│   └── GeometryFileFormat, GeometryBatchExporter
│
├── operators.py                 (修改)
│   ├── MYADDON_OT_export_gvec
│   ├── MYADDON_OT_import_gvec
│   ├── MYADDON_OT_export_gvec_batch
│   └── MYADDON_OT_import_gvec_batch
│
├── panels.py                    (修改)
│   └── 添加导入/导出按钮
│
└── Documentation
    ├── GVEC_FILE_FORMAT_GUIDE.md
    ├── GVEC_QUICK_REFERENCE.md
    ├── GVEC_IMPLEMENTATION_SUMMARY.md
    └── example_gvec_usage.py
```

---

## 性能优化策略

### 1. 内存管理

```
Large Mesh Import
    ↓
Stream Processing
    ├── Read in chunks
    ├── Process incrementally
    └── Release buffers
        ↓
    Reduced memory footprint
```

### 2. 并行处理（未来）

```
Batch Export
    ↓
Thread Pool
    ├── Thread 1: Encode Object 1
    ├── Thread 2: Encode Object 2
    └── Thread N: Encode Object N
        ↓
    Collect results
        ↓
    Write batch file
```

---

## 扩展接口

### Plugin API

```python
class CustomGeometryExporter:
    """扩展接口示例"""
    
    def pre_export(self, obj):
        """导出前钩子"""
        pass
    
    def post_export(self, filepath):
        """导出后钩子"""
        pass
    
    def custom_serialize(self, obj):
        """自定义序列化"""
        return custom_data
```

---

## 测试架构

```
Test Suite
│
├── Unit Tests
│   ├── test_serialize_mesh()
│   ├── test_deserialize_mesh()
│   ├── test_export_to_file()
│   └── test_import_from_file()
│
├── Integration Tests
│   ├── test_full_export_import_cycle()
│   ├── test_batch_operations()
│   └── test_ui_operators()
│
└── Performance Tests
    ├── test_large_mesh_export()
    ├── test_batch_export_speed()
    └── test_memory_usage()
```

---

## 版本兼容性策略

```
Version 1.0 Format
    ↓
Future Version 1.1
    ├── Add new fields
    ├── Keep required fields
    └── Backward compatible
        ↓
    Version check on import
        ├── v1.0 → Load with defaults
        └── v1.1 → Load all features
```

---

## 总结

本架构设计实现了：

✅ **模块化**：清晰的职责分离  
✅ **可扩展**：易于添加新功能  
✅ **可维护**：代码结构清晰  
✅ **可测试**：独立的组件  
✅ **高性能**：优化的数据流  
✅ **健壮性**：完善的错误处理  

系统可以作为基础继续扩展，支持更复杂的场景和需求。
