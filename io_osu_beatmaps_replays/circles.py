# osu_importer/circles.py

import bpy
from .utils import get_ms_per_frame, SCALE_FACTOR

def create_circle_at_position(x, y, name, start_time_ms, global_index, circles_collection, offset, early_frames=5, end_time_ms=None):
    try:
        start_frame = (start_time_ms + offset) / get_ms_per_frame()
        early_start_frame = start_frame - early_frames

        bpy.ops.mesh.primitive_circle_add(radius=0.5, location=(x * SCALE_FACTOR, -y * SCALE_FACTOR, 0))
        circle = bpy.context.object
        circle.name = f"{global_index:03d}_{name}"

        # Keyframe zum Einblenden
        circle.hide_viewport = True
        circle.hide_render = True
        circle.keyframe_insert(data_path="hide_viewport", frame=early_start_frame - 1)
        circle.keyframe_insert(data_path="hide_render", frame=early_start_frame - 1)

        circle.hide_viewport = False
        circle.hide_render = False
        circle.keyframe_insert(data_path="hide_viewport", frame=early_start_frame)
        circle.keyframe_insert(data_path="hide_render", frame=early_start_frame)

        # Optional: Keyframe zum Ausblenden
        if end_time_ms is not None:
            end_frame = (end_time_ms + offset) / get_ms_per_frame()
            circle.hide_viewport = False
            circle.hide_render = False
            circle.keyframe_insert(data_path="hide_viewport", frame=end_frame - 1)
            circle.keyframe_insert(data_path="hide_render", frame=end_frame - 1)

            circle.hide_viewport = True
            circle.hide_render = True
            circle.keyframe_insert(data_path="hide_viewport", frame=end_frame)
            circle.keyframe_insert(data_path="hide_render", frame=end_frame)

        # Objekt zur gewünschten Collection hinzufügen
        circles_collection.objects.link(circle)
        # Aus anderen Collections entfernen
        if circle.users_collection:
            for col in circle.users_collection:
                if col != circles_collection:
                    col.objects.unlink(circle)

    except Exception as e:
        print(f"Fehler beim Erstellen eines Kreises: {e}")
