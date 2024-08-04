import bpy
from bpy.types import Menu, Operator
import os

bl_info = {
    "name": "Q",
    "author": "Divina, DeepSeek Coder v2 236b",
    "version": (1, 0, 3),
    "blender": (4, 2, 0),
    "description": "An improved favorites menu",
    "category": "Interface",
}

# Icon management functions from HardOPS
icons_collection = None
icons_directory = os.path.join(os.path.dirname(__file__), "icons")

def get_icon_id(identifier):
    """Get the icon ID for a given identifier."""
    return get_icon(identifier).icon_id

def get_icon(identifier):
    """Load or retrieve an icon from the collection."""
    if identifier and identifier in icons_collection:
        return icons_collection[identifier]
    return icons_collection.load(identifier, os.path.join(icons_directory, f"{identifier}.png"), "IMAGE")

def initialize_icons_collection():
    """Initialize the icon collection."""
    global icons_collection
    icons_collection = bpy.utils.previews.new()

def unload_icons():
    """Unload all icons from the collection."""
    bpy.utils.previews.remove(icons_collection)

class IconsMock:
    def get(self, identifier):
        return get_icon(identifier)

icons = IconsMock()
######### End Icon Stuff from HardOPS ##########

################################################
# Pie Menu Class and Methods
################################################
class VIEW3D_MT_pie_menu(Menu):
    bl_label = "Pie Menu"

    @staticmethod
    def draw_camera_box(scene, view, layout):
        """Draw the camera settings box."""
        column = layout.column(align=True)
        column.scale_x = 1
        row = column.row()
        row.scale_y = 1.5
        row.operator("machin3.smart_view_cam", text="Smart View Cam", icon='HIDE_OFF')
        
        if view.region_3d.view_perspective == 'CAMERA':
            cams = [obj for obj in scene.objects if obj.type == "CAMERA"]
            if len(cams) > 1:
                row = column.row(align=True)
                row.operator("machin3.next_cam", text="(Q) Previous Cam").previous = True
                row.operator("machin3.next_cam", text="(W) Next Cam").previous = False
        
        row = column.split(align=True)
        row.operator("machin3.make_cam_active")
        row.prop(scene, "camera", text="")
        
        row = column.split(align=True)
        row.operator("view3d.camera_to_view", text="Cam to view", icon='VIEW_CAMERA')
        text, icon = ("Unlock from View", "UNLOCKED") if view.lock_camera else ("Lock to View", "LOCKED")
        row.operator("wm.context_toggle", text=text, icon=icon).data_path = "space_data.lock_camera"

    @staticmethod
    def draw_tool_box(context, layout, columns=1):
        """Draw the tool box."""
        from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as view3d_tools
        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        
        gr = layout.grid_flow(columns=columns, even_columns=True, even_rows=True, align=True)
        space_type = context.space_data.type
        tool_active_id = getattr(ToolSelectPanelHelper._tool_active_from_context(context, space_type), "idname", None)
        
        for item in view3d_tools.tools_from_context(context):
            if item is None:
                continue
            if type(item) is tuple:
                is_active = False
                i = 0
                for i, sub_item in enumerate(item):
                    if sub_item is None:
                        continue
                    is_active = (sub_item.idname == tool_active_id)
                    if is_active:
                        index = i
                        break
                del i, sub_item
                
                if is_active:
                    view3d_tools._tool_group_active[item[0].idname] = index
                else:
                    index = view3d_tools._tool_group_active_get_from_item(item)
                
                item = item[index]
                use_menu = True
            else:
                index = -1
                use_menu = False
            
            is_active = (item.idname == tool_active_id)
            icon_value = ToolSelectPanelHelper._icon_value_from_icon_handle(item.icon)
            
            if use_menu:
                gr.operator_menu_hold("wm.tool_set_by_id", text="", depress=is_active, menu="WM_MT_toolsystem_submenu", icon_value=icon_value).name = item.idname
            else:
                gr.operator("wm.tool_set_by_id", text="", depress=is_active, icon_value=icon_value).name = item.idname
            gr.scale_x = 1.3
            gr.scale_y = 1.3

    @staticmethod
    def draw_boxcutter_box(layout):
        """Draw the Boxcutter settings box."""
        column = layout.column(align=True)
        column.scale_x = 1
        
        shapes = ['BOX', 'CIRCLE', 'NGON']
        for shape in shapes:
            row = column.split(factor=0.25, align=True)
            row.scale_y = 1.25
            row.label(text=shape.capitalize())
            op = row.operator('machin3.set_boxcutter_preset', text='Add')
            op.shape_type = shape
            op.mode = 'MAKE'
            op.set_origin = 'BBOX'
            op = row.operator('machin3.set_boxcutter_preset', text='Cut')
            op.shape_type = shape
            op.mode = 'CUT'

    @staticmethod
    def draw_misc_object_box(layout):
        """Draw miscellaneous object settings box."""
        column = layout.column(align=True)
        column.scale_x = 1
        
        row = column.row(align=True)
        row.scale_y = 1.25
        row.operator('hops.apply_modifiers', text="Hops Smart Apply", icon='MODIFIER')
        
        row = column.row(align=True)
        row.scale_y = 1.25
        row.operator('machin3.boolean_apply', text="MM Stash Apply", icon='MODIFIER')
        
        # Apply rotation and scale
        row = column.row(align=True)
        row.scale_y = 1.25
        props = row.operator("object.transform_apply", text='Apply Scale')
        props.location = False
        props.rotation = False
        props.scale = True
        props = row.operator("object.transform_apply", text='& Rotation')
        props.location = False
        props.rotation = True
        props.scale = True
        props = row.operator("object.transform_apply", text='*')
        props.location = True
        props.rotation = True
        props.scale = True
        
    @staticmethod
    def draw_pie_box(layout):
        """Draw the Machin3 Tools pie menu box."""
        if any(hasattr(bpy.types, f"MACHIN3_MT_{pie}_pie") for pie in ['shading', 'viewport', 'align', 'cursor', 'transform', 'snapping', 'collections', 'workspace']):
            column = layout.column()
            column.scale_x = 1
            
            # Artificially move the items down to be centered-ish
            for _ in range(8):
                column.separator()
            
            column = column.box().column(align=True)
            column.label(text='Machin3 Pies')
            
            pies = ['shading', 'viewport', 'align', 'cursor', 'transform', 'snapping', 'collections', 'workspace']
            for pie in pies:
                if hasattr(bpy.types, f"MACHIN3_MT_{pie}_pie"):
                    column.operator('wm.call_menu_pie', text=pie.capitalize()).name = f"MACHIN3_MT_{pie}_pie"

    @staticmethod
    def draw_addon_menu(layout):
        """Draw the addon menu box."""
        column = layout.column()
        column.scale_x = 1
        
        # Artificially move the items down to be centered-ish
        for _ in range(8):
            column.separator()
        
        column = column.box().column(align=True)
        column.label(text='Addons')
        
        addons = [("HOPS_MT_MainMenu", "Hops (M)", False), 
                  ("MACHIN3_MT_mesh_machine", "MESHmachine", False), 
                  ("UI_MT_random_flow", "Random Flow", False), 
                  ("FLUENT_MT_PieMenu", "Fluent", True), 
                  ("UI_MT_cuber", "Cuber", True), 
                  ("VIEW3D_MT_cablerator", "Cablerator", False), 
                  ("UI_MT_ice_tools", "Ice Tools", True)]
        
        for addon, text, is_pie in addons:
            if hasattr(bpy.types, addon):
                op = column.operator('wm.call_menu' + ('_pie' if is_pie else ''), text=text)
                op.name = addon

    @staticmethod
    def draw_misc_edit_box(layout):
        """Draw miscellaneous edit settings box."""
        column = layout.column(align=True)
        
        # Punch it
        row = column.row(align=True)
        row.scale_y = 1.25
        row.operator("machin3.cursor_spin", text='Cursor Spin')
        row.operator("machin3.punch_it", text='Punch It')
        column.operator("machin3.transform_edge_constrained", text="Edge Constrained Transform")
        
        # Loop Tools
        loop_tools = [("bridge", False), ("circle", None), ("curve", None), ("flatten", None), 
                      ("gstretch", None), ("bridge", True), ("relax", None), ("space", None)]
        for tool, loft in loop_tools:
            op = column.operator(f"mesh.looptools_{tool}", text=tool.capitalize())
            if loft is not None:
                op.loft = loft

    @staticmethod
    def draw_hops_operators(layout):
        """Draw the HOps operators box."""
        row = layout.box().row(align=False)
        if hasattr(bpy.types, "HOPS_MT_MainMenu"):
            col = row.column(align=True)
            col.scale_x = 1.25
            col.scale_y = 1.25
            
            # Left Column
            ops = [("hops.mod_weighted_normal", "weightednormal"), ("hops.set_autosmoouth", "30", 0.5236), 
                   ("hops.set_autosmoouth", "45", 0.7854), ("hops.set_autosmoouth", "60", 1.0472), 
                   ("hops.adjust_bevel", "bevel"), ("hops.mod_weld", "weld"), ("hops.mod_shrinkwrap", "shrinkwrap"), 
                   ("hops.mod_displace", "displace"), ("hops.mod_decimate", "decimate"), 
                   ("hops.mod_subdivision", "subsurf"), ("hops.bool_dice_v2", "Dice")]
            for op, icon, *props in ops:
                if props:
                    col.operator(op, text="", icon_value=get_icon_id(icon)).angle = props[0]
                else:
                    col.operator(op, text="", icon_value=get_icon_id(icon))
            
            # Right Column
            col = row.column(align=True)
            col.scale_x = 1.25
            col.scale_y = 1.25
            col.menu("SCREEN_MT_user_menu", text="", icon_value=get_icon_id("QuickFav"))
            
            if hasattr(bpy.types, "HOPS_MT_MainMenu"):
                col.separator()
                bool_ops = [("hops.bool_difference", "red"), ("hops.bool_union", "green"), 
                            ("hops.bool_intersect", "orange"), ("hops.bool_inset", "purple"), 
                            ("hops.bool_knife", "blue"), ("hops.slash", "yellow")]
                for op, icon in bool_ops:
                    col.operator(op, text="", icon_value=get_icon_id(icon))
                
                mod_ops = [("hops.st3_array", "Array"), ("hops.radial_array_nodes", "ArrayCircle"), 
                           ("hops.mirror_gizmo", "mirror"), ("hops.adjust_tthick", "solidify")]
                for op, icon in mod_ops:
                    col.operator(op, text="", icon_value=get_icon_id(icon))

    def draw(self, context):
        """Main draw method for the pie menu."""
        layout = self.layout
        scene = context.scene
        view = context.space_data
        
        pie = layout.menu_pie()
        
        if context.mode in ['OBJECT']:
            left_pie = pie.split().row() # Split into column of big boxes and hops buttons
            left_pie_column = left_pie.split().column()  # Object - Left
            
            self.draw_camera_box(scene, view, left_pie_column.box())  # Camera Menu
            left_pie_column.prop(view.overlay, "show_face_orientation")
            self.draw_boxcutter_box(left_pie_column.box())  # Boxcutter Menu
            self.draw_misc_object_box(left_pie_column.box())  # Misc Menu
            
            self.draw_hops_operators(left_pie.split())
            
            right_pie_row = pie.split().row()  # Object - Right
            
            self.draw_tool_box(context, right_pie_row.box())  # Draw the Toolbox
            self.draw_addon_menu(right_pie_row)
            self.draw_pie_box(right_pie_row)  # Draw the list of Machin3 Pies
            
            pie.separator()  # Bottom Most Panel
        
        elif context.mode in ['EDIT_MESH']:
            left_pie_column = pie.split().column()  # Edit - Left
            
            self.draw_misc_edit_box(left_pie_column.box())  # Misc Menu
            
            right_pie_row = pie.split().row()  # Edit - Right
            
            self.draw_tool_box(context, right_pie_row.box(), columns=3)  # Draw the Toolbox
            self.draw_addon_menu(right_pie_row)
            self.draw_pie_box(right_pie_row)  # Draw the list of Machin3 Pies
            
            pie.separator()  # Bottom Most Panel

