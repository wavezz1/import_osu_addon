# osu_importer/import_objects.py

from osu_importer.objects.circles import CircleCreator
from osu_importer.objects.slider import SliderCreator
from osu_importer.objects.spinner import SpinnerCreator
from osu_importer.objects.cursor import CursorCreator
from osu_importer.objects.approach_circle import ApproachCircleCreator
from osu_importer.objects.slider_head_tail import SliderHeadTailCreator
from .utils.utils import create_collection, timeit, tag_imported
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


def assign_materials_to_sockets(cube, socket_to_material, operator=None):
    modifier = cube.modifiers.get("GeometryNodes")
    if not modifier or not modifier.node_group:
        error_message = "No Geometry Nodes modifier or node group found on the Osu_Gameplay object."
        if operator:
            operator.report({'ERROR'}, error_message)
        print(error_message)
        return

    for socket, material in socket_to_material.items():
        if material:
            try:
                modifier[socket] = material
                print(f"Material '{material.name}' assigned to socket '{socket}'.")
            except KeyError:
                if operator:
                    operator.report({'WARNING'}, f"Socket '{socket}' not found in the node group.")
                print(f"Socket '{socket}' not found in the node group.")
        else:
            print(f"No material found for socket '{socket}', skipping.")


def setup_osu_gameplay_collections_and_materials(
        cursor, approach_circle, circles, sliders, slider_balls, spinners,
        slider_heads_tails, operator=None):

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

    # Collections zuweisen
    socket_to_collection = {
        "Socket_2": cursor,
        "Socket_3": approach_circle,
        "Socket_4": circles,
        "Socket_5": sliders,
        "Socket_6": slider_balls,
        "Socket_7": spinners,
        "Socket_8": slider_heads_tails
    }

    materials = {
        "Socket_9": bpy.data.materials.get("Cursor Material"),
        "Socket_10": bpy.data.materials.get("Circle Material"),
        "Socket_11": bpy.data.materials.get("Slider Material"),
        "Socket_12": bpy.data.materials.get("Slider Balls Material"),
        "Socket_13": bpy.data.materials.get("Slider Head/Tail Material"),
        "Socket_14": bpy.data.materials.get("Spinner Material"),
        "Socket_15": bpy.data.materials.get("Approach Circle Material"),
    }

    for socket, collection in socket_to_collection.items():
        if collection:
            assign_collections_to_sockets(cube, {socket: collection}, operator=operator)

    assign_materials_to_sockets(cube, materials, operator=operator)

    set_collection_exclude(
        ["Circles", "Sliders", "Slider Balls", "Spinners", "Cursor", "Approach Circles", "Slider Heads Tails"],
        exclude=True
    )

    return gameplay_collection

def import_hitobjects(data_manager, settings, props, operator=None):
    with timeit("Setting up collections"):
        collections = {
            "Circles": create_collection("Circles") if props.import_circles else None,
            "Sliders": create_collection("Sliders") if props.import_sliders else None,
            "Slider Balls": create_collection("Slider Balls") if props.import_slider_balls else None,
            "Spinners": create_collection("Spinners") if props.import_spinners else None,
            "Cursor": create_collection("Cursor") if props.import_cursors else None,
            "Approach Circles": create_collection("Approach Circles") if props.import_approach_circles else None,
            "Slider Heads Tails": create_collection("Slider Heads Tails") if props.import_sliders and props.import_slider_heads_tails and settings.get('import_type') == 'FULL' else None,
        }

        for collection in collections.values():
            if collection:
                tag_imported(collection)

        global_index = 1

    import_type = settings.get('import_type', 'FULL')

    settings.update({
        'approach_circle_bevel_depth': props.approach_circle_bevel_depth,
        'approach_circle_bevel_resolution': props.approach_circle_bevel_resolution
    })

    if props.import_circles:
        circles = data_manager.hitobjects_processor.circles
        for hitobject in circles:
            CircleCreator(
                hitobject=hitobject,
                global_index=global_index,
                circles_collection=collections["Circles"],
                settings=settings,
                data_manager=data_manager,
                import_type=import_type
            )
            global_index += 1

    if props.import_sliders:
        sliders = data_manager.hitobjects_processor.sliders
        for hitobject in sliders:
            SliderCreator(
                hitobject=hitobject,
                global_index=global_index,
                sliders_collection=collections["Sliders"],
                slider_balls_collection=collections["Slider Balls"],
                settings=settings,
                data_manager=data_manager,
                import_type=import_type
            )
            global_index += 1

    if props.import_spinners:
        spinners = data_manager.hitobjects_processor.spinners
        for hitobject in spinners:
            SpinnerCreator(
                hitobject=hitobject,
                global_index=global_index,
                spinners_collection=collections["Spinners"],
                settings=settings,
                data_manager=data_manager,
                import_type=import_type
            )
            global_index += 1

    if props.import_approach_circles:
        relevant_hitobjects = data_manager.hitobjects_processor.circles + data_manager.hitobjects_processor.sliders
        for hitobject in relevant_hitobjects:
            ApproachCircleCreator(
                hitobject=hitobject,
                global_index=global_index,
                approach_circles_collection=collections["Approach Circles"],
                settings=settings,
                data_manager=data_manager,
                import_type=import_type
            )
            global_index += 1

    if props.import_cursors:
        cursor_creator = CursorCreator(
            cursor_collection=collections["Cursor"],
            settings=settings,
            data_manager=data_manager,
            import_type=import_type
        )
        cursor_creator.animate_cursor()

    if props.import_sliders and props.import_slider_heads_tails and import_type == 'FULL':
        sliders = data_manager.hitobjects_processor.sliders
        for hitobject in sliders:
            # Slider Head
            SliderHeadTailCreator(
                hitobject=hitobject,
                position=hitobject.start_pos,
                global_index=global_index,
                slider_heads_tails_collection=collections["Slider Heads Tails"],
                settings=settings,
                data_manager=data_manager,
                import_type=import_type
            )
            global_index += 1

            # Slider Tail
            SliderHeadTailCreator(
                hitobject=hitobject,
                position=hitobject.end_pos,
                global_index=global_index,
                slider_heads_tails_collection=collections["Slider Heads Tails"],
                settings=settings,
                data_manager=data_manager,
                import_type=import_type
            )
            global_index += 1

    if import_type == 'BASE' and props.include_osu_gameplay:
        gameplay_collection = setup_osu_gameplay_collections_and_materials(
            cursor=collections.get("Cursor"),
            approach_circle=collections.get("Approach Circles"),
            circles=collections.get("Circles"),
            sliders=collections.get("Sliders"),
            slider_balls=collections.get("Slider Balls"),
            spinners=collections.get("Spinners"),
            slider_heads_tails=collections.get("Slider Heads Tails"),
            operator=operator
        )

        if gameplay_collection:
            tag_imported(gameplay_collection)
