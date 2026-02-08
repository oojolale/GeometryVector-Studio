"""
Geometry File Format (.gvec)
Custom file format for storing geometry vectors and mesh data
Supports both vector-only and vector+mesh hybrid storage
"""

import json
import bpy
import numpy as np
from typing import Dict, List, Optional, Tuple
from .geometry_encoder import GeometryVector


class GeometryFileFormat:
    """
    Custom file format specification for geometry data
    
    File Structure (.gvec format):
    {
        "version": "1.0",
        "type": "geometry_vector",
        "vector": [32 float values],
        "metadata": {
            "name": "object_name",
            "created": "timestamp",
            "source": "preset" | "import"
        },
        "mesh": {  # Optional - only for imported objects
            "vertices": [[x, y, z], ...],
            "edges": [[v1, v2], ...],
            "faces": [[v1, v2, v3, ...], ...],
            "normals": [[nx, ny, nz], ...],  # Optional
            "uv_coords": [[u, v], ...]  # Optional
        },
        "materials": {  # Optional
            "name": "material_name",
            "diffuse_color": [r, g, b, a],
            "metallic": 0.0,
            "roughness": 0.5
        }
    }
    """
    
    VERSION = "1.0"
    EXTENSION = ".gvec"
    
    @staticmethod
    def serialize_mesh(obj: bpy.types.Object) -> Optional[Dict]:
        """
        Convert Blender mesh to JSON-serializable format
        
        Args:
            obj: Blender object with mesh data
            
        Returns:
            Dictionary containing mesh data or None if not a mesh
        """
        if obj.type != 'MESH':
            return None
        
        mesh = obj.data
        
        # Get vertices
        vertices = [[v.co.x, v.co.y, v.co.z] for v in mesh.vertices]
        
        # Get edges
        edges = [[e.vertices[0], e.vertices[1]] for e in mesh.edges]
        
        # Get faces
        faces = [[v for v in poly.vertices] for poly in mesh.polygons]
        
        # Get normals (optional)
        normals = [[v.normal.x, v.normal.y, v.normal.z] for v in mesh.vertices]
        
        # Get UV coordinates if available
        uv_coords = []
        if mesh.uv_layers.active:
            uv_layer = mesh.uv_layers.active.data
            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                    uv = uv_layer[loop_index].uv
                    uv_coords.append([uv.x, uv.y])
        
        mesh_data = {
            "vertices": vertices,
            "edges": edges,
            "faces": faces,
            "normals": normals,
            "vertex_count": len(vertices),
            "face_count": len(faces)
        }
        
        if uv_coords:
            mesh_data["uv_coords"] = uv_coords
        
        # Save modifier information (but don't apply them)
        # User can choose to apply these modifiers after import
        modifiers = []
        for mod in obj.modifiers:
            mod_data = {
                "name": mod.name,
                "type": mod.type,
                "show_viewport": mod.show_viewport,
                "show_render": mod.show_render
            }
            
            # Store type-specific properties for common modifiers
            if mod.type == 'MIRROR':
                mod_data["use_axis"] = [mod.use_axis[0], mod.use_axis[1], mod.use_axis[2]]
                mod_data["use_bisect_axis"] = [mod.use_bisect_axis[0], mod.use_bisect_axis[1], mod.use_bisect_axis[2]]
                mod_data["use_clip"] = mod.use_clip
                mod_data["merge_threshold"] = mod.merge_threshold
            elif mod.type == 'ARRAY':
                mod_data["count"] = mod.count
                mod_data["use_relative_offset"] = mod.use_relative_offset
                mod_data["relative_offset_displace"] = list(mod.relative_offset_displace)
            elif mod.type == 'SUBSURF':
                mod_data["levels"] = mod.levels
                mod_data["render_levels"] = mod.render_levels
            elif mod.type == 'SOLIDIFY':
                mod_data["thickness"] = mod.thickness
                mod_data["offset"] = mod.offset
            elif mod.type == 'BEVEL':
                mod_data["width"] = mod.width
                mod_data["segments"] = mod.segments
            
            modifiers.append(mod_data)
        
        if modifiers:
            mesh_data["modifiers"] = modifiers
        
        return mesh_data
    
    @staticmethod
    def deserialize_mesh(mesh_data: Dict) -> bpy.types.Mesh:
        """
        Convert JSON mesh data back to Blender mesh
        
        Args:
            mesh_data: Dictionary containing mesh information
            
        Returns:
            Blender mesh object
        """
        mesh = bpy.data.meshes.new("restored_mesh")
        
        vertices = mesh_data["vertices"]
        edges = mesh_data.get("edges", [])
        faces = mesh_data["faces"]
        
        mesh.from_pydata(vertices, edges, faces)
        mesh.update()
        
        # Note: Vertex normals are automatically calculated by Blender
        # Custom normals can be set if needed, but for most cases
        # auto-calculated normals work well
        # If you need custom normals:
        # mesh.use_auto_smooth = True
        # mesh.normals_split_custom_set_from_vertices(normals)
        
        return mesh
    
    @staticmethod
    def serialize_material(obj: bpy.types.Object) -> Optional[Dict]:
        """
        Serialize basic material properties
        
        Args:
            obj: Blender object
            
        Returns:
            Dictionary with material data or None
        """
        if not obj.data.materials:
            return None
        
        mat = obj.data.materials[0]  # Get first material
        
        material_data = {
            "name": mat.name
        }
        
        # Get basic material properties if using nodes
        if mat.use_nodes and mat.node_tree:
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                material_data["diffuse_color"] = list(bsdf.inputs["Base Color"].default_value)
                material_data["metallic"] = bsdf.inputs["Metallic"].default_value
                material_data["roughness"] = bsdf.inputs["Roughness"].default_value
        
        return material_data
    
    @staticmethod
    def export_to_file(
        filepath: str,
        geom_vector: GeometryVector,
        obj: Optional[bpy.types.Object] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Export geometry vector and optional mesh data to .gvec file
        
        Args:
            filepath: Target file path (will add .gvec if missing)
            geom_vector: GeometryVector instance
            obj: Optional Blender object (for mesh data)
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful, False otherwise
        """
        # Ensure correct extension
        if not filepath.endswith(GeometryFileFormat.EXTENSION):
            filepath += GeometryFileFormat.EXTENSION
        
        # Build data structure
        data = {
            "version": GeometryFileFormat.VERSION,
            "type": "geometry_vector",
            "vector": geom_vector.vector.tolist(),  # Convert numpy to list
            "metadata": metadata or {}
        }
        
        # Add default metadata
        if "name" not in data["metadata"]:
            data["metadata"]["name"] = obj.name if obj else "unnamed"
        
        if "source" not in data["metadata"]:
            # Determine if this is a preset or imported object
            has_cache = obj and obj.get("geometry_vector_source_mesh")
            data["metadata"]["source"] = "import" if has_cache else "preset"
        
        # Add mesh data if object provided
        if obj:
            mesh_data = GeometryFileFormat.serialize_mesh(obj)
            if mesh_data:
                data["mesh"] = mesh_data
            
            # Add material data
            material_data = GeometryFileFormat.serialize_material(obj)
            if material_data:
                data["materials"] = material_data
        
        # Write to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting to {filepath}: {e}")
            return False
    
    @staticmethod
    def import_from_file(filepath: str) -> Tuple[Optional[GeometryVector], Optional[Dict]]:
        """
        Import geometry vector and mesh data from .gvec file
        
        Args:
            filepath: Source file path
            
        Returns:
            Tuple of (GeometryVector, full_data_dict) or (None, None) on error
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate version
            if data.get("version") != GeometryFileFormat.VERSION:
                print(f"Warning: File version {data.get('version')} may not be compatible")
            
            # Reconstruct GeometryVector
            vector_data = np.array(data["vector"], dtype=np.float32)
            geom_vector = GeometryVector(vector_data)
            
            return geom_vector, data
            
        except Exception as e:
            print(f"Error importing from {filepath}: {e}")
            return None, None
    
    @staticmethod
    def restore_object_from_file(filepath: str, context) -> Optional[bpy.types.Object]:
        """
        Restore complete Blender object from .gvec file
        
        Args:
            filepath: Source file path
            context: Blender context
            
        Returns:
            Restored Blender object or None on error
        """
        geom_vector, data = GeometryFileFormat.import_from_file(filepath)
        
        if not geom_vector or not data:
            return None
        
        obj_name = data["metadata"].get("name", "restored_object")
        
        # Check if mesh data is available
        if "mesh" in data:
            # Restore from mesh data
            print(f"[GVEC] Restoring from mesh data (vertices: {len(data['mesh']['vertices'])})")
            mesh = GeometryFileFormat.deserialize_mesh(data["mesh"])
            obj = bpy.data.objects.new(obj_name, mesh)
            
            # Store the vector data
            for i in range(32):
                obj[f"geom_vector_{i}"] = float(geom_vector.vector[i])
            
            # Store metadata
            obj["geometry_vector_source"] = data["metadata"].get("source", "import")
            obj["geometry_vector_version"] = data["metadata"].get("version", "1.0")
            
            # Store modifier data (as JSON string) for later application
            if "modifiers" in data["mesh"]:
                import json
                obj["geometry_vector_modifiers"] = json.dumps(data["mesh"]["modifiers"])
                print(f"[GVEC] Stored {len(data['mesh']['modifiers'])} modifiers for later application")
            
            # Cache the mesh for future use
            obj["geometry_vector_source_mesh"] = mesh.name
            
        else:
            # No mesh data - create empty object with vector data
            # The import operator will handle reconstruction
            print(f"[GVEC] No mesh data found, will reconstruct from vector...")
            mesh = bpy.data.meshes.new(obj_name)
            obj = bpy.data.objects.new(obj_name, mesh)
            
            # Store vector data (will be used for reconstruction)
            for i in range(32):
                obj[f"geom_vector_{i}"] = float(geom_vector.vector[i])
            
            # Store metadata
            obj["geometry_vector_source"] = data["metadata"].get("source", "preset")
            obj["geometry_vector_version"] = data["metadata"].get("version", "1.0")
            
            # For preset objects, restore the preset name
            if "preset_name" in data["metadata"]:
                obj["geometry_vector_preset_name"] = data["metadata"]["preset_name"]
        
        # Link to scene
        context.collection.objects.link(obj)
        
        # Restore material if available
        if "materials" in data:
            mat_data = data["materials"]
            mat = bpy.data.materials.new(name=mat_data.get("name", "restored_material"))
            mat.use_nodes = True
            
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf and "diffuse_color" in mat_data:
                bsdf.inputs["Base Color"].default_value = mat_data["diffuse_color"]
                if "metallic" in mat_data:
                    bsdf.inputs["Metallic"].default_value = mat_data["metallic"]
                if "roughness" in mat_data:
                    bsdf.inputs["Roughness"].default_value = mat_data["roughness"]
            
            obj.data.materials.append(mat)
        
        return obj


# Batch operations
class GeometryBatchExporter:
    """Export multiple objects to a single batch file"""
    
    @staticmethod
    def export_batch(filepath: str, objects: List[bpy.types.Object]) -> bool:
        """
        Export multiple objects to a single .gvec_batch file
        
        Args:
            filepath: Target file path
            objects: List of Blender objects
            
        Returns:
            True if successful
        """
        if not filepath.endswith(".gvec_batch"):
            filepath += ".gvec_batch"
        
        batch_data = {
            "version": GeometryFileFormat.VERSION,
            "type": "geometry_batch",
            "count": len(objects),
            "objects": []
        }
        
        for obj in objects:
            # Encode object
            from .geometry_encoder import GeometryEncoder
            geom_vector = GeometryEncoder.encode_object(obj)
            
            obj_data = {
                "name": obj.name,
                "vector": geom_vector.vector.tolist(),
                "mesh": GeometryFileFormat.serialize_mesh(obj),
                "transform": {
                    "location": list(obj.location),
                    "rotation": list(obj.rotation_euler),
                    "scale": list(obj.scale)
                }
            }
            
            batch_data["objects"].append(obj_data)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(batch_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting batch: {e}")
            return False
    
    @staticmethod
    def import_batch(filepath: str, context) -> List[bpy.types.Object]:
        """
        Import multiple objects from .gvec_batch file
        
        Args:
            filepath: Source file path
            context: Blender context
            
        Returns:
            List of imported objects
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
            
            imported_objects = []
            
            for obj_data in batch_data["objects"]:
                # Restore mesh
                mesh = GeometryFileFormat.deserialize_mesh(obj_data["mesh"])
                obj = bpy.data.objects.new(obj_data["name"], mesh)
                
                # Restore transform
                transform = obj_data["transform"]
                obj.location = transform["location"]
                obj.rotation_euler = transform["rotation"]
                obj.scale = transform["scale"]
                
                # Store vector
                vector = np.array(obj_data["vector"], dtype=np.float32)
                for i in range(32):
                    obj[f"geom_vector_{i}"] = float(vector[i])
                
                # Mark source as import_batch so Decode & Render can recognize it
                obj["geometry_vector_source"] = "import_batch"
                
                # Store preset name if available
                if "preset_name" in obj_data:
                    obj["geometry_vector_preset_name"] = obj_data["preset_name"]
                
                # Store modifier data (as JSON string) for later application
                if "modifiers" in obj_data["mesh"]:
                    obj["geometry_vector_modifiers"] = json.dumps(obj_data["mesh"]["modifiers"])
                    print(f"[GVEC Batch] Stored {len(obj_data['mesh']['modifiers'])} modifiers for {obj.name}")
                
                context.collection.objects.link(obj)
                imported_objects.append(obj)
            
            return imported_objects
            
        except Exception as e:
            print(f"Error importing batch: {e}")
            return []
