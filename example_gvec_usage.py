"""
Example usage of .gvec file format
Demonstrates various import/export scenarios
"""

import bpy
from blenderUI.geometry_file_format import GeometryFileFormat, GeometryBatchExporter
from blenderUI.geometry_encoder import GeometryEncoder

# ============================================================================
# Example 1: Export a preset object (vector only)
# ============================================================================

def example_export_preset():
    """Export a preset-generated object as pure vector"""
    
    # Create a simple cube (preset mode)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    obj = bpy.context.active_object
    
    # Encode to vector
    geom_vec = GeometryEncoder.encode_object(obj)
    
    # Export without mesh data (pure vector)
    success = GeometryFileFormat.export_to_file(
        filepath="cube_preset.gvec",
        geom_vector=geom_vec,
        obj=None,  # No mesh data
        metadata={"source": "preset", "shape": "cube"}
    )
    
    print(f"Preset export: {'Success' if success else 'Failed'}")
    return success


# ============================================================================
# Example 2: Export an imported object (vector + mesh)
# ============================================================================

def example_export_imported(blend_file_path):
    """Export an imported complex object with full mesh data"""
    
    # Import object from .blend file
    with bpy.data.libraries.load(blend_file_path) as (data_from, data_to):
        data_to.objects = data_from.objects[:1]  # Import first object
    
    obj = data_to.objects[0]
    bpy.context.collection.objects.link(obj)
    
    # Encode to vector
    geom_vec = GeometryEncoder.encode_object(obj)
    
    # Export with mesh data
    success = GeometryFileFormat.export_to_file(
        filepath="imported_model.gvec",
        geom_vector=geom_vec,
        obj=obj,  # Include full mesh
        metadata={"source": "import", "original_file": blend_file_path}
    )
    
    print(f"Import export: {'Success' if success else 'Failed'}")
    return success


# ============================================================================
# Example 3: Import and restore object
# ============================================================================

def example_import_restore(gvec_file_path):
    """Import a .gvec file and restore the object"""
    
    # Restore object from file
    obj = GeometryFileFormat.restore_object_from_file(
        filepath=gvec_file_path,
        context=bpy.context
    )
    
    if obj:
        print(f"Restored object: {obj.name}")
        print(f"Vertices: {len(obj.data.vertices)}")
        print(f"Faces: {len(obj.data.polygons)}")
        return obj
    else:
        print("Failed to restore object")
        return None


# ============================================================================
# Example 4: Batch export selected objects
# ============================================================================

def example_batch_export():
    """Export all selected objects to a batch file"""
    
    # Select multiple objects
    selected_objects = [obj for obj in bpy.context.selected_objects 
                       if obj.type == 'MESH']
    
    if not selected_objects:
        print("No mesh objects selected")
        return False
    
    # Export batch
    success = GeometryBatchExporter.export_batch(
        filepath="scene_objects.gvec_batch",
        objects=selected_objects
    )
    
    print(f"Batch export: {len(selected_objects)} objects, {'Success' if success else 'Failed'}")
    return success


# ============================================================================
# Example 5: Batch import
# ============================================================================

def example_batch_import(batch_file_path):
    """Import all objects from a batch file"""
    
    imported_objects = GeometryBatchExporter.import_batch(
        filepath=batch_file_path,
        context=bpy.context
    )
    
    print(f"Batch import: {len(imported_objects)} objects restored")
    for obj in imported_objects:
        print(f"  - {obj.name}")
    
    return imported_objects


# ============================================================================
# Example 6: Read and modify vector data programmatically
# ============================================================================

def example_vector_manipulation(gvec_file_path):
    """Load, modify, and save vector data"""
    
    # Import geometry vector
    geom_vec, data = GeometryFileFormat.import_from_file(gvec_file_path)
    
    if not geom_vec:
        print("Failed to load vector")
        return False
    
    print("Original vector:")
    print(f"  Scale X: {geom_vec.vector[2]:.3f}")
    print(f"  Scale Y: {geom_vec.vector[3]:.3f}")
    print(f"  Scale Z: {geom_vec.vector[4]:.3f}")
    
    # Modify scale parameters
    geom_vec.vector[2] *= 2.0  # Double X scale
    geom_vec.vector[3] *= 2.0  # Double Y scale
    geom_vec.vector[4] *= 2.0  # Double Z scale
    
    # Modify rotation
    import math
    geom_vec.vector[22] = math.radians(45)  # Rotate 45° around X
    
    # Save modified vector
    success = GeometryFileFormat.export_to_file(
        filepath="modified_geometry.gvec",
        geom_vector=geom_vec,
        obj=None,
        metadata={"modified": True, "source_file": gvec_file_path}
    )
    
    print(f"Modified vector saved: {'Success' if success else 'Failed'}")
    return success


# ============================================================================
# Example 7: JSON inspection (external tools)
# ============================================================================

