import os

import bpy
from bpy.types import Menu, Operator

bl_info = {
    "name": "Q",
    "author": "Divina, Zed: Gemini 2.5 Flash Thinking",
    "version": (2, 0, 0),
    "blender": (4, 5, 0),
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
    return icons_collection.load(
        identifier, os.path.join(icons_directory, identifier + ".png"), "IMAGE"
    )


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


def separate(layout, count=1):
    """
    Adds separators to a blender ui layout object

    Args:
        layout (bpy.types.UILayout): The UI layout to add the separator to
        count (int): The number to add
    """
    for _ in range(count):
        layout.separator()


def operator_if_exists(
    layout, operator_id, text="", icon="NONE", icon_value=0, **kwargs
):
    """
    Adds an operator to the UI layout only if the operator's bl_id exists in bpy.ops.

    Args:
        layout (bpy.types.UILayout): The UI layout to add the operator to.
        operator_id (str): The bl_id of the operator (e.g., "object.transform_apply").
        text (str): The text to display for the operator button.
        icon (str): The icon to display for the operator button (Blender built-in icon).
        icon_value (int): The custom icon value to display.
        **kwargs: Additional keyword arguments to pass to the operator.

    Returns:
        bpy.types.OperatorProperties: The operator properties if added, otherwise None.
    """
    if hasattr(bpy.ops, operator_id.split(".")[0]):
        op_module = getattr(bpy.ops, operator_id.split(".")[0])
        if hasattr(op_module, operator_id.split(".")[1]):
            try:
                props = layout.operator(
                    operator_id, text=text, icon=icon, icon_value=icon_value
                )
                for key, value in kwargs.items():
                    setattr(props, key, value)
                return props
            except Exception as e:
                print(f"An error occurred: {e}")
                return layout
    return None


class VIEW3D_MT_div_qpie_menu(Menu):
    """
    Main pie menu for quick access to various tools and addons.
    """

    bl_label = "Q Menu"
    bl_idname = "VIEW3D_MT_div_qpie_menu"

    def draw_camera_box(self, scene, view, layout):
        """
        Draws the camera-related operators.

        Args:
            scene (bpy.types.Scene): The current scene.
            view (bpy.types.SpaceView3D): The current 3D view space data.
            layout (bpy.types.UILayout): The layout to draw the box in.
        """
        column = layout.column(align=True)
        column.scale_x = 1

        row = column.row()
        row.scale_y = 1.5
        operator_if_exists(
            row, "machin3.smart_view_cam", text="Smart View Cam", icon="HIDE_OFF"
        )

        if view.region_3d.view_perspective == "CAMERA":
            cams = [obj for obj in scene.objects if obj.type == "CAMERA"]
            if len(cams) > 1:
                row = column.row(align=True)
                operator_if_exists(
                    row, "machin3.next_cam", text="(Q) Previous Cam", previous=True
                )
                operator_if_exists(
                    row, "machin3.next_cam", text="(W) Next Cam", previous=False
                )

        row = column.split(align=True)
        operator_if_exists(row, "machin3.make_cam_active")
        row.prop(scene, "camera", text="")

        row = column.split(align=True)
        operator_if_exists(
            row, "view3d.camera_to_view", text="Cam to view", icon="VIEW_CAMERA"
        )

        text, icon = (
            ("Unlock from View", "UNLOCKED")
            if view.lock_camera
            else ("Lock to View", "LOCKED")
        )
        op = operator_if_exists(row, "wm.context_toggle", text=text, icon=icon)
        if op:
            op.data_path = "space_data.lock_camera"

    def draw_tool_box(self, context, layout, columns=1):
        """
        Draws the active tool selection box.

        Args:
            context (bpy.types.Context): The current Blender context.
            layout (bpy.types.UILayout): The layout to draw the box in.
            columns (int): Number of columns for the grid flow.
        """
        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        from bl_ui.space_toolsystem_toolbar import (
            VIEW3D_PT_tools_active as view3d_tools,
        )

        gr = layout.grid_flow(
            columns=columns, even_columns=True, even_rows=True, align=True
        )

        space_type = context.space_data.type
        tool_active_id = getattr(
            ToolSelectPanelHelper._tool_active_from_context(context, space_type),
            "idname",
            None,
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
                    is_active = sub_item.idname == tool_active_id
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

            is_active = item.idname == tool_active_id
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

    def draw_boxcutter_box(self, layout):
        """
        Draws the Boxcutter-related operators.

        Args:
            layout (bpy.types.UILayout): The layout to draw the box in.
        """
        column = layout.column(align=True)
        column.scale_x = 1

        shapes = {"Box": "BOX", "Circle": "CIRCLE", "NGon": "NGON"}

        for text, shape_type in shapes.items():
            row = column.split(factor=0.25, align=True)
            row.scale_y = 1.25
            row.label(text=text)
            operator_if_exists(
                row,
                "machin3.set_boxcutter_preset",
                text="Add",
                shape_type=shape_type,
                mode="MAKE",
                set_origin="BBOX",
            )
            operator_if_exists(
                row,
                "machin3.set_boxcutter_preset",
                text="Cut",
                shape_type=shape_type,
                mode="CUT",
            )

    def draw_misc_object_box(self, layout):
        """
        Draws miscellaneous object-related operators.

        Args:
            layout (bpy.types.UILayout): The layout to draw the box in.
        """
        column = layout.column(align=True)
        column.scale_x = 1

        row = column.row(align=True)
        row.scale_y = 1.25
        operator_if_exists(
            row, "hops.apply_modifiers", text="Hops Smart Apply", icon="MODIFIER"
        )

        row = column.row(align=True)
        row.scale_y = 1.25
        operator_if_exists(
            row, "machin3.boolean_apply", text="MM Stash Apply", icon="MODIFIER"
        )

        # Apply rotation and scale
        row = column.row(align=True)
        row.scale_y = 1.25
        operator_if_exists(
            row,
            "object.transform_apply",
            text="Apply Scale",
            location=False,
            rotation=False,
            scale=True,
        )
        operator_if_exists(
            row,
            "object.transform_apply",
            text="& Rotation",
            location=False,
            rotation=True,
            scale=True,
        )
        operator_if_exists(
            row,
            "object.transform_apply",
            text="*",
            location=True,
            rotation=True,
            scale=True,
        )

        # TODO Add Metashape
        # TODO Add Unparent

    def draw_pie_box(self, layout):
        """
        Draws a box containing Machin3Tools pie menus.

        Args:
            layout (bpy.types.UILayout): The layout to draw the box in.
        """
        machin3_pies = {
            "MACHIN3_MT_modes_pie": "Modes",
            "MACHIN3_MT_save_pie": "Save",
            "MACHIN3_MT_shading_pie": "Shading",
            "MACHIN3_MT_viewport_pie": "Views",
            "MACHIN3_MT_align_pie": "Align",
            "MACHIN3_MT_cursor_pie": "Cursor",
            "MACHIN3_MT_transform_pie": "Transform",
            "MACHIN3_MT_snapping_pie": "Snapping",
            "MACHIN3_MT_collections_pie": "Collections",
            "MACHIN3_MT_workspace_pie": "Workspace",
        }

        # Check to see if any Machin3 Tools Pie Menus are enabled
        if any(hasattr(bpy.types, pie_name) for pie_name in machin3_pies.keys()):
            column = layout.column()
            column.scale_x = 1

            # Artificially move the items down to be centered-ish
            separate(column, 8)

            column = column.box().column(align=True)
            column.scale_x = 1
            column.label(text="Machin3 Pies")

            for pie_id, text in machin3_pies.items():
                if hasattr(bpy.types, pie_id):
                    op = operator_if_exists(column, "wm.call_menu_pie", text=text)
                    if op:
                        op.name = pie_id

    def draw_addon_menu(self, layout):
        """
        Draws a menu for various addon-related operators.

        Args:
            layout (bpy.types.UILayout): The layout to draw the menu in.
        """
        column = layout.column()
        column.scale_x = 1

        # Artificially move the items down to be centered-ish
        separate(column, 8)

        column = column.box().column(align=True)
        column.label(text="Addons")

        addons = [
            ("HOPS_MT_MainMenu", "Hops (M)", "wm.call_menu"),
            ("MACHIN3_MT_mesh_machine", "MESHmachine", "wm.call_menu"),
            ("UI_MT_random_flow", "Random Flow", "wm.call_menu"),
            ("FLUENT_MT_PieMenu", "Fluent", "wm.call_menu_pie"),
            ("UI_MT_cuber", "Cuber", "wm.call_menu_pie"),
            ("VIEW3D_MT_cablerator", "Cablerator", "wm.call_menu"),
            ("UI_MT_ice_tools", "Ice Tools", "wm.call_menu_pie"),
        ]

        for addon_id, text, operator_type in addons:
            if hasattr(bpy.types, addon_id):
                op = operator_if_exists(column, operator_type, text=text)
                if op:
                    op.name = addon_id

    def draw_misc_edit_box(self, layout):
        """
        Draws miscellaneous edit mode operators.

        Args:
            layout (bpy.types.UILayout): The layout to draw the box in.
        """
        column = layout.column(align=True)

        # Punch it
        row = column.row(align=True)
        row.scale_y = 1.25
        operator_if_exists(row, "machin3.cursor_spin", text="Cursor Spin")
        operator_if_exists(row, "machin3.punch_it", text="Punch It")
        operator_if_exists(
            column,
            "machin3.transform_edge_constrained",
            text="Edge Constrained Transform",
        )

        # Loop Tools
        loop_tools_ops = {
            "mesh.looptools_bridge": {"text": "Bridge", "loft": False},
            "mesh.looptools_circle": {"text": "Circle"},
            "mesh.looptools_curve": {"text": "Curve"},
            "mesh.looptools_flatten": {"text": "Flatten"},
            "mesh.looptools_gstretch": {"text": "Gstretch"},
            "mesh.looptools_bridge": {"text": "Loft", "loft": True},
            "mesh.looptools_relax": {"text": "Relax"},
            "mesh.looptools_space": {"text": "Space"},
        }

        for op_id, props in loop_tools_ops.items():
            operator_if_exists(column, op_id, **props)

    def draw_hops_operators(self, layout):
        """
        Draws HardOps related operators.

        Args:
            layout (bpy.types.UILayout): The layout to draw the operators in.
        """
        # odd structures with IF statements are to cover the cases where HOps isn't installed
        row = layout.box().row(align=False)
        if hasattr(bpy.types, "HOPS_MT_MainMenu"):
            # Left Column
            col = row.column(align=True)
            col.scale_x = 1.25
            col.scale_y = 1.25
            operator_if_exists(
                col,
                "hops.mod_weighted_normal",
                text="",
                icon_value=get_icon_id("weightednormal"),
            )
            operator_if_exists(
                col,
                "hops.set_autosmoouth",
                text="",
                icon_value=get_icon_id("30"),
                angle=0.5236,
            )
            operator_if_exists(
                col,
                "hops.set_autosmoouth",
                text="",
                icon_value=get_icon_id("45"),
                angle=0.7854,
            )
            operator_if_exists(
                col,
                "hops.set_autosmoouth",
                text="",
                icon_value=get_icon_id("60"),
                angle=1.0472,
            )
            col.separator()
            operator_if_exists(
                col, "hops.adjust_bevel", text="", icon_value=get_icon_id("bevel")
            )
            operator_if_exists(
                col, "hops.mod_weld", text="", icon_value=get_icon_id("weld")
            )
            operator_if_exists(
                col,
                "hops.mod_shrinkwrap",
                text="",
                icon_value=get_icon_id("shrinkwrap"),
            )
            operator_if_exists(
                col, "hops.mod_displace", text="", icon_value=get_icon_id("displace")
            )
            operator_if_exists(
                col, "hops.mod_decimate", text="", icon_value=get_icon_id("decimate")
            )
            operator_if_exists(
                col, "hops.mod_subdivision", text="", icon_value=get_icon_id("subsurf")
            )
            operator_if_exists(
                col, "hops.bool_dice_v2", text="", icon_value=get_icon_id("Dice")
            )

        # Right column
        col = row.column(align=True)
        col.scale_x = 1.25
        col.scale_y = 1.25
        col.menu("SCREEN_MT_user_menu", text="", icon_value=get_icon_id("QuickFav"))

        if hasattr(bpy.types, "HOPS_MT_MainMenu"):
            col.separator()
            operator_if_exists(
                col, "hops.bool_difference", text="", icon_value=get_icon_id("red")
            )
            operator_if_exists(
                col, "hops.bool_union", text="", icon_value=get_icon_id("green")
            )
            operator_if_exists(
                col, "hops.bool_intersect", text="", icon_value=get_icon_id("orange")
            )
            operator_if_exists(
                col, "hops.bool_inset", text="", icon_value=get_icon_id("purple")
            )
            operator_if_exists(
                col, "hops.bool_knife", text="", icon_value=get_icon_id("blue")
            )
            operator_if_exists(
                col, "hops.slash", text="", icon_value=get_icon_id("yellow")
            )
            col.separator()
            operator_if_exists(
                col, "hops.st3_array", text="", icon_value=get_icon_id("Array")
            )
            operator_if_exists(
                col,
                "hops.radial_array_nodes",
                text="",
                icon_value=get_icon_id("ArrayCircle"),
            )
            operator_if_exists(
                col, "hops.mirror_gizmo", text="", icon_value=get_icon_id("mirror")
            )
            operator_if_exists(
                col, "hops.adjust_tthick", text="", icon_value=get_icon_id("solidify")
            )

    def draw(self, context):
        """
        Draws the main pie menu layout based on the current mode.

        Args:
            context (bpy.types.Context): The current Blender context.
        """
        layout = self.layout
        scene = context.scene
        view = context.space_data

        pie = layout.menu_pie()

        if context.mode in ["OBJECT"]:
            left_pie = pie.split().row()
            left_pie_column = left_pie.split().column()

            self.draw_camera_box(scene, view, left_pie_column.box())
            left_pie_column.prop(view.overlay, "show_face_orientation")
            self.draw_boxcutter_box(left_pie_column.box())
            self.draw_misc_object_box(left_pie_column.box())

            self.draw_hops_operators(left_pie.split())

            right_pie_row = pie.split().row()

            self.draw_tool_box(context, right_pie_row.box())
            self.draw_addon_menu(right_pie_row)
            self.draw_pie_box(right_pie_row)

            pie.separator()

        elif context.mode in ["EDIT_MESH"]:
            left_pie_column = pie.split().column()

            self.draw_misc_edit_box(left_pie_column.box())

            right_pie_row = pie.split().row()

            separate(right_pie_row, 3)

            self.draw_tool_box(context, right_pie_row.box(), columns=3)
            self.draw_addon_menu(right_pie_row)
            self.draw_pie_box(right_pie_row)

            separate(pie, 2)


class WM_OT_show_div_qpie_menu(bpy.types.Operator):
    """
    Operator to show the custom pie menu.
    """

    bl_idname = "wm.show_q_pie_menu"
    bl_label = "Show Q Pie Menu"

    def execute(self, context):
        """
        Executes the operator to show the pie menu.

        Args:
            context (bpy.types.Context): The current Blender context.

        Returns:
            set: {'FINISHED'} if successful.
        """
        if hasattr(bpy.ops, "wm") and hasattr(bpy.ops.wm, "call_menu_pie"):
            bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_div_qpie_menu")
        return {"FINISHED"}


addon_keymaps = []


def register_keymap():
    """
    Registers the keymap for the pie menu.
    """
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new("wm.show_q_pie_menu", "Q", "PRESS")
        addon_keymaps.append((km, kmi))


def unregister_keymap():
    """
    Unregisters the keymap for the pie menu.
    """
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


classes = (
    VIEW3D_MT_div_qpie_menu,
    WM_OT_show_div_qpie_menu,
)


def register():
    """
    Registers all classes and initializes icons and keymaps.
    """
    for cls in classes:
        bpy.utils.register_class(cls)
    initialize_icons_collection()
    register_keymap()


def unregister():
    """
    Unregisters all classes and unloads icons and keymaps.
    """
    unregister_keymap()
    unload_icons()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
