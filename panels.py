import bpy
import os

class VIEW3D_PT_my_panel(bpy.types.Panel):
    bl_label = "Simple Panel"
    bl_idname = "VIEW3D_PT_my_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'My Addon'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Button to run external script
        layout.operator("myaddon.button")
        # Button to open icon popup (without passing item data)
        layout.operator("myaddon.open_icon_popup", text="Open Icon Popup")

        # Dropdown
        layout.prop(scene, "my_dropdown")

        # --- Resource selection (only when OPTION_B is active) ---
        if scene.my_dropdown == 'OPTION_B':
            row = layout.row()
            row.operator("object.choose_person_files", text="Select Resources")
            if scene.my_addon_selected_files:
                row.operator("object.clear_person_files", text="Clear")

            if scene.my_addon_selected_files:
                box = layout.box()
                col = box.column(align=True)
                for i, item in enumerate(scene.my_addon_selected_files):
                    row = col.row(align=True)
                    row.label(text=os.path.basename(item.path))
                    open_op = row.operator("object.open_resource", text="", icon='FILE')
                    open_op.filepath = item.path
                    remove_op = row.operator("object.remove_selected_file", text="", icon='X')
                    remove_op.index = i
                layout.label(text=f"Total files: {len(scene.my_addon_selected_files)}")
            else:
                layout.label(text="No files selected")

        # --- Collapsible item list ---
        icon = 'TRIA_DOWN' if scene.show_collapsible else 'TRIA_RIGHT'
        layout.operator(
            "myaddon.toggle_collapsible",
            icon=icon,
            text="List of Items",
            emboss=False
        )

        if scene.show_collapsible:
            box = layout.box()
            if not scene.my_items:
                box.label(text="No items", icon='INFO')
                box.operator("myaddon.init_items", icon='ADD')
            else:
                for item in scene.my_items:
                    row = box.row()
                    select_op = row.operator("myaddon.select_item", text=item.name)
                    select_op.item_id = item.id
                    select_op.item_name = item.name
                    # Small button to open icon popup with this item's data
                    popup_op = row.operator("myaddon.open_icon_popup", text="", icon='IMAGE_DATA')
                    popup_op.item_id = item.id
                    popup_op.item_name = item.name

        # --- API Fetch ---
        layout.separator()
        box = layout.box()
        box.label(text="API Fetch")
        box.operator("myaddon.fetch_api", icon='URL')

        # --- Reorderable Panels ---
        layout.separator()
        layout.label(text="Reorderable Panels:")

        rows = min(len(scene.my_panels), 10) if scene.my_panels else 4
        layout.template_list(
            "MYADDON_UL_panels_list", "",
            scene, "my_panels",
            scene, "my_panels_active_index",
            rows=rows
        )

        # Add new panel button
        layout.operator("myaddon.add_panel", icon='ADD', text="Add Panel")

class VIEW3D_PT_my_second_panel(bpy.types.Panel):
    bl_label = "Second Panel"
    bl_idname = "VIEW3D_PT_my_second_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'My Addon'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Row 1")
        row.operator("myaddon.button", text="Button A")

        split = layout.split(factor=0.5)
        col1 = split.column()
        col2 = split.column()
        col1.label(text="Left Column")
        col2.label(text="Right Column")

        box = layout.box()
        box.label(text="Box Title")
        box.operator("myaddon.init_items", text="Init Items")

