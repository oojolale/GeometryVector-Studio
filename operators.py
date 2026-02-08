import bpy
import os
import subprocess
import urllib.request
import json
import math
import numpy as np
from mathutils import Vector
from .geometry_encoder import (
    GeometryVector, GeometryEncoder, GeometryDecoder,
    GeometryLatentSpace, get_latent_space
)
from .geometry_file_format import (
    GeometryFileFormat, GeometryBatchExporter
)

class MYADDON_OT_button(bpy.types.Operator):
    bl_idname = "myaddon.button"
    bl_label = "open outer script"
    bl_description = "Button action"

    def execute(self, context):
        script_path = r"D:\Users\PC\PycharmProjects\blenderUI\script.py"
        if not os.path.exists(script_path):
            self.report({'ERROR'}, "Script not found")
            return {'CANCELLED'}
        try:
            subprocess.Popen(["python", script_path])
        except Exception as e:
            self.report({'ERROR'}, f"Failed to start script: {e}")
            return {'CANCELLED'}
        self.report({'INFO'}, "Button clicked")
        return {'FINISHED'}

class MYADDON_OT_select_item(bpy.types.Operator):
    bl_idname = "myaddon.select_item"
    bl_label = "Select Item"
    bl_description = "Item selected"

    item_id: bpy.props.IntProperty()
    item_name: bpy.props.StringProperty()

    def execute(self, context):
        self.report({'INFO'}, f"Selected item: id={self.item_id}, name={self.item_name}")
        return {'FINISHED'}

class MYADDON_OT_init_items(bpy.types.Operator):
    bl_idname = "myaddon.init_items"
    bl_label = "Init Items"
    bl_description = "Initialize item list"

    def execute(self, context):
        scene = context.scene
        scene.my_items.clear()

        item1 = scene.my_items.add()
        item1.id = 1
        item1.name = "张三"

        item2 = scene.my_items.add()
        item2.id = 2
        item2.name = "李四"

        self.report({'INFO'}, "Items initialized")
        return {'FINISHED'}

class MYADDON_OT_toggle_collapsible(bpy.types.Operator):
    bl_idname = "myaddon.toggle_collapsible"
    bl_label = "Toggle Collapsible"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.scene.show_collapsible = not context.scene.show_collapsible
        return {'FINISHED'}

