# osu_importer/objects/slider_head_tail.py

import bpy
import math
from osu_importer.utils.utils import map_osu_to_blender, timeit, get_keyframe_values
from osu_importer.utils.constants import SCALE_FACTOR
from osu_importer.geo_nodes.geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes
from osu_importer.osu_data_manager import OsuDataManager
from osu_importer.parsers.hitobjects import HitObject


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

        # Überprüfen, ob das HitObject die notwendigen Frame-Attribute besitzt
        if not hasattr(hitobject, 'start_frame') or not hasattr(hitobject, 'end_frame'):
            print(f"HitObject {hitobject} hat keine Attribute 'start_frame' oder 'end_frame'.")
            return

        with timeit(f"Erstellen von SliderHeadTail {self.global_index:03d}_head_tail_{hitobject.time}"):
            data_manager = self.data_manager

            approach_rate = data_manager.adjusted_ar
            osu_radius = data_manager.osu_radius
            preempt_frames = data_manager.preempt_frames

            start_frame = int(hitobject.start_frame)
            end_frame = int(hitobject.end_frame)
            early_start_frame = int(start_frame - preempt_frames)

            corrected_x, corrected_y, corrected_z = self.position.x, self.position.y, self.position.z

            if self.import_type == 'FULL':
                # Erstellen eines gefüllten Kreises für den Slider-Head/Tail
                bpy.ops.mesh.primitive_circle_add(
                    fill_type='NGON',
                    radius=osu_radius * SCALE_FACTOR * 2,
                    location=(corrected_x, corrected_y, corrected_z),
                    rotation=(math.radians(90), 0, 0)
                )
                head_tail_obj = bpy.context.object
            elif self.import_type == 'BASE':
                # Erstellen eines einfachen Mesh-Objekts für den Slider-Head/Tail
                mesh = bpy.data.meshes.new(f"SliderHeadTail_{self.global_index:03d}_{hitobject.time}_mesh")
                mesh.from_pydata([ (0, 0, 0) ], [], [])
                mesh.update()

                head_tail_obj = bpy.data.objects.new(f"SliderHeadTail_{self.global_index:03d}_{hitobject.time}", mesh)
                head_tail_obj.location = (corrected_x, corrected_y, corrected_z)
            else:
                print(f"Unsupported import type '{self.import_type}' for SliderHeadTail.")
                return

            head_tail_obj.name = f"SliderHeadTail_{self.global_index:03d}_{hitobject.time}"

            # Hinzufügen zur entsprechenden Collection und Entfernen aus anderen Collections
            self.slider_heads_tails_collection.objects.link(head_tail_obj)
            if head_tail_obj.users_collection:
                for col in head_tail_obj.users_collection:
                    if col != self.slider_heads_tails_collection:
                        col.objects.unlink(head_tail_obj)

            if self.import_type == 'BASE':
                # Hinzufügen des Geometry Nodes Modifiers
                create_geometry_nodes_modifier(head_tail_obj, "slider_head_tail")

            # Setzen von Keyframes basierend auf den vorab berechneten Frames
            frame_values, fixed_values = get_keyframe_values(
                self.hitobject,
                'slider_head_tail',
                self.import_type,
                start_frame,
                end_frame,
                early_start_frame,
                approach_rate,
                osu_radius,
                extra_params={}
            )

            attributes = {
                "show": 'BOOLEAN',
                "scale": 'FLOAT',
                "cs": 'FLOAT',
            }
            fixed_values = {"cs": osu_radius * SCALE_FACTOR}

            set_modifier_inputs_with_keyframes(head_tail_obj, attributes, frame_values, fixed_values)

            if self.import_type == 'FULL':
                # Keyframes für Sichtbarkeit setzen
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
