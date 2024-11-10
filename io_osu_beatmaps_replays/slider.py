# slider.py

import bpy
import math
from mathutils import Vector
from .constants import SCALE_FACTOR
from .utils import map_osu_to_blender, get_ms_per_frame, evaluate_curve_at_t
from .geometry_nodes import create_geometry_nodes_modifier, connect_attributes_with_drivers
from .osu_replay_data_manager import OsuReplayDataManager
from .hitobjects import HitObject


class SliderCreator:
    def __init__(self, hitobject: HitObject, global_index: int, sliders_collection, slider_balls_collection, settings: dict,
                 data_manager: OsuReplayDataManager):
        self.hitobject = hitobject
        self.global_index = global_index
        self.sliders_collection = sliders_collection
        self.slider_balls_collection = slider_balls_collection
        self.settings = settings
        self.data_manager = data_manager
        self.create_slider()

    def create_slider(self):
        approach_rate = self.data_manager.calculate_adjusted_ar()
        preempt_frames = self.data_manager.calculate_preempt_time(approach_rate) / get_ms_per_frame()
        circle_size = self.data_manager.calculate_adjusted_cs()
        osu_radius = (54.4 - 4.48 * circle_size) / 2
        audio_lead_in_frames = self.data_manager.beatmap_info["audio_lead_in"] / get_ms_per_frame()

        start_frame = (self.hitobject.time / self.settings.get('speed_multiplier', 1.0)) / get_ms_per_frame() + audio_lead_in_frames
        early_start_frame = start_frame - preempt_frames

        if self.hitobject.extras:
            # Extrahiere Slider-Daten korrekt
            curve_data = self.hitobject.extras[0]
            repeat_count = int(self.hitobject.extras[1]) if len(self.hitobject.extras) > 1 else 1
            pixel_length = float(self.hitobject.extras[2]) if len(self.hitobject.extras) > 2 else 100.0

            # Parse curve data
            slider_data = curve_data.split('|')
            slider_type = slider_data[0]
            slider_control_points = slider_data[1:]

            # Erstelle die Liste der Kontrollpunkte, beginnend mit der Startposition
            points = [(self.hitobject.x, self.hitobject.y)]
            for cp in slider_control_points:
                x_str, y_str = cp.split(':')
                x, y = float(x_str), float(y_str)
                points.append((x, y))

            # Verarbeite Ankerpunkte (doppelte Punkte)
            segments = []
            current_segment = [points[0]]
            for i in range(1, len(points)):
                if points[i] == points[i - 1]:
                    segments.append(current_segment)
                    current_segment = [points[i]]
                else:
                    current_segment.append(points[i])
            if current_segment:
                segments.append(current_segment)

            # Erstelle die Kurve basierend auf dem Slider-Typ
            curve_data = bpy.data.curves.new(
                name=f"{self.global_index:03d}_slider_{self.hitobject.time}_{slider_type}_curve", type='CURVE')
            curve_data.dimensions = '3D'

            if slider_type == "L":
                # Lineare Slider
                for segment in segments:
                    spline = curve_data.splines.new('POLY')
                    spline.points.add(len(segment) - 1)
                    for i, point in enumerate(segment):
                        corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                        spline.points[i].co = (corrected_x, corrected_y, corrected_z, 1)
            elif slider_type == "P":
                # Perfekte Kreis-Slider
                for segment in segments:
                    if len(segment) >= 3:
                        spline_points = self.create_perfect_circle_spline(segment)
                        spline = curve_data.splines.new('POLY')
                        spline.points.add(len(spline_points) - 1)
                        for i, point in enumerate(spline_points):
                            corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                            spline.points[i].co = (corrected_x, corrected_y, corrected_z, 1)
                    else:
                        # Fallback auf lineare Spline
                        spline = curve_data.splines.new('POLY')
                        spline.points.add(len(segment) - 1)
                        for i, point in enumerate(segment):
                            corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                            spline.points[i].co = (corrected_x, corrected_y, corrected_z, 1)
            elif slider_type == "B":
                # Bezier-Kurve evaluieren und POLY-Spline erstellen
                for segment in segments:
                    if len(segment) < 2:
                        continue

                    # Kontrollpunkte extrahieren und konvertieren
                    control_points = []
                    for point in segment:
                        x, y = point
                        corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)
                        control_points.append(Vector((corrected_x, corrected_y, corrected_z)))

                    # Anzahl der Punkte für eine glatte Kurve
                    num_points = 100
                    evaluated_points = []
                    for t in [i / num_points for i in range(num_points + 1)]:
                        point = self.evaluate_bezier_curve(control_points, t)
                        evaluated_points.append(point)

                    # POLY-Spline mit den ausgewerteten Punkten erstellen
                    spline = curve_data.splines.new('POLY')
                    spline.points.add(len(evaluated_points) - 1)
                    for i, point in enumerate(evaluated_points):
                        spline.points[i].co = (point.x, point.y, point.z, 1)
            elif slider_type == "C":
                # Catmull-Rom-Spline erstellen
                for segment in segments:
                    spline_points = self.create_catmull_rom_spline(segment)
                    spline = curve_data.splines.new('POLY')
                    spline.points.add(len(spline_points) - 1)
                    for i, point in enumerate(spline_points):
                        corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                        spline.points[i].co = (corrected_x, corrected_y, corrected_z, 1)
            else:
                # Standardmäßig lineare Spline
                for segment in segments:
                    spline = curve_data.splines.new('POLY')
                    spline.points.add(len(segment) - 1)
                    for i, point in enumerate(segment):
                        corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                        spline.points[i].co = (corrected_x, corrected_y, corrected_z, 1)

            # Erstelle das Slider-Objekt
            slider = bpy.data.objects.new(f"{self.global_index:03d}_slider_{self.hitobject.time}_{slider_type}",
                                          curve_data)

            # Berechne die Slider-Dauer
            slider_duration_ms = self.data_manager.calculate_slider_duration(self.hitobject)
            slider_duration_frames = int(slider_duration_ms / get_ms_per_frame())
            end_frame = (self.hitobject.time + slider_duration_ms) / self.settings.get('speed_multiplier',
                                                                                       1.0) / get_ms_per_frame()
            slider["ar"] = approach_rate
            slider["cs"] = osu_radius * SCALE_FACTOR

            # Keyframes für 'was_hit' und 'was_completed'
            slider["was_hit"] = False
            slider.keyframe_insert(data_path='["was_hit"]', frame=start_frame - 1)
            slider["was_hit"] = self.hitobject.was_hit
            slider.keyframe_insert(data_path='["was_hit"]', frame=start_frame)

            slider["was_completed"] = False
            slider.keyframe_insert(data_path='["was_completed"]', frame=end_frame - 1)
            slider["was_completed"] = self.hitobject.was_completed
            slider.keyframe_insert(data_path='["was_completed"]', frame=end_frame)

            slider["show"] = False
            slider.keyframe_insert(data_path='["show"]', frame=early_start_frame - 1)
            slider["show"] = True
            slider.keyframe_insert(data_path='["show"]', frame=early_start_frame)

            slider["slider_duration_ms"] = slider_duration_ms
            slider["slider_duration_frames"] = slider_duration_ms / (1000 / bpy.context.scene.render.fps)

            # Füge den Slider zu der Collection hinzu
            self.sliders_collection.objects.link(slider)
            if slider.users_collection:
                for col in slider.users_collection:
                    if col != self.sliders_collection:
                        col.objects.unlink(slider)

            # Verbinde Geometry Nodes
            create_geometry_nodes_modifier(slider, "slider")
            connect_attributes_with_drivers(slider, {
                "show": 'BOOLEAN',
                "slider_duration": 'FLOAT',
                "slider_duration_frames": 'FLOAT',
                "ar": 'FLOAT',
                "cs": 'FLOAT',
                "was_hit": 'BOOLEAN',
                "was_completed": 'BOOLEAN'
            })

            # Erstelle Slider-Ball und Slider-Ticks
            if self.settings.get('import_slider_balls', False):
                self.create_slider_ball(slider, start_frame, slider_duration_frames, repeat_count)
            if self.settings.get('import_slider_ticks', False):
                self.create_slider_ticks(slider, curve_data, slider_duration_ms, repeat_count)

    def evaluate_bezier_curve(self, points, t):
        if len(points) == 1:
            return points[0]
        new_points = [points[i].lerp(points[i + 1], t) for i in range(len(points) - 1)]
        return self.evaluate_bezier_curve(new_points, t)

    def create_perfect_circle_spline(self, points):
        if len(points) < 3:
            return points

        p1, p2, p3 = [Vector((pt[0], pt[1])) for pt in points[:3]]

        def circle_center(p1, p2, p3):
            temp = p2 - p1
            temp2 = p3 - p1

            a = temp.length_squared
            b = temp.dot(temp2)
            c = temp2.length_squared
            d = 2 * (temp.x * temp2.y - temp.y * temp2.x)

            if d == 0:
                return None

            center_x = p1.x + (temp2.y * a - temp.y * c) / d
            center_y = p1.y + (temp.x * c - temp2.x * a) / d

            return Vector((center_x, center_y))

        center = circle_center(p1, p2, p3)
        if center is None:
            return points

        radius = (p1 - center).length

        # Berechne die Winkel zwischen dem Mittelpunkt und den Punkten
        angle_start = math.atan2(p1.y - center.y, p1.x - center.x)
        angle_end = math.atan2(p3.y - center.y, p3.x - center.x)

        # Bestimme die Richtung des Bogens
        cross = (p2 - p1).cross(p3 - p2)
        clockwise = cross < 0

        # Passe die Winkel basierend auf der Richtung an
        if clockwise:
            if angle_end > angle_start:
                angle_end -= 2 * math.pi
        else:
            if angle_end < angle_start:
                angle_end += 2 * math.pi

        # Generiere Punkte entlang des Kreisbogens
        num_points = 50
        arc_points = []
        for i in range(num_points + 1):
            t = i / num_points
            angle = angle_start + t * (angle_end - angle_start)
            x = center.x + radius * math.cos(angle)
            y = center.y + radius * math.sin(angle)
            arc_points.append((x, y))

        return arc_points

    def create_catmull_rom_spline(self, points, tension=0.0):
        if len(points) < 2:
            return points

        spline_points = []
        n = len(points)
        for i in range(n - 1):
            p0 = Vector(points[i - 1]) if i > 0 else Vector(points[i])
            p1 = Vector(points[i])
            p2 = Vector(points[i + 1])
            p3 = Vector(points[i + 2]) if i + 2 < n else Vector(points[i + 1])

            for t in [j / 20.0 for j in range(21)]:
                t0 = ((-tension * t + 2 * tension * t ** 2 - tension * t ** 3) / 2)
                t1 = ((1 + (tension - 3) * t ** 2 + (2 - tension) * t ** 3) / 2)
                t2 = ((tension * t + (3 - 2 * tension) * t ** 2 + (tension - 2) * t ** 3) / 2)
                t3 = ((-tension * t ** 2 + tension * t ** 3) / 2)
                point = t0 * p0 + t1 * p1 + t2 * p2 + t3 * p3
                spline_points.append((point.x, point.y))

        return spline_points

    def create_slider_ball(self, slider, start_frame, slider_duration_frames, repeat_count):
        # Erstelle eine Kugel für den Slider-Ball
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=slider.location)
        slider_ball = bpy.context.object
        slider_ball.name = f"{slider.name}_ball"

        # Füge eine Follow Path Constraint zum Slider-Ball hinzu
        follow_path = slider_ball.constraints.new(type='FOLLOW_PATH')
        follow_path.target = slider
        follow_path.use_fixed_location = True
        follow_path.use_curve_follow = True
        follow_path.forward_axis = 'FORWARD_Y'
        follow_path.up_axis = 'UP_Z'

        # Stelle sicher, dass die Kurve die Pfadanimation aktiviert hat
        total_duration_frames = slider_duration_frames * repeat_count
        slider.data.use_path = True
        slider.data.path_duration = total_duration_frames  # Wichtig für den Constraint

        # Animiere den offset_factor des Follow Path Constraints
        follow_path.offset_factor = 0.0
        follow_path.keyframe_insert(data_path="offset_factor", frame=start_frame)

        follow_path.offset_factor = 1.0
        follow_path.keyframe_insert(data_path="offset_factor", frame=start_frame + total_duration_frames)

        # Linke den Slider-Ball zur eigenen Collection
        self.slider_balls_collection.objects.link(slider_ball)
        bpy.context.collection.objects.unlink(slider_ball)

    def create_slider_ticks(self, slider, curve_data, slider_duration_ms, repeat_count):
        # Berechne die Anzahl der Ticks basierend auf der Dauer und einem festen Intervall (z.B. alle 100ms)
        tick_interval_ms = 100
        total_ticks = int(slider_duration_ms / tick_interval_ms) * repeat_count

        for tick in range(total_ticks):
            t = (tick * tick_interval_ms) / (slider_duration_ms * repeat_count)
            t = min(max(t, 0.0), 1.0)  # Sicherstellen, dass t zwischen 0 und 1 liegt

            # Berechne die exakte Position entlang der Kurve
            tick_position = evaluate_curve_at_t(slider, t)

            # Erstelle eine kleine Kugel als Tick
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(tick_position.x, tick_position.y, tick_position.z))
            tick_obj = bpy.context.object
            tick_obj.name = f"{slider.name}_tick_{tick}"

            # Füge den Ticks die Sliders Collection hinzu
            self.sliders_collection.objects.link(tick_obj)
            bpy.context.collection.objects.unlink(tick_obj)  # Entferne den Tick aus der aktiven Collection