class OBJECT_OT_choose_person_files(bpy.types.Operator):
    bl_idname = "object.choose_person_files"
    bl_label = "Select Resource Files"
    bl_description = "Select one or more resource files (blend, images, models)"

    directory: bpy.props.StringProperty(subtype='DIR_PATH')
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)
    filter_glob: bpy.props.StringProperty(
        default="*.blend;*.jpg;*.jpeg;*.png;*.tga;*.bmp;*.exr;*.hdr;*.tif;*.tiff;"
                "*.obj;*.fbx;*.stl;*.dae;*.glb;*.gltf;*.ply;*.abc",
        options={'HIDDEN'}
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        context.scene.my_addon_selected_files.clear()
        for f in self.files:
            full_path = os.path.join(self.directory, f.name)
            item = context.scene.my_addon_selected_files.add()
            item.path = full_path
        self.report({'INFO'}, f"Selected {len(self.files)} files")
        return {'FINISHED'}

class OBJECT_OT_clear_person_files(bpy.types.Operator):
    bl_idname = "object.clear_person_files"
    bl_label = "Clear Selection"
    bl_options = {'REGISTER'}

    def execute(self, context):
        count = len(context.scene.my_addon_selected_files)
        context.scene.my_addon_selected_files.clear()
        self.report({'INFO'}, f"Cleared {count} files")
        return {'FINISHED'}

class OBJECT_OT_open_resource(bpy.types.Operator):
    bl_idname = "object.open_resource"
    bl_label = "Open/Import Resource"
    bl_description = "Open blend file, load image, or import 3D model"

    filepath: bpy.props.StringProperty()

    def execute(self, context):
        filepath = self.filepath
        if not os.path.exists(filepath):
            self.report({'ERROR'}, f"File not found: {filepath}")
            return {'CANCELLED'}

        ext = os.path.splitext(filepath)[1].lower()

        # Blend file
        if ext == '.blend':
            bpy.ops.wm.open_mainfile(filepath=filepath)
            self.report({'INFO'}, f"Opened blend file: {filepath}")
            return {'FINISHED'}

        # Image files
        image_exts = {'.jpg', '.jpeg', '.png', '.tga', '.bmp', '.exr', '.hdr', '.tif', '.tiff', '.gif', '.webp'}
        if ext in image_exts:
            try:
                img = bpy.data.images.load(filepath)
                for area in context.screen.areas:
                    if area.type == 'IMAGE_EDITOR':
                        area.spaces.active.image = img
                        break
                self.report({'INFO'}, f"Loaded image: {filepath}")
                return {'FINISHED'}
            except Exception as e:
                self.report({'ERROR'}, f"Failed to load image: {e}")
                return {'CANCELLED'}

        # 3D model import
        import_ops = {
            '.obj': bpy.ops.import_scene.obj,
            '.fbx': bpy.ops.import_scene.fbx,
            '.stl': bpy.ops.import_mesh.stl,
            '.dae': bpy.ops.wm.collada_import,
            '.glb': bpy.ops.import_scene.gltf,
            '.gltf': bpy.ops.import_scene.gltf,
            '.ply': bpy.ops.import_mesh.ply,
            '.abc': bpy.ops.wm.alembic_import,
        }
        if ext in import_ops:
            try:
                import_ops[ext](filepath=filepath)
                self.report({'INFO'}, f"Imported {ext[1:]} file: {filepath}")
                return {'FINISHED'}
            except Exception as e:
                self.report({'ERROR'}, f"Import failed: {e}")
                return {'CANCELLED'}

        self.report({'ERROR'}, f"Unsupported file type: {ext}")
        return {'CANCELLED'}

class OBJECT_OT_remove_selected_file(bpy.types.Operator):
    bl_idname = "object.remove_selected_file"
    bl_label = "Remove"
    bl_description = "Remove this file from the list"

    index: bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        if 0 <= self.index < len(scene.my_addon_selected_files):
            scene.my_addon_selected_files.remove(self.index)
            self.report({'INFO'}, "File removed")
        else:
            self.report({'ERROR'}, "Invalid index")
        return {'FINISHED'}

class MYADDON_OT_add_panel(bpy.types.Operator):
    bl_idname = "myaddon.add_panel"
    bl_label = "Add Panel"
    bl_description = "Add a new panel"

    def execute(self, context):
        scene = context.scene
        new_panel = scene.my_panels.add()
        new_panel.name = f"Panel {len(scene.my_panels)}"
        return {'FINISHED'}

class MYADDON_OT_remove_panel(bpy.types.Operator):
    bl_idname = "myaddon.remove_panel"
    bl_label = "Remove Panel"
    bl_description = "Remove this panel"

    index: bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        if 0 <= self.index < len(scene.my_panels):
            scene.my_panels.remove(self.index)
        return {'FINISHED'}

class MYADDON_OT_open_icon_popup(bpy.types.Operator):
    bl_idname = "myaddon.open_icon_popup"
    bl_label = "Icon Preview Popup"
    bl_options = {'REGISTER', 'INTERNAL'}

    item_id: bpy.props.IntProperty(default=-1)
    item_name: bpy.props.StringProperty(default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if self.item_id != -1 or self.item_name:
            box = layout.box()
            if self.item_id != -1:
                box.label(text=f"Item ID: {self.item_id}")
            if self.item_name:
                box.label(text=f"Item Name: {self.item_name}")
            layout.separator()

        layout.label(text="Select an Icon:")
        layout.template_icon_view(scene, "my_icon_preview", show_labels=True, scale=6.0)
        layout.separator()
        layout.prop(scene, "my_icon_preview", text="Selected")
        layout.separator()

        op = layout.operator("myaddon.icon_callback", text="Select Icon")
        op.icon_id = scene.my_icon_preview
        op.item_id = self.item_id
        op.item_name = self.item_name

        layout.operator("myaddon.button", text="Run External Script")
        layout.operator("wm.quit_blender", text="Close Blender")  # demo only

    def execute(self, context):
        return {'FINISHED'}

class MYADDON_OT_icon_callback(bpy.types.Operator):
    bl_idname = "myaddon.icon_callback"
    bl_label = "Icon Callback"
    bl_description = "Callback when icon selected"

    icon_id: bpy.props.StringProperty()
    item_id: bpy.props.IntProperty()
    item_name: bpy.props.StringProperty()

    def execute(self, context):
        msg = f"Icon '{self.icon_id}' selected"
        if self.item_id != -1:
            msg += f" for item {self.item_id} ({self.item_name})"
        self.report({'INFO'}, msg)
        print(msg)
        return {'FINISHED'}

class MYADDON_OT_fetch_api(bpy.types.Operator):
    bl_idname = "myaddon.fetch_api"
    bl_label = "Fetch API Data"
    bl_description = "Retrieve data from http://www.pcnx.cn/api/hello"

    def execute(self, context):
        url = "http://www.pcnx.cn/api/hello"
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                data = response.read().decode('utf-8')
                # Try to parse as JSON for pretty print
                try:
                    json_obj = json.loads(data)
                    formatted = json.dumps(json_obj, indent=2, ensure_ascii=False)
                except json.JSONDecodeError:
                    formatted = data
            # Show the response in a popup
            bpy.ops.myaddon.show_api_response('INVOKE_DEFAULT', text=formatted)
        except urllib.error.URLError as e:
            self.report({'ERROR'}, f"Failed to fetch: {e.reason}")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        return {'FINISHED'}

class MYADDON_OT_show_api_response(bpy.types.Operator):
    bl_idname = "myaddon.show_api_response"
    bl_label = "API Response"
    bl_options = {'INTERNAL'}

    text: bpy.props.StringProperty(name="Response", default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        if not self.text:
            layout.label(text="No data received.")
            return
        lines = self.text.splitlines()
        col = layout.column(align=True)
        for line in lines:
            col.label(text=line)

    def execute(self, context):
        return {'FINISHED'}

class MYADDON_OT_create_shape(bpy.types.Operator):
    bl_idname = "myaddon.create_shape"
    bl_label = "Create/Update Shape"
    bl_description = "Create a round cube shape with given dimensions and radius"

    def execute(self, context):
        scene = context.scene
        dims = scene.my_shape_dimensions
        radius = scene.my_shape_radius

        obj = bpy.data.objects.get("MyShapeObject")
        if obj is None:
            # Create new
            bpy.ops.mesh.primitive_round_cube_add(radius=radius, size=dims)
            obj = context.active_object
            obj.name = "MyShapeObject"
        else:
            # Update existing
            # For round cube, we need to adjust the object's dimensions? Actually the round cube object has a "Round Cube" data with parameters.
            # We can set the object's dimensions directly? The round cube uses a mesh with geometry nodes? Actually it's a built-in mesh with parameters accessible via object.data.
            # In Blender 3.0+, the round cube mesh is a bpy.types.Mesh with attributes? It might have "size" and "radius" properties.
            # Let's check: bpy.ops.mesh.primitive_round_cube_add creates a mesh with modifiers? Actually it creates a mesh with a "Geometry Nodes" modifier "Round Cube"? Hmm.
            # Better approach: we can simply delete and recreate for simplicity.
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.ops.mesh.primitive_round_cube_add(radius=radius, size=dims)
            obj = context.active_object
            obj.name = "MyShapeObject"
        return {'FINISHED'}

class MYADDON_OT_split_shape(bpy.types.Operator):
    bl_idname = "myaddon.split_shape"
    bl_label = "Split Shape"
    bl_description = "Split MyShapeObject into separate parts"

    def execute(self, context):
        scene = context.scene
        obj = bpy.data.objects.get("MyShapeObject")
        
        if obj is None:
            self.report({'WARNING'}, "MyShapeObject not found")
            return {'CANCELLED'}
        
        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        # Enter edit mode and separate by loose parts
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Clear the parts list
        scene.my_shape_parts.clear()
        
        # Find all separated parts and organize them
        separated_objects = [o for o in context.selected_objects]
        
        if not separated_objects:
            self.report({'WARNING'}, "No parts to split")
            return {'CANCELLED'}
        
        # Create or get collection for parts
        collection_name = "MyShapeObject"
        if collection_name not in bpy.data.collections:
            parts_collection = bpy.data.collections.new(collection_name)
            context.scene.collection.children.link(parts_collection)
        else:
            parts_collection = bpy.data.collections[collection_name]
        
        # Rename and organize parts
        part_names = {
            'Fuselage': 0, 'Wings': 0, 'VTail': 0, 'HTail': 0, 
            'Engine': 0, 'Nose': 0, 'TailBoom': 0, 'MainRotor': 0,
            'Blade': 0, 'TailRotor': 0, 'Skid': 0
        }
        
        for i, part_obj in enumerate(separated_objects):
            # Determine part type from original name or mesh type
            part_type = "Part"
            for key in part_names.keys():
                if key.lower() in part_obj.name.lower():
                    part_type = key
                    break
            
            # Generate unique name
            if part_type in part_names:
                part_names[part_type] += 1
                new_name = f"{part_obj.data.name}_{part_type}.{part_names[part_type]:03d}"
            else:
                new_name = f"{part_obj.data.name}_Part.{i+1:03d}"
            
            part_obj.name = new_name
            
            # Move to parts collection
            for coll in part_obj.users_collection:
                coll.objects.unlink(part_obj)
            parts_collection.objects.link(part_obj)
            
            # Add to list
            item = scene.my_shape_parts.add()
            item.name = new_name
            item.object_ref = new_name
        
        self.report({'INFO'}, f"Split into {len(separated_objects)} parts")
        return {'FINISHED'}

class MYADDON_OT_focus_part(bpy.types.Operator):
    bl_idname = "myaddon.focus_part"
    bl_label = "Focus Part"
    bl_description = "Focus camera on selected part"
    
    part_name: bpy.props.StringProperty()
    
    def execute(self, context):
        obj = bpy.data.objects.get(self.part_name)
        
        if obj is None:
            self.report({'WARNING'}, f"Part {self.part_name} not found")
            return {'CANCELLED'}
        
        # Deselect all and select this part
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        # Frame selected object in all 3D views
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'area': area, 'region': region}
                        with context.temp_override(**override):
                            bpy.ops.view3d.view_selected()
        
        self.report({'INFO'}, f"Focused on {self.part_name}")
        return {'FINISHED'}

class MYADDON_OT_edit_part_material(bpy.types.Operator):
    bl_idname = "myaddon.edit_part_material"
    bl_label = "Edit Material"
    bl_description = "Edit material for this part"
    
    part_name: bpy.props.StringProperty()
    material_type: bpy.props.EnumProperty(
        name="Material Type",
        items=[
            ('STEEL', "Steel", "Metallic steel material"),
            ('ALLOY', "Alloy", "Aluminum alloy material"),
            ('CARBON', "Carbon Fiber", "Carbon fiber composite"),
            ('GLASS', "Glass", "Transparent glass material"),
            ('PLASTIC', "Plastic", "Matte plastic material"),
            ('PAINT_MATTE', "Matte Paint", "Matte painted surface"),
            ('PAINT_GLOSSY', "Glossy Paint", "Glossy painted surface"),
        ],
        default='STEEL'
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Material for: {self.part_name}", icon='MATERIAL')
        layout.separator()
        layout.prop(self, "material_type", text="Material")
    
    def execute(self, context):
        obj = bpy.data.objects.get(self.part_name)
        
        if obj is None:
            self.report({'WARNING'}, f"Part {self.part_name} not found")
            return {'CANCELLED'}
        
        # Create material based on type
        mat_name = f"MAT_{self.material_type}_{self.part_name}"
        mat = bpy.data.materials.get(mat_name)
        
        if mat is None:
            mat = bpy.data.materials.new(name=mat_name)
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            # Clear default nodes
            nodes.clear()
            
            # Add Principled BSDF
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf.location = (0, 0)
            
            # Add Material Output
            output = nodes.new(type='ShaderNodeOutputMaterial')
            output.location = (300, 0)
            
            # Link
            links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
            
            # Set material properties based on type
            if self.material_type == 'STEEL':
                bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.35, 1.0)
                bsdf.inputs['Metallic'].default_value = 1.0
                bsdf.inputs['Roughness'].default_value = 0.3
            elif self.material_type == 'ALLOY':
                bsdf.inputs['Base Color'].default_value = (0.6, 0.6, 0.65, 1.0)
                bsdf.inputs['Metallic'].default_value = 1.0
                bsdf.inputs['Roughness'].default_value = 0.2
            elif self.material_type == 'CARBON':
                bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
                bsdf.inputs['Metallic'].default_value = 0.0
                bsdf.inputs['Roughness'].default_value = 0.4
                bsdf.inputs['Specular'].default_value = 0.5
            elif self.material_type == 'GLASS':
                bsdf.inputs['Base Color'].default_value = (0.8, 0.9, 1.0, 1.0)
                bsdf.inputs['Metallic'].default_value = 0.0
                bsdf.inputs['Roughness'].default_value = 0.0
                bsdf.inputs['Transmission'].default_value = 0.95
                bsdf.inputs['IOR'].default_value = 1.45
            elif self.material_type == 'PLASTIC':
                bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
                bsdf.inputs['Metallic'].default_value = 0.0
                bsdf.inputs['Roughness'].default_value = 0.5
            elif self.material_type == 'PAINT_MATTE':
                bsdf.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1.0)  # Red
                bsdf.inputs['Metallic'].default_value = 0.0
                bsdf.inputs['Roughness'].default_value = 0.8
            elif self.material_type == 'PAINT_GLOSSY':
                bsdf.inputs['Base Color'].default_value = (0.1, 0.3, 0.8, 1.0)  # Blue
                bsdf.inputs['Metallic'].default_value = 0.0
                bsdf.inputs['Roughness'].default_value = 0.1
                bsdf.inputs['Clearcoat'].default_value = 1.0
        
        # Assign material to object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        
        self.report({'INFO'}, f"Applied {self.material_type} material to {self.part_name}")
        return {'FINISHED'}

class MYADDON_OT_apply_preset(bpy.types.Operator):
    bl_idname = "myaddon.apply_preset"
    bl_label = "Apply Preset"
    bl_description = "Apply preset shape configuration"

    def execute(self, context):
        scene = context.scene
        preset = scene.my_shape_preset
        
        if preset == 'SPIRAL_CORRIDOR':
            # Spiral Corridor preset
            scene.my_shape_dimensions = (0.5, 0.5, 1.0)
            scene.my_shape_helix_turns = 5
            scene.my_shape_helix_radius = 3.0
            scene.my_shape_helix_height = 20.0
            scene.my_shape_sphericity = 0.3
            scene.my_shape_taper = 0.0
            scene.my_shape_twist = 0.0
            scene.my_shape_bend = 0.0
            scene.my_shape_inflate = 0.0
            scene.my_shape_wave_amplitude = 0.0
            scene.my_shape_noise_strength = 0.0
            self.report({'INFO'}, "Applied Spiral Corridor preset")
            
        elif preset == 'DNA_HELIX':
            # DNA Double Helix preset
            scene.my_shape_dimensions = (0.2, 0.2, 0.5)
            scene.my_shape_helix_turns = 8
            scene.my_shape_helix_radius = 1.5
            scene.my_shape_helix_height = 15.0
            scene.my_shape_sphericity = 1.0
            scene.my_shape_taper = 0.0
            scene.my_shape_twist = 0.0
            scene.my_shape_bend = 0.0
            scene.my_shape_inflate = 0.0
            scene.my_shape_wave_amplitude = 0.0
            scene.my_shape_noise_strength = 0.0
            self.report({'INFO'}, "Applied DNA Helix preset")
            
        elif preset == 'SPRING':
            # Spring Coil preset
            scene.my_shape_dimensions = (0.3, 0.3, 0.3)
            scene.my_shape_helix_turns = 10
            scene.my_shape_helix_radius = 2.0
            scene.my_shape_helix_height = 12.0
            scene.my_shape_sphericity = 1.0
            scene.my_shape_taper = 0.0
            scene.my_shape_twist = 0.0
            scene.my_shape_bend = 0.0
            scene.my_shape_inflate = 0.0
            scene.my_shape_wave_amplitude = 0.0
            scene.my_shape_noise_strength = 0.0
            self.report({'INFO'}, "Applied Spring Coil preset")
            
        elif preset == 'TWISTED_TOWER':
            # Twisted Tower preset
            scene.my_shape_dimensions = (1.5, 1.5, 8.0)
            scene.my_shape_helix_turns = 0
            scene.my_shape_helix_radius = 2.0
            scene.my_shape_helix_height = 10.0
            scene.my_shape_sphericity = 0.0
            scene.my_shape_taper = 0.2
            scene.my_shape_twist = 1.57
            scene.my_shape_bend = 0.0
            scene.my_shape_inflate = 0.0
            scene.my_shape_wave_amplitude = 0.0
            scene.my_shape_noise_strength = 0.0
            self.report({'INFO'}, "Applied Twisted Tower preset")
            
        elif preset == 'FIGHTER_JET':
            # Fighter Jet preset
            scene.my_aircraft_fuselage_length = 12.0
            scene.my_aircraft_wing_span = 10.0
            scene.my_aircraft_wing_sweep = 0.785  # 45 degrees
            scene.my_aircraft_tail_size = 3.0
            scene.my_aircraft_engine_count = 2
            scene.my_shape_helix_turns = 0
            self.report({'INFO'}, "Applied Fighter Jet preset")
            
        elif preset == 'BOMBER':
            # Bomber Aircraft preset
            scene.my_aircraft_fuselage_length = 20.0
            scene.my_aircraft_wing_span = 30.0
            scene.my_aircraft_wing_sweep = 0.2  # Slight sweep
            scene.my_aircraft_tail_size = 5.0
            scene.my_aircraft_engine_count = 4
            scene.my_shape_helix_turns = 0
            self.report({'INFO'}, "Applied Bomber preset")
            
        elif preset == 'HELICOPTER':
            # Helicopter preset
            scene.my_aircraft_fuselage_length = 10.0
            scene.my_aircraft_wing_span = 12.0  # Main rotor diameter
            scene.my_aircraft_wing_sweep = 0.0
            scene.my_aircraft_tail_size = 6.0  # Tail boom
            scene.my_aircraft_engine_count = 1
            scene.my_shape_helix_turns = 0
            self.report({'INFO'}, "Applied Helicopter preset")
            
        elif preset == 'STAIRCASE':
            # Staircase preset - default values already set
            self.report({'INFO'}, "Applied Staircase preset")
            
        elif preset == 'CHARACTER':
            # Character preset - default values already set
            self.report({'INFO'}, "Applied Character preset")
        
        return {'FINISHED'}

class MYADDON_OT_update_shape(bpy.types.Operator):
    bl_idname = "myaddon.update_shape"
    bl_label = "Update Shape"
    bl_description = "Create or update the shape with given dimensions and transformations"

    def execute(self, context):
        scene = context.scene
        
        # Clear vector editor binding when creating preset from Shape Transformer
        # This prevents conflict between Shape Transformer workflow and Geometry Vectors workflow
        scene.vector_source_preset = "NONE"
        
        dims = scene.my_shape_dimensions
        sphericity = scene.my_shape_sphericity
        taper = scene.my_shape_taper
        twist = scene.my_shape_twist
        bend = scene.my_shape_bend
        inflate = scene.my_shape_inflate
        wave_amp = scene.my_shape_wave_amplitude
        wave_freq = scene.my_shape_wave_frequency
        noise_str = scene.my_shape_noise_strength
        noise_scale = scene.my_shape_noise_scale
        helix_turns = scene.my_shape_helix_turns
        helix_radius = scene.my_shape_helix_radius
        helix_height = scene.my_shape_helix_height
        preset = scene.my_shape_preset

        # Check if we need to create aircraft structure
        if preset in ['FIGHTER_JET', 'BOMBER', 'HELICOPTER']:
            return self.create_aircraft(context, preset)
        
        # Check if we need to create staircase
        if preset == 'STAIRCASE':
            return self.create_staircase(context)
        
        # Check if we need to create character
        if preset == 'CHARACTER':
            return self.create_character(context)

        # Check if we need to create helix structure
        if helix_turns > 0:
            return self.create_helix_structure(context, dims, helix_turns, helix_radius, 
                                              helix_height, sphericity)

        # Otherwise create standard transformed shape
        # Try to use currently selected object if it's a vector-based mesh
        obj = None
        active_obj = context.active_object
        if active_obj and active_obj.type == 'MESH':
            # Check if this is a vector-based object or the default MyShapeObject
            has_vector_data = all(f"geom_vector_{i}" in active_obj for i in range(32))
            if has_vector_data or active_obj.name == "MyShapeObject":
                obj = active_obj
                print(f"[UpdateShape] Using selected object: {obj.name}")
        
        # Fallback to MyShapeObject or create new
        if obj is None:
            obj = bpy.data.objects.get("MyShapeObject")
        if obj is None:
            bpy.ops.mesh.primitive_cube_add(size=2.0)
            obj = context.active_object
            obj.name = "MyShapeObject"

        # Clear all existing modifiers to rebuild from scratch
        obj.modifiers.clear()

        # Determine if we need subdivision (for smooth deformations)
        needs_subdivision = (sphericity > 0.0 or inflate != 0.0 or 
                           wave_amp > 0.0 or noise_str > 0.0)

        if needs_subdivision:
            subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
            subsurf.levels = 3
            subsurf.render_levels = 3

        # 1. Sphericity (Cast to Sphere)
        if sphericity > 0.0:
            cast_mod = obj.modifiers.new(name="CastToSphere", type='CAST')
            cast_mod.cast_type = 'SPHERE'
            cast_mod.factor = sphericity

        # 2. Taper (Simple Deform)
        if taper != 0.0:
            taper_mod = obj.modifiers.new(name="Taper", type='SIMPLE_DEFORM')
            taper_mod.deform_method = 'TAPER'
            taper_mod.factor = taper
            taper_mod.deform_axis = 'Z'

        # 3. Twist (Simple Deform)
        if twist != 0.0:
            twist_mod = obj.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
            twist_mod.deform_method = 'TWIST'
            twist_mod.angle = twist
            twist_mod.deform_axis = 'Z'

        # 4. Bend (Simple Deform)
        if bend != 0.0:
            bend_mod = obj.modifiers.new(name="Bend", type='SIMPLE_DEFORM')
            bend_mod.deform_method = 'BEND'
            bend_mod.angle = bend
            bend_mod.deform_axis = 'Z'

        # 5. Inflate/Deflate (Displace with spherical gradient)
        if inflate != 0.0:
            displace_mod = obj.modifiers.new(name="Inflate", type='DISPLACE')
            displace_mod.strength = inflate * 0.5
            displace_mod.mid_level = 0.5
            displace_mod.direction = 'NORMAL'

        # 6. Wave deformation
        if wave_amp > 0.0:
            wave_mod = obj.modifiers.new(name="Wave", type='WAVE')
            wave_mod.use_cyclic = False
            wave_mod.height = wave_amp
            wave_mod.width = 1.0 / wave_freq if wave_freq > 0 else 1.0
            wave_mod.time_offset = 0.0

        # 7. Noise displacement
        if noise_str > 0.0:
            tex_name = "NoiseTexture_Shape"
            tex = bpy.data.textures.get(tex_name)
            if tex is None:
                tex = bpy.data.textures.new(tex_name, 'CLOUDS')
                tex.noise_scale = noise_scale
            else:
                tex.noise_scale = noise_scale
            
            noise_mod = obj.modifiers.new(name="Noise", type='DISPLACE')
            noise_mod.texture = tex
            noise_mod.strength = noise_str
            noise_mod.direction = 'NORMAL'

        # Set dimensions via scale
        obj.scale = (dims[0] / 2.0, dims[1] / 2.0, dims[2] / 2.0)
        obj.location = (0, 0, 0)
        
        self.report({'INFO'}, f"Shape updated with {len(obj.modifiers)} modifiers")
        return {'FINISHED'}

    def create_helix_structure(self, context, dims, turns, radius, height, sphericity):
        """Create helix/spiral structure using curve and array"""
        import math
        
        # Remove old objects if they exist
        for name in ["MyShapeObject", "HelixCurve", "HelixArray"]:
            obj = bpy.data.objects.get(name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)
        
        # 1. Create base object (cylinder or cube based on sphericity)
        if sphericity > 0.5:
            bpy.ops.mesh.primitive_cylinder_add(
                radius=dims[0],
                depth=dims[2],
                location=(radius, 0, 0)
            )
        else:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(radius, 0, 0))
        
        base_obj = context.active_object
        base_obj.name = "MyShapeObject"
        base_obj.scale = (dims[0], dims[1], dims[2])
        
        # 2. Create helix curve path
        curve_data = bpy.data.curves.new(name="HelixCurvePath", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new(type='NURBS')
        
        # Generate helix points
        segments = turns * 32  # points per turn
        spline.points.add(segments - 1)  # Already has 1 point
        
        for i in range(segments + 1):
            t = i / segments
            angle = t * turns * 2 * math.pi
            z = t * height - height / 2  # Center vertically
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            if i < len(spline.points):
                spline.points[i].co = (x, y, z, 1.0)
        
        curve_obj = bpy.data.objects.new("HelixCurve", curve_data)
        context.collection.objects.link(curve_obj)
        
        # 3. Add Array modifier to base object
        array_mod = base_obj.modifiers.new(name="Array", type='ARRAY')
        array_mod.fit_type = 'FIT_CURVE'
        array_mod.curve = curve_obj
        array_mod.count = turns * 8  # instances
        array_mod.use_merge_vertices = True
        array_mod.merge_threshold = 0.01
        
        # 4. Add Curve modifier to follow path
        curve_mod = base_obj.modifiers.new(name="Curve", type='CURVE')
        curve_mod.object = curve_obj
        curve_mod.deform_axis = 'POS_Z'
        
        # 5. Add smooth shading
        if sphericity > 0.0:
            subsurf = base_obj.modifiers.new(name="Subdivision", type='SUBSURF')
            subsurf.levels = 2
            subsurf.render_levels = 2
        
        # Hide curve object
        curve_obj.hide_set(True)
        curve_obj.hide_render = True
        
        self.report({'INFO'}, f"Helix structure created: {turns} turns, radius {radius}, height {height}")
        return {'FINISHED'}

    def create_aircraft(self, context, aircraft_type):
        """Create aircraft structure with fuselage, wings, tail"""
        import math
        
        scene = context.scene
        fuselage_len = scene.my_aircraft_fuselage_length
        wing_span = scene.my_aircraft_wing_span
        wing_sweep = scene.my_aircraft_wing_sweep
        tail_size = scene.my_aircraft_tail_size
        engine_count = scene.my_aircraft_engine_count
        
        # Clear old aircraft objects
        for obj in bpy.data.objects:
            if obj.name.startswith(("Aircraft_", "MyShapeObject")):
                bpy.data.objects.remove(obj, do_unlink=True)
        
        created_objects = []
        
        if aircraft_type == 'FIGHTER_JET':
            # 1. Fuselage - streamlined, tapered
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.8,
                depth=fuselage_len,
                location=(0, 0, 0),
                rotation=(0, math.pi/2, 0)
            )
            fuselage = context.active_object
            fuselage.name = "Aircraft_Fuselage"
            fuselage.scale = (1.0, 1.0, 1.2)  # Elongated
            
            # Add taper to fuselage
            taper_mod = fuselage.modifiers.new(name="Taper", type='SIMPLE_DEFORM')
            taper_mod.deform_method = 'TAPER'
            taper_mod.factor = 0.6
            taper_mod.deform_axis = 'X'
            
            # Smooth fuselage
            subsurf = fuselage.modifiers.new(name="Subdivision", type='SUBSURF')
            subsurf.levels = 2
            created_objects.append(fuselage)
            
            # 2. Main Wings - delta wing style
            wing_chord = fuselage_len * 0.4
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(0, 0, -0.3)
            )
            wings = context.active_object
            wings.name = "Aircraft_Wings"
            wings.scale = (wing_chord, wing_span/2, 0.1)
            
            # Apply wing sweep
            if wing_sweep != 0:
                shear_mod = wings.modifiers.new(name="Shear", type='SIMPLE_DEFORM')
                shear_mod.deform_method = 'TWIST'
                shear_mod.angle = wing_sweep
                shear_mod.deform_axis = 'Z'
            
            created_objects.append(wings)
            
            # 3. Tail stabilizers
            # Vertical stabilizer
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(-fuselage_len*0.45, 0, tail_size*0.3)
            )
            vtail = context.active_object
            vtail.name = "Aircraft_VTail"
            vtail.scale = (tail_size*0.5, 0.1, tail_size)
            created_objects.append(vtail)
            
            # Horizontal stabilizers
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(-fuselage_len*0.45, 0, 0.2)
            )
            htail = context.active_object
            htail.name = "Aircraft_HTail"
            htail.scale = (tail_size*0.6, tail_size*1.5, 0.1)
            created_objects.append(htail)
            
            # 4. Engines (if any)
            for i in range(engine_count):
                offset_y = (i - (engine_count-1)/2) * 2.0
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=0.4,
                    depth=fuselage_len*0.3,
                    location=(-fuselage_len*0.15, offset_y, -0.5),
                    rotation=(0, math.pi/2, 0)
                )
                engine = context.active_object
                engine.name = f"Aircraft_Engine_{i+1}"
                created_objects.append(engine)
            
            # 5. Nose cone
            bpy.ops.mesh.primitive_cone_add(
                radius1=0.8,
                depth=fuselage_len*0.15,
                location=(fuselage_len*0.55, 0, 0),
                rotation=(0, -math.pi/2, 0)
            )
            nose = context.active_object
            nose.name = "Aircraft_Nose"
            created_objects.append(nose)
            
        elif aircraft_type == 'BOMBER':
            # 1. Fuselage - larger, cylindrical
            bpy.ops.mesh.primitive_cylinder_add(
                radius=1.5,
                depth=fuselage_len,
                location=(0, 0, 0),
                rotation=(0, math.pi/2, 0)
            )
            fuselage = context.active_object
            fuselage.name = "Aircraft_Fuselage"
            
            subsurf = fuselage.modifiers.new(name="Subdivision", type='SUBSURF')
            subsurf.levels = 2
            created_objects.append(fuselage)
            
            # 2. Large straight wings
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(0, 0, -0.5)
            )
            wings = context.active_object
            wings.name = "Aircraft_Wings"
            wings.scale = (fuselage_len*0.25, wing_span/2, 0.15)
            created_objects.append(wings)
            
            # 3. Tail
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(-fuselage_len*0.45, 0, tail_size*0.5)
            )
            vtail = context.active_object
            vtail.name = "Aircraft_VTail"
            vtail.scale = (tail_size*0.6, 0.15, tail_size)
            created_objects.append(vtail)
            
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(-fuselage_len*0.45, 0, 0.5)
            )
            htail = context.active_object
            htail.name = "Aircraft_HTail"
            htail.scale = (tail_size*0.8, tail_size*2.0, 0.15)
            created_objects.append(htail)
            
            # 4. Multiple engines under wings
            for i in range(engine_count):
                wing_pos = -wing_span/2 + (i+1) * wing_span/(engine_count+1)
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=0.6,
                    depth=fuselage_len*0.25,
                    location=(fuselage_len*0.1, wing_pos, -1.2),
                    rotation=(0, math.pi/2, 0)
                )
                engine = context.active_object
                engine.name = f"Aircraft_Engine_{i+1}"
                created_objects.append(engine)
                
        elif aircraft_type == 'HELICOPTER':
            # 1. Fuselage - rounded body
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=1.2,
                location=(0, 0, 0)
            )
            fuselage = context.active_object
            fuselage.name = "Aircraft_Fuselage"
            fuselage.scale = (fuselage_len*0.08, 1.0, 0.8)
            created_objects.append(fuselage)
            
            # 2. Tail boom
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.3,
                depth=tail_size,
                location=(-tail_size/2 - fuselage_len*0.04, 0, 0.5),
                rotation=(0, math.pi/2, 0)
            )
            tail_boom = context.active_object
            tail_boom.name = "Aircraft_TailBoom"
            created_objects.append(tail_boom)
            
            # 3. Main rotor (represented as thin disk)
            bpy.ops.mesh.primitive_cylinder_add(
                radius=wing_span/2,
                depth=0.05,
                location=(0, 0, 2.0)
            )
            main_rotor = context.active_object
            main_rotor.name = "Aircraft_MainRotor"
            created_objects.append(main_rotor)
            
            # 4. Rotor blades (4 blades)
            for i in range(4):
                angle = i * math.pi / 2
                blade_x = (wing_span/2 - 0.5) * math.cos(angle)
                blade_y = (wing_span/2 - 0.5) * math.sin(angle)
                
                bpy.ops.mesh.primitive_cube_add(
                    size=1.0,
                    location=(blade_x, blade_y, 2.05),
                    rotation=(0, 0, angle)
                )
                blade = context.active_object
                blade.name = f"Aircraft_Blade_{i+1}"
                blade.scale = (wing_span/2 - 1, 0.2, 0.02)
                created_objects.append(blade)
            
            # 5. Tail rotor
            bpy.ops.mesh.primitive_cylinder_add(
                radius=tail_size*0.2,
                depth=0.05,
                location=(-tail_size - fuselage_len*0.04, 0, 1.2),
                rotation=(math.pi/2, 0, 0)
            )
            tail_rotor = context.active_object
            tail_rotor.name = "Aircraft_TailRotor"
            created_objects.append(tail_rotor)
            
            # 6. Landing skids
            for side in [-1, 1]:
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=0.1,
                    depth=fuselage_len*0.06,
                    location=(0, side * 1.5, -1.0),
                    rotation=(0, math.pi/2, 0)
                )
                skid = context.active_object
                skid.name = f"Aircraft_Skid_{side}"
                created_objects.append(skid)
        
        # Join all objects into one
        if created_objects:
            context.view_layer.objects.active = created_objects[0]
            for obj in created_objects:
                obj.select_set(True)
            bpy.ops.object.join()
            
            final_obj = context.active_object
            final_obj.name = "MyShapeObject"
            final_obj.location = (0, 0, 0)
        
        self.report({'INFO'}, f"{aircraft_type} created successfully")
        return {'FINISHED'}
    
    def create_staircase(self, context):
        """Create staircase structure"""
        import math
        
        scene = context.scene
        steps = scene.my_stair_steps
        step_width = scene.my_stair_step_width
        step_height = scene.my_stair_step_height
        step_depth = scene.my_stair_step_depth
        stair_type = scene.my_stair_type
        
        # Clear old objects
        for obj in bpy.data.objects:
            if obj.name.startswith(("Stair_", "MyShapeObject")):
                bpy.data.objects.remove(obj, do_unlink=True)
        
        created_objects = []
        
        if stair_type == 'STRAIGHT':
            # Create straight staircase
            for i in range(steps):
                bpy.ops.mesh.primitive_cube_add(
                    size=1.0,
                    location=(0, i * step_depth, i * step_height)
                )
                step = context.active_object
                step.name = f"Stair_Step_{i+1:03d}"
                step.scale = (step_width/2, step_depth/2, step_height/2)
                created_objects.append(step)
        
        elif stair_type == 'SPIRAL':
            # Create spiral staircase
            center_radius = step_width * 0.5
            angle_per_step = (2 * math.pi) / (steps * 0.5)  # Half rotation per full height
            
            for i in range(steps):
                angle = i * angle_per_step
                x = center_radius * math.cos(angle)
                y = center_radius * math.sin(angle)
                z = i * step_height
                
                bpy.ops.mesh.primitive_cube_add(
                    size=1.0,
                    location=(x, y, z),
                    rotation=(0, 0, angle)
                )
                step = context.active_object
                step.name = f"Stair_Step_{i+1:03d}"
                step.scale = (step_width/2, step_depth/2, step_height/2)
                created_objects.append(step)
            
            # Add center column
            bpy.ops.mesh.primitive_cylinder_add(
                radius=center_radius * 0.3,
                depth=steps * step_height,
                location=(0, 0, steps * step_height / 2)
            )
            column = context.active_object
            column.name = "Stair_Column"
            created_objects.append(column)
        
        elif stair_type == 'L_SHAPED':
            # Create L-shaped staircase with landing
            half_steps = steps // 2
            
            # First flight (going forward)
            for i in range(half_steps):
                bpy.ops.mesh.primitive_cube_add(
                    size=1.0,
                    location=(0, i * step_depth, i * step_height)
                )
                step = context.active_object
                step.name = f"Stair_Step_{i+1:03d}"
                step.scale = (step_width/2, step_depth/2, step_height/2)
                created_objects.append(step)
            
            # Landing
            landing_z = half_steps * step_height
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(step_width/2, (half_steps-1) * step_depth + step_width/2, landing_z)
            )
            landing = context.active_object
            landing.name = "Stair_Landing"
            landing.scale = (step_width, step_width, step_height/2)
            created_objects.append(landing)
            
            # Second flight (going right)
            remaining_steps = steps - half_steps
            for i in range(remaining_steps):
                bpy.ops.mesh.primitive_cube_add(
                    size=1.0,
                    location=(step_width + i * step_depth, 
                             (half_steps-1) * step_depth + step_width/2,
                             landing_z + (i+1) * step_height)
                )
                step = context.active_object
                step.name = f"Stair_Step_{half_steps+i+1:03d}"
                step.scale = (step_depth/2, step_width/2, step_height/2)
                created_objects.append(step)
        
        # Join all objects into one
        if created_objects:
            context.view_layer.objects.active = created_objects[0]
            for obj in created_objects:
                obj.select_set(True)
            bpy.ops.object.join()
            
            final_obj = context.active_object
            final_obj.name = "MyShapeObject"
            final_obj.location = (0, 0, 0)
        
        self.report({'INFO'}, f"{stair_type} staircase created with {steps} steps")
        return {'FINISHED'}
    
    def create_character(self, context):
        """Create basic character model"""
        import math
        
        scene = context.scene
        gender = scene.my_character_gender
        age = scene.my_character_age
        height = scene.my_character_height
        build = scene.my_character_build
        
        # Clear old objects
        for obj in bpy.data.objects:
            if obj.name.startswith(("Char_", "MyShapeObject")):
                bpy.data.objects.remove(obj, do_unlink=True)
        
        created_objects = []
        
        # Scale factors based on age
        age_scale = {
            'CHILD': 0.6,
            'TEEN': 0.85,
            'ADULT': 1.0,
            'ELDER': 0.95
        }
        scale_factor = age_scale[age]
        adjusted_height = height * scale_factor
        
        # Body proportions (based on adult proportions)
        head_size = adjusted_height * 0.12
        torso_height = adjusted_height * 0.35
        torso_width = head_size * 1.2 * build
        torso_depth = head_size * 0.8 * build
        leg_length = adjusted_height * 0.45
        leg_thickness = head_size * 0.35 * build
        arm_length = adjusted_height * 0.35
        arm_thickness = head_size * 0.25 * build
        
        # Gender-specific adjustments
        if gender == 'FEMALE':
            torso_width *= 0.85
            shoulder_width = torso_width * 1.3
            hip_width = torso_width * 1.2
            leg_thickness *= 0.9
            arm_thickness *= 0.85
        else:
            shoulder_width = torso_width * 1.5
            hip_width = torso_width * 0.95
        
        # Age-specific adjustments
        if age == 'CHILD':
            head_size *= 1.3  # Children have proportionally larger heads
            leg_thickness *= 1.1
            arm_thickness *= 1.1
        elif age == 'ELDER':
            torso_height *= 0.95  # Slightly shorter torso
            shoulder_width *= 0.9
        
        # 1. Head
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=head_size/2,
            location=(0, 0, adjusted_height - head_size/2)
        )
        head = context.active_object
        head.name = "Char_Head"
        head.scale = (1.0, 0.9, 1.1)  # Slightly elongated
        created_objects.append(head)
        
        # 2. Neck
        neck_height = adjusted_height * 0.05
        bpy.ops.mesh.primitive_cylinder_add(
            radius=head_size * 0.25,
            depth=neck_height,
            location=(0, 0, adjusted_height - head_size - neck_height/2)
        )
        neck = context.active_object
        neck.name = "Char_Neck"
        created_objects.append(neck)
        
        # 3. Upper Torso (chest)
        chest_z = adjusted_height - head_size - neck_height - torso_height * 0.3
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(0, 0, chest_z)
        )
        chest = context.active_object
        chest.name = "Char_Chest"
        chest.scale = (shoulder_width/2, torso_depth/2, torso_height * 0.3)
        
        # Add subdivision for smooth body
        subsurf = chest.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 2
        created_objects.append(chest)
        
        # 4. Lower Torso (abdomen and hips)
        abdomen_z = chest_z - torso_height * 0.35
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(0, 0, abdomen_z)
        )
        abdomen = context.active_object
        abdomen.name = "Char_Abdomen"
        abdomen.scale = ((shoulder_width + hip_width) / 4, torso_depth/2, torso_height * 0.35)
        
        subsurf = abdomen.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 2
        created_objects.append(abdomen)
        
        # 5. Legs
        leg_z = abdomen_z - torso_height * 0.35 - leg_length/2
        leg_separation = hip_width * 0.4
        
        for side in [-1, 1]:
            # Upper leg (thigh)
            bpy.ops.mesh.primitive_cylinder_add(
                radius=leg_thickness,
                depth=leg_length * 0.55,
                location=(side * leg_separation, 0, leg_z + leg_length * 0.225)
            )
            thigh = context.active_object
            thigh.name = f"Char_Thigh_{['L', 'R'][side>0]}"
            
            # Taper modifier for natural leg shape
            taper_mod = thigh.modifiers.new(name="Taper", type='SIMPLE_DEFORM')
            taper_mod.deform_method = 'TAPER'
            taper_mod.factor = -0.3
            taper_mod.deform_axis = 'Z'
            
            created_objects.append(thigh)
            
            # Lower leg (calf)
            bpy.ops.mesh.primitive_cylinder_add(
                radius=leg_thickness * 0.7,
                depth=leg_length * 0.45,
                location=(side * leg_separation, 0, leg_z - leg_length * 0.275)
            )
            calf = context.active_object
            calf.name = f"Char_Calf_{['L', 'R'][side>0]}"
            
            taper_mod = calf.modifiers.new(name="Taper", type='SIMPLE_DEFORM')
            taper_mod.deform_method = 'TAPER'
            taper_mod.factor = -0.2
            taper_mod.deform_axis = 'Z'
            
            created_objects.append(calf)
            
            # Foot
            foot_z = leg_z - leg_length/2 - head_size * 0.15
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(side * leg_separation, head_size * 0.15, foot_z)
            )
            foot = context.active_object
            foot.name = f"Char_Foot_{['L', 'R'][side>0]}"
            foot.scale = (leg_thickness * 0.8, head_size * 0.4, head_size * 0.2)
            created_objects.append(foot)
        
        # 6. Arms
        arm_z = chest_z
        arm_separation = shoulder_width * 0.6
        
        for side in [-1, 1]:
            # Upper arm
            bpy.ops.mesh.primitive_cylinder_add(
                radius=arm_thickness,
                depth=arm_length * 0.5,
                location=(side * arm_separation, 0, arm_z - arm_length * 0.25)
            )
            upper_arm = context.active_object
            upper_arm.name = f"Char_UpperArm_{['L', 'R'][side>0]}"
            
            taper_mod = upper_arm.modifiers.new(name="Taper", type='SIMPLE_DEFORM')
            taper_mod.deform_method = 'TAPER'
            taper_mod.factor = -0.25
            taper_mod.deform_axis = 'Z'
            
            created_objects.append(upper_arm)
            
            # Lower arm (forearm)
            bpy.ops.mesh.primitive_cylinder_add(
                radius=arm_thickness * 0.8,
                depth=arm_length * 0.5,
                location=(side * arm_separation, 0, arm_z - arm_length * 0.75)
            )
            forearm = context.active_object
            forearm.name = f"Char_Forearm_{['L', 'R'][side>0]}"
            
            taper_mod = forearm.modifiers.new(name="Taper", type='SIMPLE_DEFORM')
            taper_mod.deform_method = 'TAPER'
            taper_mod.factor = -0.2
            taper_mod.deform_axis = 'Z'
            
            created_objects.append(forearm)
            
            # Hand
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(side * arm_separation, 0, arm_z - arm_length - head_size * 0.1)
            )
            hand = context.active_object
            hand.name = f"Char_Hand_{['L', 'R'][side>0]}"
            hand.scale = (arm_thickness * 0.6, arm_thickness * 0.8, head_size * 0.15)
            
            subsurf = hand.modifiers.new(name="Subdivision", type='SUBSURF')
            subsurf.levels = 1
            
            created_objects.append(hand)
        
        # Join all objects into one
        if created_objects:
            context.view_layer.objects.active = created_objects[0]
            for obj in created_objects:
                obj.select_set(True)
            bpy.ops.object.join()
            
            final_obj = context.active_object
            final_obj.name = "MyShapeObject"
            final_obj.location = (0, 0, 0)
        
        self.report({'INFO'}, f"{age} {gender} character created (height: {adjusted_height:.2f}m)")
        return {'FINISHED'}


