"""Test script to verify handlers module can be imported in Blender"""
import sys
import os

# Add addon path
addon_path = r"d:\Users\PC\PycharmProjects\blenderUI"
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)

try:
    import handlers
    print("✓ handlers module imported successfully")
    print(f"✓ Available functions: {[x for x in dir(handlers) if not x.startswith('_')]}")
    
    if hasattr(handlers, 'on_depsgraph_update'):
        print("✓ on_depsgraph_update function found")
        print(f"  Type: {type(handlers.on_depsgraph_update)}")
        print(f"  Callable: {callable(handlers.on_depsgraph_update)}")
    else:
        print("✗ on_depsgraph_update function NOT found")
        
except Exception as e:
    print(f"✗ Failed to import handlers: {e}")
    import traceback
    traceback.print_exc()
