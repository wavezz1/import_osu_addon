# cursor.py

import bpy
from .utils import get_ms_per_frame, map_osu_to_blender
from .geometry_nodes import create_geometry_nodes_modifier, connect_attributes_with_drivers
from .osu_replay_data_manager import OsuReplayDataManager


class CursorCreator:
    def __init__(self, cursor_collection, settings, data_manager: OsuReplayDataManager):
        self.cursor_collection = cursor_collection
        self.settings = settings
        self.data_manager = data_manager
        self.cursor = None  # Speichert das Cursor-Objekt
        self.create_cursor()

    def create_cursor(self):
        try:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, 0))
            cursor = bpy.context.object
            cursor.name = "Cursor"

            cursor["k1"] = False
            cursor["k2"] = False
            cursor["m1"] = False
            cursor["m2"] = False

            self.cursor_collection.objects.link(cursor)
            if cursor.users_collection:
                for col in cursor.users_collection:
                    if col != self.cursor_collection:
                        col.objects.unlink(cursor)

            # Nachdem die Geometrie Nodes Modifier erstellt wurde
            create_geometry_nodes_modifier(cursor, "cursor")

            # Dynamisches Verbinden der Attribute mit den Treibern
            connect_attributes_with_drivers(cursor, {
                "k1": 'BOOLEAN',
                "k2": 'BOOLEAN',
                "m1": 'BOOLEAN',
                "m2": 'BOOLEAN'
            })
            self.cursor = cursor
            print(f"Cursor '{cursor.name}' created successfully.")
            return cursor
        except Exception as e:
            print(f"Error creating cursor: {e}")
            return None

    def animate_cursor(self):
        if self.cursor is None:
            print("Cursor object is None, skipping animation.")
            return

        replay_data = self.data_manager.replay_data
        key_presses = self.data_manager.key_presses
        speed_multiplier = self.settings.get('speed_multiplier', 1.0)
        audio_lead_in = self.data_manager.beatmap_info.get("audio_lead_in", 0)

        audio_lead_in_frames = audio_lead_in / get_ms_per_frame()
        total_time = 0

        try:
            for i, event in enumerate(replay_data):
                total_time += event.time_delta
                if event.x == -256 and event.y == -256:
                    continue  # Ignoriere spezielle Cursor-Events, falls vorhanden

                corrected_x, corrected_y, corrected_z = map_osu_to_blender(event.x, event.y)
                self.cursor.location = (corrected_x, corrected_y, corrected_z)

                adjusted_time_ms = total_time / speed_multiplier
                frame = (adjusted_time_ms / get_ms_per_frame()) + audio_lead_in_frames

                self.cursor["k1"] = key_presses[i]['k1']
                self.cursor["k2"] = key_presses[i]['k2']
                self.cursor["m1"] = key_presses[i]['m1']
                self.cursor["m2"] = key_presses[i]['m2']

                self.cursor.keyframe_insert(data_path='location', frame=frame)
                self.cursor.keyframe_insert(data_path='["k1"]', frame=frame)
                self.cursor.keyframe_insert(data_path='["k2"]', frame=frame)
                self.cursor.keyframe_insert(data_path='["m1"]', frame=frame)
                self.cursor.keyframe_insert(data_path='["m2"]', frame=frame)

            print(f"Cursor '{self.cursor.name}' animated successfully.")
        except Exception as e:
            print(f"Error animating cursor: {e}")
