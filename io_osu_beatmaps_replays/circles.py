# circles.py

import bpy
import math
from .utils import map_osu_to_blender, timeit
from .constants import SCALE_FACTOR
from .geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes
from .osu_replay_data_manager import OsuReplayDataManager


class CircleCreator:
    def __init__(self, hitobject, global_index, circles_collection, settings, data_manager: OsuReplayDataManager,
                 import_type):
        self.hitobject = hitobject
        self.global_index = global_index
        self.circles_collection = circles_collection
        self.settings = settings
        self.data_manager = data_manager
        self.import_type = import_type
        self.create_circle()

    def create_circle(self):
        with timeit(f"Erstellen von Kreis {self.global_index:03d}_circle_{self.hitobject.time}"):
            data_manager = self.data_manager

            approach_rate = data_manager.adjusted_ar
            preempt_frames = data_manager.preempt_frames
            circle_size = data_manager.adjusted_cs
            audio_lead_in_frames = data_manager.audio_lead_in_frames
            osu_radius = data_manager.osu_radius

            x = self.hitobject.x
            y = self.hitobject.y
            time_ms = self.hitobject.time
            speed_multiplier = data_manager.speed_multiplier
            ms_per_frame = data_manager.ms_per_frame

            start_frame = ((time_ms / speed_multiplier) / ms_per_frame) + audio_lead_in_frames
            early_start_frame = start_frame - preempt_frames

            corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)

            if self.import_type == 'FULL':
                bpy.ops.mesh.primitive_circle_add(
                    fill_type='NGON',
                    radius=osu_radius * SCALE_FACTOR * 2,
                    location=(corrected_x, corrected_y, corrected_z),
                    rotation=(math.radians(90), 0, 0)
                )
                circle = bpy.context.object
            elif self.import_type == 'BASE':
                mesh = bpy.data.meshes.new(f"{self.global_index:03d}_circle_{time_ms}")

                mesh.vertices.add(1)
                mesh.vertices[0].co = (0, 0, 0)

                mesh.use_auto_texspace = True

                circle = bpy.data.objects.new(f"{self.global_index:03d}_circle_{time_ms}", mesh)
                circle.location = (corrected_x, corrected_y, corrected_z)

            circle.name = f"{self.global_index:03d}_circle_{time_ms}"

            circle["ar"] = approach_rate
            circle["cs"] = osu_radius * SCALE_FACTOR

            self.circles_collection.objects.link(circle)
            if circle.users_collection:
                for col in circle.users_collection:
                    if col != self.circles_collection:
                        col.objects.unlink(circle)

            create_geometry_nodes_modifier(circle, "circle")

            if self.import_type == 'BASE':
                frame_values = {
                    "show": [
                        (int(early_start_frame - 1), False),
                        (int(early_start_frame), True)
                    ],
                    "was_hit": [
                        (int(start_frame - 1), False),
                        (int(start_frame), self.hitobject.was_hit)
                    ]
                }

                fixed_values = {
                    "ar": approach_rate,
                    "cs": osu_radius * SCALE_FACTOR * 2
                }

                set_modifier_inputs_with_keyframes(circle, {
                    "show": 'BOOLEAN',
                    "was_hit": 'BOOLEAN',
                    "ar": 'FLOAT',
                    "cs": 'FLOAT'
                }, frame_values, fixed_values)

            elif self.import_type == 'FULL':
                frame_values = {
                    "show": [
                        (int(early_start_frame - 1), False),
                        (int(early_start_frame), True),
                        (int(start_frame + 1), False)
                    ],
                    "was_hit": [
                        (int(start_frame - 1), False),
                        (int(start_frame), self.hitobject.was_hit)
                    ]
                }

                fixed_values = {
                    "ar": approach_rate,
                    "cs": osu_radius * SCALE_FACTOR
                }

                set_modifier_inputs_with_keyframes(circle, {
                    "show": 'BOOLEAN',
                    "was_hit": 'BOOLEAN',
                    "ar": 'FLOAT',
                    "cs": 'FLOAT'
                }, frame_values, fixed_values)

                circle.hide_viewport = True
                circle.hide_render = True
                circle.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame - 1))
                circle.hide_viewport = False
                circle.hide_render = False
                circle.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame))
                circle.keyframe_insert(data_path="hide_render", frame=int(early_start_frame))
                circle.hide_viewport = True
                circle.hide_render = True
                circle.keyframe_insert(data_path="hide_viewport", frame=int(start_frame + 1))
                circle.keyframe_insert(data_path="hide_render", frame=int(start_frame + 1))
