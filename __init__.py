bl_info = {
    "name": "Simple Panel Demo",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > UI > My Addon",
    "description": "Demonstrates button, dropdown, collapsible list, reorderable panels, icon popup, and API fetch",
    "category": "Interface",
}

import bpy

def unregister():
    try:
        from . import handlers
        
        # Remove load_post handler
        try:
            if handlers.on_load_post in bpy.app.handlers.load_post:
                bpy.app.handlers.load_post.remove(handlers.on_load_post)
        except (AttributeError, ValueError) as e:
            print(f"[Addon] Could not remove on_load_post: {e}")
        
        # Remove depsgraph_update_post handler (may not exist in old versions)
        try:
            if hasattr(handlers, 'on_depsgraph_update'):
                if handlers.on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
                    bpy.app.handlers.depsgraph_update_post.remove(handlers.on_depsgraph_update)
        except (AttributeError, ValueError) as e:
            print(f"[Addon] Could not remove on_depsgraph_update: {e}")
            
    except Exception as e:
        print(f"[Addon] Warning: Could not import handlers: {e}")
    
    # Unregister modules
    try:
        from . import panels, ui_lists, operators, properties
        panels.unregister()
        ui_lists.unregister()
        operators.unregister()
        properties.unregister()
    except Exception as e:
        print(f"[Addon] Warning during unregister: {e}")

def register():
    if hasattr(bpy.types, 'VIEW3D_PT_my_panel'):
        unregister()

    from . import properties, operators, ui_lists, panels, handlers
    
    # Debug: Check if handler function exists
    if not hasattr(handlers, 'on_depsgraph_update'):
        print("[Addon] ERROR: handlers.on_depsgraph_update not found!")
        print(f"[Addon] Available in handlers module: {dir(handlers)}")
    
    properties.register()
    operators.register()
    ui_lists.register()
    panels.register()

    try:
        for scene in bpy.data.scenes:
            handlers.init_scene_items(scene)
    except Exception as e:
        print(f"[Addon] Warning: Could not init scenes: {e}")
    
    # Register handlers
    try:
        bpy.app.handlers.load_post.append(handlers.on_load_post)
        print("[Addon] Registered on_load_post handler")
    except Exception as e:
        print(f"[Addon] Failed to register on_load_post: {e}")
    
    try:
        bpy.app.handlers.depsgraph_update_post.append(handlers.on_depsgraph_update)
        print("[Addon] Registered on_depsgraph_update handler")
    except Exception as e:
        print(f"[Addon] Failed to register on_depsgraph_update: {e}")

if __name__ == "__main__":
    register()
