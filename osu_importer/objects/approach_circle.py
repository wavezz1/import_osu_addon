# osu_importer/objects/approach_circle.py

import bpy
import math
from osu_importer.utils.utils import map_osu_to_blender, timeit, tag_imported
from osu_importer.utils.constants import SCALE_FACTOR
from osu_importer.geo_nodes.geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes
from osu_importer.osu_data_manager import OsuDataManager

class ApproachCircleCreator:
    def __init__(self, hitobject, global_index, approach_circles_collection, config, data_manager, import_type):
        self.hitobject = hitobject
        self.global_index = global_index
        self.approach_circles_collection = approach_circles_collection
        self.config = config
        self.data_manager = data_manager
        self.import_type = import_type
        self.create_approach_circle()

    def create_approach_circle(self):
        hitobject = self.hitobject

        if not (hitobject.hit_type & 1 or hitobject.hit_type & 2):
            print(f"HitObject {hitobject.time} ist kein Circle oder Slider. Approach Circle wird nicht erstellt.")
            return

        if not hasattr(hitobject, 'start_frame') or not hasattr(hitobject, 'end_frame'):
            print(f"HitObject {hitobject.time} hat keine Attribute 'start_frame' oder 'end_frame'.")
            return

        with timeit(f"Create ApproachCircle {self.global_index:03d}_approach_{hitobject.time}"):
            data_manager = self.data_manager

            preempt_frames = data_manager.preempt_frames
            osu_radius = data_manager.osu_radius

            start_frame = hitobject.start_frame
            end_frame = hitobject.end_frame
            early_start_frame = start_frame - preempt_frames

            x, y = hitobject.x, hitobject.y
            corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)

            print(f"Creating Approach Circle for HitObject {hitobject.time} at position ({corrected_x}, {corrected_y}, {corrected_z})")
            print(f"  Start Frame: {start_frame}, Early Start Frame: {early_start_frame}, End Frame: {end_frame}")

            start_scale = 4.0
            end_scale = 1.0

            if self.import_type == 'FULL':
                bpy.ops.curve.primitive_bezier_circle_add(
                    radius=osu_radius * SCALE_FACTOR * 2,
                    enter_editmode=False,
                    align='WORLD',
                    location=(corrected_x, corrected_y, corrected_z),
                    rotation=(math.radians(90), 0.0, 0.0)
                )
                approach_obj = bpy.context.object
                approach_obj.name = f"approach_{hitobject.time}"

                tag_imported(approach_obj)

                bevel_depth = self.config.approach_circle_bevel_depth
                approach_obj.data.bevel_depth = bevel_depth

                bevel_resolution = self.config.approach_circle_bevel_resolution
                approach_obj.data.bevel_resolution = bevel_resolution

                self.approach_circles_collection.objects.link(approach_obj)
                if approach_obj.users_collection:
                    for col in approach_obj.users_collection:
                        if col != self.approach_circles_collection:
                            col.objects.unlink(approach_obj)

                approach_obj.scale = (start_scale, start_scale, start_scale)
                approach_obj.keyframe_insert(data_path="scale", frame=int(early_start_frame))
                approach_obj.scale = (end_scale, end_scale, end_scale)
                approach_obj.keyframe_insert(data_path="scale", frame=int(start_frame))

                approach_obj.hide_viewport = True
                approach_obj.hide_render = True
                approach_obj.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame - 1))
                approach_obj.keyframe_insert(data_path="hide_render", frame=int(early_start_frame - 1))

                approach_obj.hide_viewport = False
                approach_obj.hide_render = False
                approach_obj.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame))
                approach_obj.keyframe_insert(data_path="hide_render", frame=int(early_start_frame))

                approach_obj.hide_viewport = True
                approach_obj.hide_render = True
                approach_obj.keyframe_insert(data_path="hide_viewport", frame=int(start_frame))
                approach_obj.keyframe_insert(data_path="hide_render", frame=int(start_frame))

                print(f"  Approach Circle '{approach_obj.name}' created with bevel_depth={bevel_depth}, bevel_resolution={bevel_resolution}")

            elif self.import_type == 'BASE':
                mesh = bpy.data.meshes.new(f"approach_{hitobject.time}_mesh")
                mesh.from_pydata([ (0, 0, 0) ], [], [])
                mesh.update()

                approach_obj = bpy.data.objects.new(f"approach_{hitobject.time}", mesh)
                approach_obj.location = (corrected_x, corrected_y, corrected_z)

                tag_imported(approach_obj)

                self.approach_circles_collection.objects.link(approach_obj)
                if approach_obj.users_collection:
                    for col in approach_obj.users_collection:
                        if col != self.approach_circles_collection:
                            col.objects.unlink(approach_obj)

                create_geometry_nodes_modifier(approach_obj, "approach_circle")

                frame_values = {
                    "show": [
                        (early_start_frame - 1, False),
                        (early_start_frame, True),
                        (start_frame, False),
                    ],
                    "scale": [
                        (early_start_frame, start_scale),
                        (start_frame, end_scale),
                    ]
                }
                fixed_values = {"cs": osu_radius * SCALE_FACTOR}

                set_modifier_inputs_with_keyframes(approach_obj, {
                    "show": 'BOOLEAN',
                    "scale": 'FLOAT',
                    "cs": 'FLOAT',
                }, frame_values, fixed_values)

                print(f"Approach Circle '{approach_obj.name}' created with Geometry Nodes Modifier")
