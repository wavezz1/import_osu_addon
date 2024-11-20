# osu_importer/import_objects.py

from osu_importer.objects.circles import CircleCreator
from osu_importer.objects.slider import SliderCreator
from osu_importer.objects.spinner import SpinnerCreator
from osu_importer.objects.cursor import CursorCreator
from osu_importer.objects.approach_circle import ApproachCircleCreator
from osu_importer.objects.slider_head_tail import SliderHeadTailCreator
from .utils.utils import create_collection, timeit, map_osu_to_blender
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

def setup_osu_gameplay_collections(cursor, approach_circle, circles, sliders, slider_balls, spinners, operator=None):
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
        "Socket_3": approach_circle,
        "Socket_4": circles,
        "Socket_5": sliders,
        "Socket_6": slider_balls,
        "Socket_7": spinners

    }
    assign_collections_to_sockets(cube, socket_to_collection, operator=operator)

    set_collection_exclude(["Circles", "Sliders", "Slider Balls", "Spinners", "Cursor", "Approach Circles"], exclude=True)

def import_hitobjects(data_manager, settings, props, operator=None):
    with timeit("Setting up collections"):
        collections = {
            "Circles": create_collection("Circles"),
            "Sliders": create_collection("Sliders"),
            "Slider Balls": create_collection("Slider Balls"),
            "Spinners": create_collection("Spinners"),
            "Cursor": create_collection("Cursor"),
            "Approach Circles": create_collection("Approach Circles"),
            "Slider Heads Tails": create_collection("Slider Heads Tails"),
        }

    global_index = 1
    import_type = settings.get('import_type', 'FULL')

    if props.import_circles:
        circles = data_manager.hitobjects_processor.circles
        for i, hitobject in enumerate(circles):
            CircleCreator(hitobject, global_index + i, collections["Circles"], settings, data_manager, import_type)
        global_index += len(circles)

    if props.import_sliders:
        sliders = data_manager.hitobjects_processor.sliders
        for i, hitobject in enumerate(sliders):
            SliderCreator(hitobject, global_index + i, collections["Sliders"], collections["Slider Balls"], settings, data_manager, import_type)
        global_index += len(sliders)

    if props.import_spinners:
        spinners = data_manager.hitobjects_processor.spinners
        for i, hitobject in enumerate(spinners):
            SpinnerCreator(hitobject, global_index + i, collections["Spinners"], settings, data_manager, import_type)
        global_index += len(spinners)

    if props.import_approach_circles:
        relevant_hitobjects = data_manager.hitobjects_processor.circles + data_manager.hitobjects_processor.sliders
        for i, hitobject in enumerate(relevant_hitobjects):
            ApproachCircleCreator(hitobject, global_index + i, collections["Approach Circles"], settings, data_manager, import_type)
        global_index += len(relevant_hitobjects)

    if props.import_cursors:
        cursor_creator = CursorCreator(collections["Cursor"], settings, data_manager, import_type)
        cursor_creator.animate_cursor()

    if props.import_sliders and props.import_slider_heads_tails and import_type == 'FULL':
        sliders = data_manager.hitobjects_processor.sliders
        for i, hitobject in enumerate(sliders):
            # Extrahiere Start- und Endposition des Sliders
            # Annahme: hitobject hat ein Attribut 'curve_points', eine Liste von (x, y) Tupeln
            if hasattr(hitobject, 'curve_points') and len(hitobject.curve_points) >= 2:
                start_point = hitobject.curve_points[0]
                end_point = hitobject.curve_points[-1]
                start_pos = map_osu_to_blender(start_point[0], start_point[1])  # (x, y, z)
                end_pos = map_osu_to_blender(end_point[0], end_point[1])  # (x, y, z)

                # Slider Head erstellen
                SliderHeadTailCreator(
                    hitobject=hitobject,
                    position=start_pos,
                    global_index=global_index + i * 2,
                    slider_heads_tails_collection=collections["Slider Heads Tails"],
                    settings=settings,
                    data_manager=data_manager
                )

                # Slider Tail erstellen
                SliderHeadTailCreator(
                    hitobject=hitobject,
                    position=end_pos,
                    global_index=global_index + i * 2 + 1,
                    slider_heads_tails_collection=collections["Slider Heads Tails"],
                    settings=settings,
                    data_manager=data_manager
                )
        global_index += len(sliders) * 2

    if import_type == 'BASE' and props.include_osu_gameplay:
        setup_osu_gameplay_collections(
            cursor=collections["Cursor"],
            approach_circle=collections["Approach Circles"],
            circles=collections["Circles"],
            sliders=collections["Sliders"],
            slider_balls=collections["Slider Balls"],
            spinners=collections["Spinners"],
            operator=operator
        )