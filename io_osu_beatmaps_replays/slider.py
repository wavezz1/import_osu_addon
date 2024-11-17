# slider.py

import bpy
import math
from mathutils import Vector
from .constants import SCALE_FACTOR
from .utils import map_osu_to_blender, evaluate_curve_at_t, timeit, get_keyframe_values
from .geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes
from .osu_replay_data_manager import OsuReplayDataManager
from .hitobjects import HitObject

class SliderCreator:
    def __init__(self, hitobject: HitObject, global_index: int, sliders_collection, slider_balls_collection, settings: dict,
                 data_manager: OsuReplayDataManager, import_type):
        self.hitobject = hitobject
        self.global_index = global_index
        self.sliders_collection = sliders_collection
        self.slider_balls_collection = slider_balls_collection
        self.settings = settings
        self.data_manager = data_manager
        self.import_type = import_type
        self.create_slider()

    def create_slider(self):
        with timeit(f"Erstellen von Slider {self.global_index:03d}_slider_{self.hitobject.time}"):
            data_manager = self.data_manager

            approach_rate = data_manager.adjusted_ar
            circle_size = data_manager.adjusted_cs
            osu_radius = data_manager.osu_radius
            preempt_frames = data_manager.preempt_frames
            audio_lead_in_frames = data_manager.audio_lead_in_frames
            speed_multiplier = data_manager.speed_multiplier
            ms_per_frame = data_manager.ms_per_frame

            start_time_ms = self.hitobject.time / speed_multiplier
            slider_duration_ms = data_manager.calculate_slider_duration(self.hitobject)
            end_time_ms = (self.hitobject.time + slider_duration_ms) / speed_multiplier

            start_frame = start_time_ms / ms_per_frame + audio_lead_in_frames
            end_frame = end_time_ms / ms_per_frame + audio_lead_in_frames
            early_start_frame = start_frame - preempt_frames

            slider_duration_frames = slider_duration_ms / ms_per_frame

            if self.hitobject.extras:
                curve_data_str = self.hitobject.extras[0]
                repeat_count = int(self.hitobject.extras[1]) if len(self.hitobject.extras) > 1 else 1
                pixel_length = float(self.hitobject.extras[2]) if len(self.hitobject.extras) > 2 else 100.0

                slider_data = curve_data_str.split('|')
                slider_type = slider_data[0]
                slider_control_points = slider_data[1:]

                points = [(self.hitobject.x, self.hitobject.y)]
                for cp in slider_control_points:
                    x_str, y_str = cp.split(':')
                    x, y = float(x_str), float(y_str)
                    points.append((x, y))

                segments = []
                current_segment = [points[0]]
                for i in range(1, len(points)):
                    if points[i] == points[i - 1]:
                        segments.append((slider_type, current_segment))
                        current_segment = [points[i]]
                    else:
                        current_segment.append(points[i])
                if current_segment:
                    segments.append((slider_type, current_segment))

                curve_data = bpy.data.curves.new(
                    name=f"{self.global_index:03d}_slider_{self.hitobject.time}_curve", type='CURVE')
                curve_data.dimensions = '3D'
                curve_data.resolution_u = 64

                spline = curve_data.splines.new('POLY')
                all_points = []

                for segment_type, segment_points in segments:
                    if len(segment_points) == 0:
                        continue
                    curve_points = self.evaluate_curve(segment_type, segment_points)
                    all_points.extend(curve_points)

                spline.points.add(len(all_points) - 1)
                for i, point in enumerate(all_points):
                    spline.points[i].co = (point.x, point.y, point.z, 1)

                if self.import_type == 'FULL':
                    slider = bpy.data.objects.new(f"{self.global_index:03d}_slider_{self.hitobject.time}_curve", curve_data)
                    curve_data.extrude = osu_radius * SCALE_FACTOR * 2
                elif self.import_type == 'BASE':
                    slider = bpy.data.objects.new(f"{self.global_index:03d}_slider_{self.hitobject.time}_curve", curve_data)

                slider["ar"] = approach_rate
                slider["cs"] = osu_radius * SCALE_FACTOR

                slider["slider_duration_ms"] = slider_duration_ms
                slider["slider_duration_frames"] = slider_duration_frames
                slider["repeat_count"] = repeat_count
                slider["pixel_length"] = pixel_length

                self.sliders_collection.objects.link(slider)
                if slider.users_collection:
                    for col in slider.users_collection:
                        if col != self.sliders_collection:
                            col.objects.unlink(slider)

                create_geometry_nodes_modifier(slider, "slider")

                # Vorbereitung der extra_params für get_keyframe_values
                extra_params = {
                    "slider_duration_ms": slider_duration_ms,
                    "slider_duration_frames": slider_duration_frames,
                    "repeat_count": repeat_count,
                    "pixel_length": pixel_length
                }

                # Verwendung der generischen get_keyframe_values-Funktion
                frame_values, fixed_values = get_keyframe_values(
                    self.hitobject,
                    'slider',
                    self.import_type,
                    start_frame,
                    end_frame,
                    early_start_frame,
                    approach_rate,
                    osu_radius,
                    extra_params
                )

                attributes = {
                    "show": 'BOOLEAN',
                    "slider_duration_ms": 'FLOAT',
                    "slider_duration_frames": 'FLOAT',
                    "ar": 'FLOAT',
                    "cs": 'FLOAT',
                    "was_hit": 'BOOLEAN',
                    "was_completed": 'BOOLEAN',
                    "repeat_count": 'INT',
                    "pixel_length": 'FLOAT'
                }

                set_modifier_inputs_with_keyframes(slider, attributes, frame_values, fixed_values)

                # Setzen der Sichtbarkeits-Keyframes für 'FULL' Importtyp
                if self.import_type == 'FULL':
                    slider.hide_viewport = True
                    slider.hide_render = True
                    slider.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame - 1))
                    slider.keyframe_insert(data_path="hide_render", frame=int(early_start_frame - 1))

                    slider.hide_viewport = False
                    slider.hide_render = False
                    slider.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame))
                    slider.keyframe_insert(data_path="hide_render", frame=int(early_start_frame))

                    slider.hide_viewport = True
                    slider.hide_render = True
                    slider.keyframe_insert(data_path="hide_viewport", frame=int(end_frame))
                    slider.keyframe_insert(data_path="hide_render", frame=int(end_frame))

                if self.settings.get('import_slider_balls', False):
                    self.create_slider_ball(slider, start_frame, slider_duration_frames, repeat_count)
                if self.settings.get('import_slider_ticks', False):
                    self.create_slider_ticks(slider, curve_data, slider_duration_ms, repeat_count)

    def evaluate_curve(self, segment_type, segment_points):
        if segment_type == "L":
            # Lineare Segmente
            return [Vector(map_osu_to_blender(point[0], point[1])) for point in segment_points]
        elif segment_type == "P":
            # Perfekte Kreis-Segmente
            return self.evaluate_perfect_circle(segment_points)
        elif segment_type == "B":
            # Bezier-Kurven-Segmente
            return self.evaluate_bezier_curve(segment_points)
        elif segment_type == "C":
            # Catmull-Rom-Spline-Segmente
            return self.evaluate_catmull_rom_spline(segment_points)
        else:
            # Standardmäßig lineare Segmente
            return [Vector(map_osu_to_blender(point[0], point[1])) for point in segment_points]

    def evaluate_bezier_curve(self, control_points_osu, num_points=None):
        if num_points is None:
            num_points = self.settings.get('slider_resolution', 100)
        n = len(control_points_osu) - 1
        curve_points = []

        # Mapping der Kontrollpunkte von osu! zu Blender-Koordinaten
        control_points = [Vector(map_osu_to_blender(x, y)) for x, y in control_points_osu]

        for t in [i / num_points for i in range(num_points + 1)]:
            point = Vector((0.0, 0.0, 0.0))
            for i in range(n + 1):
                bernstein = self.bernstein_polynomial(i, n, t)
                point += bernstein * control_points[i]
            curve_points.append(point)
        return curve_points

    def bernstein_polynomial(self, i, n, t):
        return math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

    def evaluate_perfect_circle(self, points_osu):
        if len(points_osu) < 3:
            return [Vector(map_osu_to_blender(point[0], point[1])) for point in points_osu]

        p1, p2, p3 = [Vector(point) for point in points_osu[:3]]

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
            return [Vector(map_osu_to_blender(point[0], point[1])) for point in points_osu]

        radius = (p1 - center).length

        angle_start = math.atan2(p1.y - center.y, p1.x - center.x)
        angle_end = math.atan2(p3.y - center.y, p3.x - center.x)

        cross = (p2 - p1).cross(p3 - p2)
        clockwise = cross < 0

        if clockwise:
            if angle_end > angle_start:
                angle_end -= 2 * math.pi
        else:
            if angle_end < angle_start:
                angle_end += 2 * math.pi

        num_points = self.settings.get('slider_resolution', 50)
        arc_points = []
        for i in range(num_points + 1):
            t = i / num_points
            angle = angle_start + t * (angle_end - angle_start)
            x = center.x + radius * math.cos(angle)
            y = center.y + radius * math.sin(angle)
            arc_points.append(Vector(map_osu_to_blender(x, y)))

        return arc_points

    def evaluate_catmull_rom_spline(self, points_osu, tension=0.0):
        if len(points_osu) < 2:
            return [Vector(map_osu_to_blender(point[0], point[1])) for point in points_osu]

        spline_points = []
        n = len(points_osu)
        num_points = self.settings.get('slider_resolution', 20)
        for i in range(n - 1):
            p0 = Vector(points_osu[i - 1]) if i > 0 else Vector(points_osu[i])
            p1 = Vector(points_osu[i])
            p2 = Vector(points_osu[i + 1])
            p3 = Vector(points_osu[i + 2]) if i + 2 < n else Vector(points_osu[i + 1])

            # Mapping der Punkte zu Blender-Koordinaten
            p0 = Vector(map_osu_to_blender(p0.x, p0.y))
            p1 = Vector(map_osu_to_blender(p1.x, p1.y))
            p2 = Vector(map_osu_to_blender(p2.x, p2.y))
            p3 = Vector(map_osu_to_blender(p3.x, p3.y))

            for t in [j / num_points for j in range(int(num_points) + 1)]:
                t0 = ((-tension * t + 2 * tension * t ** 2 - tension * t ** 3) / 2)
                t1 = ((1 + (tension - 3) * t ** 2 + (2 - tension) * t ** 3) / 2)
                t2 = ((tension * t + (3 - 2 * tension) * t ** 2 + (tension - 2) * t ** 3) / 2)
                t3 = ((-tension * t ** 2 + tension * t ** 3) / 2)
                point = t0 * p0 + t1 * p1 + t2 * p2 + t3 * p3
                spline_points.append(point)

        return spline_points

    def create_slider_ball(self, slider, start_frame, slider_duration_frames, repeat_count):
        if self.import_type == 'BASE':
            mesh = bpy.data.meshes.new(f"{slider.name}_ball")

            mesh.vertices.add(1)
            mesh.vertices[0].co = (0, 0, 0)

            mesh.use_auto_texspace = True

            slider_ball = bpy.data.objects.new(f"{slider.name}_ball", mesh)
            slider_ball.location = slider.location

            create_geometry_nodes_modifier(slider_ball, "slider_ball")

            end_frame = start_frame + slider_duration_frames

            frame_values = {
                "show": [
                    (int(start_frame - 1), False),
                    (int(start_frame), True),
                    (int(end_frame), False)
                ]
            }

            set_modifier_inputs_with_keyframes(
                slider_ball,
                {
                    "show": 'BOOLEAN',
                },
                frame_values,
                fixed_values=None
            )

        elif self.import_type == 'FULL':
            circle_size = self.data_manager.calculate_adjusted_cs()
            osu_radius = (54.4 - 4.48 * circle_size) / 2
            bpy.ops.mesh.primitive_uv_sphere_add(radius=osu_radius * SCALE_FACTOR * 2, location=slider.location)
            slider_ball = bpy.context.object
            slider_ball.name = f"{slider.name}_ball"

        follow_path = slider_ball.constraints.new(type='FOLLOW_PATH')
        follow_path.target = slider
        follow_path.use_fixed_location = True
        follow_path.use_curve_follow = True
        follow_path.forward_axis = 'FORWARD_Y'
        follow_path.up_axis = 'UP_Z'

        speed_multiplier = self.settings.get('speed_multiplier', 1.0)
        slider_multiplier = float(self.data_manager.osu_parser.difficulty_settings.get("SliderMultiplier", 1.4))
        inherited_multiplier = 1.0

        timing_points = sorted(set(self.data_manager.beatmap_info["timing_points"]), key=lambda tp: tp[0])
        start_time_ms = self.hitobject.time

        for offset, beat_length in timing_points:
            if start_time_ms >= offset:
                if beat_length < 0:
                    inherited_multiplier = -100 / beat_length
            else:
                break

        effective_speed = slider_multiplier * inherited_multiplier
        adjusted_duration_frames = (slider_duration_frames / effective_speed) * speed_multiplier

        slider.data.use_path = True
        slider.data.path_duration = int(adjusted_duration_frames)

        repeat_duration_frames = adjusted_duration_frames / repeat_count if repeat_count > 0 else adjusted_duration_frames

        for repeat in range(repeat_count):
            repeat_start_frame = start_frame + repeat * repeat_duration_frames
            if repeat % 2 == 0:
                follow_path.offset_factor = 0.0
                follow_path.keyframe_insert(data_path="offset_factor", frame=repeat_start_frame)
                follow_path.offset_factor = 1.0
                follow_path.keyframe_insert(data_path="offset_factor",
                                            frame=repeat_start_frame + repeat_duration_frames)
            else:
                follow_path.offset_factor = 1.0
                follow_path.keyframe_insert(data_path="offset_factor", frame=repeat_start_frame)
                follow_path.offset_factor = 0.0
                follow_path.keyframe_insert(data_path="offset_factor",
                                            frame=repeat_start_frame + repeat_duration_frames)

            if slider_ball.animation_data and slider_ball.animation_data.action:
                for fcurve in slider_ball.animation_data.action.fcurves:
                    for keyframe in fcurve.keyframe_points:
                        keyframe.interpolation = 'LINEAR'

        self.slider_balls_collection.objects.link(slider_ball)

        if slider_ball.users_collection:
            for col in slider_ball.users_collection:
                if col != self.slider_balls_collection:
                    col.objects.unlink(slider_ball)

        if self.import_type == 'FULL':
            early_start_frame = start_frame - (slider_duration_frames / speed_multiplier)
            end_frame = start_frame + slider_duration_frames

            slider_ball.hide_viewport = True
            slider_ball.hide_render = True
            slider_ball.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame - 1))
            slider_ball.keyframe_insert(data_path="hide_render", frame=int(early_start_frame - 1))

            slider_ball.hide_viewport = False
            slider_ball.hide_render = False
            slider_ball.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame))
            slider_ball.keyframe_insert(data_path="hide_render", frame=int(early_start_frame))

            slider_ball.keyframe_insert(data_path="hide_viewport", frame=int(end_frame))
            slider_ball.keyframe_insert(data_path="hide_render", frame=int(end_frame))

            slider_ball.hide_viewport = True
            slider_ball.hide_render = True
            slider_ball.keyframe_insert(data_path="hide_viewport", frame=int(end_frame))
            slider_ball.keyframe_insert(data_path="hide_render", frame=int(end_frame))


    def create_slider_ticks(self, slider, curve_data, slider_duration_ms, repeat_count):
        tick_interval_ms = 100
        total_ticks = int(slider_duration_ms / tick_interval_ms) * repeat_count

        for tick in range(total_ticks):
            t = (tick * tick_interval_ms) / (slider_duration_ms * repeat_count)
            t = min(max(t, 0.0), 1.0)

            tick_position = evaluate_curve_at_t(slider, t)

            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(tick_position.x, tick_position.y, tick_position.z))
            tick_obj = bpy.context.object
            tick_obj.name = f"{slider.name}_tick_{tick}"

            self.sliders_collection.objects.link(tick_obj)
            bpy.context.collection.objects.unlink(tick_obj)
