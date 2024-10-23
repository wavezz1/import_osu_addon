# cursor.py

import bpy
from .utils import get_ms_per_frame, map_osu_to_blender
from .geometry_nodes import create_geometry_nodes_modifier_cursor

def create_cursor(cursor_collection):
    try:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, 0))
        cursor = bpy.context.object
        cursor.name = "Cursor"

        cursor_collection.objects.link(cursor)
        if cursor.users_collection:
            for col in cursor.users_collection:
                if col != cursor_collection:
                    col.objects.unlink(cursor)

        # Füge den Geometry Nodes Modifier hinzu
        create_geometry_nodes_modifier_cursor(cursor, "Cursor")

        return cursor
    except Exception as e:
        print(f"Fehler beim Erstellen des Cursors: {e}")
        return None


def animate_cursor(cursor, replay_data, key_presses, speed_multiplier=1.0):
    if cursor is None:
        print("Cursor-Objekt ist None, Animation wird übersprungen.")
        return

    total_time = 0
    try:
        for i, event in enumerate(replay_data):
            total_time += event.time_delta
            if event.x == -256 and event.y == -256:
                continue

            corrected_x, corrected_y, corrected_z = map_osu_to_blender(event.x, event.y)
            cursor.location = (corrected_x, corrected_y, corrected_z)

            # Zeitberechnung und Frame
            adjusted_time_ms = total_time / speed_multiplier
            frame = (adjusted_time_ms / get_ms_per_frame())

            # Setze die Properties für k1, k2, m1 und m2
            cursor["k1"] = key_presses[i]['k1']
            cursor["k2"] = key_presses[i]['k2']
            cursor["m1"] = key_presses[i]['m1']
            cursor["m2"] = key_presses[i]['m2']

            # Setze die Keyframes
            cursor.keyframe_insert(data_path='location', frame=frame)
            cursor.keyframe_insert(data_path='["k1"]', frame=frame)
            cursor.keyframe_insert(data_path='["k2"]', frame=frame)
            cursor.keyframe_insert(data_path='["m1"]', frame=frame)
            cursor.keyframe_insert(data_path='["m2"]', frame=frame)

    except Exception as e:
        print(f"Fehler beim Animieren des Cursors: {e}")