class MYADDON_OT_encode_geometry(bpy.types.Operator):
    bl_idname = "myaddon.encode_geometry"
    bl_label = "Encode Geometry"
    bl_description = "Encode current geometry to vector representation"
    
    def execute(self, context):
        scene = context.scene
        
        # Try to use currently selected object if it's a vector-based mesh
        obj = None
        active_obj = context.active_object
        if active_obj and active_obj.type == 'MESH':
            has_vector_data = all(f"geom_vector_{i}" in active_obj for i in range(32))
            if has_vector_data or active_obj.name == "MyShapeObject":
                obj = active_obj
        
        # Fallback to MyShapeObject
        if obj is None:
            obj = bpy.data.objects.get("MyShapeObject")
        
        # Encode current preset
        preset = scene.my_shape_preset
        vec = GeometryEncoder.encode_preset(preset, scene)
        
        # Store in latent space
        latent_space = get_latent_space()
        latent_space.add_geometry(f"preset_{preset}", vec)
        
        # Display vector info
        self.report({'INFO'}, f"Encoded {preset}: {vec}")
        
        # Store vector in scene custom property for visualization
        vec_str = ','.join([f"{v:.4f}" for v in vec.vector[:8]])  # First 8 dims
        self.report({'INFO'}, f"Vector (first 8 dims): [{vec_str}...]")
        
        return {'FINISHED'}


