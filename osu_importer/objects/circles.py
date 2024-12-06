# osu_importer/objects/circles.py

import bpy
import math
from osu_importer.objects.base_creator import BaseHitObjectCreator
from osu_importer.utils.utils import map_osu_to_blender, get_keyframe_values
from osu_importer.utils.constants import SCALE_FACTOR
from osu_importer.geo_nodes.geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes

class CircleCreator(BaseHitObjectCreator):
    def create_object(self):
        osu_radius = self.config.osu_radius

        x = self.hitobject.x
        y = self.hitobject.y
        corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)

        if self.import_type == 'FULL':
            bpy.ops.mesh.primitive_circle_add(
                fill_type='NGON',
                radius=osu_radius * SCALE_FACTOR * 2,
                location=(corrected_x, corrected_y, corrected_z),
                rotation=(math.radians(90), 0, 0)
            )
            circle = bpy.context.object
        else:
            mesh = bpy.data.meshes.new(f"{self.global_index:03d}_circle_{self.hitobject.time}_mesh")
            mesh.from_pydata([(0, 0, 0)], [], [])
            mesh.update()
            circle = bpy.data.objects.new(f"{self.global_index:03d}_circle_{self.hitobject.time}", mesh)
            circle.location = (corrected_x, corrected_y, corrected_z)

            create_geometry_nodes_modifier(circle, "circle")

        circle.name = f"{self.global_index:03d}_circle_{self.hitobject.time}"
        return circle

    def animate_object(self, circle):
        approach_rate = self.config.adjusted_ar
        preempt_frames = self.config.data_manager.preempt_frames
        osu_radius = self.config.osu_radius

        start_frame = int(self.hitobject.start_frame)
        end_frame = int(start_frame + 1)
        early_start_frame = int(start_frame - preempt_frames)

        frame_values, fixed_values = get_keyframe_values(
            self.hitobject,
            'circle',
            self.import_type,
            start_frame,
            end_frame,
            early_start_frame,
            approach_rate,
            osu_radius
        )

        attributes = {
            "show": 'BOOLEAN',
            "was_hit": 'BOOLEAN',
            "ar": 'FLOAT',
            "cs": 'FLOAT',
            "combo": 'INT',
            "combo_color_idx": 'INT',
            "combo_color": 'FLOAT_VECTOR'
        }

        if self.hitobject.combo_number is not None:
            fixed_values['combo'] = self.hitobject.combo_number
            fixed_values['combo_color'] = self.hitobject.combo_color
            fixed_values['combo_color_idx'] = self.hitobject.combo_color_idx

        if self.import_type == 'FULL':
            circle.hide_viewport = True
            circle.hide_render = True
            circle.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame - 1))
            circle.keyframe_insert(data_path="hide_render", frame=int(early_start_frame - 1))

            circle.hide_viewport = False
            circle.hide_render = False
            circle.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame))
            circle.keyframe_insert(data_path="hide_render", frame=int(early_start_frame))

            circle.hide_viewport = True
            circle.hide_render = True
            circle.keyframe_insert(data_path="hide_viewport", frame=int(end_frame))
            circle.keyframe_insert(data_path="hide_render", frame=int(end_frame))
        else:
            set_modifier_inputs_with_keyframes(circle, attributes, frame_values, fixed_values)
