# osu_importer/objects/slider_head_tail.py

import bpy
import math
from osu_importer.utils.utils import map_osu_to_blender, timeit
from osu_importer.utils.constants import SCALE_FACTOR
from osu_importer.geo_nodes.geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes

class SliderHeadTailCreator:
    def __init__(self, hitobject, position, global_index, slider_heads_tails_collection, settings, data_manager, import_type):
        self.hitobject = hitobject
        self.position = position  # (x, y, z)
        self.global_index = global_index
        self.slider_heads_tails_collection = slider_heads_tails_collection
        self.settings = settings
        self.data_manager = data_manager
        self.import_type = import_type
        self.create_slider_head_tail()

    def create_slider_head_tail(self):
        hitobject = self.hitobject
        position = self.position

        with timeit(f"Creating SliderHeadTail {self.global_index:03d}_head_tail"):
            approach_rate = self.data_manager.adjusted_ar
            preempt_frames = self.data_manager.preempt_frames
            osu_radius = self.data_manager.osu_radius

            if self.import_type == 'FULL':
                # Erstellen eines Mesh-Circles
                bpy.ops.mesh.primitive_circle_add(
                    fill_type='NGON',
                    radius=osu_radius * SCALE_FACTOR,
                    location=position,
                    rotation=(math.radians(90), 0, 0)
                )
                head_tail_obj = bpy.context.object
                head_tail_obj.name = f"SliderHeadTail_{self.global_index:03d}_{hitobject.time}"

                # Hinzufügen zur Collection
                self.slider_heads_tails_collection.objects.link(head_tail_obj)
                if head_tail_obj.users_collection:
                    for col in head_tail_obj.users_collection:
                        if col != self.slider_heads_tails_collection:
                            col.objects.unlink(head_tail_obj)

                # Animieren der Skalierung
                head_tail_obj.scale = (2.0, 2.0, 2.0)
                head_tail_obj.keyframe_insert(data_path="scale", frame=int(hitobject.frame - preempt_frames))
                head_tail_obj.scale = (1.0, 1.0, 1.0)
                head_tail_obj.keyframe_insert(data_path="scale", frame=int(hitobject.frame))

                # Animieren der Sichtbarkeit
                head_tail_obj.hide_viewport = True
                head_tail_obj.hide_render = True
                head_tail_obj.keyframe_insert(data_path="hide_viewport", frame=int(hitobject.frame - preempt_frames - 1))
                head_tail_obj.keyframe_insert(data_path="hide_render", frame=int(hitobject.frame - preempt_frames - 1))

                head_tail_obj.hide_viewport = False
                head_tail_obj.hide_render = False
                head_tail_obj.keyframe_insert(data_path="hide_viewport", frame=int(hitobject.frame - preempt_frames))
                head_tail_obj.keyframe_insert(data_path="hide_render", frame=int(hitobject.frame - preempt_frames))

                head_tail_obj.hide_viewport = True
                head_tail_obj.hide_render = True
                head_tail_obj.keyframe_insert(data_path="hide_viewport", frame=int(hitobject.frame))
                head_tail_obj.keyframe_insert(data_path="hide_render", frame=int(hitobject.frame))
