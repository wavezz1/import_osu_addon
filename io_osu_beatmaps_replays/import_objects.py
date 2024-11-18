# import_objects.py

from .circles import CircleCreator
from .slider import SliderCreator
from .spinner import SpinnerCreator
from .cursor import CursorCreator
from .utils import create_collection, timeit
from .geometry_nodes import assign_collections_to_sockets
from .geometry_nodes_osu_instance import gn_osu_node_group
import bpy


def set_collection_exclude(collection_names, exclude=False, view_layer=None):
    if view_layer is None:
        view_layer = bpy.context.view_layer

    if isinstance(collection_names, str):
        collection_names = [collection_names]

    for collection_name in collection_names:
        layer_collection = view_layer.layer_collection.children.get(collection_name)

        if layer_collection:
            layer_collection.exclude = exclude
            print(
                f"'Exclude from View Layer' für Collection '{collection_name}' auf {exclude} in View Layer '{view_layer.name}' gesetzt.")
        else:
            print(f"Collection '{collection_name}' wurde im View Layer '{view_layer.name}' nicht gefunden.")

def import_hitobjects(data_manager, settings, props, operator=None):
    with timeit("Erstellen der Sammlungen"):
        circles_collection = create_collection("Circles")
        sliders_collection = create_collection("Sliders")
        slider_balls_collection = create_collection("Slider Balls")
        spinners_collection = create_collection("Spinners")
        cursor_collection = create_collection("Cursor")

        global_index = 1

        import_type = settings.get('import_type', 'FULL')

        if props.import_circles:
            for hitobject in data_manager.hitobjects_processor.circles:
                CircleCreator(hitobject, global_index, circles_collection, settings, data_manager, import_type)
                global_index += 1

        if props.import_sliders:
            for hitobject in data_manager.hitobjects_processor.sliders:
                SliderCreator(hitobject, global_index, sliders_collection, slider_balls_collection, settings, data_manager, import_type)
                global_index += 1

        if props.import_spinners:
            for hitobject in data_manager.hitobjects_processor.spinners:
                SpinnerCreator(hitobject, global_index, spinners_collection, settings, data_manager, import_type)
                global_index += 1

        if props.import_cursors:
            cursor_creator = CursorCreator(cursor_collection, settings, data_manager, import_type)
            cursor_creator.animate_cursor()

        gn_osu_node_group()

    with timeit("Erstellen des Osu_Gameplay Würfels"):

        if import_type == 'BASE':
            gameplay_collection = create_collection("Osu_Gameplay")

            # Placeholder Mesh for Geo Nodes
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
            cube = bpy.context.object
            cube.name = "Osu_Gameplay"

            gameplay_collection.objects.link(cube)

            if cube.users_collection:
                for col in cube.users_collection:
                    if col != gameplay_collection:
                        col.objects.unlink(cube)

            node_group_name = "GN_Osu"

            node_group = bpy.data.node_groups.get(node_group_name)
            if node_group is None:
                error_message = f"Node Group '{node_group_name}' nicht gefunden. Bitte erstellen Sie sie zuerst."
                if operator:
                    operator.report({'ERROR'}, error_message)
                print(error_message)
            else:
                if not cube.modifiers.get("GeometryNodes"):
                    modifier = cube.modifiers.new(name="GeometryNodes", type='NODES')
                    modifier.node_group = node_group
                    print(f"Geometry Nodes Modifier mit Node Group '{node_group_name}' zum Würfel hinzugefügt.")
                else:
                    modifier = cube.modifiers.get("GeometryNodes")
                    print(f"Geometry Nodes Modifier bereits auf dem Würfel '{cube.name}' vorhanden.")

                socket_to_collection = {
                    "Socket_2": cursor_collection,
                    "Socket_3": circles_collection,
                    "Socket_4": sliders_collection,
                    "Socket_5": slider_balls_collection,
                    "Socket_6": spinners_collection,
                }

                assign_collections_to_sockets(cube, socket_to_collection, operator=operator)

            set_collection_exclude(["Circles", "Sliders", "Slider Balls", "Spinners", "Cursor"], exclude=True)