# New panel for shape transformation
class VIEW3D_PT_shape_transformer(bpy.types.Panel):
    bl_label = "Shape Transformer"
    bl_idname = "VIEW3D_PT_shape_transformer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'My Addon'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Preset selector
        box = layout.box()
        box.label(text="Quick Presets", icon='PRESET')
        box.prop(scene, "my_shape_preset", text="")
        if scene.my_shape_preset != 'NONE':
            box.operator("myaddon.apply_preset", icon='PLAY', text="Apply Preset")

        # Aircraft parameters (collapsible)
        if scene.my_shape_preset in ['FIGHTER_JET', 'BOMBER', 'HELICOPTER']:
            box = layout.box()
            row = box.row()
            row.prop(scene, "show_aircraft_params", 
                    icon='TRIA_DOWN' if scene.show_aircraft_params else 'TRIA_RIGHT',
                    icon_only=True, emboss=False)
            row.label(text="Aircraft Parameters", icon='LIGHT_SUN')
            
            if scene.show_aircraft_params:
                box.prop(scene, "my_aircraft_fuselage_length")
                box.prop(scene, "my_aircraft_wing_span")
                box.prop(scene, "my_aircraft_wing_sweep")
                box.prop(scene, "my_aircraft_tail_size")
                box.prop(scene, "my_aircraft_engine_count")
        
        # Staircase parameters (collapsible)
        if scene.my_shape_preset == 'STAIRCASE':
            box = layout.box()
            row = box.row()
            row.prop(scene, "show_stair_params",
                    icon='TRIA_DOWN' if scene.show_stair_params else 'TRIA_RIGHT',
                    icon_only=True, emboss=False)
            row.label(text="Staircase Parameters", icon='MESH_GRID')
            
            if scene.show_stair_params:
                box.prop(scene, "my_stair_type")
                box.prop(scene, "my_stair_steps")
                box.prop(scene, "my_stair_step_width")
                box.prop(scene, "my_stair_step_height")
                box.prop(scene, "my_stair_step_depth")
        
        # Character parameters (collapsible)
        if scene.my_shape_preset == 'CHARACTER':
            box = layout.box()
            row = box.row()
            row.prop(scene, "show_character_params",
                    icon='TRIA_DOWN' if scene.show_character_params else 'TRIA_RIGHT',
                    icon_only=True, emboss=False)
            row.label(text="Character Parameters", icon='ARMATURE_DATA')
            
            if scene.show_character_params:
                box.prop(scene, "my_character_gender")
                box.prop(scene, "my_character_age")
                box.prop(scene, "my_character_height")
                box.prop(scene, "my_character_build", slider=True)

        # Basic dimensions (collapsible)
        box = layout.box()
        row = box.row()
        row.prop(scene, "show_basic_props",
                icon='TRIA_DOWN' if scene.show_basic_props else 'TRIA_RIGHT',
                icon_only=True, emboss=False)
        row.label(text="Basic Properties", icon='MESH_CUBE')
        
        if scene.show_basic_props:
            box.prop(scene, "my_shape_dimensions")
        
        # Helix/Spiral parameters (collapsible)
        box = layout.box()
        row = box.row()
        row.prop(scene, "show_helix_params",
                icon='TRIA_DOWN' if scene.show_helix_params else 'TRIA_RIGHT',
                icon_only=True, emboss=False)
        row.label(text="Helix/Spiral Parameters", icon='CURVE_BEZCIRCLE')
        
        if scene.show_helix_params:
            box.prop(scene, "my_shape_helix_turns")
            box.prop(scene, "my_shape_helix_radius")
            box.prop(scene, "my_shape_helix_height")
        
        # Topology transformations (collapsible)
        box = layout.box()
        row = box.row()
        row.prop(scene, "show_topology_transforms",
                icon='TRIA_DOWN' if scene.show_topology_transforms else 'TRIA_RIGHT',
                icon_only=True, emboss=False)
        row.label(text="Topology Transformations", icon='MOD_SIMPLEDEFORM')
        
        if scene.show_topology_transforms:
            box.prop(scene, "my_shape_sphericity", slider=True)
            box.prop(scene, "my_shape_taper", slider=True)
            box.prop(scene, "my_shape_twist", slider=True)
            box.prop(scene, "my_shape_bend", slider=True)
            box.prop(scene, "my_shape_inflate", slider=True)
        
        # Wave deformation (collapsible)
        box = layout.box()
        row = box.row()
        row.prop(scene, "show_wave_deform",
                icon='TRIA_DOWN' if scene.show_wave_deform else 'TRIA_RIGHT',
                icon_only=True, emboss=False)
        row.label(text="Wave Deformation", icon='MOD_WAVE')
        
        if scene.show_wave_deform:
            box.prop(scene, "my_shape_wave_amplitude", slider=True)
            box.prop(scene, "my_shape_wave_frequency", slider=True)
        
        # Noise displacement (collapsible)
        box = layout.box()
        row = box.row()
        row.prop(scene, "show_noise_displace",
                icon='TRIA_DOWN' if scene.show_noise_displace else 'TRIA_RIGHT',
                icon_only=True, emboss=False)
        row.label(text="Noise Displacement", icon='FORCE_TURBULENCE')
        
        if scene.show_noise_displace:
            box.prop(scene, "my_shape_noise_strength", slider=True)
            box.prop(scene, "my_shape_noise_scale", slider=True)
        
        # Update and Split buttons
        layout.separator()
        layout.operator("myaddon.update_shape", icon='FILE_REFRESH', text="Update Shape")
        layout.operator("myaddon.split_shape", icon='MOD_EXPLODE', text="Split Shape")
        
        # Shape parts list
        if scene.my_shape_parts:
            layout.separator()
            box = layout.box()
            box.label(text="Shape Parts", icon='OUTLINER')
            box.template_list(
                "MYADDON_UL_shape_parts_list", "",
                scene, "my_shape_parts",
                scene, "my_shape_parts_index",
                rows=min(len(scene.my_shape_parts), 5)
            )


