"""
Geometry Encoder/Decoder System
Unified representation of geometric objects as high-dimensional vectors
"""

import bpy
import math
import numpy as np
from mathutils import Vector
from typing import Dict, List, Tuple, Optional


class GeometryVector:
    """
    Unified vector representation for all geometric objects
    Maps any mesh to a standardized N-dimensional parameter space
    """
    
    # Define the unified parameter space dimensions
    VECTOR_DIM = 32  # Total dimensionality of latent space
    
    # Parameter indices in the vector
    IDX_SHAPE_TYPE = 0          # 0-1: Shape type (continuous encoding)
    IDX_COMPLEXITY = 1          # Geometric complexity measure
    IDX_SCALE_X = 2             # Global scale
    IDX_SCALE_Y = 3
    IDX_SCALE_Z = 4
    IDX_SYMMETRY = 5            # Symmetry measure
    IDX_CURVATURE = 6           # Overall curvature
    IDX_TOPOLOGY_GENUS = 7      # Topological genus (holes)
    IDX_ASPECT_RATIO_XY = 8     # Shape ratios
    IDX_ASPECT_RATIO_XZ = 9
    IDX_ASPECT_RATIO_YZ = 10
    IDX_ELONGATION = 11         # Elongation factor
    IDX_TWIST = 12              # Twist amount
    IDX_TAPER = 13              # Taper factor
    IDX_BEND = 14               # Bending
    IDX_WAVE_FREQ = 15          # Wave parameters
    IDX_WAVE_AMP = 16
    IDX_NOISE_SCALE = 17        # Noise parameters
    IDX_NOISE_STRENGTH = 18
    IDX_SPHERICITY = 19         # Shape morphing
    IDX_CUBICITY = 20
    IDX_CYLINDRICITY = 21
    IDX_ROT_X = 22              # Rotation angles (radians)
    IDX_ROT_Y = 23
    IDX_ROT_Z = 24
    IDX_LOC_X = 25              # Location (position)
    IDX_LOC_Y = 26
    IDX_LOC_Z = 27
    # Universal appearance parameters (topology-agnostic)
    IDX_SMOOTHNESS = 28         # Surface smoothness (0-1)
    IDX_EDGE_SHARPNESS = 29     # Edge sharpness (0-1)
    IDX_INFLATION = 30          # Inflate/deflate (-1 to 1)
    IDX_RANDOMNESS = 31         # Random displacement (0-1)
    
    def __init__(self, vector: Optional[np.ndarray] = None):
        """Initialize with vector or create zero vector"""
        if vector is not None:
            self.vector = np.array(vector, dtype=np.float32)
        else:
            self.vector = np.zeros(self.VECTOR_DIM, dtype=np.float32)
    
    def __repr__(self):
        return f"GeometryVector(dim={self.VECTOR_DIM}, norm={np.linalg.norm(self.vector):.3f})"
    
    def to_dict(self) -> Dict[str, float]:
        """Convert vector to named parameters"""
        return {
            'shape_type': float(self.vector[self.IDX_SHAPE_TYPE]),
            'complexity': float(self.vector[self.IDX_COMPLEXITY]),
            'scale': [float(self.vector[i]) for i in [self.IDX_SCALE_X, self.IDX_SCALE_Y, self.IDX_SCALE_Z]],
            'symmetry': float(self.vector[self.IDX_SYMMETRY]),
            'curvature': float(self.vector[self.IDX_CURVATURE]),
            'topology_genus': float(self.vector[self.IDX_TOPOLOGY_GENUS]),
            'aspect_ratios': [float(self.vector[i]) for i in [self.IDX_ASPECT_RATIO_XY, self.IDX_ASPECT_RATIO_XZ, self.IDX_ASPECT_RATIO_YZ]],
            'deformations': {
                'elongation': float(self.vector[self.IDX_ELONGATION]),
                'twist': float(self.vector[self.IDX_TWIST]),
                'taper': float(self.vector[self.IDX_TAPER]),
                'bend': float(self.vector[self.IDX_BEND]),
            },
            'wave': {
                'frequency': float(self.vector[self.IDX_WAVE_FREQ]),
                'amplitude': float(self.vector[self.IDX_WAVE_AMP]),
            },
            'noise': {
                'scale': float(self.vector[self.IDX_NOISE_SCALE]),
                'strength': float(self.vector[self.IDX_NOISE_STRENGTH]),
            },
            'shape_morphing': {
                'sphericity': float(self.vector[self.IDX_SPHERICITY]),
                'cubicity': float(self.vector[self.IDX_CUBICITY]),
                'cylindricity': float(self.vector[self.IDX_CYLINDRICITY]),
            }
        }
    
    def distance_to(self, other: 'GeometryVector') -> float:
        """Calculate Euclidean distance to another geometry vector"""
        return float(np.linalg.norm(self.vector - other.vector))
    
    def interpolate(self, other: 'GeometryVector', t: float) -> 'GeometryVector':
        """Linear interpolation between two geometry vectors"""
        t = np.clip(t, 0.0, 1.0)
        new_vector = (1 - t) * self.vector + t * other.vector
        return GeometryVector(new_vector)
    
    def add(self, other: 'GeometryVector', weight: float = 1.0) -> 'GeometryVector':
        """Vector addition in latent space"""
        new_vector = self.vector + weight * other.vector
        return GeometryVector(new_vector)
    
    def normalize(self) -> 'GeometryVector':
        """Normalize the vector"""
        norm = np.linalg.norm(self.vector)
        if norm > 1e-6:
            return GeometryVector(self.vector / norm)
        return GeometryVector(self.vector)