def example_json_inspection(gvec_file_path):
    """Inspect .gvec file structure without Blender API"""
    
    import json
    
    with open(gvec_file_path, 'r') as f:
        data = json.load(f)
    
    print("File structure:")
    print(f"  Version: {data['version']}")
    print(f"  Type: {data['type']}")
    print(f"  Object name: {data['metadata']['name']}")
    print(f"  Source: {data['metadata']['source']}")
    print(f"  Vector dimensions: {len(data['vector'])}")
    
    if 'mesh' in data:
        print(f"  Mesh data: YES")
        print(f"    Vertices: {data['mesh']['vertex_count']}")
        print(f"    Faces: {data['mesh']['face_count']}")
    else:
        print(f"  Mesh data: NO (vector only)")
    
    if 'materials' in data:
        print(f"  Material: {data['materials']['name']}")
        print(f"    Color: {data['materials'].get('diffuse_color', 'N/A')}")
    
    return data


# ============================================================================
# Example 8: Generate random geometries
# ============================================================================

def example_generate_random_dataset(count=10):
    """Generate random geometry vectors for testing/training"""
    
    import numpy as np
    from blenderUI.geometry_encoder import GeometryVector
    
    for i in range(count):
        # Generate random vector
        random_values = np.random.randn(32) * 0.5
        
        # Set reasonable defaults
        random_values[2:5] = np.abs(random_values[2:5]) + 0.5  # Scale > 0
        random_values[22:25] = random_values[22:25] * np.pi    # Rotation in radians
        
        geom_vec = GeometryVector(random_values)
        
        # Export
        success = GeometryFileFormat.export_to_file(
            filepath=f"random_{i:03d}.gvec",
            geom_vector=geom_vec,
            obj=None,
            metadata={"type": "random", "index": i}
        )
        
        print(f"Generated random_{i:03d}.gvec: {'OK' if success else 'FAIL'}")
    
    print(f"Generated {count} random geometry vectors")


# ============================================================================
# Example 9: Machine learning dataset preparation
# ============================================================================

def example_prepare_ml_dataset(output_dir="ml_dataset"):
    """Prepare dataset for machine learning training"""
    
    import os
    import numpy as np
    import json
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    vectors = []
    labels = []
    
    # Export all objects in scene
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        
        # Encode object
        geom_vec = GeometryEncoder.encode_object(obj)
        
        # Save individual file
        filepath = os.path.join(output_dir, f"{obj.name}.gvec")
        GeometryFileFormat.export_to_file(filepath, geom_vec, obj)
        
        # Collect for numpy array
        vectors.append(geom_vec.vector)
        labels.append(obj.name)
    
    # Save as numpy arrays
    X = np.array(vectors)
    np.save(os.path.join(output_dir, "vectors.npy"), X)
    
    with open(os.path.join(output_dir, "labels.json"), 'w') as f:
        json.dump(labels, f, indent=2)
    
    print(f"ML Dataset prepared: {len(vectors)} samples")
    print(f"  Shape: {X.shape}")
    print(f"  Output: {output_dir}/")
    
    return X, labels


# ============================================================================
# Example 10: Vector interpolation and morphing
# ============================================================================

def example_vector_morphing(start_gvec, end_gvec, steps=10):
    """Create morph animation between two geometries"""
    
    import numpy as np
    
    # Load start and end vectors
    vec_start, _ = GeometryFileFormat.import_from_file(start_gvec)
    vec_end, _ = GeometryFileFormat.import_from_file(end_gvec)
    
    if not vec_start or not vec_end:
        print("Failed to load vectors")
        return
    
    # Interpolate
    for i in range(steps):
        t = i / (steps - 1)  # 0 to 1
        
        # Linear interpolation
        interpolated = vec_start.vector * (1 - t) + vec_end.vector * t
        
        from blenderUI.geometry_encoder import GeometryVector
        morph_vec = GeometryVector(interpolated)
        
        # Export intermediate step
        success = GeometryFileFormat.export_to_file(
            filepath=f"morph_frame_{i:03d}.gvec",
            geom_vector=morph_vec,
            obj=None,
            metadata={"morph_t": t, "frame": i}
        )
        
        print(f"Frame {i:03d} (t={t:.2f}): {'OK' if success else 'FAIL'}")
    
    print(f"Morphing animation: {steps} frames generated")


# ============================================================================
# Run examples
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("GVEC File Format Examples")
    print("=" * 70)
    
    # Run basic examples
    print("\n[1] Export preset object (vector only)")
    example_export_preset()
    
    print("\n[3] Import and restore")
    example_import_restore("cube_preset.gvec")
    
    print("\n[6] Vector manipulation")
    example_vector_manipulation("cube_preset.gvec")
    
    print("\n[7] JSON inspection")
    example_json_inspection("cube_preset.gvec")
    
    print("\n[8] Generate random dataset")
    example_generate_random_dataset(count=5)
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)
