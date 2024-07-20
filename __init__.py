# 1. Setup and Imports
import bpy
from bpy.types import Menu, Operator
import os

bl_info = {
    "name": "Q",
    "author": "Divina, ChatGPT",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "description": "An improved favorites menu",
    "category": "Interface",
}

################################################
# Icon stuff from HardOPS
################################################
icons_collection = None
icons_directory = os.path.join(os.path.dirname(__file__), "icons")


def get_icon_id(identifier):
    # The initialize_icons_collection function needs to be called first.
    return get_icon(identifier).icon_id


def get_icon(identifier):
    if (not identifier is None) and (identifier in icons_collection):
        return icons_collection[identifier]
    return icons_collection.load(identifier, os.path.join(icons_directory, identifier + ".png"), "IMAGE")


def initialize_icons_collection():
    global icons_collection
    icons_collection = bpy.utils.previews.new()


def unload_icons():
    bpy.utils.previews.remove(icons_collection)


class IconsMock:
    def get(self, identifier):
        return get_icon(identifier)


icons = IconsMock()
######### End Icon Stuff from HardOPS ##########



################################################
# Pie Menu
################################################
class VIEW3D_MT_pie_menu(Menu):
    bl_label = "Pie Menu"

    @staticmethod
    def draw_camera_box(scene, view, layout):
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
        # import math
        from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as view3d_tools
        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper

        gr = layout.grid_flow(columns=columns, even_columns=True, even_rows=True, align=True)

        space_type = context.space_data.type
        tool_active_id = getattr(
            ToolSelectPanelHelper._tool_active_from_context(context, space_type),
            "idname", None,
        )
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
                    # not ideal, write this every time :S
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
                gr.operator_menu_hold(
                    "wm.tool_set_by_id",
                    text="",
                    depress=is_active,
                    menu="WM_MT_toolsystem_submenu",
                    icon_value=icon_value,
                ).name = item.idname
            else:
                gr.operator(
                    "wm.tool_set_by_id",
                    text="",
                    depress=is_active,
                    icon_value=icon_value,
                ).name = item.idname
            gr.scale_x = 1.3
            gr.scale_y = 1.3

    @staticmethod
    def draw_boxcutter_box(layout):
        column = layout.column(align=True)
        column.scale_x = 1

        row = column.split(factor=0.25, align=True)
        row.scale_y = 1.25
        row.label(text='Box')
        op = row.operator('machin3.set_boxcutter_preset', text='Add')
        op.shape_type = 'BOX'
        op.mode = 'MAKE'
        op.set_origin = 'BBOX'
        op = row.operator('machin3.set_boxcutter_preset', text='Cut')
        op.shape_type = 'BOX'
        op.mode = 'CUT'

        row = column.split(factor=0.25, align=True)
        row.scale_y = 1.25
        row.label(text='Circle')
        op = row.operator('machin3.set_boxcutter_preset', text='Add')
        op.shape_type = 'CIRCLE'
        op.mode = 'MAKE'
        op.set_origin = 'BBOX'
        op = row.operator('machin3.set_boxcutter_preset', text='Cut')
        op.shape_type = 'CIRCLE'
        op.mode = 'CUT'

        row = column.split(factor=0.25, align=True)
        row.scale_y = 1.25
        row.label(text='NGon')
        op = row.operator('machin3.set_boxcutter_preset', text='Add')
        op.shape_type = 'NGON'
        op.mode = 'MAKE'
        op.set_origin = 'BBOX'
        op = row.operator('machin3.set_boxcutter_preset', text='Cut')
        op.shape_type = 'NGON'
        op.mode = 'CUT'

    @staticmethod
    def draw_misc_object_box(layout):
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

        # TODO Add Metashape
        # TODO Add Unparent

    ################################################
    # Pie menu of Machin3 Tools' Pie Menus
    ################################################
    @staticmethod
    def draw_pie_box(layout):

        # Check to see if any Machin3 Tools Pie Menus are enabled
        if hasattr(bpy.types, "MACHIN3_MT_shading_pie") or hasattr(bpy.types, "MACHIN3_MT_viewport_pie") or hasattr(bpy.types, "MACHIN3_MT_align_pie") or hasattr(bpy.types, "MACHIN3_MT_cursor_pie") or hasattr(bpy.types, "MACHIN3_MT_transform_pie") or hasattr(bpy.types, "MACHIN3_MT_snapping_pie") or hasattr(bpy.types, "MACHIN3_MT_collections_pie") or hasattr(bpy.types, "MACHIN3_MT_workspace_pie"):
            column = layout.column()
            column.scale_x = 1
            
            # Artificially move the items down to be centered-ish
            column.separator()
            column.separator()
            column.separator()
            column.separator()
            column.separator()
            column.separator()
            column.separator()
            column.separator()

            column = column.box().column(align=True)
            column.scale_x = 1
            column.label(text='Machin3 Pies')

            if hasattr(bpy.types, "MACHIN3_MT_shading_pie"):
                column.operator('wm.call_menu_pie', text='Shading').name = "MACHIN3_MT_shading_pie"
            if hasattr(bpy.types, "MACHIN3_MT_viewport_pie"):
                column.operator('wm.call_menu_pie', text='Views').name = "MACHIN3_MT_viewport_pie"
            if hasattr(bpy.types, "MACHIN3_MT_align_pie"):
                column.operator('wm.call_menu_pie', text='Align').name = "MACHIN3_MT_align_pie"
            if hasattr(bpy.types, "MACHIN3_MT_cursor_pie"):
                column.operator('wm.call_menu_pie', text='Cursor').name = "MACHIN3_MT_cursor_pie"
            if hasattr(bpy.types, "MACHIN3_MT_transform_pie"):
                column.operator('wm.call_menu_pie', text='Transform').name = "MACHIN3_MT_transform_pie"
            if hasattr(bpy.types, "MACHIN3_MT_snapping_pie"):
                column.operator('wm.call_menu_pie', text='Snapping').name = "MACHIN3_MT_snapping_pie"
            if hasattr(bpy.types, "MACHIN3_MT_collections_pie"):
                column.operator('wm.call_menu_pie', text='Collections').name = "MACHIN3_MT_collections_pie"
            if hasattr(bpy.types, "MACHIN3_MT_workspace_pie"):
                column.operator('wm.call_menu_pie', text='Workspace').name = "MACHIN3_MT_workspace_pie"


    ################################################
    #   Creates a panel listing the main menus/pies
    # for several popular addons
    ################################################
    @staticmethod
    def draw_addon_menu(layout):
        column = layout.column()
        column.scale_x = 1
        
        # Artificially move the items down to be centered-ish
        column.separator()
        column.separator()
        column.separator()
        column.separator()
        column.separator()
        column.separator()
        column.separator()
        column.separator()

        column = column.box().column(align=True)
        column.label(text='Addons')
        if hasattr(bpy.types, "HOPS_MT_MainMenu"):
            column.operator("wm.call_menu", text="Hops (M)").name = "HOPS_MT_MainMenu"
        if hasattr(bpy.types, "MACHIN3_MT_mesh_machine"):
            column.operator("wm.call_menu", text="MESHmachine").name = "MACHIN3_MT_mesh_machine"  # Mesh Machine Row
        if hasattr(bpy.types, "UI_MT_random_flow"):
            column.operator('wm.call_menu', text='Random Flow').name = "UI_MT_random_flow"  # Random Flow Row
        if hasattr(bpy.types, "FLUENT_MT_PieMenu"):
            column.operator('wm.call_menu_pie', text='Fluent').name = "FLUENT_MT_PieMenu"  # Fluent Row
        if hasattr(bpy.types, "UI_MT_cuber"):
            column.operator('wm.call_menu_pie', text='Cuber').name = "UI_MT_cuber"  # Cuber Row
        if hasattr(bpy.types, "VIEW3D_MT_cablerator"):
            column.operator("wm.call_menu", text="Cablerator").name = "VIEW3D_MT_cablerator"  # Cablerator Row
        if hasattr(bpy.types, "UI_MT_ice_tools"):
            column.operator('wm.call_menu_pie', text='Ice Tools').name = "UI_MT_ice_tools"  # ICE Tools Row

    ################################################
    ################################################
    @staticmethod
    def draw_misc_edit_box(layout):
        column = layout.column(align=True)

        # Punch it
        row = column.row(align=True)
        row.scale_y = 1.25
        row.operator("machin3.cursor_spin", text='Cursor Spin')
        row.operator("machin3.punch_it", text='Punch It')
        column.operator("machin3.transform_edge_constrained", text="Edge Constrained Transform")

        # Loop Tools
        column.operator("mesh.looptools_bridge", text="Bridge").loft = False
        column.operator("mesh.looptools_circle", text="Circle")
        column.operator("mesh.looptools_curve", text="Curve")
        column.operator("mesh.looptools_flatten", text="Flatten")
        column.operator("mesh.looptools_gstretch", text="Gstretch")
        column.operator("mesh.looptools_bridge", text="Loft").loft = True
        column.operator("mesh.looptools_relax", text="Relax")
        column.operator("mesh.looptools_space", text="Space")

    ################################################
    # Vertical assortment of popular HOps operators
    ################################################
    @staticmethod
    def draw_hops_operators(layout):

        # odd structures with IF statements are to cover the cases where HOps isn't installed
        row = layout.box().row(align=False)
        if hasattr(bpy.types, "HOPS_MT_MainMenu"):
            # Left Column
            col = row.column(align=True)
            col.scale_x = 1.25
            col.scale_y = 1.25
            col.operator("hops.mod_weighted_normal", text="", icon_value=get_icon_id("weightednormal"))
            col.operator('hops.set_autosmoouth', text='', icon_value=get_icon_id("30")).angle = 0.5236
            col.operator('hops.set_autosmoouth', text='', icon_value=get_icon_id("45")).angle = 0.7854
            col.operator('hops.set_autosmoouth', text='', icon_value=get_icon_id("60")).angle = 1.0472
            col.separator()
            col.operator("hops.adjust_bevel", text="", icon_value=get_icon_id("bevel"))
            col.operator("hops.mod_weld", text="", icon_value=get_icon_id("weld"))
            col.operator("hops.mod_shrinkwrap", text="", icon_value=get_icon_id("shrinkwrap"))
            col.operator("hops.mod_displace", text="", icon_value=get_icon_id("displace"))
            col.operator("hops.mod_decimate", text="", icon_value=get_icon_id("decimate"))
            col.operator("hops.mod_subdivision", text="", icon_value=get_icon_id("subsurf"))
            col.operator("hops.bool_dice_v2", text="", icon_value=get_icon_id("Dice"))

        # Right column
        col = row.column(align=True)
        col.scale_x = 1.25
        col.scale_y = 1.25
        col.menu("SCREEN_MT_user_menu", text="", icon_value=get_icon_id("QuickFav"))

        if hasattr(bpy.types, "HOPS_MT_MainMenu"):
            col.separator()
            col.operator("hops.bool_difference", text="", icon_value=get_icon_id("red"))
            col.operator("hops.bool_union", text="", icon_value=get_icon_id("green"))
            col.operator("hops.bool_intersect", text="", icon_value=get_icon_id("orange"))
            col.operator("hops.bool_inset", text="", icon_value=get_icon_id("purple"))
            col.operator("hops.bool_knife", text="", icon_value=get_icon_id("blue"))
            col.operator("hops.slash", text="", icon_value=get_icon_id("yellow"))
            col.separator()
            col.operator("hops.st3_array", text="", icon_value=get_icon_id("Array"))
            col.operator("hops.radial_array_nodes", text="", icon_value=get_icon_id("ArrayCircle"))
            col.operator("hops.mirror_gizmo", text="", icon_value=get_icon_id("mirror"))
            col.operator("hops.adjust_tthick", text="", icon_value=get_icon_id("solidify"))
        
        


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        view = context.space_data

        pie = layout.menu_pie()

        # 'OBJECT' 'EDIT_MESH' 'EDIT_ARMATURE' 'POSE' 'EDIT_CURVE' 'EDIT_TEXT' 'EDIT_SURFACE' 'EDIT_METABALL' 'EDIT_LATTICE' 'EDIT_GPENCIL' 'PAINT_GPENCIL' 'SCULPT_GPENCIL' 'WEIGHT_GPENCIL'

        if context.mode in ['OBJECT']:

            left_pie = pie.split().row() # Split into column of big boxes and hops buttons
            left_pie_column = left_pie.split().column()  # Object - Left

            #left_pie_column.separator()  # Camera Box
            #left_pie_column.separator()  # Boxcutter
            #left_pie_column.separator()  # Misc

            self.draw_camera_box(scene, view, left_pie_column.box())  # Camera Menu
            left_pie_column.prop(view.overlay, "show_face_orientation")
            self.draw_boxcutter_box(left_pie_column.box())  # Boxcutter Menu
            self.draw_misc_object_box(left_pie_column.box())  # Misc Menu

            self.draw_hops_operators(left_pie.split())

            right_pie_row = pie.split().row()  # Object - Right

            #right_pie_row.separator()  # Tool Box
            #right_pie_row.separator()  # Pie Box
            #right_pie_row.separator()  # Addon Box

            self.draw_tool_box(context, right_pie_row.box())  # Draw the Toolbox
            self.draw_addon_menu(right_pie_row)
            self.draw_pie_box(right_pie_row)  # Draw the list of Machin3 Pies
            

            pie.separator()  # Bottom Most Panel
            #pie.separator()  # Top Most Panel

        elif context.mode in ['EDIT_MESH']:

            left_pie_column = pie.split().column()  # Edit - Left

            self.draw_misc_edit_box(left_pie_column.box())  # Misc Menu

            right_pie_row = pie.split().row()  # Edit - Right

            right_pie_row.separator()  # Tool Box
            right_pie_row.separator()  # Pie Box
            right_pie_row.separator()  # Addon Box

            self.draw_tool_box(context, right_pie_row.box(), columns=3)  # Draw the Toolbox
            self.draw_addon_menu(right_pie_row)
            self.draw_pie_box(right_pie_row)  # Draw the list of Machin3 Pies
            

            # Bottom Most Panel
            pie.separator()
            # Top Most Panel
            pie.separator()


# Define the Operator for Key Press
class WM_OT_show_pie_menu(Operator):
    bl_idname = "wm.show_pie_menu"
    bl_label = "Show Pie Menu"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_pie_menu")
        return {'FINISHED'}

# 4. Keymap Configuration
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

# 5. Registration and Unregistration
def register():
    bpy.utils.register_class(VIEW3D_MT_pie_menu)
    bpy.utils.register_class(WM_OT_show_pie_menu)
    register_keymap()
    initialize_icons_collection()

def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_pie_menu)
    bpy.utils.unregister_class(WM_OT_show_pie_menu)
    unregister_keymap()

# 6. Blender Add-on Boilerplate
if __name__ == "__main__":
    register()
    

