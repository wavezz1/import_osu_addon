# slider.py

import bpy
import math
from mathutils import Vector
from .constants import SCALE_FACTOR
from .utils import map_osu_to_blender, get_ms_per_frame
from .geometry_nodes import create_geometry_nodes_modifier_slider
from .osu_replay_data_manager import OsuReplayDataManager
from .hitobjects import HitObject
from .exec import connect_attributes_with_drivers


class SliderCreator:
    def __init__(self, hitobject: HitObject, global_index: int, sliders_collection, settings: dict,
                 data_manager: OsuReplayDataManager):
        self.hitobject = hitobject
        self.global_index = global_index
        self.sliders_collection = sliders_collection
        self.settings = settings
        self.data_manager = data_manager
        self.create_slider()

    def vector_lerp(self, p0, p1, t):
        return Vector(p0).lerp(Vector(p1), t)

    def create_perfect_circle_spline(self, points):
        if len(points) != 3:
            return points

        p1, p2, p3 = Vector((points[0][0], points[0][1], 0)), Vector((points[1][0], points[1][1], 0)), Vector(
            (points[2][0], points[2][1], 0))

        def circle_center(p1, p2, p3):
            temp, temp2 = p2 - p1, p3 - p1
            d = 2 * (temp.x * temp2.y - temp.y * temp2.x)
            if d == 0:
                return None
            center = p1 + Vector(((temp2.y * temp.length_squared - temp.y * temp2.length_squared) / d,
                                  (temp.x * temp2.length_squared - temp2.x * temp.length_squared) / d, 0))
            return center

        center = circle_center(p1, p2, p3)
        if center is None:
            return [p1, p3]

        radius = (p1 - center).length
        angles = [(p - center).to_2d().angle_signed(Vector((1, 0))) for p in (p1, p2, p3)]
        for i in range(1, len(angles)):
            while angles[i] - angles[i - 1] > math.pi:
                angles[i] -= 2 * math.pi
            while angles[i] - angles[i - 1] < -math.pi:
                angles[i] += 2 * math.pi

        return [center + Vector((math.cos(a) * radius, math.sin(a) * radius, 0)) for a in
                [angles[0] + t * (angles[2] - angles[0]) for t in [i / 49 for i in range(50)]]]

    def create_catmull_rom_spline(self, points, tension=0.5):
        spline_points = []
        n = len(points)
        if n < 2:
            return points
        for i in range(n - 1):
            p0, p1, p2, p3 = Vector(points[i - 1]) if i > 0 else Vector(points[i]), Vector(points[i]), Vector(
                points[i + 1]), Vector(points[i + 2]) if i < n - 2 else Vector(points[i + 1])
            for t in [j / 10.0 for j in range(11)]:
                t2, t3 = t * t, t * t * t
                m1, m2 = (1 - tension) * (p2 - p0) * 0.5, (1 - tension) * (p3 - p1) * 0.5
                spline_points.append(
                    (2 * t3 - 3 * t2 + 1) * p1 + (t3 - 2 * t2 + t) * m1 + (-2 * t3 + 3 * t2) * p2 + (t3 - t2) * m2)
        return spline_points

    def create_linear_spline(self, points):
        return points

    def create_bezier_spline(self, points):
        bezier_points = []
        n = len(points)
        if n == 2:
            p0, p1 = Vector(points[0]), Vector(points[1])
            bezier_points.extend([self.vector_lerp(p0, p1, t) for t in [j / 10.0 for j in range(11)]])
            return bezier_points

        if n == 3:
            p0, p1, p2 = Vector(points[0]), Vector(points[1]), Vector(points[2])
            bezier_points.extend(
                [((1 - t) ** 2 * p0) + (2 * (1 - t) * t * p1) + (t ** 2 * p2) for t in [j / 10.0 for j in range(11)]])
            return bezier_points

        if n >= 4:
            for i in range(0, n - 3, 3):
                p0, p1, p2, p3 = Vector(points[i]), Vector(points[i + 1]), Vector(points[i + 2]), Vector(points[i + 3])
                bezier_points.extend(
                    [((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3) for t in
                     [j / 10.0 for j in range(11)]])
        return bezier_points

    def create_slider(self):
        approach_rate = self.data_manager.calculate_adjusted_ar()
        preempt_frames = self.data_manager.calculate_preempt_time(approach_rate) / get_ms_per_frame()
        circle_size, osu_radius = self.data_manager.calculate_adjusted_cs(), (
                                                                                         54.4 - 4.48 * self.data_manager.calculate_adjusted_cs()) / 2
        audio_lead_in_frames = self.data_manager.beatmap_info["audio_lead_in"] / get_ms_per_frame()

        start_frame = (self.hitobject.time / self.settings.get('speed_multiplier',
                                                               1.0)) / get_ms_per_frame() + audio_lead_in_frames
        early_start_frame = start_frame - preempt_frames

        if self.hitobject.extras:
            slider_data = self.hitobject.extras[0].split('|')
            if len(slider_data) > 1:
                slider_type, slider_control_points = slider_data[0], slider_data[1:]
                points = [(self.hitobject.x, self.hitobject.y)] + [(float(px), float(py)) for point in
                                                                   slider_control_points for px, py in
                                                                   [point.split(':')]]

                if slider_type == "L":
                    points = self.create_linear_spline(points)
                    curve_type = 'POLY'
                elif slider_type == "P":
                    points = self.create_perfect_circle_spline(points)
                    curve_type = 'POLY'
                elif slider_type == "B":
                    points = self.create_bezier_spline(points)
                    curve_type = 'BEZIER'
                elif slider_type == "C":
                    points = self.create_catmull_rom_spline(points, tension=0.0)
                    curve_type = 'NURBS'
                else:
                    points, curve_type = self.create_linear_spline(points), 'POLY'

                curve_data = bpy.data.curves.new(
                    name=f"{self.global_index:03d}_slider_{self.hitobject.time}_{slider_type}_curve", type='CURVE')
                curve_data.dimensions = '3D'

                if curve_type == 'POLY':
                    spline = curve_data.splines.new('POLY')
                    spline.points.add(len(points) - 1)
                    for i, point in enumerate(points):
                        corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                        spline.points[i].co = (corrected_x, corrected_y, corrected_z, 1)
                elif curve_type == 'BEZIER':
                    spline = curve_data.splines.new('BEZIER')
                    spline.bezier_points.add(len(points) - 1)
                    for i, point in enumerate(points):
                        corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                        bp = spline.bezier_points[i]
                        bp.co = (corrected_x, corrected_y, corrected_z)
                        bp.handle_left_type = 'AUTO'
                        bp.handle_right_type = 'AUTO'
                elif curve_type == 'NURBS':
                    spline = curve_data.splines.new('NURBS')
                    spline.points.add(len(points) - 1)
                    for i, point in enumerate(points):
                        corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                        spline.points[i].co = (corrected_x, corrected_y, corrected_z, 1)
                    spline.order_u = 3

                slider = bpy.data.objects.new(f"{self.global_index:03d}_slider_{self.hitobject.time}_{slider_type}",
                                              curve_data)
                slider["ar"], slider["cs"] = approach_rate, osu_radius * SCALE_FACTOR

        slider_duration_ms = self.data_manager.calculate_slider_duration(self.hitobject)
        end_frame = (self.hitobject.time + slider_duration_ms) / self.settings.get('speed_multiplier',
                                                                                   1.0) / get_ms_per_frame()

        slider["was_hit"] = self.hitobject.was_hit
        slider.keyframe_insert(data_path='["was_hit"]', frame=start_frame)

        slider["was_completed"] = True
        slider.keyframe_insert(data_path='["was_completed"]', frame=end_frame - 1)

        slider["show"] = True
        slider.keyframe_insert(data_path='["show"]', frame=early_start_frame)

        slider["slider_duration_ms"] = slider_duration_ms
        slider["slider_duration_frames"] = slider_duration_ms / (1000 / bpy.context.scene.render.fps)

        self.sliders_collection.objects.link(slider)
        if slider.users_collection:
            for col in slider.users_collection:
                if col != self.sliders_collection:
                    col.objects.unlink(slider)

        # Geometry Nodes Modifier hinzufügen
        node_group_name = f"Geometry Nodes Slider {self.global_index:03d}"
        create_geometry_nodes_modifier_slider(slider, node_group_name)

        # Fahrer (Drivers) verbinden
        connect_attributes_with_drivers(slider, {
            "show": 'BOOLEAN',
            "slider_duration": 'FLOAT',
            "slider_duration_frames": 'FLOAT',
            "ar": 'FLOAT',
            "cs": 'FLOAT',
            "was_hit": 'BOOLEAN',
            "was_completed": 'BOOLEAN'
        })