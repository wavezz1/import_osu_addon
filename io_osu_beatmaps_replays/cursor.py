# cursor.py

import bpy
from .utils import get_ms_per_frame, map_osu_to_blender
from .geometry_nodes import create_geometry_nodes_modifier_cursor, connect_attributes_with_drivers
from .osu_replay_data_manager import OsuReplayDataManager

def create_cursor(cursor_collection, data_manager: OsuReplayDataManager):
    try:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, 0))
        cursor = bpy.context.object
        cursor.name = "Cursor"

        cursor_collection.objects.link(cursor)
        if cursor.users_collection:
            for col in cursor.users_collection:
                if col != cursor_collection:
                    col.objects.unlink(cursor)

        # Geometry Nodes Modifier hinzufügen
        node_group_name = "Geometry Nodes Cursor"
        create_geometry_nodes_modifier_cursor(cursor, node_group_name)

        # Fahrer (Drivers) verbinden
        connect_attributes_with_drivers(cursor, {"k1": 'BOOLEAN', "k2": 'BOOLEAN', "m1": 'BOOLEAN', "m2": 'BOOLEAN'})

        return cursor
    except Exception as e:
        print(f"Error creating cursor: {e}")
        return None

def animate_cursor(cursor, replay_data, key_presses, speed_multiplier=1.0, audio_lead_in=0):
    if cursor is None:
        print("Cursor object is None, skipping animation.")
        return

    audio_lead_in_frames = audio_lead_in / get_ms_per_frame()
    total_time = 0
    try:
        for i, event in enumerate(replay_data):
            total_time += event.time_delta
            if event.x == -256 and event.y == -256:
                continue

            corrected_x, corrected_y, corrected_z = map_osu_to_blender(event.x, event.y)
            cursor.location = (corrected_x, corrected_y, corrected_z)

            adjusted_time_ms = total_time / speed_multiplier
            frame = (adjusted_time_ms / get_ms_per_frame()) + audio_lead_in_frames

            cursor["k1"] = key_presses[i]['k1']
            cursor["k2"] = key_presses[i]['k2']
            cursor["m1"] = key_presses[i]['m1']
            cursor["m2"] = key_presses[i]['m2']

            # Insert keyframes
            cursor.keyframe_insert(data_path='location', frame=frame)
            cursor.keyframe_insert(data_path='["k1"]', frame=frame)
            cursor.keyframe_insert(data_path='["k2"]', frame=frame)
            cursor.keyframe_insert(data_path='["m1"]', frame=frame)
            cursor.keyframe_insert(data_path='["m2"]', frame=frame)

    except Exception as e:
        print(f"Error animating cursor: {e}")
