import bpy

class MYADDON_UL_panels_list(bpy.types.UIList):
    """List that shows each panel with a toggle, name, delete button and drag handle."""
    use_reorder = True
    bl_options = {'GRAB_CURSOR'}

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        col = layout.column(align=True)
        row = col.row(align=True)

        row.prop(item, "expanded",
                 icon_only=True,
                 icon='TRIA_DOWN' if item.expanded else 'TRIA_RIGHT',
                 emboss=False)
        row.prop(item, "name", text="", emboss=False)
        delete_op = row.operator("myaddon.remove_panel", icon='X', text="")
        delete_op.index = index

        if item.expanded:
            box = col.box()
            box.label(text="This is the content of the panel.")

class MYADDON_UL_shape_parts_list(bpy.types.UIList):
    """UIList for displaying shape parts"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            # Part name - clickable to focus
            op = row.operator("myaddon.focus_part", text=item.name, icon='MESH_DATA', emboss=False)
            op.part_name = item.object_ref
            # Material editor button
            op = row.operator("myaddon.edit_part_material", text="", icon='MATERIAL', emboss=False)
            op.part_name = item.object_ref
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='MESH_DATA')

classes = (MYADDON_UL_panels_list, MYADDON_UL_shape_parts_list)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
