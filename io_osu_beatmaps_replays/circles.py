# circles.py

import bpy
import math
from .utils import map_osu_to_blender, get_ms_per_frame, timeit
from .constants import SCALE_FACTOR
from .geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes
from .osu_replay_data_manager import OsuReplayDataManager

class CircleCreator:
    def __init__(self, hitobject, global_index, circles_collection, settings, data_manager: OsuReplayDataManager):
        self.hitobject = hitobject
        self.global_index = global_index
        self.circles_collection = circles_collection
        self.settings = settings
        self.data_manager = data_manager
        self.create_circle()

    def create_circle(self):
        with timeit(f"Erstellen von Kreis {self.global_index:03d}_circle_{self.hitobject.time}"):
            approach_rate = self.data_manager.calculate_adjusted_ar()
            preempt_ms = self.data_manager.calculate_preempt_time(approach_rate)
            preempt_frames = preempt_ms / get_ms_per_frame()

            circle_size = self.data_manager.calculate_adjusted_cs()
            audio_lead_in_frames = self.data_manager.beatmap_info["audio_lead_in"] / get_ms_per_frame()

            x = self.hitobject.x
            y = self.hitobject.y
            time_ms = self.hitobject.time
            speed_multiplier = self.settings.get('speed_multiplier', 1.0)
            start_frame = ((time_ms / speed_multiplier) / get_ms_per_frame()) + audio_lead_in_frames
            early_start_frame = start_frame - preempt_frames

            corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)

            osu_radius = (54.4 - 4.48 * circle_size) / 2

            bpy.ops.mesh.primitive_circle_add(
                fill_type='NGON',
                radius=0.5,
                location=(corrected_x, corrected_y, corrected_z),
                rotation=(math.radians(90), 0, 0)
            )
            circle = bpy.context.object
            circle.name = f"{self.global_index:03d}_circle_{time_ms}"

            circle["ar"] = approach_rate
            circle["cs"] = osu_radius * SCALE_FACTOR

            circle["was_hit"] = False
            circle.keyframe_insert(data_path='["was_hit"]', frame=(start_frame - 1))

            circle["was_hit"] = self.hitobject.was_hit
            circle.keyframe_insert(data_path='["was_hit"]', frame=start_frame)

            circle["show"] = False
            circle.keyframe_insert(data_path='["show"]', frame=(early_start_frame - 1))
            circle["show"] = True
            circle.keyframe_insert(data_path='["show"]', frame=early_start_frame)

            self.circles_collection.objects.link(circle)
            if circle.users_collection:
                for col in circle.users_collection:
                    if col != self.circles_collection:
                        col.objects.unlink(circle)

            create_geometry_nodes_modifier(circle, "circle")

            # Define keyframe values
            frame_values = {
                "show": [
                    (int(early_start_frame - 1), False),
                    (int(early_start_frame), True)
                ],
                "was_hit": [
                    (int(start_frame - 1), False),
                    (int(start_frame), self.hitobject.was_hit)
                ],
                "ar": [
                    (int(start_frame), approach_rate)
                ],
                "cs": [
                    (int(start_frame), osu_radius * SCALE_FACTOR)
                ]
            }

            # Set modifier inputs with keyframes
            set_modifier_inputs_with_keyframes(circle, {
                "show": 'BOOLEAN',
                "was_hit": 'BOOLEAN',
                "ar": 'FLOAT',
                "cs": 'FLOAT'
            }, frame_values)