class GeometryEncoder:
    """
    Encodes Blender objects/presets into unified geometry vectors
    """
    
    @staticmethod
    def encode_preset(preset_name: str, scene) -> GeometryVector:
        """Encode a preset into geometry vector"""
        vec = GeometryVector()
        
        if preset_name == 'NONE':
            # Default cube
            vec.vector[GeometryVector.IDX_SHAPE_TYPE] = 0.0
            vec.vector[GeometryVector.IDX_COMPLEXITY] = 0.1
            vec.vector[GeometryVector.IDX_SCALE_X:GeometryVector.IDX_SCALE_Z+1] = [1.0, 1.0, 1.0]
            vec.vector[GeometryVector.IDX_CUBICITY] = 1.0
            
        elif preset_name == 'SPIRAL_CORRIDOR':
            vec.vector[GeometryVector.IDX_SHAPE_TYPE] = 0.15
            vec.vector[GeometryVector.IDX_COMPLEXITY] = 0.7
            vec.vector[GeometryVector.IDX_SCALE_X:GeometryVector.IDX_SCALE_Z+1] = [0.5, 0.5, 20.0]
            vec.vector[GeometryVector.IDX_ELONGATION] = 0.8
            vec.vector[GeometryVector.IDX_TWIST] = 3.14
            vec.vector[GeometryVector.IDX_SPHERICITY] = 0.3
            vec.vector[GeometryVector.IDX_TOPOLOGY_GENUS] = 0.5
            
        elif preset_name == 'DNA_HELIX':
            vec.vector[GeometryVector.IDX_SHAPE_TYPE] = 0.2
            vec.vector[GeometryVector.IDX_COMPLEXITY] = 0.8
            vec.vector[GeometryVector.IDX_SCALE_X:GeometryVector.IDX_SCALE_Z+1] = [0.2, 0.2, 15.0]
            vec.vector[GeometryVector.IDX_ELONGATION] = 0.9
            vec.vector[GeometryVector.IDX_TWIST] = 6.28
            vec.vector[GeometryVector.IDX_SPHERICITY] = 1.0
            vec.vector[GeometryVector.IDX_SYMMETRY] = 0.9
            
        elif preset_name == 'SPRING':
            vec.vector[GeometryVector.IDX_SHAPE_TYPE] = 0.25
            vec.vector[GeometryVector.IDX_COMPLEXITY] = 0.6
            vec.vector[GeometryVector.IDX_SCALE_X:GeometryVector.IDX_SCALE_Z+1] = [0.3, 0.3, 12.0]
            vec.vector[GeometryVector.IDX_ELONGATION] = 0.85
            vec.vector[GeometryVector.IDX_TWIST] = 9.42
            vec.vector[GeometryVector.IDX_SPHERICITY] = 1.0
            vec.vector[GeometryVector.IDX_CYLINDRICITY] = 0.8
            
        elif preset_name == 'TWISTED_TOWER':
            vec.vector[GeometryVector.IDX_SHAPE_TYPE] = 0.3
            vec.vector[GeometryVector.IDX_COMPLEXITY] = 0.5
            vec.vector[GeometryVector.IDX_SCALE_X:GeometryVector.IDX_SCALE_Z+1] = [1.5, 1.5, 8.0]
            vec.vector[GeometryVector.IDX_ELONGATION] = 0.7
            vec.vector[GeometryVector.IDX_TWIST] = 1.57
            vec.vector[GeometryVector.IDX_TAPER] = 0.2
            vec.vector[GeometryVector.IDX_CUBICITY] = 0.8
            
        elif preset_name == 'FIGHTER_JET':
            vec.vector[GeometryVector.IDX_SHAPE_TYPE] = 0.5
            vec.vector[GeometryVector.IDX_COMPLEXITY] = 0.75
            vec.vector[GeometryVector.IDX_SCALE_X:GeometryVector.IDX_SCALE_Z+1] = [12.0, 10.0, 3.0]
            vec.vector[GeometryVector.IDX_ASPECT_RATIO_XY] = 1.2
            vec.vector[GeometryVector.IDX_SYMMETRY] = 1.0
            vec.vector[GeometryVector.IDX_ELONGATION] = 0.9
            vec.vector[GeometryVector.IDX_TAPER] = 0.6
            vec.vector[GeometryVector.IDX_CYLINDRICITY] = 0.7
            
        elif preset_name == 'BOMBER':
            vec.vector[GeometryVector.IDX_SHAPE_TYPE] = 0.55
            vec.vector[GeometryVector.IDX_COMPLEXITY] = 0.8
            vec.vector[GeometryVector.IDX_SCALE_X:GeometryVector.IDX_SCALE_Z+1] = [20.0, 30.0, 5.0]
            vec.vector[GeometryVector.IDX_ASPECT_RATIO_XY] = 0.67
            vec.vector[GeometryVector.IDX_SYMMETRY] = 1.0
            vec.vector[GeometryVector.IDX_ELONGATION] = 0.8
            vec.vector[GeometryVector.IDX_CYLINDRICITY] = 0.9
            
        elif preset_name == 'HELICOPTER':
            vec.vector[GeometryVector.IDX_SHAPE_TYPE] = 0.6
            vec.vector[GeometryVector.IDX_COMPLEXITY] = 0.85
            vec.vector[GeometryVector.IDX_SCALE_X:GeometryVector.IDX_SCALE_Z+1] = [10.0, 12.0, 6.0]
            vec.vector[GeometryVector.IDX_SYMMETRY] = 1.0
            vec.vector[GeometryVector.IDX_SPHERICITY] = 0.6
            vec.vector[GeometryVector.IDX_TOPOLOGY_GENUS] = 0.3
            
        elif preset_name == 'STAIRCASE':
            vec.vector[GeometryVector.IDX_SHAPE_TYPE] = 0.7
            vec.vector[GeometryVector.IDX_COMPLEXITY] = 0.4
            vec.vector[GeometryVector.IDX_SCALE_X:GeometryVector.IDX_SCALE_Z+1] = [2.0, 3.0, 2.0]
            vec.vector[GeometryVector.IDX_SYMMETRY] = 0.5
            vec.vector[GeometryVector.IDX_CUBICITY] = 0.9
            vec.vector[GeometryVector.IDX_ELONGATION] = 0.6
            
        elif preset_name == 'CHARACTER':
            vec.vector[GeometryVector.IDX_SHAPE_TYPE] = 0.8
            vec.vector[GeometryVector.IDX_COMPLEXITY] = 0.9
            vec.vector[GeometryVector.IDX_SCALE_X:GeometryVector.IDX_SCALE_Z+1] = [0.6, 0.4, 1.75]
            vec.vector[GeometryVector.IDX_SYMMETRY] = 1.0
            vec.vector[GeometryVector.IDX_SPHERICITY] = 0.5
            vec.vector[GeometryVector.IDX_CYLINDRICITY] = 0.6
            vec.vector[GeometryVector.IDX_TOPOLOGY_GENUS] = 0.7  # Multiple parts
            
        return vec
    
    @staticmethod
    def encode_object(obj) -> GeometryVector:
        """Encode a Blender object into geometry vector"""
        vec = GeometryVector()
        
        if obj is None or obj.type != 'MESH':
            return vec
        
        mesh = obj.data
        
        # Basic measurements
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        dimensions = obj.dimensions
        
        # Scale - store actual object scale (not dimensions)
        # This preserves the original scale factor when restoring from cached mesh
        vec.vector[GeometryVector.IDX_SCALE_X] = obj.scale.x
        vec.vector[GeometryVector.IDX_SCALE_Y] = obj.scale.y
        vec.vector[GeometryVector.IDX_SCALE_Z] = obj.scale.z
        
        # Location (position in world space)
        vec.vector[GeometryVector.IDX_LOC_X] = obj.location.x
        vec.vector[GeometryVector.IDX_LOC_Y] = obj.location.y
        vec.vector[GeometryVector.IDX_LOC_Z] = obj.location.z
        
        # Rotation (store in radians)
        vec.vector[GeometryVector.IDX_ROT_X] = obj.rotation_euler.x
        vec.vector[GeometryVector.IDX_ROT_Y] = obj.rotation_euler.y
        vec.vector[GeometryVector.IDX_ROT_Z] = obj.rotation_euler.z
        
        # Complexity (vertex count normalized)
        vertex_count = len(mesh.vertices)
        vec.vector[GeometryVector.IDX_COMPLEXITY] = min(1.0, vertex_count / 10000.0)
        
        # Aspect ratios
        if dimensions.y > 1e-6:
            vec.vector[GeometryVector.IDX_ASPECT_RATIO_XY] = dimensions.x / dimensions.y
        if dimensions.z > 1e-6:
            vec.vector[GeometryVector.IDX_ASPECT_RATIO_XZ] = dimensions.x / dimensions.z
            vec.vector[GeometryVector.IDX_ASPECT_RATIO_YZ] = dimensions.y / dimensions.z
        
        # Elongation
        max_dim = max(dimensions.x, dimensions.y, dimensions.z)
        if max_dim > 1e-6:
            vec.vector[GeometryVector.IDX_ELONGATION] = max_dim / (dimensions.x + dimensions.y + dimensions.z)
        
        # Analyze modifiers
        for mod in obj.modifiers:
            if mod.type == 'SUBSURF':
                # Use for both curvature (old) and smoothness (new)
                vec.vector[GeometryVector.IDX_CURVATURE] = 0.5 + mod.levels * 0.1
                vec.vector[GeometryVector.IDX_SMOOTHNESS] = mod.levels / 3.0  # Normalize to 0-1
            elif mod.type == 'EDGE_SPLIT':
                # Edge sharpness
                if mod.use_edge_angle:
                    vec.vector[GeometryVector.IDX_EDGE_SHARPNESS] = 1.0 - (mod.split_angle / math.pi)
            elif mod.type == 'CAST':
                vec.vector[GeometryVector.IDX_SPHERICITY] = mod.factor
            elif mod.type == 'SIMPLE_DEFORM':
                if mod.deform_method == 'TWIST':
                    vec.vector[GeometryVector.IDX_TWIST] = mod.angle / (2 * math.pi)
                elif mod.deform_method == 'TAPER':
                    vec.vector[GeometryVector.IDX_TAPER] = mod.factor
                elif mod.deform_method == 'BEND':
                    vec.vector[GeometryVector.IDX_BEND] = mod.angle / (2 * math.pi)
            elif mod.type == 'WAVE':
                vec.vector[GeometryVector.IDX_WAVE_AMP] = mod.height
                vec.vector[GeometryVector.IDX_WAVE_FREQ] = 1.0 / max(mod.width, 0.1)
            elif mod.type == 'DISPLACE':
                # Distinguish between noise and inflation
                if mod.direction == 'NORMAL':
                    # Inflation: displacement along normals
                    vec.vector[GeometryVector.IDX_INFLATION] = mod.strength / 0.5
                elif mod.texture and mod.texture.type == 'CLOUDS':
                    # Noise/randomness: textured displacement
                    if 'Random' in mod.name or 'random' in mod.name.lower():
                        vec.vector[GeometryVector.IDX_RANDOMNESS] = mod.strength / 0.1
                    else:
                        vec.vector[GeometryVector.IDX_NOISE_STRENGTH] = mod.strength
                        vec.vector[GeometryVector.IDX_NOISE_SCALE] = mod.texture.noise_scale
        
        return vec
    
    @staticmethod
    def encode_scene_parameters(scene) -> GeometryVector:
        """Encode current scene parameters into vector"""
        vec = GeometryVector()
        
        # Basic dimensions
        dims = scene.my_shape_dimensions
        vec.vector[GeometryVector.IDX_SCALE_X:GeometryVector.IDX_SCALE_Z+1] = [dims[0], dims[1], dims[2]]
        
        # Topology transforms
        vec.vector[GeometryVector.IDX_SPHERICITY] = scene.my_shape_sphericity
        vec.vector[GeometryVector.IDX_TAPER] = scene.my_shape_taper
        vec.vector[GeometryVector.IDX_TWIST] = scene.my_shape_twist / (2 * math.pi)
        vec.vector[GeometryVector.IDX_BEND] = scene.my_shape_bend / (2 * math.pi)
        
        # Wave and noise
        vec.vector[GeometryVector.IDX_WAVE_AMP] = scene.my_shape_wave_amplitude
        vec.vector[GeometryVector.IDX_WAVE_FREQ] = scene.my_shape_wave_frequency
        vec.vector[GeometryVector.IDX_NOISE_STRENGTH] = scene.my_shape_noise_strength
        vec.vector[GeometryVector.IDX_NOISE_SCALE] = scene.my_shape_noise_scale
        
        return vec


