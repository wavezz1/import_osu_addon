# import_objects.py

from osu_importer.objects.circles import CircleCreator
from osu_importer.objects.slider import SliderCreator
from osu_importer.objects.spinner import SpinnerCreator
from osu_importer.objects.cursor import CursorCreator
from .utils import create_collection, timeit
from osu_importer.geo_nodes.geometry_nodes import assign_collections_to_sockets
from osu_importer.geo_nodes.geometry_nodes_osu_instance import gn_osu_node_group
import bpy


def set_collection_exclude(collection_names, exclude=False, view_layer=None):
    if view_layer is None:
        view_layer = bpy.context.view_layer

    collection_names = [collection_names] if isinstance(collection_names, str) else collection_names

    for collection_name in collection_names:
        layer_collection = view_layer.layer_collection.children.get(collection_name)
        if layer_collection:
            layer_collection.exclude = exclude
            print(f"Set 'Exclude from View Layer' for collection '{collection_name}' to {exclude}.")
        else:
            print(f"Collection '{collection_name}' not found in view layer '{view_layer.name}'.")


def create_gameplay_placeholder():
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    cube = bpy.context.object
    cube.name = "Osu_Gameplay"
    return cube


def setup_osu_gameplay_collections(cursor, circles, sliders, slider_balls, spinners, operator=None):
    gameplay_collection = create_collection("Osu_Gameplay")
    cube = create_gameplay_placeholder()

    gameplay_collection.objects.link(cube)
    if cube.users_collection:
        for col in cube.users_collection:
            if col != gameplay_collection:
                col.objects.unlink(cube)

    gn_osu_node_group()

    node_group_name = "GN_Osu"
    node_group = bpy.data.node_groups.get(node_group_name)
    if not node_group:
        error_message = f"Node Group '{node_group_name}' not found. Please create it first."
        if operator:
            operator.report({'ERROR'}, error_message)
        print(error_message)
        return

    modifier = cube.modifiers.new(name="GeometryNodes", type='NODES') if not cube.modifiers.get("GeometryNodes") else cube.modifiers.get("GeometryNodes")
    modifier.node_group = node_group

    socket_to_collection = {
        "Socket_2": cursor,
        "Socket_3": circles,
        "Socket_4": sliders,
        "Socket_5": slider_balls,
        "Socket_6": spinners,
    }
    assign_collections_to_sockets(cube, socket_to_collection, operator=operator)

    set_collection_exclude(["Circles", "Sliders", "Slider Balls", "Spinners", "Cursor"], exclude=True)


def import_hitobjects(data_manager, settings, props, operator=None):
    with timeit("Setting up collections"):
        collections = {
            "Circles": create_collection("Circles"),
            "Sliders": create_collection("Sliders"),
            "Slider Balls": create_collection("Slider Balls"),
            "Spinners": create_collection("Spinners"),
            "Cursor": create_collection("Cursor"),
        }

    global_index = 1
    import_type = settings.get('import_type', 'FULL')

    hitobject_importers = {
        "circles": lambda: [
            CircleCreator(hitobject, global_index + i, collections["Circles"], settings, data_manager, import_type)
            for i, hitobject in enumerate(data_manager.hitobjects_processor.circles)
        ],
        "sliders": lambda: [
            SliderCreator(hitobject, global_index + i, collections["Sliders"], collections["Slider Balls"], settings, data_manager, import_type)
            for i, hitobject in enumerate(data_manager.hitobjects_processor.sliders)
        ],
        "spinners": lambda: [
            SpinnerCreator(hitobject, global_index + i, collections["Spinners"], settings, data_manager, import_type)
            for i, hitobject in enumerate(data_manager.hitobjects_processor.spinners)
        ],
    }

    if props.import_circles:
        hitobject_importers["circles"]()
        global_index += len(data_manager.hitobjects_processor.circles)

    if props.import_sliders:
        hitobject_importers["sliders"]()
        global_index += len(data_manager.hitobjects_processor.sliders)

    if props.import_spinners:
        hitobject_importers["spinners"]()
        global_index += len(data_manager.hitobjects_processor.spinners)

    if props.import_cursors:
        cursor_creator = CursorCreator(collections["Cursor"], settings, data_manager, import_type)
        cursor_creator.animate_cursor()

    if import_type == 'BASE' and props.include_osu_gameplay:
        setup_osu_gameplay_collections(
            cursor=collections["Cursor"],
            circles=collections["Circles"],
            sliders=collections["Sliders"],
            slider_balls=collections["Slider Balls"],
            spinners=collections["Spinners"],
            operator=operator
        )
