# osu_importer/objects/spinner.py

import bpy
import math
from mathutils import Vector
from osu_importer.objects.base_creator import BaseHitObjectCreator
from osu_importer.utils.utils import map_osu_to_blender, get_keyframe_values
from osu_importer.utils.constants import SPINNER_CENTER_X, SPINNER_CENTER_Y
from osu_importer.geo_nodes.geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes
from osu_importer.parsers.hitobjects import HitObject

class SpinnerCreator(BaseHitObjectCreator):
    def __init__(self, hitobject: HitObject, global_index: int, collection, config, data_manager, import_type):
        super().__init__(hitobject, global_index, collection, config, data_manager, import_type)

    def create_object(self):
        corrected_x, corrected_y, corrected_z = map_osu_to_blender(SPINNER_CENTER_X, SPINNER_CENTER_Y)

        if self.config.import_type == 'FULL':
            bpy.ops.mesh.primitive_circle_add(
                fill_type='NGON',
                radius=4,
                location=(corrected_x, corrected_y, corrected_z),
                rotation=(math.radians(90), 0, 0)
            )
            spinner = bpy.context.object
        else:
            mesh = bpy.data.meshes.new(f"{self.global_index:03d}_spinner_{self.hitobject.time}_mesh")
            mesh.from_pydata([(0, 0, 0)], [], [])
            mesh.update()

            spinner = bpy.data.objects.new(f"{self.global_index:03d}_spinner_{self.hitobject.time}", mesh)
            spinner.location = (corrected_x, corrected_y, corrected_z)
            create_geometry_nodes_modifier(spinner, "spinner")

        spinner.name = f"{self.global_index:03d}_spinner_{self.hitobject.time}"
        return spinner

    def animate_object(self, spinner):
        approach_rate = self.config.adjusted_ar

        start_frame = int(self.hitobject.start_frame)
        end_frame = int(self.hitobject.end_frame)

        spinner_duration_ms = self.hitobject.duration_frames * self.config.ms_per_frame * self.config.speed_multiplier
        spinner_duration_frames = self.hitobject.duration_frames

        frame_values, fixed_values = get_keyframe_values(
            self.hitobject,
            'spinner',
            self.config.import_type,
            start_frame,
            end_frame,
            start_frame,
            approach_rate,
            osu_radius=0,
            extra_params={
                "spinner_duration_ms": spinner_duration_ms,
                "spinner_duration_frames": spinner_duration_frames
            },
            ms_per_frame=self.config.ms_per_frame,
            audio_lead_in_frames=self.config.audio_lead_in_frames
        )

        attributes = {
            "show": 'BOOLEAN',
            "spinner_duration_ms": 'FLOAT',
            "spinner_duration_frames": 'FLOAT',
            "was_hit": 'BOOLEAN',
            "was_completed": 'BOOLEAN'
        }

        set_modifier_inputs_with_keyframes(spinner, attributes, frame_values, fixed_values)

        if self.config.import_type == 'FULL':
            spinner.hide_viewport = True
            spinner.hide_render = True
            spinner.keyframe_insert(data_path="hide_viewport", frame=int(start_frame - 1))
            spinner.keyframe_insert(data_path="hide_render", frame=int(start_frame - 1))

            spinner.hide_viewport = False
            spinner.hide_render = False
            spinner.keyframe_insert(data_path="hide_viewport", frame=int(start_frame))
            spinner.keyframe_insert(data_path="hide_render", frame=int(start_frame))

            if self.hitobject.was_completed:
                spinner.hide_viewport = False
                spinner.hide_render = False
            else:
                spinner.hide_viewport = True
                spinner.hide_render = True
            spinner.keyframe_insert(data_path="hide_viewport", frame=int(end_frame))
            spinner.keyframe_insert(data_path="hide_render", frame=int(end_frame))
