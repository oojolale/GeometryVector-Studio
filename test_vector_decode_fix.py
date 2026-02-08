"""
Vector Decode & Export Fix - Test Script

This script tests the complete modify-export-import workflow
to ensure vectors are properly saved and restored.
"""

import bpy
import os


def test_vector_decode_export_import():
    """Test the complete workflow"""
    
    print("=" * 60)
    print("Testing Vector Decode & Export Fix")
    print("=" * 60)
    
    # Clean scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    scene = bpy.context.scene
    
    # Step 1: Create initial object
    print("\n[1/7] Creating initial cube...")
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    obj_a = bpy.context.active_object
    obj_a.name = "Original"
    
    # Step 2: Export as .gvec
    print("[2/7] Exporting original.gvec...")
    filepath_original = "C:/temp/test_original.gvec"
    bpy.ops.myaddon.export_gvec(filepath=filepath_original, include_mesh=True)
    
    # Step 3: Load vector to editor
    print("[3/7] Loading vector to editor...")
    bpy.ops.myaddon.vector_load_from_object()
    
    # Step 4: Modify vector parameters
    print("[4/7] Modifying vector parameters...")
    original_values = [scene.geom_vector_current[i] for i in range(32)]
    
    # Make significant modifications
    scene.geom_vector_current[0] = 0.8  # Shape Type
    scene.geom_vector_current[1] = 0.6  # Complexity
    scene.geom_vector_current[8] = 0.5  # Twist
    scene.geom_vector_current[18] = 0.7  # Smoothness
    
    modified_values = [scene.geom_vector_current[i] for i in range(32)]
    
    print(f"   Original vector[0]: {original_values[0]:.4f}")
    print(f"   Modified vector[0]: {modified_values[0]:.4f}")
    
    # Step 5: Decode & Render
    print("[5/7] Decode & Render new object...")
    bpy.ops.myaddon.vector_decode_and_render()
    obj_b = bpy.context.active_object
    obj_b.name = "Modified"
    
    # Verify vector was saved to object
    has_vector = all(f"geom_vector_{i}" in obj_b for i in range(32))
    print(f"   ✓ Vector saved to object: {has_vector}")
    
    if has_vector:
        saved_value = obj_b["geom_vector_0"]
        print(f"   ✓ Saved vector[0]: {saved_value:.4f}")
        print(f"   ✓ Source: {obj_b.get('geometry_vector_source', 'unknown')}")
    
    # Step 6: Export modified object
    print("[6/7] Exporting modified.gvec...")
    filepath_modified = "C:/temp/test_modified.gvec"
    bpy.ops.myaddon.export_gvec(filepath=filepath_modified, include_mesh=True)
    
    # Delete object
    bpy.ops.object.delete()
    
    # Step 7: Import modified.gvec and verify
    print("[7/7] Importing modified.gvec...")
    bpy.ops.myaddon.import_gvec(filepath=filepath_modified)
    obj_c = bpy.context.active_object
    obj_c.name = "Restored"
    
    # Verify restored vector matches modified vector
    restored_value = obj_c.get("geom_vector_0")
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Original vector[0]:  {original_values[0]:.4f}")
    print(f"Modified vector[0]:  {modified_values[0]:.4f}")
    print(f"Restored vector[0]:  {restored_value:.4f}")
    
    # Check if restored matches modified (not original)
    if abs(restored_value - modified_values[0]) < 0.001:
        print("\n✅ TEST PASSED! Restored object matches modified vector.")
        print("   The fix is working correctly!")
        success = True
    else:
        print("\n❌ TEST FAILED! Restored object doesn't match modified vector.")
        print("   The fix may not be working.")
        success = False
    
    print("=" * 60)
    
    # Cleanup
    if os.path.exists(filepath_original):
        os.remove(filepath_original)
    if os.path.exists(filepath_modified):
        os.remove(filepath_modified)
    
    return success


def test_batch_export():
    """Test batch export with stored vectors"""
    
    print("\n" + "=" * 60)
    print("Testing Batch Export with Stored Vectors")
    print("=" * 60)
    
    # Clean scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    scene = bpy.context.scene
    
    # Create multiple objects with different vectors
    print("\n[1/4] Creating objects with different vectors...")
    objects = []
    
    for i in range(3):
        # Create cube
        bpy.ops.mesh.primitive_cube_add(size=1, location=(i * 3, 0, 0))
        obj = bpy.context.active_object
        obj.name = f"Object_{i}"
        
        # Modify vector
        scene.geom_vector_current[0] = 0.1 + i * 0.3
        scene.geom_vector_current[1] = 0.5 + i * 0.1
        
        # Decode & Render to save vector
        bpy.ops.myaddon.vector_decode_and_render()
        obj = bpy.context.active_object
        obj.select_set(True)
        objects.append(obj)
        
        print(f"   Created {obj.name} with vector[0] = {obj['geom_vector_0']:.4f}")
    
    # Batch export
    print("\n[2/4] Batch exporting...")
    filepath_batch = "C:/temp/test_batch.gvec_batch"
    bpy.ops.myaddon.export_gvec_batch(filepath=filepath_batch)
    
    # Store original values
    original_vectors = [[obj[f"geom_vector_{i}"] for i in range(32)] for obj in objects]
    
    # Delete all
    print("[3/4] Deleting all objects...")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Batch import
    print("[4/4] Batch importing...")
    bpy.ops.myaddon.import_gvec_batch(filepath=filepath_batch)
    
    imported_objects = list(bpy.context.selected_objects)
    
    print("\n" + "=" * 60)
    print("BATCH TEST RESULTS")
    print("=" * 60)
    
    success = True
    for i, obj in enumerate(imported_objects):
        if i < len(original_vectors):
            original = original_vectors[i][0]
            restored = obj.get("geom_vector_0", 0.0)
            
            match = abs(restored - original) < 0.001
            status = "✅" if match else "❌"
            
            print(f"{status} {obj.name}: original={original:.4f}, restored={restored:.4f}")
            
            if not match:
                success = False
    
    if success:
        print("\n✅ BATCH TEST PASSED! All vectors restored correctly.")
    else:
        print("\n❌ BATCH TEST FAILED! Some vectors not restored.")
    
    print("=" * 60)
    
    # Cleanup
    if os.path.exists(filepath_batch):
        os.remove(filepath_batch)
    
    return success


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("VECTOR DECODE & EXPORT FIX TEST SUITE")
    print("=" * 60)
    
    # Ensure temp directory exists
    os.makedirs("C:/temp", exist_ok=True)
    
    try:
        # Test 1: Single object workflow
        test1_passed = test_vector_decode_export_import()
        
        # Test 2: Batch export workflow
        test2_passed = test_batch_export()
        
        # Final summary
        print("\n" + "=" * 60)
        print("FINAL TEST SUMMARY")
        print("=" * 60)
        print(f"Test 1 (Single Export): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
        print(f"Test 2 (Batch Export):  {'✅ PASSED' if test2_passed else '❌ FAILED'}")
        
        if test1_passed and test2_passed:
            print("\n🎉 ALL TESTS PASSED! The fix is working perfectly.")
        else:
            print("\n⚠️ SOME TESTS FAILED. Please review the output above.")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


# Run tests
if __name__ == "__main__":
    main()
