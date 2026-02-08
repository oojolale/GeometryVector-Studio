import bpy
from bpy.app.handlers import persistent

def init_scene_items(scene):
    if scene is None:
        return
    if not scene.my_items:
        item1 = scene.my_items.add()
        item1.id = 1
        item1.name = "张三"
        item2 = scene.my_items.add()
        item2.id = 2
        item2.name = "李四"

@persistent
def on_load_post(dummy):
    for scene in bpy.data.scenes:
        init_scene_items(scene)

# Store last selected object to detect changes
_last_selected = None

@persistent
def on_depsgraph_update(scene, depsgraph):
    """
    Auto-bind vector editor to currently selected object.
    When user selects a different object with vector data, automatically load its vectors.
    """
    global _last_selected
    
    context = bpy.context
    if not context or not context.scene:
        return
    
    current_scene = context.scene
    
    # Only update if vector editor auto-bind is enabled
    if not getattr(current_scene, 'vector_editor_auto_bind', True):
        return
    
    # Get current active object
    active_obj = context.active_object
    
    # Check if selection changed
    if active_obj == _last_selected:
        return
    
    _last_selected = active_obj
    
    # If no object or not a mesh, clear binding
    if not active_obj or active_obj.type != 'MESH':
        return
    
    # Check if this object has vector data
    has_vector_data = all(f"geom_vector_{i}" in active_obj for i in range(32))
    
    if has_vector_data:
        # Load vector from this object
        try:
            for i in range(32):
                current_scene.geom_vector_current[i] = float(active_obj[f"geom_vector_{i}"])
            
            # Update source info
            source = active_obj.get("geometry_vector_source", "unknown")
            if source == "preset":
                # Try to identify which preset
                preset_name = _identify_preset_from_vector(current_scene)
                current_scene.vector_source_preset = preset_name if preset_name else "NONE"
            else:
                current_scene.vector_source_preset = "NONE"
            
            print(f"[VectorEditor] Auto-bound to object: {active_obj.name}")
        except Exception as e:
            print(f"[VectorEditor] Failed to auto-bind: {e}")

def _identify_preset_from_vector(scene):
    """Try to identify which preset the current vector represents"""
    # This is a simplified check - you could add more sophisticated matching
    from .geometry_encoder import GeometryEncoder
    import numpy as np
    
    current_vec = np.array([scene.geom_vector_current[i] for i in range(32)])
    
    preset_names = [
        'SPIRAL_CORRIDOR', 'DNA_HELIX', 'SPRING', 'TWISTED_TOWER',
        'FIGHTER_JET', 'BOMBER', 'HELICOPTER', 'STAIRCASE', 'CHARACTER'
    ]
    
    min_dist = float('inf')
    closest_preset = None
    
    for preset in preset_names:
        preset_vec = GeometryEncoder.encode_preset(preset, scene)
        dist = np.linalg.norm(current_vec - preset_vec.vector)
        if dist < min_dist and dist < 0.1:  # Threshold for "close enough"
            min_dist = dist
            closest_preset = preset
    
    return closest_preset
