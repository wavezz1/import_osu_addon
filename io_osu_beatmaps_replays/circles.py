# circles.py

import bpy
import math
from .utils import map_osu_to_blender, get_ms_per_frame
from .geometry_nodes import create_geometry_nodes_modifier_circle
from .info_parser import OsuParser


class CircleCreator:
    def __init__(self, hitobject, global_index, circles_collection, settings, osu_parser: OsuParser):
        self.hitobject = hitobject
        self.global_index = global_index
        self.circles_collection = circles_collection
        self.settings = settings
        self.osu_parser = osu_parser
        self.create_circle()

    def create_circle(self):
        approach_rate = float(self.osu_parser.difficulty_settings.get("ApproachRate", 5.0))
        circle_size = float(self.osu_parser.difficulty_settings.get("CircleSize", 5.0))

        x = self.hitobject.x
        y = self.hitobject.y
        time_ms = self.hitobject.time
        speed_multiplier = self.settings.get('speed_multiplier', 1.0)
        start_frame = ((time_ms / speed_multiplier) / get_ms_per_frame())

        # Berechne die early_frames abhängig von der AR
        early_frames = self.calculate_early_frames(approach_rate, speed_multiplier)
        early_start_frame = start_frame - early_frames

        corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)
        bpy.ops.mesh.primitive_circle_add(
            fill_type='NGON',
            radius=0.5,
            location=(corrected_x, corrected_y, corrected_z),
            rotation=(math.radians(90), 0, 0)
        )
        circle = bpy.context.object
        circle.name = f"{self.global_index:03d}_circle_{time_ms}"

        # Füge "ar" und "cs" als Eigenschaften zum Kreis hinzu
        circle["ar"] = approach_rate
        circle["cs"] = circle_size

        # Setzen der Keyframes und Eigenschaften
        circle["show"] = False
        circle.keyframe_insert(data_path='["show"]', frame=(early_start_frame - 1))
        circle["show"] = True
        circle.keyframe_insert(data_path='["show"]', frame=early_start_frame)
        circle["show"] = False
        circle.keyframe_insert(data_path='["show"]', frame=(early_start_frame + 1))

        self.circles_collection.objects.link(circle)
        if circle.users_collection:
            for col in circle.users_collection:
                if col != self.circles_collection:
                    col.objects.unlink(circle)

        create_geometry_nodes_modifier_circle(circle, circle.name)

    def calculate_early_frames(self, approach_rate, speed_multiplier):
        ar = approach_rate * speed_multiplier
        if ar <= 5:
            early_frames = 1200 + (600 * (5 - ar))
        else:
            early_frames = 1200 - (750 * (ar - 5))

        early_frames /= get_ms_per_frame()

        return early_frames