class GeometryDecoder:
    """
    Decodes geometry vectors back into Blender scene parameters
    """
    
    @staticmethod
    def decode_to_scene(vec: GeometryVector, scene) -> Dict[str, any]:
        """Decode vector and apply to scene parameters"""
        params = {}
        
        # Basic dimensions
        params['dimensions'] = [
            vec.vector[GeometryVector.IDX_SCALE_X],
            vec.vector[GeometryVector.IDX_SCALE_Y],
            vec.vector[GeometryVector.IDX_SCALE_Z]
        ]
        scene.my_shape_dimensions = params['dimensions']
        
        # Topology transforms
        params['sphericity'] = vec.vector[GeometryVector.IDX_SPHERICITY]
        scene.my_shape_sphericity = params['sphericity']
        
        params['taper'] = vec.vector[GeometryVector.IDX_TAPER]
        scene.my_shape_taper = params['taper']
        
        params['twist'] = vec.vector[GeometryVector.IDX_TWIST] * 2 * math.pi
        scene.my_shape_twist = params['twist']
        
        params['bend'] = vec.vector[GeometryVector.IDX_BEND] * 2 * math.pi
        scene.my_shape_bend = params['bend']
        
        # Wave and noise
        params['wave_amplitude'] = vec.vector[GeometryVector.IDX_WAVE_AMP]
        scene.my_shape_wave_amplitude = params['wave_amplitude']
        
        params['wave_frequency'] = vec.vector[GeometryVector.IDX_WAVE_FREQ]
        scene.my_shape_wave_frequency = params['wave_frequency']
        
        params['noise_strength'] = vec.vector[GeometryVector.IDX_NOISE_STRENGTH]
        scene.my_shape_noise_strength = params['noise_strength']
        
        params['noise_scale'] = vec.vector[GeometryVector.IDX_NOISE_SCALE]
        scene.my_shape_noise_scale = params['noise_scale']
        
        return params
    
    @staticmethod
    def find_nearest_preset(vec: GeometryVector, scene) -> str:
        """Find the closest preset to the given vector"""
        presets = ['NONE', 'SPIRAL_CORRIDOR', 'DNA_HELIX', 'SPRING', 'TWISTED_TOWER',
                   'FIGHTER_JET', 'BOMBER', 'HELICOPTER', 'STAIRCASE', 'CHARACTER']
        
        min_distance = float('inf')
        nearest_preset = 'NONE'
        
        for preset in presets:
            preset_vec = GeometryEncoder.encode_preset(preset, scene)
            distance = vec.distance_to(preset_vec)
            if distance < min_distance:
                min_distance = distance
                nearest_preset = preset
        
        return nearest_preset


