"""
Geometry Vector Visualization Demo
Run this in Blender's Python console to see vector operations in action
"""

import bpy
import sys
import os

# Add the addon directory to path
addon_path = r"d:\Users\PC\PycharmProjects\blenderUI"
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)

from geometry_encoder import (
    GeometryVector, GeometryEncoder, GeometryDecoder,
    GeometryLatentSpace, get_latent_space
)
import numpy as np


def demo_basic_encoding():
    """Demo 1: Basic encoding and decoding"""
    print("\n" + "="*60)
    print("DEMO 1: Basic Encoding and Decoding")
    print("="*60)
    
    scene = bpy.context.scene
    
    # Encode a preset
    print("\nEncoding Fighter Jet...")
    vec_jet = GeometryEncoder.encode_preset("FIGHTER_JET", scene)
    print(f"Vector: {vec_jet}")
    print(f"Norm: {np.linalg.norm(vec_jet.vector):.3f}")
    
    # Show first 8 dimensions
    print(f"\nFirst 8 dimensions:")
    for i, val in enumerate(vec_jet.vector[:8]):
        print(f"  [{i}] = {val:.4f}")
    
    # Convert to dict
    params = vec_jet.to_dict()
    print(f"\nScale: {params['scale']}")
    print(f"Complexity: {params['complexity']:.3f}")
    print(f"Symmetry: {params['symmetry']:.3f}")


def demo_interpolation():
    """Demo 2: Interpolation between two geometries"""
    print("\n" + "="*60)
    print("DEMO 2: Geometry Interpolation")
    print("="*60)
    
    scene = bpy.context.scene
    
    # Encode two presets
    vec_spiral = GeometryEncoder.encode_preset("SPIRAL_CORRIDOR", scene)
    vec_jet = GeometryEncoder.encode_preset("FIGHTER_JET", scene)
    
    print(f"\nSpiral Corridor vector norm: {np.linalg.norm(vec_spiral.vector):.3f}")
    print(f"Fighter Jet vector norm: {np.linalg.norm(vec_jet.vector):.3f}")
    
    # Calculate distance
    distance = vec_spiral.distance_to(vec_jet)
    print(f"\nDistance in latent space: {distance:.3f}")
    
    # Interpolate
    print("\nInterpolation path (t=0.0 to 1.0):")
    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        vec_interp = vec_spiral.interpolate(vec_jet, t)
        print(f"  t={t:.2f}: norm={np.linalg.norm(vec_interp.vector):.3f}")


def demo_blending():
    """Demo 3: Blending multiple geometries"""
    print("\n" + "="*60)
    print("DEMO 3: Geometry Blending")
    print("="*60)
    
    scene = bpy.context.scene
    latent_space = get_latent_space()
    
    # Encode three presets
    presets = ["FIGHTER_JET", "BOMBER", "HELICOPTER"]
    weights = [0.5, 0.3, 0.2]
    
    print("\nBlending formula:")
    print(f"  Result = ", end="")
    for preset, weight in zip(presets, weights):
        print(f"{weight}*{preset} + ", end="")
    print("\b\b ")
    
    # Add to latent space and blend
    for preset in presets:
        vec = GeometryEncoder.encode_preset(preset, scene)
        latent_space.add_geometry(preset, vec)
    
    blended = latent_space.blend_geometries(presets, weights)
    
    print(f"\nBlended vector norm: {np.linalg.norm(blended.vector):.3f}")
    
    # Find nearest preset
    nearest = GeometryDecoder.find_nearest_preset(blended, scene)
    print(f"Nearest preset: {nearest}")


def demo_similarity():
    """Demo 4: Similarity search"""
    print("\n" + "="*60)
    print("DEMO 4: Similarity Search")
    print("="*60)
    
    scene = bpy.context.scene
    latent_space = get_latent_space()
    
    # Encode all presets
    all_presets = [
        'SPIRAL_CORRIDOR', 'DNA_HELIX', 'SPRING', 'TWISTED_TOWER',
        'FIGHTER_JET', 'BOMBER', 'HELICOPTER', 'STAIRCASE', 'CHARACTER'
    ]
    
    print("\nPopulating latent space...")
    for preset in all_presets:
        vec = GeometryEncoder.encode_preset(preset, scene)
        latent_space.add_geometry(preset, vec)
    
    # Query with a preset
    query = "FIGHTER_JET"
    query_vec = latent_space.vectors[query]
    
    print(f"\nQuery: {query}")
    print("Finding 5 nearest neighbors...")
    
    neighbors = latent_space.get_neighbors(query_vec, k=6)  # 6 because query itself is included
    
    print("\nResults:")
    for i, (name, distance) in enumerate(neighbors):
        if name == query:
            print(f"  {i}. {name} (query) - distance: {distance:.3f}")
        else:
            print(f"  {i}. {name} - distance: {distance:.3f}")


