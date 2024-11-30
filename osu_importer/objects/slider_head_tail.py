# osu_importer/objects/slider_head_tail.py

import bpy
import math
from osu_importer.utils.utils import timeit, get_keyframe_values, tag_imported
from osu_importer.utils.constants import SCALE_FACTOR
from osu_importer.geo_nodes.geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes

class SliderHeadTailCreator:
    def __init__(self, hitobject, position, global_index, slider_heads_tails_collection, settings, data_manager, import_type):
        self.hitobject = hitobject
        self.position = position
        self.global_index = global_index
        self.slider_heads_tails_collection = slider_heads_tails_collection
        self.settings = settings
        self.data_manager = data_manager
        self.import_type = import_type
        self.create_slider_head_tail()

    def create_slider_head_tail(self):
        hitobject = self.hitobject

        if not hasattr(hitobject, 'start_frame') or not hasattr(hitobject, 'end_frame'):
            print(f"HitObject {hitobject} hat keine Attribute 'start_frame' oder 'end_frame'.")
            return

        with timeit(f"Create SliderHeadTail {self.global_index:03d}_head_tail_{hitobject.time}"):
            data_manager = self.data_manager

            approach_rate = data_manager.adjusted_ar
            osu_radius = data_manager.osu_radius
            preempt_frames = data_manager.preempt_frames

            start_frame = int(hitobject.start_frame)
            end_frame = int(hitobject.end_frame)
            early_start_frame = int(start_frame - preempt_frames)

            corrected_x, corrected_y, corrected_z = self.position.x, self.position.y, self.position.z

            if self.import_type == 'FULL':
                bpy.ops.mesh.primitive_circle_add(
                    fill_type='NGON',
                    radius=osu_radius * SCALE_FACTOR * 2,
                    location=(corrected_x, corrected_y, corrected_z),
                    rotation=(math.radians(90), 0, 0)
                )
                head_tail_obj = bpy.context.object

                head_tail_obj.name = f"SliderHeadTail_{self.global_index:03d}_{hitobject.time}"

                tag_imported(head_tail_obj)

                head_tail_obj.hide_viewport = True
                head_tail_obj.hide_render = True
                head_tail_obj.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame - 1))
                head_tail_obj.keyframe_insert(data_path="hide_render", frame=int(early_start_frame - 1))

                head_tail_obj.hide_viewport = False
                head_tail_obj.hide_render = False
                head_tail_obj.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame))
                head_tail_obj.keyframe_insert(data_path="hide_render", frame=int(early_start_frame))

                head_tail_obj.hide_viewport = True
                head_tail_obj.hide_render = True
                head_tail_obj.keyframe_insert(data_path="hide_viewport", frame=int(end_frame))
                head_tail_obj.keyframe_insert(data_path="hide_render", frame=int(end_frame))

                self.slider_heads_tails_collection.objects.link(head_tail_obj)
                if head_tail_obj.users_collection:
                    for col in head_tail_obj.users_collection:
                        if col != self.slider_heads_tails_collection:
                            col.objects.unlink(head_tail_obj)

            else:
                print(f"Unsupported import type '{self.import_type}' for SliderHeadTail.")
                return
