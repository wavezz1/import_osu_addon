# osu_importer/cursor.py

import bpy
from .utils import get_ms_per_frame, map_osu_to_blender

def create_animated_cursor(cursor_collection):
    # Ihre bestehende Implementierung
    try:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, 0))
        cursor = bpy.context.object
        cursor.name = "Cursor"

        # Link zum gewünschten Collection hinzufügen
        cursor_collection.objects.link(cursor)
        # Aus anderen Collections entfernen
        if cursor.users_collection:
            for col in cursor.users_collection:
                if col != cursor_collection:
                    col.objects.unlink(cursor)

        return cursor
    except Exception as e:
        print(f"Fehler beim Erstellen des Cursors: {e}")
        return None

def animate_cursor(cursor, replay_data, offset, speed_multiplier=1.0):
    if cursor is None:
        print("Cursor-Objekt ist None, Animation wird übersprungen.")
        return
    total_time = 0
    try:
        for event in replay_data:
            total_time += event.time_delta
            if event.x == -256 and event.y == -256:
                continue  # Cursor ist nicht auf dem Bildschirm
            corrected_x, corrected_y, corrected_z = map_osu_to_blender(event.x, event.y)
            cursor.location = (corrected_x, corrected_y, corrected_z)
            adjusted_time = (total_time + offset) / speed_multiplier
            frame = adjusted_time / get_ms_per_frame()
            cursor.keyframe_insert(data_path="location", frame=frame)
    except Exception as e:
        print(f"Fehler beim Animieren des Cursors: {e}")
