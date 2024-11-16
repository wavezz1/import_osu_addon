# cursor.py

import bpy
from .utils import get_ms_per_frame, map_osu_to_blender, timeit
from .geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes
from .osu_replay_data_manager import OsuReplayDataManager


class CursorCreator:
    def __init__(self, cursor_collection, settings, data_manager: OsuReplayDataManager, import_type):
        self.cursor_collection = cursor_collection
        self.settings = settings
        self.data_manager = data_manager
        self.import_type = import_type
        self.cursor = None  # Speichert das Cursor-Objekt
        self.create_cursor()

    def create_cursor(self):
        try:
            if self.import_type == 'FULL':
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, 0))
                cursor = bpy.context.object
            elif self.import_type == 'BASE':
                mesh = bpy.data.meshes.new("Cursor")

                # Füge den Vertex direkt in den Mesh-Daten hinzu
                mesh.vertices.add(1)
                mesh.vertices[0].co = (0, 0, 0)

                # Erstelle das Objekt und setze die Position
                cursor = bpy.data.objects.new("Cursor", mesh)
                cursor.location = (0, 0, 0)

                # Setze Viewport Display auf Bounds und Sphere
                cursor.display_type = 'BOUNDS'
                cursor.display_bounds_type = 'SPHERE'

            cursor.name = "Cursor"

            # Add Geometry Nodes modifier
            create_geometry_nodes_modifier(cursor, "cursor")

            # Define initial keyframe values (optional)
            frame_values = {
                "k1": [
                    (1, False),
                    # Weitere Keyframes werden in animate_cursor gesetzt
                ],
                "k2": [
                    (1, False),
                ],
                "m1": [
                    (1, False),
                ],
                "m2": [
                    (1, False),
                ]
            }

            # Set initial modifier inputs with keyframes
            set_modifier_inputs_with_keyframes(cursor, {
                "k1": 'BOOLEAN',
                "k2": 'BOOLEAN',
                "m1": 'BOOLEAN',
                "m2": 'BOOLEAN'
            }, frame_values)

            self.cursor_collection.objects.link(cursor)
            if cursor.users_collection:
                for col in cursor.users_collection:
                    if col != self.cursor_collection:
                        col.objects.unlink(cursor)

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

                # Define keyframe values for cursor attributes
                frame_values = {
                    "k1": [
                        (int(frame), bool(key_presses[i]['k1']))
                    ],
                    "k2": [
                        (int(frame), bool(key_presses[i]['k2']))
                    ],
                    "m1": [
                        (int(frame), bool(key_presses[i]['m1']))
                    ],
                    "m2": [
                        (int(frame), bool(key_presses[i]['m2']))
                    ]
                }

                # Set modifier inputs with keyframes
                set_modifier_inputs_with_keyframes(self.cursor, {
                    "k1": 'BOOLEAN',
                    "k2": 'BOOLEAN',
                    "m1": 'BOOLEAN',
                    "m2": 'BOOLEAN'
                }, frame_values, fixed_values=None)

                # Set location keyframe
                self.cursor.keyframe_insert(data_path='location', frame=frame)

            print(f"Cursor '{self.cursor.name}' animated successfully.")
        except Exception as e:
            print(f"Error animating cursor: {e}")

    def animate_cursor_full(self):
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

                # Define keyframe values for cursor attributes
                frame_values = {
                    "k1": [
                        (int(frame), bool(key_presses[i]['k1']))
                    ],
                    "k2": [
                        (int(frame), bool(key_presses[i]['k2']))
                    ],
                    "m1": [
                        (int(frame), bool(key_presses[i]['m1']))
                    ],
                    "m2": [
                        (int(frame), bool(key_presses[i]['m2']))
                    ]
                }

                # Set modifier inputs with keyframes
                set_modifier_inputs_with_keyframes(self.cursor, {
                    "k1": 'BOOLEAN',
                    "k2": 'BOOLEAN',
                    "m1": 'BOOLEAN',
                    "m2": 'BOOLEAN'
                }, frame_values, fixed_values=None)

                # Set location keyframe
                self.cursor.keyframe_insert(data_path='location', frame=frame)

                # Optionally, handle visibility keyframes if needed for FULL import
                # For example, show cursor only during active frames
                # This can be customized based on specific requirements

            print(f"Cursor '{self.cursor.name}' animated successfully.")
        except Exception as e:
            print(f"Error animating cursor: {e}")
