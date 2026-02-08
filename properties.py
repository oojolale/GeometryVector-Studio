import bpy

def update_dropdown(self, context):
    print(f"Dropdown selected: {self.my_dropdown}")

# Icons for the preview popup
icon_preview_items = [
    ('QUESTION', "Question", "", 'QUESTION', 0),
    ('FILE_FOLDER', "Folder", "", 'FILE_FOLDER', 1),
    ('BLENDER', "Blender", "", 'BLENDER', 2),
    ('MESH_CUBE', "Cube", "", 'MESH_CUBE', 3),
    ('MATERIAL', "Material", "", 'MATERIAL', 4),
    ('IMAGE_DATA', "Image", "", 'IMAGE_DATA', 5),
    ('OBJECT_DATA', "Object", "", 'OBJECT_DATA', 6),
]

class FilePathItem(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="File Path")

class ListItem(bpy.types.PropertyGroup):
    id: bpy.props.IntProperty()
    name: bpy.props.StringProperty()

class PanelItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="Panel")
    expanded: bpy.props.BoolProperty(name="Expanded", default=True)

class ShapePartItem(bpy.types.PropertyGroup):
    """Property group for shape parts list"""
    name: bpy.props.StringProperty(name="Part Name")
    object_ref: bpy.props.StringProperty(name="Object Reference")

