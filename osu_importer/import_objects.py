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
        collections = {}
        if props.import_circles:
            collections["Circles"] = create_collection("Circles")

        if props.import_sliders:
            collections["Sliders"] = create_collection("Sliders")

        if props.import_slider_balls:
            collections["Slider Balls"] = create_collection("Slider Balls")

        if props.import_spinners:
            collections["Spinners"] = create_collection("Spinners")

        if props.import_cursors:
            collections["Cursor"] = create_collection("Cursor")

        if props.import_approach_circles:
            collections["Approach Circles"] = create_collection("Approach Circles")

        if props.import_sliders and props.import_slider_heads_tails and settings.get('import_type') == 'FULL':
            collections["Slider Heads Tails"] = create_collection("Slider Heads Tails")

        # Initialisieren des global_index für eindeutige Objektkennzeichnungen
        global_index = 1

    import_type = settings.get('import_type', 'FULL')

    # Aktualisieren der Einstellungen mit zusätzlichen Parametern
    settings.update({
        'approach_circle_bevel_depth': props.approach_circle_bevel_depth,
        'approach_circle_bevel_resolution': props.approach_circle_bevel_resolution
    })

    # Importieren der Kreise
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
            global_index += 1  # Inkrementieren nach jedem erstellten Objekt

    # Importieren der Slider
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

    # Importieren der Spinner
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

    # Importieren der Approach Circles
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

    # Importieren der Cursor
    if props.import_cursors:
        cursor_creator = CursorCreator(
            cursor_collection=collections["Cursor"],
            settings=settings,
            data_manager=data_manager,
            import_type=import_type
        )
        cursor_creator.animate_cursor()

    # Importieren der Slider Heads und Tails (für FULL Import Typ)
    if props.import_sliders and props.import_slider_heads_tails and import_type == 'FULL':
        sliders = data_manager.hitobjects_processor.sliders
        for hitobject in sliders:
            # Slider Head erstellen
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

            # Slider Tail erstellen
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

    # Setup der Osu Gameplay Collections, falls aktiviert
    if import_type == 'BASE' and props.include_osu_gameplay:
        setup_osu_gameplay_collections(
            cursor=collections.get("Cursor"),
            approach_circle=collections.get("Approach Circles"),
            circles=collections.get("Circles"),
            sliders=collections.get("Sliders"),
            slider_balls=collections.get("Slider Balls"),
            spinners=collections.get("Spinners"),
            operator=operator
        )
