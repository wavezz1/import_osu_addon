# import_objects.py

from .circles import CircleCreator
from .slider import SliderCreator
from .spinner import SpinnerCreator
from .cursor import CursorCreator
from .utils import create_collection, timeit
from .geometry_nodes_osu_instance import gn_osu_node_group
import bpy

def assign_collections_to_sockets(obj, socket_to_collection, operator=None):
    modifier = obj.modifiers.get("GeometryNodes")
    if not modifier:
        error_message = f"No GeometryNodes modifier found on object '{obj.name}'."
        if operator:
            operator.report({'ERROR'}, error_message)
        print(error_message)
        return

    for socket_name, collection in socket_to_collection.items():
        try:
            # Überprüfen, ob der Modifier den Socket unterstützt
            if socket_name in modifier:
                modifier[socket_name] = collection
                print(f"Assigned collection '{collection.name}' to '{socket_name}'.")
            else:
                error_message = f"Socket '{socket_name}' not found in modifier 'GeometryNodes'."
                if operator:
                    operator.report({'ERROR'}, error_message)
                print(error_message)
        except Exception as e:
            error_message = f"Error assigning collection '{collection.name}' to '{socket_name}': {e}"
            if operator:
                operator.report({'ERROR'}, error_message)
            print(error_message)

def import_hitobjects(data_manager, settings, props, operator=None):
    with timeit("Erstellen der Sammlungen"):
        circles_collection = create_collection("Circles")
        sliders_collection = create_collection("Sliders")
        slider_balls_collection = create_collection("Slider Balls")  # Hinzugefügt
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

    # Neuer Abschnitt: Erstellen des Würfels in der Sammlung "Osu_Gameplay"
    with timeit("Erstellen des Osu_Gameplay Würfels"):
        # Sammlung erstellen oder abrufen

        if import_type == 'BASE':
            gameplay_collection = create_collection("Osu_Gameplay")

            # Würfel hinzufügen
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))  # Größe und Position nach Bedarf anpassen
            cube = bpy.context.object
            cube.name = "Osu_Gameplay_Cube"

            # Würfel zur "Osu_Gameplay" Sammlung hinzufügen
            gameplay_collection.objects.link(cube)

            # Würfel aus anderen Sammlungen entfernen, falls vorhanden
            if cube.users_collection:
                for col in cube.users_collection:
                    if col != gameplay_collection:
                        col.objects.unlink(cube)

            # Optional: Weitere Anpassungen am Würfel vornehmen
            # Beispiel: Skalieren des Würfels
            cube.scale = (2.0, 2.0, 2.0)  # Passen Sie die Skalierung nach Bedarf an

            # Sicherstellen, dass der GN_Osu Node Group existiert
            gn_osu_node_group()

            # Hinzufügen des Geometry Nodes Modifiers mit GN_Osu Node Tree
            node_group_name = "GN_Osu"  # Name des vorhandenen Node Trees

            # Überprüfen, ob der Node Group existiert
            node_group = bpy.data.node_groups.get(node_group_name)
            if node_group is None:
                error_message = f"Node Group '{node_group_name}' nicht gefunden. Bitte erstellen Sie sie zuerst."
                if operator:
                    operator.report({'ERROR'}, error_message)
                print(error_message)
            else:
                # Hinzufügen des Geometry Nodes Modifiers zum Würfel, falls noch nicht vorhanden
                if not cube.modifiers.get("GeometryNodes"):
                    modifier = cube.modifiers.new(name="GeometryNodes", type='NODES')
                    modifier.node_group = node_group
                    print(f"Geometry Nodes Modifier mit Node Group '{node_group_name}' zum Würfel hinzugefügt.")
                else:
                    modifier = cube.modifiers.get("GeometryNodes")
                    print(f"Geometry Nodes Modifier bereits auf dem Würfel '{cube.name}' vorhanden.")

                # Definieren der Zuordnung zwischen Sockets und Sammlungen
                socket_to_collection = {
                    "Socket_2": cursor_collection,
                    "Socket_3": circles_collection,
                    "Socket_4": sliders_collection,
                    "Socket_5": slider_balls_collection,
                    "Socket_6": spinners_collection,
                }

                # Anwenden der Zuordnung mittels der neuen Funktion
                assign_collections_to_sockets(cube, socket_to_collection, operator=operator)