def demo_distance_matrix():
    """Demo 5: Distance matrix between all presets"""
    print("\n" + "="*60)
    print("DEMO 5: Distance Matrix")
    print("="*60)
    
    scene = bpy.context.scene
    latent_space = get_latent_space()
    
    # Select a few presets for clarity
    presets = ['SPIRAL_CORRIDOR', 'FIGHTER_JET', 'CHARACTER', 'STAIRCASE']
    
    # Encode
    for preset in presets:
        vec = GeometryEncoder.encode_preset(preset, scene)
        latent_space.add_geometry(preset, vec)
    
    # Calculate distance matrix
    n = len(presets)
    distances = np.zeros((n, n))
    
    for i, preset1 in enumerate(presets):
        for j, preset2 in enumerate(presets):
            vec1 = latent_space.vectors[preset1]
            vec2 = latent_space.vectors[preset2]
            distances[i, j] = vec1.distance_to(vec2)
    
    # Print matrix
    print("\nDistance Matrix:")
    print("       ", end="")
    for preset in presets:
        print(f"{preset[:8]:>8}", end=" ")
    print()
    
    for i, preset1 in enumerate(presets):
        print(f"{preset1[:8]:>8}", end=" ")
        for j in range(n):
            print(f"{distances[i,j]:>8.3f}", end=" ")
        print()
    
    # Find most similar pair
    min_dist = float('inf')
    pair = None
    for i in range(n):
        for j in range(i+1, n):
            if distances[i,j] < min_dist:
                min_dist = distances[i,j]
                pair = (presets[i], presets[j])
    
    print(f"\nMost similar pair: {pair[0]} <-> {pair[1]} (distance: {min_dist:.3f})")


def demo_vector_arithmetic():
    """Demo 6: Vector arithmetic"""
    print("\n" + "="*60)
    print("DEMO 6: Vector Arithmetic")
    print("="*60)
    
    scene = bpy.context.scene
    
    # Encode presets
    vec_jet = GeometryEncoder.encode_preset("FIGHTER_JET", scene)
    vec_bomber = GeometryEncoder.encode_preset("BOMBER", scene)
    vec_heli = GeometryEncoder.encode_preset("HELICOPTER", scene)
    
    print("\nVector operations:")
    print("1. vec_jet + vec_bomber")
    vec_sum = vec_jet.add(vec_bomber, 1.0)
    print(f"   Result norm: {np.linalg.norm(vec_sum.vector):.3f}")
    
    print("\n2. vec_jet - vec_bomber")
    vec_diff = vec_jet.add(vec_bomber, -1.0)
    print(f"   Result norm: {np.linalg.norm(vec_diff.vector):.3f}")
    
    print("\n3. 0.5*vec_jet + 0.5*vec_heli")
    vec_avg = vec_jet.interpolate(vec_heli, 0.5)
    print(f"   Result norm: {np.linalg.norm(vec_avg.vector):.3f}")
    
    # Find nearest to sum
    print("\n4. Finding nearest preset to (vec_jet + vec_bomber):")
    nearest = GeometryDecoder.find_nearest_preset(vec_sum, scene)
    print(f"   Nearest: {nearest}")


def run_all_demos():
    """Run all demonstrations"""
    print("\n" + "#"*60)
    print("#" + " "*58 + "#")
    print("#  GEOMETRY VECTORS - LATENT SPACE DEMONSTRATION" + " "*10 + "#")
    print("#" + " "*58 + "#")
    print("#"*60)
    
    try:
        demo_basic_encoding()
        demo_interpolation()
        demo_blending()
        demo_similarity()
        demo_distance_matrix()
        demo_vector_arithmetic()
        
        print("\n" + "="*60)
        print("All demos completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_demos()