classes = (FilePathItem, ListItem, PanelItem, ShapePartItem)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.my_addon_selected_files = bpy.props.CollectionProperty(type=FilePathItem)
    bpy.types.Scene.my_dropdown = bpy.props.EnumProperty(
        name="Options",
        items=[
            ('OPTION_A', "Option A", "First option"),
            ('OPTION_B', "resourceChoose", "Second option"),
        ],
        update=update_dropdown
    )
    bpy.types.Scene.show_collapsible = bpy.props.BoolProperty(name="Show List", default=False)
    bpy.types.Scene.my_items = bpy.props.CollectionProperty(type=ListItem)
    bpy.types.Scene.my_panels = bpy.props.CollectionProperty(type=PanelItem)
    bpy.types.Scene.my_panels_active_index = bpy.props.IntProperty()
    bpy.types.Scene.my_icon_preview = bpy.props.EnumProperty(
        name="Icon Preview",
        items=icon_preview_items,
        default='QUESTION',
    )
    # New shape properties
    bpy.types.Scene.my_shape_dimensions = bpy.props.FloatVectorProperty(
        name="Dimensions",
        default=(2.0, 2.0, 2.0),
        min=0.001,
        subtype='XYZ'
    )
    bpy.types.Scene.my_shape_sphericity = bpy.props.FloatProperty(
        name="Sphericity",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        description="Transform cube to sphere"
    )
    # Additional topology transformation parameters
    bpy.types.Scene.my_shape_taper = bpy.props.FloatProperty(
        name="Taper",
        default=0.0,
        min=-1.0,
        max=1.0,
        subtype='FACTOR',
        description="Taper the shape (cone-like)"
    )
    bpy.types.Scene.my_shape_twist = bpy.props.FloatProperty(
        name="Twist",
        default=0.0,
        min=-3.14159,
        max=3.14159,
        subtype='ANGLE',
        description="Twist the shape along Z axis"
    )
    bpy.types.Scene.my_shape_bend = bpy.props.FloatProperty(
        name="Bend",
        default=0.0,
        min=-3.14159,
        max=3.14159,
        subtype='ANGLE',
        description="Bend the shape"
    )
    bpy.types.Scene.my_shape_inflate = bpy.props.FloatProperty(
        name="Inflate",
        default=0.0,
        min=-1.0,
        max=1.0,
        subtype='FACTOR',
        description="Inflate/deflate the shape"
    )
    bpy.types.Scene.my_shape_wave_amplitude = bpy.props.FloatProperty(
        name="Wave Amplitude",
        default=0.0,
        min=0.0,
        max=2.0,
        description="Wave deformation amplitude"
    )
    bpy.types.Scene.my_shape_wave_frequency = bpy.props.FloatProperty(
        name="Wave Frequency",
        default=1.0,
        min=0.1,
        max=10.0,
        description="Wave deformation frequency"
    )
    bpy.types.Scene.my_shape_noise_strength = bpy.props.FloatProperty(
        name="Noise Strength",
        default=0.0,
        min=0.0,
        max=2.0,
        description="Random noise displacement"
    )
    bpy.types.Scene.my_shape_noise_scale = bpy.props.FloatProperty(
        name="Noise Scale",
        default=0.5,
        min=0.01,
        max=5.0,
        description="Scale of noise pattern"
    )
    # Advanced helix/spiral parameters
    bpy.types.Scene.my_shape_helix_turns = bpy.props.IntProperty(
        name="Helix Turns",
        default=3,
        min=1,
        max=20,
        description="Number of spiral turns"
    )
    bpy.types.Scene.my_shape_helix_radius = bpy.props.FloatProperty(
        name="Helix Radius",
        default=2.0,
        min=0.1,
        max=10.0,
        description="Radius of helix spiral"
    )
    bpy.types.Scene.my_shape_helix_height = bpy.props.FloatProperty(
        name="Helix Height",
        default=10.0,
        min=1.0,
        max=50.0,
        description="Total height of helix"
    )
    bpy.types.Scene.my_shape_preset = bpy.props.EnumProperty(
        name="Preset",
        items=[
            ('NONE', "None", "No preset"),
            ('SPIRAL_CORRIDOR', "Spiral Corridor", "Create a spiral corridor"),
            ('DNA_HELIX', "DNA Double Helix", "Create DNA double helix structure"),
            ('SPRING', "Spring Coil", "Create spring coil"),
            ('TWISTED_TOWER', "Twisted Tower", "Create twisted tower structure"),
            ('FIGHTER_JET', "Fighter Jet", "Create fighter jet aircraft"),
            ('BOMBER', "Bomber Aircraft", "Create heavy bomber aircraft"),
            ('HELICOPTER', "Helicopter", "Create helicopter with rotor"),
            ('STAIRCASE', "Staircase", "Create staircase structure"),
            ('CHARACTER', "Character", "Create basic character model"),
        ],
        default='NONE',
        description="Apply shape preset"
    )
    # Aircraft-specific parameters
    bpy.types.Scene.my_aircraft_fuselage_length = bpy.props.FloatProperty(
        name="Fuselage Length",
        default=10.0,
        min=1.0,
        max=50.0,
        description="Length of aircraft fuselage"
    )
    bpy.types.Scene.my_aircraft_wing_span = bpy.props.FloatProperty(
        name="Wing Span",
        default=12.0,
        min=1.0,
        max=60.0,
        description="Width of aircraft wings"
    )
    bpy.types.Scene.my_aircraft_wing_sweep = bpy.props.FloatProperty(
        name="Wing Sweep Angle",
        default=0.0,
        min=-1.57,
        max=1.57,
        subtype='ANGLE',
        description="Sweep angle of wings (delta wing effect)"
    )
    bpy.types.Scene.my_aircraft_tail_size = bpy.props.FloatProperty(
        name="Tail Size",
        default=3.0,
        min=0.5,
        max=10.0,
        description="Size of tail stabilizers"
    )
    bpy.types.Scene.my_aircraft_engine_count = bpy.props.IntProperty(
        name="Engine Count",
        default=2,
        min=0,
        max=4,
        description="Number of engines"
    )
    # Shape parts collection
    bpy.types.Scene.my_shape_parts = bpy.props.CollectionProperty(type=ShapePartItem)
    bpy.types.Scene.my_shape_parts_index = bpy.props.IntProperty()
    
    # Staircase parameters
    bpy.types.Scene.my_stair_steps = bpy.props.IntProperty(
        name="Number of Steps",
        default=10,
        min=1,
        max=50,
        description="Number of stair steps"
    )
    bpy.types.Scene.my_stair_step_width = bpy.props.FloatProperty(
        name="Step Width",
        default=2.0,
        min=0.5,
        max=10.0,
        description="Width of each step"
    )
    bpy.types.Scene.my_stair_step_height = bpy.props.FloatProperty(
        name="Step Height",
        default=0.2,
        min=0.05,
        max=1.0,
        description="Height of each step"
    )
    bpy.types.Scene.my_stair_step_depth = bpy.props.FloatProperty(
        name="Step Depth",
        default=0.3,
        min=0.1,
        max=2.0,
        description="Depth of each step"
    )
    bpy.types.Scene.my_stair_type = bpy.props.EnumProperty(
        name="Stair Type",
        items=[
            ('STRAIGHT', "Straight", "Straight staircase"),
            ('SPIRAL', "Spiral", "Spiral staircase"),
            ('L_SHAPED', "L-Shaped", "L-shaped staircase with landing"),
        ],
        default='STRAIGHT',
        description="Type of staircase"
    )
    # Character parameters
    bpy.types.Scene.my_character_gender = bpy.props.EnumProperty(
        name="Gender",
        items=[
            ('MALE', "Male", "Male character"),
            ('FEMALE', "Female", "Female character"),
        ],
        default='MALE',
        description="Character gender"
    )
    bpy.types.Scene.my_character_age = bpy.props.EnumProperty(
        name="Age Group",
        items=[
            ('CHILD', "Child", "Child (5-12 years)"),
            ('TEEN', "Teen", "Teenager (13-19 years)"),
            ('ADULT', "Adult", "Adult (20-60 years)"),
            ('ELDER', "Elder", "Elder (60+ years)"),
        ],
        default='ADULT',
        description="Character age group"
    )
    bpy.types.Scene.my_character_height = bpy.props.FloatProperty(
        name="Height",
        default=1.75,
        min=0.5,
        max=2.5,
        description="Character height in meters"
    )
    bpy.types.Scene.my_character_build = bpy.props.FloatProperty(
        name="Build",
        default=1.0,
        min=0.5,
        max=1.5,
        subtype='FACTOR',
        description="Character build (thin to heavy)"
    )
    # Collapse/expand states for parameter sections
    bpy.types.Scene.show_aircraft_params = bpy.props.BoolProperty(name="Show Aircraft Parameters", default=True)
    bpy.types.Scene.show_basic_props = bpy.props.BoolProperty(name="Show Basic Properties", default=True)
    bpy.types.Scene.show_helix_params = bpy.props.BoolProperty(name="Show Helix Parameters", default=False)
    bpy.types.Scene.show_topology_transforms = bpy.props.BoolProperty(name="Show Topology Transformations", default=False)
    bpy.types.Scene.show_wave_deform = bpy.props.BoolProperty(name="Show Wave Deformation", default=False)
    bpy.types.Scene.show_noise_displace = bpy.props.BoolProperty(name="Show Noise Displacement", default=False)
    bpy.types.Scene.show_stair_params = bpy.props.BoolProperty(name="Show Staircase Parameters", default=True)
    bpy.types.Scene.show_character_params = bpy.props.BoolProperty(name="Show Character Parameters", default=True)
    
    # Geometry vector editing properties
    bpy.types.Scene.geom_vector_current = bpy.props.FloatVectorProperty(
        name="Geometry Vector",
        size=32,
        default=[0.0] * 32,
        description="Current 32D geometry vector for editing"
    )
    bpy.types.Scene.geom_vector_clipboard = bpy.props.FloatVectorProperty(
        name="Vector Clipboard",
        size=32,
        default=[0.0] * 32,
        description="Clipboard for vector operations"
    )
    bpy.types.Scene.show_vector_editor = bpy.props.BoolProperty(
        name="Show Vector Editor",
        default=False,
        description="Show detailed vector editor"
    )
    bpy.types.Scene.vector_arithmetic_operation = bpy.props.EnumProperty(
        name="Operation",
        items=[
            ('ADD', "Add (+)", "Add clipboard to current vector"),
            ('SUBTRACT', "Subtract (-)", "Subtract clipboard from current vector"),
            ('MULTIPLY', "Multiply (*)", "Multiply current vector by scalar"),
            ('DIVIDE', "Divide (/)", "Divide current vector by scalar"),
            ('LERP', "Interpolate", "Linear interpolation with clipboard"),
        ],
        default='ADD',
        description="Vector arithmetic operation"
    )
    bpy.types.Scene.vector_scalar_value = bpy.props.FloatProperty(
        name="Scalar",
        default=1.0,
        description="Scalar value for multiply/divide operations"
    )
    bpy.types.Scene.vector_lerp_factor = bpy.props.FloatProperty(
        name="Blend Factor",
        default=0.5,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        description="Interpolation factor (0=current, 1=clipboard)"
    )
    bpy.types.Scene.vector_source_preset = bpy.props.StringProperty(
        name="Source Preset",
        default="NONE",
        description="The preset this vector was loaded from"
    )
    
    # Store original mesh data name for imported objects
    bpy.types.Scene.vector_source_mesh = bpy.props.StringProperty(
        name="Source Mesh",
        default="",
        description="Name of the original mesh data for imported objects"
    )
    
    # Auto-bind vector editor to selected object
    bpy.types.Scene.vector_editor_auto_bind = bpy.props.BoolProperty(
        name="Auto-Bind to Selection",
        default=True,
        description="Automatically load vectors from selected object"
    )