class MYADDON_OT_interpolate_geometry(bpy.types.Operator):
    bl_idname = "myaddon.interpolate_geometry"
    bl_label = "Interpolate Geometry"
    bl_description = "Interpolate between two presets"
    
    preset_a: bpy.props.EnumProperty(
        name="Preset A",
        items=[
            ('SPIRAL_CORRIDOR', "Spiral Corridor", ""),
            ('DNA_HELIX', "DNA Helix", ""),
            ('SPRING', "Spring", ""),
            ('TWISTED_TOWER', "Twisted Tower", ""),
            ('FIGHTER_JET', "Fighter Jet", ""),
            ('BOMBER', "Bomber", ""),
            ('HELICOPTER', "Helicopter", ""),
            ('STAIRCASE', "Staircase", ""),
            ('CHARACTER', "Character", ""),
        ],
        default='SPIRAL_CORRIDOR'
    )
    
    preset_b: bpy.props.EnumProperty(
        name="Preset B",
        items=[
            ('SPIRAL_CORRIDOR', "Spiral Corridor", ""),
            ('DNA_HELIX', "DNA Helix", ""),
            ('SPRING', "Spring", ""),
            ('TWISTED_TOWER', "Twisted Tower", ""),
            ('FIGHTER_JET', "Fighter Jet", ""),
            ('BOMBER', "Bomber", ""),
            ('HELICOPTER', "Helicopter", ""),
            ('STAIRCASE', "Staircase", ""),
            ('CHARACTER', "Character", ""),
        ],
        default='FIGHTER_JET'
    )
    
    interpolation_factor: bpy.props.FloatProperty(
        name="Interpolation (t)",
        default=0.5,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        description="Interpolation factor (0=A, 1=B)"
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Interpolate Between Presets", icon='ANIM')
        layout.separator()
        
        row = layout.row(align=True)
        row.prop(self, "preset_a", text="From")
        row.label(text="→")
        row.prop(self, "preset_b", text="To")
        
        layout.separator()
        layout.prop(self, "interpolation_factor", slider=True)
        
        # Show visual representation
        box = layout.box()
        box.label(text=f"t = {self.interpolation_factor:.2f}")
        col = box.column(align=True)
        col.label(text=f"├─ {int((1-self.interpolation_factor)*100)}% {self.preset_a}")
        col.label(text=f"└─ {int(self.interpolation_factor*100)}% {self.preset_b}")
    
    def execute(self, context):
        scene = context.scene
        
        # Encode both presets
        vec_a = GeometryEncoder.encode_preset(self.preset_a, scene)
        vec_b = GeometryEncoder.encode_preset(self.preset_b, scene)
        
        # Interpolate
        vec_interpolated = vec_a.interpolate(vec_b, self.interpolation_factor)
        
        # Decode back to scene parameters
        GeometryDecoder.decode_to_scene(vec_interpolated, scene)
        
        # Update the shape
        bpy.ops.myaddon.update_shape()
        
        self.report({'INFO'}, 
                   f"Interpolated: {self.preset_a}({1-self.interpolation_factor:.1f}) + "
                   f"{self.preset_b}({self.interpolation_factor:.1f})")
        
        return {'FINISHED'}


class MYADDON_OT_blend_geometry(bpy.types.Operator):
    bl_idname = "myaddon.blend_geometry"
    bl_label = "Blend Geometry"
    bl_description = "Blend multiple presets with custom weights"
    
    weight_1: bpy.props.FloatProperty(name="Weight 1", default=1.0, min=0.0, max=2.0)
    weight_2: bpy.props.FloatProperty(name="Weight 2", default=1.0, min=0.0, max=2.0)
    weight_3: bpy.props.FloatProperty(name="Weight 3", default=0.0, min=0.0, max=2.0)
    
    preset_1: bpy.props.EnumProperty(
        name="Preset 1",
        items=[
            ('SPIRAL_CORRIDOR', "Spiral Corridor", ""),
            ('DNA_HELIX', "DNA Helix", ""),
            ('TWISTED_TOWER', "Twisted Tower", ""),
            ('FIGHTER_JET', "Fighter Jet", ""),
        ],
        default='SPIRAL_CORRIDOR'
    )
    
    preset_2: bpy.props.EnumProperty(
        name="Preset 2",
        items=[
            ('SPIRAL_CORRIDOR', "Spiral Corridor", ""),
            ('DNA_HELIX', "DNA Helix", ""),
            ('TWISTED_TOWER', "Twisted Tower", ""),
            ('FIGHTER_JET', "Fighter Jet", ""),
        ],
        default='FIGHTER_JET'
    )
    
    preset_3: bpy.props.EnumProperty(
        name="Preset 3",
        items=[
            ('NONE', "None", ""),
            ('SPIRAL_CORRIDOR', "Spiral Corridor", ""),
            ('DNA_HELIX', "DNA Helix", ""),
            ('TWISTED_TOWER', "Twisted Tower", ""),
            ('CHARACTER', "Character", ""),
        ],
        default='NONE'
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Blend Multiple Geometries", icon='FORCE_HARMONIC')
        layout.separator()
        
        # Preset 1
        row = layout.row(align=True)
        row.prop(self, "preset_1", text="")
        row.prop(self, "weight_1", text="Weight")
        
        # Preset 2
        row = layout.row(align=True)
        row.prop(self, "preset_2", text="")
        row.prop(self, "weight_2", text="Weight")
        
        # Preset 3
        row = layout.row(align=True)
        row.prop(self, "preset_3", text="")
        row.prop(self, "weight_3", text="Weight")
        
        # Show normalized weights
        total = self.weight_1 + self.weight_2 + self.weight_3
        if total > 1e-6:
            box = layout.box()
            box.label(text="Normalized Contributions:")
            if self.weight_1 > 0:
                box.label(text=f"  {self.preset_1}: {self.weight_1/total*100:.1f}%")
            if self.weight_2 > 0:
                box.label(text=f"  {self.preset_2}: {self.weight_2/total*100:.1f}%")
            if self.weight_3 > 0 and self.preset_3 != 'NONE':
                box.label(text=f"  {self.preset_3}: {self.weight_3/total*100:.1f}%")
    
    def execute(self, context):
        scene = context.scene
        latent_space = get_latent_space()
        
        # Collect presets and weights
        presets = [self.preset_1, self.preset_2]
        weights = [self.weight_1, self.weight_2]
        
        if self.preset_3 != 'NONE' and self.weight_3 > 0:
            presets.append(self.preset_3)
            weights.append(self.weight_3)
        
        # Encode presets
        for preset in presets:
            vec = GeometryEncoder.encode_preset(preset, scene)
            latent_space.add_geometry(preset, vec)
        
        # Blend
        blended_vec = latent_space.blend_geometries(presets, weights)
        
        if blended_vec is None:
            self.report({'ERROR'}, "Failed to blend geometries")
            return {'CANCELLED'}
        
        # Decode
        GeometryDecoder.decode_to_scene(blended_vec, scene)
        
        # Update
        bpy.ops.myaddon.update_shape()
        
        self.report({'INFO'}, f"Blended {len(presets)} geometries")
        return {'FINISHED'}


class MYADDON_OT_find_similar_geometry(bpy.types.Operator):
    bl_idname = "myaddon.find_similar_geometry"
    bl_label = "Find Similar"
    bl_description = "Find geometries similar to current one in latent space"
    
    def execute(self, context):
        scene = context.scene
        
        # Try to use currently selected object if it's a vector-based mesh
        obj = None
        active_obj = context.active_object
        if active_obj and active_obj.type == 'MESH':
            has_vector_data = all(f"geom_vector_{i}" in active_obj for i in range(32))
            if has_vector_data or active_obj.name == "MyShapeObject":
                obj = active_obj
        
        # Fallback to MyShapeObject
        if obj is None:
            obj = bpy.data.objects.get("MyShapeObject")
        
        if obj is None:
            self.report({'WARNING'}, "No object selected or found")
            return {'CANCELLED'}
        
        # Encode current object
        current_vec = GeometryEncoder.encode_object(obj)
        
        # Initialize latent space with all presets
        latent_space = get_latent_space()
        presets = ['SPIRAL_CORRIDOR', 'DNA_HELIX', 'SPRING', 'TWISTED_TOWER',
                   'FIGHTER_JET', 'BOMBER', 'HELICOPTER', 'STAIRCASE', 'CHARACTER']
        
        for preset in presets:
            vec = GeometryEncoder.encode_preset(preset, scene)
            latent_space.add_geometry(preset, vec)
        
        # Find neighbors
        neighbors = latent_space.get_neighbors(current_vec, k=5)
        
        # Report results
        self.report({'INFO'}, "Similar geometries:")
        for i, (name, distance) in enumerate(neighbors, 1):
            print(f"{i}. {name} (distance: {distance:.3f})")
        
        if neighbors:
            self.report({'INFO'}, f"Most similar: {neighbors[0][0]} (dist: {neighbors[0][1]:.3f})")
        
        return {'FINISHED'}


class MYADDON_OT_vector_to_clipboard(bpy.types.Operator):
    bl_idname = "myaddon.vector_to_clipboard"
    bl_label = "Copy to Clipboard"
    bl_description = "Copy current vector to clipboard for operations"
    
    def execute(self, context):
        scene = context.scene
        # Copy current vector to clipboard
        for i in range(32):
            scene.geom_vector_clipboard[i] = scene.geom_vector_current[i]
        
        self.report({'INFO'}, "Vector copied to clipboard")
        return {'FINISHED'}


class MYADDON_OT_vector_from_clipboard(bpy.types.Operator):
    bl_idname = "myaddon.vector_from_clipboard"
    bl_label = "Paste from Clipboard"
    bl_description = "Paste vector from clipboard to current"
    
    def execute(self, context):
        scene = context.scene
        # Copy clipboard to current vector
        for i in range(32):
            scene.geom_vector_current[i] = scene.geom_vector_clipboard[i]
        
        self.report({'INFO'}, "Vector pasted from clipboard")
        return {'FINISHED'}


class MYADDON_OT_vector_arithmetic(bpy.types.Operator):
    bl_idname = "myaddon.vector_arithmetic"
    bl_label = "Apply Operation"
    bl_description = "Perform arithmetic operation on vectors"
    
    def execute(self, context):
        scene = context.scene
        operation = scene.vector_arithmetic_operation
        
        import numpy as np
        current = np.array([scene.geom_vector_current[i] for i in range(32)])
        clipboard = np.array([scene.geom_vector_clipboard[i] for i in range(32)])
        
        result = None
        op_desc = ""
        
        if operation == 'ADD':
            result = current + clipboard
            op_desc = "Added clipboard to current"
        elif operation == 'SUBTRACT':
            result = current - clipboard
            op_desc = "Subtracted clipboard from current"
        elif operation == 'MULTIPLY':
            scalar = scene.vector_scalar_value
            result = current * scalar
            op_desc = f"Multiplied by {scalar:.2f}"
        elif operation == 'DIVIDE':
            scalar = scene.vector_scalar_value
            if abs(scalar) < 1e-6:
                self.report({'ERROR'}, "Cannot divide by zero")
                return {'CANCELLED'}
            result = current / scalar
            op_desc = f"Divided by {scalar:.2f}"
        elif operation == 'LERP':
            t = scene.vector_lerp_factor
            result = (1 - t) * current + t * clipboard
            op_desc = f"Interpolated (t={t:.2f})"
        
        if result is not None:
            # Update current vector with result
            for i in range(32):
                scene.geom_vector_current[i] = float(result[i])
            
            self.report({'INFO'}, op_desc)
        
        return {'FINISHED'}


class MYADDON_OT_vector_reset(bpy.types.Operator):
    bl_idname = "myaddon.vector_reset"
    bl_label = "Reset Vector"
    bl_description = "Reset vector to zeros"
    
    def execute(self, context):
        scene = context.scene
        for i in range(32):
            scene.geom_vector_current[i] = 0.0
        
        self.report({'INFO'}, "Vector reset to zero")
        return {'FINISHED'}


class MYADDON_OT_vector_normalize(bpy.types.Operator):
    bl_idname = "myaddon.vector_normalize"
    bl_label = "Normalize"
    bl_description = "Normalize vector to unit length"
    
    def execute(self, context):
        scene = context.scene
        import numpy as np
        
        vec = np.array([scene.geom_vector_current[i] for i in range(32)])
        norm = np.linalg.norm(vec)
        
        if norm < 1e-6:
            self.report({'WARNING'}, "Vector is too small to normalize")
            return {'CANCELLED'}
        
        normalized = vec / norm
        for i in range(32):
            scene.geom_vector_current[i] = float(normalized[i])
        
        self.report({'INFO'}, f"Vector normalized (was {norm:.3f})")
        return {'FINISHED'}


class MYADDON_OT_apply_source_modifiers(bpy.types.Operator):
    bl_idname = "myaddon.apply_source_modifiers"
    bl_label = "Apply Source Modifiers"
    bl_description = "Apply modifiers that were saved from the original exported object"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        active_obj = context.active_object
        
        if not active_obj or active_obj.type != 'MESH':
            self.report({'WARNING'}, "Please select a mesh object")
            return {'CANCELLED'}
        
        # Check if object has stored modifier data
        if "geometry_vector_modifiers" not in active_obj:
            self.report({'WARNING'}, "No modifier data found. This object was not imported with modifiers.")
            return {'CANCELLED'}
        
        try:
            import json
            modifiers_data = json.loads(active_obj["geometry_vector_modifiers"])
            
            if not modifiers_data:
                self.report({'WARNING'}, "Modifier data is empty")
                return {'CANCELLED'}
            
            # Clear existing modifiers
            active_obj.modifiers.clear()
            
            # Apply each saved modifier
            applied_count = 0
            for mod_data in modifiers_data:
                mod_type = mod_data.get("type")
                mod_name = mod_data.get("name", mod_type)
                
                try:
                    # Create modifier
                    mod = active_obj.modifiers.new(name=mod_name, type=mod_type)
                    
                    # Apply common properties
                    mod.show_viewport = mod_data.get("show_viewport", True)
                    mod.show_render = mod_data.get("show_render", True)
                    
                    # Apply type-specific properties
                    if mod_type == 'MIRROR':
                        if "use_axis" in mod_data:
                            mod.use_axis[0] = mod_data["use_axis"][0]
                            mod.use_axis[1] = mod_data["use_axis"][1]
                            mod.use_axis[2] = mod_data["use_axis"][2]
                        if "use_bisect_axis" in mod_data:
                            mod.use_bisect_axis[0] = mod_data["use_bisect_axis"][0]
                            mod.use_bisect_axis[1] = mod_data["use_bisect_axis"][1]
                            mod.use_bisect_axis[2] = mod_data["use_bisect_axis"][2]
                        if "use_clip" in mod_data:
                            mod.use_clip = mod_data["use_clip"]
                        if "merge_threshold" in mod_data:
                            mod.merge_threshold = mod_data["merge_threshold"]
                    
                    elif mod_type == 'ARRAY':
                        if "count" in mod_data:
                            mod.count = mod_data["count"]
                        if "use_relative_offset" in mod_data:
                            mod.use_relative_offset = mod_data["use_relative_offset"]
                        if "relative_offset_displace" in mod_data:
                            mod.relative_offset_displace = mod_data["relative_offset_displace"]
                    
                    elif mod_type == 'SUBSURF':
                        if "levels" in mod_data:
                            mod.levels = mod_data["levels"]
                        if "render_levels" in mod_data:
                            mod.render_levels = mod_data["render_levels"]
                    
                    elif mod_type == 'SOLIDIFY':
                        if "thickness" in mod_data:
                            mod.thickness = mod_data["thickness"]
                        if "offset" in mod_data:
                            mod.offset = mod_data["offset"]
                    
                    elif mod_type == 'BEVEL':
                        if "width" in mod_data:
                            mod.width = mod_data["width"]
                        if "segments" in mod_data:
                            mod.segments = mod_data["segments"]
                    
                    applied_count += 1
                    print(f"[ApplyModifiers] Applied {mod_type} modifier: {mod_name}")
                    
                except Exception as e:
                    print(f"[ApplyModifiers] Failed to apply {mod_type} modifier: {e}")
                    continue
            
            self.report({'INFO'}, f"Applied {applied_count} modifier(s) from source")
            
            # Remove the stored modifier data after application
            del active_obj["geometry_vector_modifiers"]
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to parse modifier data: {e}")
            return {'CANCELLED'}


class MYADDON_OT_vector_decode_and_render(bpy.types.Operator):
    bl_idname = "myaddon.vector_decode_and_render"
    bl_label = "Decode & Render"
    bl_description = "Decode current vector and render as 3D object"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        
        # Convert scene properties to GeometryVector
        import numpy as np
        vec_array = np.array([scene.geom_vector_current[i] for i in range(32)])
        geom_vec = GeometryVector(vec_array)
        
        # Check if user wants to update an existing object
        active_obj = context.active_object
        update_existing = False
        
        if active_obj and active_obj.type == 'MESH':
            # Check if this object has vector data (was created/imported with vectors)
            has_vector_data = all(f"geom_vector_{i}" in active_obj for i in range(32))
            source = active_obj.get("geometry_vector_source", "unknown")
            
            # Allow updating for all vector-based objects
            # Only exclude "unknown" source (objects without proper vector metadata)
            if has_vector_data and source != "unknown":
                # This is a vector-based object, update it instead of creating new one
                update_existing = True
                print(f"[Decode&Render] Updating existing object: {active_obj.name} (source: {source})")
        
        if update_existing:
            # Update existing object with new vector parameters
            self._update_object_with_vector(context, active_obj, geom_vec, scene)
            self.report({'INFO'}, f"Updated {active_obj.name} with new vector parameters")
        else:
            # Create new object from vector
            # Decode to scene parameters first
            GeometryDecoder.decode_to_scene(geom_vec, scene)
            
            # Check if this vector came from a preset
            if scene.vector_source_preset and scene.vector_source_preset != "NONE":
                # Vector from preset - use preset-based workflow
                target_preset = scene.vector_source_preset
                scene.my_shape_preset = target_preset
                
                # First decode vector to scene parameters (for parameters-based presets)
                GeometryDecoder.decode_to_scene(geom_vec, scene)
                
                # Apply the preset to set parameters
                bpy.ops.myaddon.apply_preset()
                
                # Create the actual geometry from the preset
                # This will call create_aircraft/create_staircase/create_character for complex presets
                # or create standard shape with modifiers for parametric presets
                bpy.ops.myaddon.update_shape()
                
                # Get the created preset object
                preset_obj = context.active_object
                
                if preset_obj:
                    # Now apply vector modifications on top of preset
                    self._apply_vector_modifiers(preset_obj, geom_vec)
                    
                    # Store vector data
                    for i in range(32):
                        preset_obj[f"geom_vector_{i}"] = float(geom_vec.vector[i])
                    
                    preset_obj["geometry_vector_source"] = "preset"
                    preset_obj["geometry_vector_version"] = "1.0"
                    preset_obj["geometry_vector_preset_name"] = target_preset  # Save preset name!
                    preset_obj["geometry_vector_mesh_verts"] = len(preset_obj.data.vertices)
                    preset_obj["geometry_vector_mesh_faces"] = len(preset_obj.data.polygons)
                
                self.report({'INFO'}, f"Decoded and rendered as {target_preset} with vector modifications")
            else:
                # Vector from external file or custom object - generate directly from parameters
                # Create a parametric object based on decoded parameters
                self._create_geometry_from_vector(context, geom_vec, scene)
                
                self.report({'INFO'}, "Decoded and rendered from vector parameters")
        
        return {'FINISHED'}
    
    def _update_object_with_vector(self, context, obj, vec, scene):
        """Update existing object with new vector parameters"""
        # Remove all existing modifiers
        obj.modifiers.clear()
        
        # Get the base mesh (before any modifications)
        # If object was manually edited, we can't safely update it
        source = obj.get("geometry_vector_source", "unknown")
        
        if source == "manual_edit":
            # Object was manually edited - warn user
            self.report({'WARNING'}, 
                       "Object was manually edited. Creating new object to preserve edits.")
            # Create new object instead
            self._create_geometry_from_vector(context, vec, scene)
            return
        
        # Update transformations
        obj.scale = (
            vec.vector[GeometryVector.IDX_SCALE_X],
            vec.vector[GeometryVector.IDX_SCALE_Y],
            vec.vector[GeometryVector.IDX_SCALE_Z]
        )
        obj.location = (
            vec.vector[GeometryVector.IDX_LOC_X],
            vec.vector[GeometryVector.IDX_LOC_Y],
            vec.vector[GeometryVector.IDX_LOC_Z]
        )
        obj.rotation_euler = (
            vec.vector[GeometryVector.IDX_ROT_X],
            vec.vector[GeometryVector.IDX_ROT_Y],
            vec.vector[GeometryVector.IDX_ROT_Z]
        )
        
        # Reapply modifiers from vector
        self._apply_vector_modifiers(obj, vec)
        
        # Update stored vector data
        for i in range(32):
            obj[f"geom_vector_{i}"] = float(vec.vector[i])
        
        # Update mesh fingerprint
        obj["geometry_vector_mesh_verts"] = len(obj.data.vertices)
        obj["geometry_vector_mesh_faces"] = len(obj.data.polygons)
        
        print(f"[Decode&Render] Updated object with new parameters")
    
    def _apply_vector_modifiers(self, obj, vec):
        """Apply modifiers based on vector parameters"""
        import math
        
        # Apply sphericity
        sphericity = vec.vector[GeometryVector.IDX_SPHERICITY]
        if abs(sphericity) > 0.01:
            mod = obj.modifiers.new(name="Sphericity", type='CAST')
            mod.factor = sphericity
            mod.cast_type = 'SPHERE'
        
        # Apply taper
        taper = vec.vector[GeometryVector.IDX_TAPER]
        if abs(taper) > 0.01:
            mod = obj.modifiers.new(name="Taper", type='SIMPLE_DEFORM')
            mod.deform_method = 'TAPER'
            mod.factor = taper
        
        # Apply twist
        twist = vec.vector[GeometryVector.IDX_TWIST] * 2 * 3.14159
        if abs(twist) > 0.01:
            mod = obj.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
            mod.deform_method = 'TWIST'
            mod.angle = twist
        
        # Apply bend
        bend = vec.vector[GeometryVector.IDX_BEND] * 2 * 3.14159
        if abs(bend) > 0.01:
            mod = obj.modifiers.new(name="Bend", type='SIMPLE_DEFORM')
            mod.deform_method = 'BEND'
            mod.angle = bend
        
        # Apply elongation
        elongation = vec.vector[GeometryVector.IDX_ELONGATION]
        if abs(elongation - 0.33) > 0.05:
            mod = obj.modifiers.new(name="Elongation", type='SIMPLE_DEFORM')
            mod.deform_method = 'STRETCH'
            mod.factor = (elongation - 0.33) * 3.0
        
        # Apply wave
        wave_amplitude = vec.vector[GeometryVector.IDX_WAVE_AMP]
        if abs(wave_amplitude) > 0.01:
            mod = obj.modifiers.new(name="Wave", type='WAVE')
            mod.height = wave_amplitude
            mod.width = vec.vector[GeometryVector.IDX_WAVE_FREQ] * 2.0 if vec.vector[GeometryVector.IDX_WAVE_FREQ] > 0.01 else 1.0
        
        # Apply noise
        noise_strength = vec.vector[GeometryVector.IDX_NOISE_STRENGTH]
        if abs(noise_strength) > 0.01:
            mod = obj.modifiers.new(name="Noise", type='DISPLACE')
            mod.strength = noise_strength
            tex = bpy.data.textures.new("NoiseTexture", type='CLOUDS')
            tex.noise_scale = vec.vector[GeometryVector.IDX_NOISE_SCALE] * 2.0 if vec.vector[GeometryVector.IDX_NOISE_SCALE] > 0.01 else 1.0
            mod.texture = tex
        
        # Apply subdivision
        curvature = vec.vector[GeometryVector.IDX_CURVATURE]
        if curvature > 0.1:
            mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
            mod.levels = max(1, min(3, int(curvature * 5)))
            mod.render_levels = mod.levels
        
        # Apply smoothness
        smoothness = vec.vector[GeometryVector.IDX_SMOOTHNESS]
        if smoothness > 0.1:
            has_subsurf = any(m.type == 'SUBSURF' for m in obj.modifiers)
            if not has_subsurf:
                mod = obj.modifiers.new(name="Smoothness", type='SUBSURF')
                mod.levels = max(1, min(3, int(smoothness * 3)))
                mod.render_levels = mod.levels
        
        # Apply edge sharpness
        edge_sharpness = vec.vector[GeometryVector.IDX_EDGE_SHARPNESS]
        if edge_sharpness > 0.1:
            mod = obj.modifiers.new(name="EdgeSharp", type='EDGE_SPLIT')
            mod.split_angle = math.radians(180 * (1 - edge_sharpness))
            mod.use_edge_angle = True
        
        # Apply inflation
        inflation = vec.vector[GeometryVector.IDX_INFLATION]
        if abs(inflation) > 0.01:
            mod = obj.modifiers.new(name="Inflate", type='DISPLACE')
            mod.strength = inflation * 0.5
            mod.direction = 'NORMAL'
        
        # Apply randomness
        randomness = vec.vector[GeometryVector.IDX_RANDOMNESS]
        if randomness > 0.01:
            mod = obj.modifiers.new(name="Random", type='DISPLACE')
            mod.strength = randomness * 0.1
            tex_name = f"RandomTex_{obj.name}"
            tex = bpy.data.textures.get(tex_name)
            if not tex:
                tex = bpy.data.textures.new(tex_name, type='CLOUDS')
                tex.noise_scale = 5.0
            mod.texture = tex
    
    def _create_geometry_from_vector(self, context, vec, scene):
        """Create geometry directly from vector parameters without using presets"""
        import bmesh
        from mathutils import Vector, Matrix
        
        # Check if we have a cached source mesh from file import
        has_source_mesh = scene.vector_source_mesh and scene.vector_source_mesh in bpy.data.meshes
        
        if has_source_mesh:
            # Use the original imported mesh as base - this is already a complete geometry
            source_mesh = bpy.data.meshes[scene.vector_source_mesh]
            mesh = source_mesh.copy()
            mesh.name = "DecodedGeometry"
        else:
            # No source mesh - create parametric geometry from scratch
            # Create base mesh - start with a subdivided cube for flexibility
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            
            # Subdivide for more detail
            bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
            
            # Create mesh
            mesh = bpy.data.meshes.new("DecodedGeometry")
            bm.to_mesh(mesh)
            bm.free()
        
        # Remove old decoded object if exists
        old_obj = bpy.data.objects.get("DecodedGeometry")
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)
        
        # Create new object
        obj = bpy.data.objects.new("DecodedGeometry", mesh)
        context.scene.collection.objects.link(obj)
        
        # Get scale from vector
        scale_x = vec.vector[GeometryVector.IDX_SCALE_X]
        scale_y = vec.vector[GeometryVector.IDX_SCALE_Y]
        scale_z = vec.vector[GeometryVector.IDX_SCALE_Z]
        
        # Apply scale
        obj.scale = (scale_x, scale_y, scale_z)
        
        # Get location from vector
        loc_x = vec.vector[GeometryVector.IDX_LOC_X]
        loc_y = vec.vector[GeometryVector.IDX_LOC_Y]
        loc_z = vec.vector[GeometryVector.IDX_LOC_Z]
        
        # Apply location
        obj.location = (loc_x, loc_y, loc_z)
        
        # Get rotation from vector
        rot_x = vec.vector[GeometryVector.IDX_ROT_X]
        rot_y = vec.vector[GeometryVector.IDX_ROT_Y]
        rot_z = vec.vector[GeometryVector.IDX_ROT_Z]
        
        # Apply rotation (rotation is stored in radians in the vector)
        obj.rotation_euler = (rot_x, rot_y, rot_z)
        
        # If this is from a cached source mesh (imported file), 
        # DO NOT apply parametric modifiers - the geometry is already complete
        # Only apply basic transforms (scale, rotation) that were encoded
        if not has_source_mesh:
            # Only apply parametric modifiers for generated geometry (not imported)
            # Apply topology transforms through modifiers
            sphericity = vec.vector[GeometryVector.IDX_SPHERICITY]
            if abs(sphericity) > 0.01:
                mod = obj.modifiers.new(name="Sphericity", type='CAST')
                mod.factor = sphericity
                mod.cast_type = 'SPHERE'
            
            taper = vec.vector[GeometryVector.IDX_TAPER]
            if abs(taper) > 0.01:
                mod = obj.modifiers.new(name="Taper", type='SIMPLE_DEFORM')
                mod.deform_method = 'TAPER'
                mod.factor = taper
            
            twist = vec.vector[GeometryVector.IDX_TWIST] * 2 * 3.14159
            if abs(twist) > 0.01:
                mod = obj.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
                mod.deform_method = 'TWIST'
                mod.angle = twist
            
            bend = vec.vector[GeometryVector.IDX_BEND] * 2 * 3.14159
            if abs(bend) > 0.01:
                mod = obj.modifiers.new(name="Bend", type='SIMPLE_DEFORM')
                mod.deform_method = 'BEND'
                mod.angle = bend
            
            # Apply elongation as stretch deformation
            elongation = vec.vector[GeometryVector.IDX_ELONGATION]
            if abs(elongation - 0.33) > 0.05:  # 0.33 is neutral elongation
                mod = obj.modifiers.new(name="Elongation", type='SIMPLE_DEFORM')
                mod.deform_method = 'STRETCH'
                mod.factor = (elongation - 0.33) * 3.0
            
            # Apply wave deformation
            wave_amplitude = vec.vector[GeometryVector.IDX_WAVE_AMP]
            if abs(wave_amplitude) > 0.01:
                mod = obj.modifiers.new(name="Wave", type='WAVE')
                mod.height = wave_amplitude
                mod.width = vec.vector[GeometryVector.IDX_WAVE_FREQ] * 2.0 if vec.vector[GeometryVector.IDX_WAVE_FREQ] > 0.01 else 1.0
            
            # Apply noise displacement
            noise_strength = vec.vector[GeometryVector.IDX_NOISE_STRENGTH]
            if abs(noise_strength) > 0.01:
                mod = obj.modifiers.new(name="Noise", type='DISPLACE')
                mod.strength = noise_strength
                # Create texture for noise
                tex = bpy.data.textures.new("NoiseTexture", type='CLOUDS')
                tex.noise_scale = vec.vector[GeometryVector.IDX_NOISE_SCALE] * 2.0 if vec.vector[GeometryVector.IDX_NOISE_SCALE] > 0.01 else 1.0
                mod.texture = tex
            
            # Add subdivision surface for smoothness (from old curvature)
            curvature = vec.vector[GeometryVector.IDX_CURVATURE]
            if curvature > 0.1:
                mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
                mod.levels = max(1, min(3, int(curvature * 5)))
                mod.render_levels = mod.levels
        
        # ========== Universal Appearance Parameters ==========
        # These apply to BOTH Preset and Import modes
        
        # 1. Smoothness (Subdivision Surface)
        smoothness = vec.vector[GeometryVector.IDX_SMOOTHNESS]
        if smoothness > 0.1:
            # Check if already has subdivision from curvature
            has_subsurf = any(m.type == 'SUBSURF' for m in obj.modifiers)
            if not has_subsurf:
                mod = obj.modifiers.new(name="Smoothness", type='SUBSURF')
                mod.levels = max(1, min(3, int(smoothness * 3)))
                mod.render_levels = mod.levels
        
        # 2. Edge Sharpness
        edge_sharpness = vec.vector[GeometryVector.IDX_EDGE_SHARPNESS]
        if edge_sharpness > 0.1:
            mod = obj.modifiers.new(name="EdgeSharp", type='EDGE_SPLIT')
            mod.split_angle = math.radians(180 * (1 - edge_sharpness))
            mod.use_edge_angle = True
        
        # 3. Inflation (along normals)
        inflation = vec.vector[GeometryVector.IDX_INFLATION]
        if abs(inflation) > 0.01:
            mod = obj.modifiers.new(name="Inflate", type='DISPLACE')
            mod.strength = inflation * 0.5
            mod.direction = 'NORMAL'
        
        # 4. Randomness (surface perturbation)
        randomness = vec.vector[GeometryVector.IDX_RANDOMNESS]
        if randomness > 0.01:
            mod = obj.modifiers.new(name="Random", type='DISPLACE')
            mod.strength = randomness * 0.1
            # Create unique texture for this object
            tex_name = f"RandomTex_{obj.name}"
            tex = bpy.data.textures.get(tex_name)
            if not tex:
                tex = bpy.data.textures.new(tex_name, type='CLOUDS')
                tex.noise_scale = 5.0
            mod.texture = tex
        
        # ========== CRITICAL: Save vector data to object ==========
        # Store the vector that was used to create this geometry
        # This ensures Export will save the correct vector, not re-encoded one
        for i in range(32):
            obj[f"geom_vector_{i}"] = float(vec.vector[i])
        
        # Store metadata
        obj["geometry_vector_source"] = "decode_render"
        obj["geometry_vector_version"] = "1.0"
        
        # Store mesh "fingerprint" to detect manual edits later
        # This allows us to determine if object is still "pure vector"
        obj["geometry_vector_mesh_verts"] = len(obj.data.vertices)
        obj["geometry_vector_mesh_faces"] = len(obj.data.polygons)
        
        # Set as active and select
        context.view_layer.objects.active = obj
        obj.select_set(True)
        
        return obj


class MYADDON_OT_vector_load_from_preset(bpy.types.Operator):
    bl_idname = "myaddon.vector_load_from_preset"
    bl_label = "Load from Preset"
    bl_description = "Load vector from a preset"
    
    preset_name: bpy.props.EnumProperty(
        name="Preset",
        items=[
            ('NONE', "Cube", ""),
            ('SPIRAL_CORRIDOR', "Spiral Corridor", ""),
            ('DNA_HELIX', "DNA Helix", ""),
            ('SPRING', "Spring", ""),
            ('TWISTED_TOWER', "Twisted Tower", ""),
            ('FIGHTER_JET', "Fighter Jet", ""),
            ('BOMBER', "Bomber", ""),
            ('HELICOPTER', "Helicopter", ""),
            ('STAIRCASE', "Staircase", ""),
            ('CHARACTER', "Character", ""),
        ]
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name")
    
    def execute(self, context):
        scene = context.scene
        
        # Encode preset to vector
        geom_vec = GeometryEncoder.encode_preset(self.preset_name, scene)
        
        # Load into current vector
        for i in range(32):
            scene.geom_vector_current[i] = float(geom_vec.vector[i])
        
        # Store the source preset
        scene.vector_source_preset = self.preset_name
        
        # Auto-expand vector editor
        scene.show_vector_editor = True
        
        self.report({'INFO'}, f"Loaded vector from {self.preset_name}")
        return {'FINISHED'}


class MYADDON_OT_vector_load_from_object(bpy.types.Operator):
    bl_idname = "myaddon.vector_load_from_object"
    bl_label = "Load from Active Object"
    bl_description = "Encode active object to vector"
    
    def execute(self, context):
        scene = context.scene
        
        if not context.active_object or context.active_object.type != 'MESH':
            self.report({'ERROR'}, "No active mesh object")
            return {'CANCELLED'}
        
        target_obj = context.active_object
        
        # Create a backup copy of the mesh data for later decoding
        original_mesh = target_obj.data
        backup_mesh_name = f"__vector_source_{original_mesh.name}"
        
        # Remove old backup if exists
        old_backup = bpy.data.meshes.get(backup_mesh_name)
        if old_backup:
            bpy.data.meshes.remove(old_backup)
        
        # Create new backup by copying the mesh
        backup_mesh = original_mesh.copy()
        backup_mesh.name = backup_mesh_name
        
        # Store reference to backup mesh
        scene.vector_source_mesh = backup_mesh_name
        
        # Encode object to vector
        geom_vec = GeometryEncoder.encode_object(target_obj)
        
        # Load into current vector
        for i in range(32):
            scene.geom_vector_current[i] = float(geom_vec.vector[i])
        
        # Store source info
        scene.vector_source_preset = "NONE"  # Not from preset
        
        # Auto-expand vector editor
        scene.show_vector_editor = True
        
        self.report({'INFO'}, f"Loaded vector from {target_obj.name}")
        return {'FINISHED'}


class MYADDON_OT_vector_load_from_file(bpy.types.Operator):
    bl_idname = "myaddon.vector_load_from_file"
    bl_label = "Load from Blender File"
    bl_description = "Import object from .blend file and encode to vector"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to the Blender file",
        subtype='FILE_PATH'
    )
    
    filter_glob: bpy.props.StringProperty(
        default="*.blend",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        scene = context.scene
        
        if not self.filepath or not self.filepath.endswith('.blend'):
            self.report({'ERROR'}, "Please select a valid .blend file")
            return {'CANCELLED'}
        
        try:
            # Store current objects to identify new ones
            existing_objects = set(bpy.data.objects[:])
            
            # Append all mesh objects from the file
            with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
                data_to.objects = [name for name in data_from.objects]
            
            # Link imported objects to scene and find mesh objects
            imported_meshes = []
            for obj in data_to.objects:
                if obj and obj not in existing_objects:
                    if obj.type == 'MESH':
                        # Link to current scene
                        if obj.name not in scene.collection.objects:
                            scene.collection.objects.link(obj)
                        imported_meshes.append(obj)
                    elif obj.type in ['EMPTY', 'CURVE', 'LIGHT', 'CAMERA']:
                        # Link non-mesh objects but don't encode them
                        if obj.name not in scene.collection.objects:
                            scene.collection.objects.link(obj)
            
            if not imported_meshes:
                self.report({'WARNING'}, "No mesh objects found in the file")
                return {'CANCELLED'}
            
            # Use the first mesh object for encoding
            target_obj = imported_meshes[0]
            
            # Create a backup copy of the mesh data for later decoding
            original_mesh = target_obj.data
            backup_mesh_name = f"__vector_source_{original_mesh.name}"
            
            # Remove old backup if exists
            old_backup = bpy.data.meshes.get(backup_mesh_name)
            if old_backup:
                bpy.data.meshes.remove(old_backup)
            
            # Create new backup by copying the mesh
            backup_mesh = original_mesh.copy()
            backup_mesh.name = backup_mesh_name
            
            # Store reference to backup mesh
            scene.vector_source_mesh = backup_mesh_name
            
            # Set as active object
            bpy.context.view_layer.objects.active = target_obj
            target_obj.select_set(True)
            
            # Encode object to vector
            geom_vec = GeometryEncoder.encode_object(target_obj)
            
            # Load into current vector
            for i in range(32):
                scene.geom_vector_current[i] = float(geom_vec.vector[i])
            
            # Store source info
            scene.vector_source_preset = "NONE"  # Not from preset
            
            # Auto-expand vector editor
            scene.show_vector_editor = True
            
            import os
            filename = os.path.basename(self.filepath)
            self.report({'INFO'}, f"Loaded vector from {target_obj.name} ({filename})")
            
            if len(imported_meshes) > 1:
                self.report({'INFO'}, f"Imported {len(imported_meshes)} mesh objects, encoded first: {target_obj.name}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to import file: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MYADDON_OT_export_gvec(bpy.types.Operator):
    """Export geometry vector to .gvec file (vector + mesh data)"""
    bl_idname = "myaddon.export_gvec"
    bl_label = "Export .gvec File"
    bl_description = "Export current geometry to .gvec format (vector + mesh)"
    
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to save .gvec file",
        subtype='FILE_PATH'
    )
    
    filename_ext = ".gvec"
    filter_glob: bpy.props.StringProperty(
        default="*.gvec",
        options={'HIDDEN'}
    )
    
    include_mesh: bpy.props.BoolProperty(
        name="Include Mesh Data",
        description="Include full mesh geometry in file",
        default=True
    )
    
    def execute(self, context):
        scene = context.scene
        
        # Get active object
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No active mesh object selected")
            return {'CANCELLED'}
        
        try:
            # Try to get stored vector first (from Decode&Render or Import)
            geom_vec = None
            has_stored_vector = all(f"geom_vector_{i}" in obj for i in range(32))
            
            if has_stored_vector:
                # Use stored vector (modified vector that created this object)
                vector_array = np.array([obj[f"geom_vector_{i}"] for i in range(32)], dtype=np.float32)
                geom_vec = GeometryVector(vector_array)
                self.report({'INFO'}, "Using stored vector from object")
            else:
                # Re-encode from geometry (fallback)
                geom_vec = GeometryEncoder.encode_object(obj)
                self.report({'INFO'}, "Re-encoding vector from geometry")
            
            # Prepare metadata
            metadata = {
                "name": obj.name,
                "source": obj.get("geometry_vector_source", "unknown"),
                "version": obj.get("geometry_vector_version", "1.0")
            }
            
            # For preset objects, try to identify and save the preset name
            # This allows correct reconstruction on import
            if metadata["source"] == "preset":
                # Try to get preset name from various sources
                preset_name = None
                
                # Method 1: Check if stored as custom property
                if "geometry_vector_preset_name" in obj:
                    preset_name = obj["geometry_vector_preset_name"]
                    
                # Method 2: Try to identify from current vector in scene
                elif context.scene.vector_source_preset and context.scene.vector_source_preset != "NONE":
                    preset_name = context.scene.vector_source_preset
                    
                # Method 3: Try to match vector to known presets
                if not preset_name:
                    preset_name = self._identify_preset_from_object(obj, context.scene)
                
                if preset_name:
                    metadata["preset_name"] = preset_name
                    print(f"[Export] Identified preset: {preset_name}")
            
            
            # Determine if we should include mesh
            # Strategy with comprehensive edit detection:
            # 1. If user disabled mesh (include_mesh=False), respect that
            # 2. Check if decode_render object has been manually edited (topology change)
            # 3. Check if object has multiple mesh data users (merged/joined objects)
            # 4. If object was IMPORTED with mesh data, preserve mesh+vector mode
            # 5. Only use vector-only if object is unmodified decode_render with modifiers
            
            source = obj.get("geometry_vector_source", "unknown")
            has_source_mesh = obj.get("geometry_vector_source_mesh") is not None
            include_mesh_data = self.include_mesh
            
            # === Detection 1: Check mesh topology changes ===
            mesh_manually_edited = False
            if source == "decode_render":
                original_verts = obj.get("geometry_vector_mesh_verts", -1)
                original_faces = obj.get("geometry_vector_mesh_faces", -1)
                current_verts = len(obj.data.vertices)
                current_faces = len(obj.data.polygons)
                
                # If mesh topology changed, it's been manually edited
                if original_verts != -1 and (current_verts != original_verts or current_faces != original_faces):
                    mesh_manually_edited = True
                    print(f"[Export] Mesh topology changed: verts {original_verts}->{current_verts}, faces {original_faces}->{current_faces}")
            
            # === Detection 2: Check if mesh data is shared (joined objects) ===
            # If mesh data has multiple users, it might be a result of join operation
            # OR if the object has been duplicated and the mesh is linked
            mesh_is_shared = obj.data.users > 1
            if mesh_is_shared and source == "decode_render":
                print(f"[Export] Mesh data has {obj.data.users} users, may be joined/linked")
            
            # === Detection 3: Check for vertex groups (often added in manual editing) ===
            has_vertex_groups = len(obj.vertex_groups) > 0
            if has_vertex_groups and source == "decode_render":
                print(f"[Export] Object has {len(obj.vertex_groups)} vertex groups (manual edit indicator)")
                mesh_manually_edited = True
            
            # === Detection 4: Check for shape keys (animation/morphing) ===
            has_shape_keys = obj.data.shape_keys is not None and len(obj.data.shape_keys.key_blocks) > 1
            if has_shape_keys and source == "decode_render":
                print(f"[Export] Object has shape keys (manual edit indicator)")
                mesh_manually_edited = True
            
            # === Determine export mode ===
            obj_to_export = None  # Will hold the object/mesh to export
            needs_modifier_apply = False
            
            if mesh_manually_edited:
                # Mesh has been manually edited - MUST include mesh data
                include_mesh_data = True
                needs_modifier_apply = True  # Apply modifiers to get complete geometry
                self.report({'INFO'}, "Mesh manually edited, using mesh+vector mode with modifiers applied")
                # Update source flag to reflect manual editing
                obj["geometry_vector_source"] = "manual_edit"
            elif source in ["decode_render", "preset"] and len(obj.modifiers) > 0 and not has_source_mesh and not mesh_is_shared:
                # Pure vector object (from decode_render or preset) with modifiers - use vector only
                # (base mesh + modifiers can be fully reconstructed from vector)
                include_mesh_data = False
                self.report({'INFO'}, f"Pure vector object detected ({source}), using vector-only mode")
            elif has_source_mesh:
                # Imported object with original mesh - preserve mesh+vector mode
                include_mesh_data = True
                self.report({'INFO'}, "Using mesh+vector mode (preserving imported mesh)")
            else:
                # Fallback: include mesh if in doubt
                include_mesh_data = True
                self.report({'INFO'}, "Using mesh+vector mode (safety fallback)")
            
            # === Apply modifiers if needed ===
            if include_mesh_data and needs_modifier_apply and len(obj.modifiers) > 0:
                # Create a temporary evaluated mesh with all modifiers applied
                print(f"[Export] Applying {len(obj.modifiers)} modifiers to get final geometry...")
                
                # Use depsgraph to get evaluated object with modifiers applied
                depsgraph = context.evaluated_depsgraph_get()
                obj_eval = obj.evaluated_get(depsgraph)
                
                # Create a new mesh from the evaluated object
                temp_mesh = bpy.data.meshes.new_from_object(obj_eval)
                temp_obj = bpy.data.objects.new("TempExport", temp_mesh)
                
                # Copy custom properties to temp object
                for key in obj.keys():
                    temp_obj[key] = obj[key]
                
                obj_to_export = temp_obj
                print(f"[Export] Modifiers applied: {len(temp_mesh.vertices)} vertices (was {len(obj.data.vertices)})")
            else:
                obj_to_export = obj
            
            # Export to file
            success = GeometryFileFormat.export_to_file(
                self.filepath,
                geom_vec,
                obj_to_export if include_mesh_data else None,
                metadata
            )
            
            # Clean up temporary object if created
            if obj_to_export != obj:
                bpy.data.meshes.remove(obj_to_export.data)
                # temp_obj will be removed automatically when mesh is removed
            
            if success:
                mode = "vector+mesh" if include_mesh_data else "vector-only"
                self.report({'INFO'}, f"Exported to {self.filepath} ({mode})")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Export failed")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Export error: {str(e)}")
            return {'CANCELLED'}
    
    def _identify_preset_from_object(self, obj, scene):
        """Try to identify which preset the object was created from"""
        try:
            from .geometry_encoder import GeometryEncoder, GeometryVector
            import numpy as np
            
            # Get object's vector
            if not all(f"geom_vector_{i}" in obj for i in range(32)):
                return None
            
            obj_vec = np.array([obj[f"geom_vector_{i}"] for i in range(32)])
            
            preset_names = [
                'SPIRAL_CORRIDOR', 'DNA_HELIX', 'SPRING', 'TWISTED_TOWER',
                'FIGHTER_JET', 'BOMBER', 'HELICOPTER', 'STAIRCASE', 'CHARACTER'
            ]
            
            min_dist = float('inf')
            closest_preset = None
            
            for preset in preset_names:
                preset_vec = GeometryEncoder.encode_preset(preset, scene)
                dist = np.linalg.norm(obj_vec - preset_vec.vector)
                if dist < min_dist and dist < 0.5:  # Threshold
                    min_dist = dist
                    closest_preset = preset
            
            return closest_preset
        except Exception as e:
            print(f"[Export] Failed to identify preset: {e}")
            return None
    
    def invoke(self, context, event):
        if context.active_object:
            self.filepath = context.active_object.name + ".gvec"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MYADDON_OT_import_gvec(bpy.types.Operator):
    """Import geometry from .gvec file"""
    bl_idname = "myaddon.import_gvec"
    bl_label = "Import .gvec File"
    bl_description = "Import geometry from .gvec format"
    
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to .gvec file",
        subtype='FILE_PATH'
    )
    
    filter_glob: bpy.props.StringProperty(
        default="*.gvec",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        try:
            # Import the file
            obj = GeometryFileFormat.restore_object_from_file(self.filepath, context)
            
            if obj:
                # Determine if object needs reconstruction from vector
                # Cases:
                # 1. Empty mesh (no vertices) - always reconstruct
                # 2. Pure vector sources (decode_render, preset) WITHOUT source_mesh - reconstruct
                #    (this is a pure-vector export that needs reconstruction)
                # 3. Objects WITH source_mesh marker - DON'T reconstruct
                #    (this is an imported object with original mesh, use as-is)
                
                source = obj.get("geometry_vector_source", "unknown")
                has_source_mesh = obj.get("geometry_vector_source_mesh") is not None
                
                needs_reconstruction = (
                    len(obj.data.vertices) == 0 or 
                    (source in ["decode_render", "preset"] and not has_source_mesh)
                )
                
                if needs_reconstruction:
                    print(f"[Import] Object needs reconstruction from vector (source: {source}, has_mesh: {has_source_mesh})...")
                    
                    # Get the vector data and load to editor
                    scene = context.scene
                    for i in range(32):
                        val = obj.get(f"geom_vector_{i}")
                        if val is not None:
                            scene.geom_vector_current[i] = float(val)
                    
                    # Restore preset name if this was a preset object
                    if source == "preset":
                        preset_name = obj.get("geometry_vector_preset_name", "NONE")
                        scene.vector_source_preset = preset_name
                        print(f"[Import] Restored preset source: {preset_name}")
                    else:
                        scene.vector_source_preset = "NONE"
                    
                    # Delete the imported object
                    old_name = obj.name
                    bpy.data.objects.remove(obj, do_unlink=True)
                    
                    # Reconstruct using Decode & Render operator
                    bpy.ops.myaddon.vector_decode_and_render()
                    
                    # Get the newly created object
                    obj = context.active_object
                    if obj:
                        obj.name = old_name
                        print(f"[Import] Successfully reconstructed {obj.name} from vector")
                    else:
                        self.report({'ERROR'}, "Failed to reconstruct geometry from vector")
                        return {'CANCELLED'}
                else:
                    print(f"[Import] Using imported mesh as-is (source: {source}, vertices: {len(obj.data.vertices)})")
                
                # Select the new object
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
                
                # Load vector into editor
                scene = context.scene
                for i in range(32):
                    val = obj.get(f"geom_vector_{i}")
                    if val is not None:
                        scene.geom_vector_current[i] = float(val)
                
                scene.show_vector_editor = True
                
                self.report({'INFO'}, f"Imported {obj.name} from .gvec file")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to restore object")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Import error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MYADDON_OT_export_gvec_batch(bpy.types.Operator):
    """Export multiple selected objects to .gvec_batch file"""
    bl_idname = "myaddon.export_gvec_batch"
    bl_label = "Export Batch (.gvec_batch)"
    bl_description = "Export selected objects to batch file"
    
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to save batch file",
        subtype='FILE_PATH'
    )
    
    filename_ext = ".gvec_batch"
    filter_glob: bpy.props.StringProperty(
        default="*.gvec_batch",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}
        
        try:
            success = GeometryBatchExporter.export_batch(self.filepath, selected_objects)
            
            if success:
                self.report({'INFO'}, f"Exported {len(selected_objects)} objects to {self.filepath}")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Batch export failed")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Export error: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        self.filepath = "geometry_batch.gvec_batch"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MYADDON_OT_import_gvec_batch(bpy.types.Operator):
    """Import multiple objects from .gvec_batch file"""
    bl_idname = "myaddon.import_gvec_batch"
    bl_label = "Import Batch (.gvec_batch)"
    bl_description = "Import multiple objects from batch file"
    
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to batch file",
        subtype='FILE_PATH'
    )
    
    filter_glob: bpy.props.StringProperty(
        default="*.gvec_batch",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        try:
            imported_objects = GeometryBatchExporter.import_batch(self.filepath, context)
            
            if imported_objects:
                # Select imported objects
                bpy.ops.object.select_all(action='DESELECT')
                for obj in imported_objects:
                    obj.select_set(True)
                
                context.view_layer.objects.active = imported_objects[0]
                
                self.report({'INFO'}, f"Imported {len(imported_objects)} objects")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to import batch")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Import error: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MYADDON_OT_morph_animation(bpy.types.Operator):
    bl_idname = "myaddon.morph_animation"
    bl_label = "Create Morph Animation"
    bl_description = "Create animation morphing between presets"
    
    start_preset: bpy.props.EnumProperty(
        name="Start",
        items=[
            ('SPIRAL_CORRIDOR', "Spiral Corridor", ""),
            ('TWISTED_TOWER', "Twisted Tower", ""),
            ('FIGHTER_JET', "Fighter Jet", ""),
            ('CHARACTER', "Character", ""),
        ],
        default='SPIRAL_CORRIDOR'
    )
    
    end_preset: bpy.props.EnumProperty(
        name="End",
        items=[
            ('DNA_HELIX', "DNA Helix", ""),
            ('BOMBER', "Bomber", ""),
            ('STAIRCASE', "Staircase", ""),
            ('CHARACTER', "Character", ""),
        ],
        default='DNA_HELIX'
    )
    
    num_frames: bpy.props.IntProperty(
        name="Frames",
        default=120,
        min=10,
        max=500,
        description="Number of frames for the morphing animation"
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Geometry Morph Animation", icon='ANIM_DATA')
        layout.separator()
        layout.prop(self, "start_preset")
        layout.prop(self, "end_preset")
        layout.prop(self, "num_frames")
    
    def execute(self, context):
        scene = context.scene
        
        # Encode presets
        vec_start = GeometryEncoder.encode_preset(self.start_preset, scene)
        vec_end = GeometryEncoder.encode_preset(self.end_preset, scene)
        
        # Generate interpolation path
        latent_space = get_latent_space()
        latent_space.add_geometry("start", vec_start)
        latent_space.add_geometry("end", vec_end)
        
        path = latent_space.interpolate_path("start", "end", self.num_frames)
        
        # Set up animation
        scene.frame_start = 1
        scene.frame_end = self.num_frames
        
        self.report({'INFO'}, 
                   f"Created morph animation: {self.start_preset} → {self.end_preset} "
                   f"({self.num_frames} frames)")
        
        # Note: Actual keyframe creation would require more complex implementation
        # This demonstrates the concept
        
        return {'FINISHED'}


classes = (
    MYADDON_OT_button,
    MYADDON_OT_select_item,
    MYADDON_OT_init_items,
    MYADDON_OT_toggle_collapsible,
    OBJECT_OT_choose_person_files,
    OBJECT_OT_clear_person_files,
    OBJECT_OT_open_resource,
    OBJECT_OT_remove_selected_file,
    MYADDON_OT_add_panel,
    MYADDON_OT_remove_panel,
    MYADDON_OT_open_icon_popup,
    MYADDON_OT_icon_callback,
    MYADDON_OT_fetch_api,
    MYADDON_OT_show_api_response,
    MYADDON_OT_create_shape,
    MYADDON_OT_split_shape,
    MYADDON_OT_focus_part,
    MYADDON_OT_edit_part_material,
    MYADDON_OT_apply_preset,
    MYADDON_OT_update_shape,
    MYADDON_OT_encode_geometry,
    MYADDON_OT_interpolate_geometry,
    MYADDON_OT_blend_geometry,
    MYADDON_OT_find_similar_geometry,
    MYADDON_OT_vector_to_clipboard,
    MYADDON_OT_vector_from_clipboard,
    MYADDON_OT_vector_arithmetic,
    MYADDON_OT_vector_reset,
    MYADDON_OT_vector_normalize,
    MYADDON_OT_apply_source_modifiers,
    MYADDON_OT_vector_decode_and_render,
    MYADDON_OT_vector_load_from_preset,
    MYADDON_OT_vector_load_from_object,
    MYADDON_OT_vector_load_from_file,
    MYADDON_OT_morph_animation,
    # New .gvec file format operators
    MYADDON_OT_export_gvec,
    MYADDON_OT_import_gvec,
    MYADDON_OT_export_gvec_batch,
    MYADDON_OT_import_gvec_batch,
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
