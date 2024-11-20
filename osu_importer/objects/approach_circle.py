# osu_importer/objects/approach_circle.py

import bpy
import math
from osu_importer.utils.utils import map_osu_to_blender, timeit
from osu_importer.utils.constants import SCALE_FACTOR
from osu_importer.geo_nodes.geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes
from osu_importer.osu_data_manager import OsuDataManager

class ApproachCircleCreator:
    def __init__(self, hitobject, global_index, approach_circles_collection, settings, data_manager: OsuDataManager, import_type):
        self.hitobject = hitobject
        self.global_index = global_index
        self.approach_circles_collection = approach_circles_collection
        self.settings = settings
        self.data_manager = data_manager
        self.import_type = import_type
        self.create_approach_circle()

    def create_approach_circle(self):
        hitobject = self.hitobject

        # Nur Kreise und Slider Heads verarbeiten
        if not (hitobject.hit_type & 1 or hitobject.hit_type & 2):
            return

        # Sicherstellen, dass hitobject.frame existiert
        if not hasattr(hitobject, 'frame') or hitobject.frame is None:
            print(f"HitObject {hitobject} hat kein Attribut 'frame'.")
            return

        with timeit(f"Erstellen von ApproachCircle {self.global_index:03d}_approach_{hitobject.time}"):
            data_manager = self.data_manager

            approach_rate = data_manager.adjusted_ar
            preempt_frames = data_manager.preempt_frames
            osu_radius = data_manager.osu_radius

            start_frame = hitobject.frame
            early_start_frame = start_frame - preempt_frames

            corrected_x, corrected_y, corrected_z = map_osu_to_blender(hitobject.x, hitobject.y)

            if self.import_type == 'FULL':
                # Erstellen eines Mesh-Circles
                bpy.ops.mesh.primitive_circle_add(
                    fill_type='NOTHING',
                    radius=osu_radius * SCALE_FACTOR * 2,
                    location=(corrected_x, corrected_y, corrected_z),
                    rotation=(math.radians(90), 0, 0)
                )
                approach_obj = bpy.context.object
                approach_obj.name = f"{self.global_index:03d}_approach_{hitobject.time}"

                # Verbinden mit der Approach Circles Collection
                self.approach_circles_collection.objects.link(approach_obj)
                if approach_obj.users_collection:
                    for col in approach_obj.users_collection:
                        if col != self.approach_circles_collection:
                            col.objects.unlink(approach_obj)

                # Animieren der Skalierung
                approach_obj.scale = (2.0, 2.0, 2.0)  # Start Skalierung
                approach_obj.keyframe_insert(data_path="scale", frame=int(early_start_frame))
                approach_obj.scale = (1.0, 1.0, 1.0)  # End Skalierung
                approach_obj.keyframe_insert(data_path="scale", frame=int(start_frame))

                # Animieren der Sichtbarkeit
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

            elif self.import_type == 'BASE':
                # Erstellen eines Mesh-Punkts (Vertex)
                mesh = bpy.data.meshes.new(f"approach_{hitobject.time}_mesh")
                mesh.from_pydata([ (0, 0, 0) ], [], [])  # Einfacher Punkt
                mesh.update()

                approach_obj = bpy.data.objects.new(f"approach_{hitobject.time}", mesh)
                approach_obj.location = (corrected_x, corrected_y, corrected_z)

                self.approach_circles_collection.objects.link(approach_obj)
                if approach_obj.users_collection:
                    for col in approach_obj.users_collection:
                        if col != self.approach_circles_collection:
                            col.objects.unlink(approach_obj)

                create_geometry_nodes_modifier(approach_obj, "approach_circle")

                # Definieren der Attribute und Setzen der Keyframes
                attributes = {
                    "show": 'BOOLEAN',
                    "scale": 'FLOAT',
                }
                frame_values = {
                    "show": [
                        (early_start_frame, True),  # show = True
                        (start_frame, False),       # show = False
                    ],
                    "scale": [
                        (early_start_frame, 2.0),  # Start Skalierung
                        (start_frame, 1.0),        # End Skalierung
                    ]
                }
                fixed_values = {}

                set_modifier_inputs_with_keyframes(approach_obj, attributes, frame_values, fixed_values)