class GeometryLatentSpace:
    """
    Manages the latent space of geometry representations
    Provides operations like interpolation, arithmetic, and clustering
    """
    
    def __init__(self):
        self.vectors: Dict[str, GeometryVector] = {}
    
    def add_geometry(self, name: str, vec: GeometryVector):
        """Add a geometry vector to the space"""
        self.vectors[name] = vec
    
    def interpolate_path(self, start_name: str, end_name: str, steps: int = 10) -> List[GeometryVector]:
        """Generate interpolation path between two geometries"""
        if start_name not in self.vectors or end_name not in self.vectors:
            return []
        
        start_vec = self.vectors[start_name]
        end_vec = self.vectors[end_name]
        
        path = []
        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 0
            path.append(start_vec.interpolate(end_vec, t))
        
        return path
    
    def blend_geometries(self, names: List[str], weights: List[float]) -> Optional[GeometryVector]:
        """Blend multiple geometries with given weights"""
        if len(names) != len(weights):
            return None
        
        result = GeometryVector()
        total_weight = sum(weights)
        
        if total_weight < 1e-6:
            return result
        
        for name, weight in zip(names, weights):
            if name in self.vectors:
                result = result.add(self.vectors[name], weight / total_weight)
        
        return result
    
    def get_neighbors(self, vec: GeometryVector, k: int = 5) -> List[Tuple[str, float]]:
        """Find k nearest neighbors in latent space"""
        distances = []
        for name, stored_vec in self.vectors.items():
            dist = vec.distance_to(stored_vec)
            distances.append((name, dist))
        
        distances.sort(key=lambda x: x[1])
        return distances[:k]


# Singleton instance
_latent_space = GeometryLatentSpace()

def get_latent_space() -> GeometryLatentSpace:
    """Get the global latent space instance"""
    return _latent_space
