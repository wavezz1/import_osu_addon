# osu_importer/objects/circles.py

import bpy
import math
from osu_importer.utils.utils import map_osu_to_blender, timeit, get_keyframe_values
from osu_importer.utils.constants import SCALE_FACTOR
from osu_importer.geo_nodes.geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes
from osu_importer.osu_data_manager import OsuDataManager

class CircleCreator:
    def __init__(self, hitobject, global_index, circles_collection, settings, data_manager: OsuDataManager,
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
            audio_lead_in_frames = data_manager.audio_lead_in_frames
            osu_radius = data_manager.osu_radius

            # Verwenden der vorab berechneten Frames
            start_frame = int(self.hitobject.start_frame)
            end_frame = int(start_frame + 1)  # Kreise haben eine Dauer von 1 Frame
            early_start_frame = int(start_frame - preempt_frames)

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
            elif self.import_type == 'BASE':
                mesh = bpy.data.meshes.new(f"{self.global_index:03d}_circle_{self.hitobject.time}_mesh")
                mesh.from_pydata([ (0, 0, 0) ], [], [])
                mesh.update()

                circle = bpy.data.objects.new(f"{self.global_index:03d}_circle_{self.hitobject.time}", mesh)
                circle.location = (corrected_x, corrected_y, corrected_z)

            circle.name = f"{self.global_index:03d}_circle_{self.hitobject.time}"

            circle["ar"] = approach_rate
            circle["cs"] = osu_radius * SCALE_FACTOR

            self.circles_collection.objects.link(circle)
            if circle.users_collection:
                for col in circle.users_collection:
                    if col != self.circles_collection:
                        col.objects.unlink(circle)

            if self.import_type == 'BASE':
                create_geometry_nodes_modifier(circle, "circle")

            # Keyframe-Setzungen basierend auf vorab berechneten Frames
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
                "cs": 'FLOAT'
            }

            set_modifier_inputs_with_keyframes(circle, attributes, frame_values, fixed_values)

            if self.import_type == 'FULL':
                # Keyframes für Sichtbarkeit setzen
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