def unregister():
    try:
        del bpy.types.Scene.vector_editor_auto_bind
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.vector_source_preset
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.vector_source_mesh
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.vector_lerp_factor
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.vector_scalar_value
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.vector_arithmetic_operation
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.show_vector_editor
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.geom_vector_clipboard
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.geom_vector_current
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.show_character_params
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.show_stair_params
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.show_noise_displace
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.show_wave_deform
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.show_topology_transforms
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.show_helix_params
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.show_basic_props
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.show_aircraft_params
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_character_build
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_character_height
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_character_age
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_character_gender
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_stair_type
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_stair_step_depth
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_stair_step_height
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_stair_step_width
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_stair_steps
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_parts_index
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_parts
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_aircraft_engine_count
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_aircraft_tail_size
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_aircraft_wing_sweep
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_aircraft_wing_span
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_aircraft_fuselage_length
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_preset
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_helix_height
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_helix_radius
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_helix_turns
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_noise_scale
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_noise_strength
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_wave_frequency
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_wave_amplitude
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_inflate
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_bend
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_twist
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_taper
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_sphericity
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_shape_dimensions
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_icon_preview
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_panels_active_index
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_panels
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_items
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.show_collapsible
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_dropdown
    except AttributeError:
        pass
    try:
        del bpy.types.Scene.my_addon_selected_files
    except AttributeError:
        pass

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
