# slider.py

import bpy
import math
from mathutils import Vector
from .constants import SCALE_FACTOR
from .utils import map_osu_to_blender, get_ms_per_frame
from .geometry_nodes import create_geometry_nodes_modifier_slider
from .osu_replay_data_manager import OsuReplayDataManager
from .hitobjects import HitObject


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
        p0 = Vector(p0)
        p1 = Vector(p1)
        return p0.lerp(p1, t)

    def create_perfect_circle_spline(self, points):
        if len(points) != 3:
            print("Perfekter Slider erfordert genau 3 Punkte.")
            return points  # Fallback auf Originalpunkte

        p1, p2, p3 = Vector(points[0]), Vector(points[1]), Vector(points[2])

        # Berechnung des Kreismittelpunktes
        def circle_center(p1, p2, p3):
            temp = p2 - p1
            temp2 = p3 - p1

            a = temp.length_squared
            b = temp.dot(temp2)
            c = temp2.length_squared
            d = 2 * (temp.x * temp2.y - temp.y * temp2.x)

            if d == 0:
                print("Punkte sind kolinear, können keinen Kreis bilden.")
                return None

            center = p1 + Vector((
                (temp2.y * a - temp.y * c) / d,
                (temp.x * c - temp2.x * a) / d,
                0
            ))
            return center

        center = circle_center(p1, p2, p3)
        if center is None:
            return [p1, p3]  # Fallback auf eine Linie zwischen erstem und letztem Punkt

        radius = (p1 - center).length

        # Berechnung der Winkel
        angle1 = (p1 - center).to_2d().angle_signed(Vector((1, 0)))
        angle2 = (p2 - center).to_2d().angle_signed(Vector((1, 0)))
        angle3 = (p3 - center).to_2d().angle_signed(Vector((1, 0)))

        # Korrigiere Winkel für Kontinuität
        angles = [angle1, angle2, angle3]
        for i in range(1, len(angles)):
            while angles[i] - angles[i - 1] > math.pi:
                angles[i] -= 2 * math.pi
            while angles[i] - angles[i - 1] < -math.pi:
                angles[i] += 2 * math.pi

        # Erstellen des Kreisbogens
        num_points = 50  # Anzahl der Punkte für die Kurve
        spline_points = []
        for t in [i / (num_points - 1) for i in range(num_points)]:
            angle = angles[0] + t * (angles[2] - angles[0])
            point = center + Vector((math.cos(angle) * radius, math.sin(angle) * radius, 0))
            spline_points.append(point)

        return spline_points

    def create_catmull_rom_spline(self, points, tension=0.5):
        spline_points = []
        n = len(points)
        if n < 2:
            return points  # Nicht genug Punkte für eine Kurve

        for i in range(n - 1):
            p0 = Vector(points[i - 1]) if i > 0 else Vector(points[i])
            p1 = Vector(points[i])
            p2 = Vector(points[i + 1])
            p3 = Vector(points[i + 2]) if i < n - 2 else Vector(points[i + 1])

            for t in [j / 10.0 for j in range(11)]:
                t2 = t * t
                t3 = t2 * t
                m1 = (1 - tension) * (p2 - p0) * 0.5
                m2 = (1 - tension) * (p3 - p1) * 0.5
                spline_point = (2 * t3 - 3 * t2 + 1) * p1 + (t3 - 2 * t2 + t) * m1 + (-2 * t3 + 3 * t2) * p2 + (
                            t3 - t2) * m2
                spline_points.append(spline_point)

        return spline_points

    def create_linear_spline(self, points):
        return points

    def create_bezier_spline(self, points):
        bezier_points = []
        n = len(points)

        if n == 2:
            p0, p1 = Vector(points[0]), Vector(points[1])
            for t in [j / 10.0 for j in range(11)]:
                bezier_point = self.vector_lerp(p0, p1, t)
                bezier_points.append(bezier_point)
            return bezier_points

        if n == 3:
            p0, p1, p2 = Vector(points[0]), Vector(points[1]), Vector(points[2])
            for t in [j / 10.0 for j in range(11)]:
                bezier_point = ((1 - t) ** 2 * p0) + (2 * (1 - t) * t * p1) + (t ** 2 * p2)
                bezier_points.append(bezier_point)
            return bezier_points

        if n >= 4:
            for i in range(0, n - 3, 3):
                p0, p1, p2, p3 = Vector(points[i]), Vector(points[i + 1]), Vector(points[i + 2]), Vector(points[i + 3])
                for t in [j / 10.0 for j in range(11)]:
                    bezier_point = ((1 - t) ** 3 * p0 +
                                    3 * (1 - t) ** 2 * t * p1 +
                                    3 * (1 - t) * t ** 2 * p2 +
                                    t ** 3 * p3)
                    bezier_points.append(bezier_point)

        return bezier_points

    def create_slider(self):
        # Hole Werte über data_manager
        approach_rate = self.data_manager.calculate_approach_rate()
        preempt_ms = self.data_manager.calculate_preempt_time(approach_rate)
        preempt_frames = preempt_ms / get_ms_per_frame()

        circle_size = self.data_manager.beatmap_info["circle_size"]
        audio_lead_in_frames = self.data_manager.beatmap_info["audio_lead_in"] / get_ms_per_frame()
        slider_multiplier = float(self.data_manager.osu_parser.difficulty_settings.get("SliderMultiplier", 1.4))
        timing_points = self.data_manager.osu_parser.timing_points

        osu_radius = (54.4 - 4.48 * circle_size) / 2

        x = self.hitobject.x
        y = self.hitobject.y
        time_ms = self.hitobject.time
        speed_multiplier = self.settings.get('speed_multiplier', 1.0)
        start_frame = ((time_ms / speed_multiplier) / get_ms_per_frame()) + audio_lead_in_frames
        early_start_frame = start_frame - preempt_frames

        if self.hitobject.extras:
            slider_data = self.hitobject.extras[0].split('|')
            if len(slider_data) > 1:
                slider_type = slider_data[0]
                slider_control_points = slider_data[1:]
                points = [(self.hitobject.x, self.hitobject.y)]
                for point in slider_control_points:
                    if ':' in point:
                        px_str, py_str = point.split(':')
                        px, py = float(px_str), float(py_str)
                        points.append((px, py))

                # Behandlung der Slider-Typen
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
                    print(f"Unbekannter Slider-Typ: {slider_type}. Verwende lineare Spline.")
                    points = self.create_linear_spline(points)
                    curve_type = 'POLY'

                # Kurve erstellen
                curve_data = bpy.data.curves.new(name=f"{self.global_index:03d}_slider_{time_ms}_{slider_type}_curve",
                                                 type='CURVE')
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
                        bp = spline.bezier_points[i]
                        corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                        bp.co = (corrected_x, corrected_y, corrected_z)
                        bp.handle_left_type = 'AUTO'
                        bp.handle_right_type = 'AUTO'
                elif curve_type == 'NURBS':
                    spline = curve_data.splines.new('NURBS')
                    spline.points.add(len(points) - 1)
                    for i, point in enumerate(points):
                        corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                        spline.points[i].co = (corrected_x, corrected_y, corrected_z, 1)
                    spline.order_u = 3  # Ordnung der NURBS-Kurve

                slider = bpy.data.objects.new(f"{self.global_index:03d}_slider_{time_ms}_{slider_type}", curve_data)
                slider["ar"] = approach_rate
                slider["cs"] = osu_radius * SCALE_FACTOR

        repeat_count = int(self.hitobject.extras[1]) if len(self.hitobject.extras) > 1 else 1
        pixel_length = float(self.hitobject.extras[2]) if len(self.hitobject.extras) > 2 else 100

        slider_duration_ms = self.data_manager.calculate_slider_duration(self.hitobject)
        end_time_ms = time_ms + slider_duration_ms
        end_frame = ((end_time_ms / speed_multiplier) / get_ms_per_frame())

        slider["was_hit"] = False
        slider.keyframe_insert(data_path='["was_hit"]', frame=start_frame - 1)

        slider["was_hit"] = self.hitobject.was_hit
        slider.keyframe_insert(data_path='["was_hit"]', frame=start_frame)

        # Initialisiere 'was_completed' auf False
        slider["was_completed"] = False

        # Berechne den Frame vor dem Ende des Sliders
        before_end_frame = end_frame - 1

        # Prüfe, ob der Slider nur einen Frame dauert oder weniger
        if before_end_frame <= start_frame:
            # Fallback für Slider mit sehr kurzer Dauer
            before_end_frame = start_frame
            end_frame_adjusted = start_frame + 1
        else:
            end_frame_adjusted = end_frame

        # Keyframe 'was_completed' auf False vor dem Ende des Sliders
        slider.keyframe_insert(data_path='["was_completed"]', frame=before_end_frame)

        # Setze 'was_completed' hartkodiert auf True am Ende des Sliders
        slider["was_completed"] = True
        slider.keyframe_insert(data_path='["was_completed"]', frame=end_frame_adjusted)


        slider["show"] = False
        slider.keyframe_insert(data_path='["show"]', frame=(early_start_frame - 1))

        slider["show"] = True
        slider.keyframe_insert(data_path='["show"]', frame=early_start_frame)

        slider["slider_duration_ms"] = slider_duration_ms

        scene_fps = bpy.context.scene.render.fps
        slider_duration_frames = slider_duration_ms / (1000 / scene_fps)
        slider["slider_duration_frames"] = slider_duration_frames

        self.sliders_collection.objects.link(slider)
        if slider.users_collection:
            for col in slider.users_collection:
                if col != self.sliders_collection:
                    col.objects.unlink(slider)

        create_geometry_nodes_modifier_slider(slider, slider.name)