# Define the Operator for Key Press
class WM_OT_show_pie_menu(Operator):
    bl_idname = "wm.show_pie_menu"
    bl_label = "Show Pie Menu"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_pie_menu")
        return {'FINISHED'}

# New Operator to append Geometry Nodes modifier from another blend file
class WM_OT_append_geometry_nodes(Operator):
    bl_idname = "wm.append_geometry_nodes"
    bl_label = "Append Geometry Nodes Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    node_group_name: bpy.props.StringProperty()

    def execute(self, context):
        with bpy.data.libraries.load(self.filepath) as (data_from, data_to):
            if self.node_group_name in data_from.node_groups:
                data_to.node_groups = [self.node_group_name]
        
        for node_group in data_to.node_groups:
            for obj in context.selected_objects:
                modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
                modifier.node_group = node_group
        
        return {'FINISHED'}

# Keymap Configuration
addon_keymaps = []

def register_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')
        kmi = km.keymap_items.new("wm.show_pie_menu", 'Q', 'PRESS')  # Change 'Q' to desired key
        addon_keymaps.append((km, kmi))

def unregister_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

# Registration and Unregistration
def register():
    bpy.utils.register_class(VIEW3D_MT_pie_menu)
    bpy.utils.register_class(WM_OT_show_pie_menu)
    bpy.utils.register_class(WM_OT_append_geometry_nodes)
    register_keymap()
    initialize_icons_collection()

def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_pie_menu)
    bpy.utils.unregister_class(WM_OT_show_pie_menu)
    bpy.utils.unregister_class(WM_OT_append_geometry_nodes)
    unregister_keymap()
    unload_icons()

if __name__ == "__main__":
    register()