# New panel for geometry vector operations
class VIEW3D_PT_geometry_vectors(bpy.types.Panel):
    bl_label = "Geometry Vectors (Latent Space)"
    bl_idname = "VIEW3D_PT_geometry_vectors"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'My Addon'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Header
        box = layout.box()
        box.label(text="Unified Vector Representation", icon='FORCE_FORCE')
        col = box.column(align=True)
        col.label(text="All geometries → 32D vector space")
        col.label(text="Mathematical operations in latent space")
        
        layout.separator()
        
        # === NEW: Vector Editor Section ===
        box = layout.box()
        row = box.row()
        row.prop(scene, "show_vector_editor",
                icon='TRIA_DOWN' if scene.show_vector_editor else 'TRIA_RIGHT',
                icon_only=True, emboss=False)
        row.label(text="Vector Editor", icon='EDITMODE_HLT')
        
        if scene.show_vector_editor:
            # Auto-bind toggle
            col = box.column(align=True)
            col.prop(scene, "vector_editor_auto_bind", text="Auto-Bind to Selected Object", icon='LINKED')
            col.separator()
            
            # Load vector buttons
            col.label(text="Load Vector:", icon='IMPORT')
            row = col.row(align=True)
            row.operator("myaddon.vector_load_from_preset", text="From Preset", icon='PRESET')
            row.operator("myaddon.vector_load_from_object", text="From Object", icon='OBJECT_DATA')
            col.operator("myaddon.vector_load_from_file", text="From Blender File", icon='FILE_BLEND')
            
            # New .gvec file format import/export
            col.separator()
            col.label(text="Custom Format (.gvec):", icon='FILE')
            row = col.row(align=True)
            row.operator("myaddon.import_gvec", text="Import .gvec", icon='IMPORT')
            row.operator("myaddon.export_gvec", text="Export .gvec", icon='EXPORT')
            
            # Batch operations
            row = col.row(align=True)
            row.operator("myaddon.import_gvec_batch", text="Import Batch", icon='LINENUMBERS_ON')
            row.operator("myaddon.export_gvec_batch", text="Export Batch", icon='LINENUMBERS_OFF')
            
            # Show source preset if available
            if scene.vector_source_preset and scene.vector_source_preset != "NONE":
                info_box = col.box()
                info_box.label(text=f"Source: {scene.vector_source_preset}", icon='INFO')
            
            box.separator()
            
            # Display vector values (organized by groups)
            col = box.column(align=True)
            col.label(text="Vector Values (32D):", icon='SETTINGS')
            
            # Basic shape parameters [0-7]
            sub_box = col.box()
            sub_box.label(text="Shape & Topology [0-7]:", icon='MESH_DATA')
            grid = sub_box.grid_flow(row_major=True, columns=2, align=True)
            for i in range(8):
                grid.prop(scene, "geom_vector_current", index=i, text=f"[{i}]")
            
            # Aspect & Deformation [8-14]
            sub_box = col.box()
            sub_box.label(text="Aspect & Deformation [8-14]:", icon='MOD_SIMPLEDEFORM')
            grid = sub_box.grid_flow(row_major=True, columns=2, align=True)
            for i in range(8, 15):
                grid.prop(scene, "geom_vector_current", index=i, text=f"[{i}]")
            
            # Wave & Noise [15-18]
            sub_box = col.box()
            sub_box.label(text="Wave & Noise [15-18]:", icon='FORCE_TURBULENCE')
            grid = sub_box.grid_flow(row_major=True, columns=2, align=True)
            for i in range(15, 19):
                grid.prop(scene, "geom_vector_current", index=i, text=f"[{i}]")
            
            # Shape Morphing [19-21]
            sub_box = col.box()
            sub_box.label(text="Shape Morphing [19-21]:", icon='SHAPEKEY_DATA')
            grid = sub_box.grid_flow(row_major=True, columns=2, align=True)
            for i in range(19, 22):
                grid.prop(scene, "geom_vector_current", index=i, text=f"[{i}]")
            
            # Reserved [22-31]
            sub_box = col.box()
            sub_box.label(text="Reserved [22-31]:", icon='QUESTION')
            grid = sub_box.grid_flow(row_major=True, columns=2, align=True)
            for i in range(22, 32):
                grid.prop(scene, "geom_vector_current", index=i, text=f"[{i}]")
            
            box.separator()
            
            # Vector operations
            col = box.column(align=True)
            col.label(text="Vector Operations:", icon='MODIFIER')
            row = col.row(align=True)
            row.operator("myaddon.vector_to_clipboard", text="Copy", icon='COPYDOWN')
            row.operator("myaddon.vector_from_clipboard", text="Paste", icon='PASTEDOWN')
            row = col.row(align=True)
            row.operator("myaddon.vector_reset", text="Reset", icon='LOOP_BACK')
            row.operator("myaddon.vector_normalize", text="Normalize", icon='NORMALIZE_FCURVES')
            
            box.separator()
            
            # Arithmetic operations
            col = box.column(align=True)
            col.label(text="Vector Arithmetic:", icon='PREFERENCES')
            col.prop(scene, "vector_arithmetic_operation", text="")
            
            if scene.vector_arithmetic_operation in ['MULTIPLY', 'DIVIDE']:
                col.prop(scene, "vector_scalar_value")
            elif scene.vector_arithmetic_operation == 'LERP':
                col.prop(scene, "vector_lerp_factor", slider=True)
            
            col.operator("myaddon.vector_arithmetic", icon='PLAY')
            
            box.separator()
            
            # Decode and render
            col = box.column(align=True)
            col.scale_y = 1.5
            col.operator("myaddon.vector_decode_and_render", icon='MESH_DATA')
            
            # Apply source modifiers button
            col = box.column(align=True)
            col.scale_y = 1.2
            op = col.operator("myaddon.apply_source_modifiers", icon='MODIFIER')
            
            # Show info if current object has stored modifiers
            if context.active_object and "geometry_vector_modifiers" in context.active_object:
                import json
                try:
                    mods = json.loads(context.active_object["geometry_vector_modifiers"])
                    box.label(text=f"Available: {len(mods)} modifier(s)", icon='INFO')
                except:
                    pass
        
        layout.separator()
        
        # Encode current geometry
        box = layout.box()
        box.label(text="Encoding", icon='EXPORT')
        box.operator("myaddon.encode_geometry", text="Encode Current Geometry", icon='PLAY')
        box.label(text="Converts geometry to vector", icon='INFO')
        
        layout.separator()
        
        # Interpolation
        box = layout.box()
        box.label(text="Interpolation", icon='ANIM')
        box.operator("myaddon.interpolate_geometry", text="Interpolate Presets", icon='SMOOTHCURVE')
        col = box.column(align=True)
        col.label(text="Morph between two geometries")
        col.label(text="Linear path in latent space")
        
        layout.separator()
        
        # Blending
        box = layout.box()
        box.label(text="Blending", icon='FORCE_HARMONIC')
        box.operator("myaddon.blend_geometry", text="Blend Multiple", icon='GROUP_VERTEX')
        col = box.column(align=True)
        col.label(text="Weighted combination of")
        col.label(text="multiple geometries")
        
        layout.separator()
        
        # Similarity search
        box = layout.box()
        box.label(text="Similarity", icon='VIEWZOOM')
        box.operator("myaddon.find_similar_geometry", text="Find Similar", icon='ZOOM_IN')
        col = box.column(align=True)
        col.label(text="Find nearest neighbors")
        col.label(text="in latent space")
        
        layout.separator()
        
        # Animation
        box = layout.box()
        box.label(text="Animation", icon='ANIM_DATA')
        box.operator("myaddon.morph_animation", text="Morph Animation", icon='PREVIEW_RANGE')
        col = box.column(align=True)
        col.label(text="Animated interpolation")
        col.label(text="between geometries")
        
        layout.separator()
        
        # Information
        box = layout.box()
        box.label(text="Vector Space Operations:", icon='PREFERENCES')
        col = box.column(align=True)
        col.label(text="• Distance: Euclidean metric")
        col.label(text="• Interpolate: Linear (LERP)")
        col.label(text="• Blend: Weighted average")
        col.label(text="• Dimension: 32D latent space")


classes = (
    VIEW3D_PT_my_panel,
    VIEW3D_PT_my_second_panel,
    VIEW3D_PT_shape_transformer,
    VIEW3D_PT_geometry_vectors,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
