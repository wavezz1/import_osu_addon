# slider.py

import bpy
import math
from mathutils import Vector
from .constants import SCALE_FACTOR
from .utils import map_osu_to_blender, get_ms_per_frame, evaluate_curve_at_t, timeit
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
            approach_rate = self.data_manager.calculate_adjusted_ar()
            circle_size = self.data_manager.calculate_adjusted_cs()
            osu_radius = (54.4 - 4.48 * circle_size) / 2

            speed_multiplier = self.settings.get('speed_multiplier', 1.0)
            audio_lead_in_frames = self.data_manager.beatmap_info["audio_lead_in"] / get_ms_per_frame()

            start_time_ms = self.hitobject.time / speed_multiplier
            slider_duration_ms = self.data_manager.calculate_slider_duration(self.hitobject)
            end_time_ms = (self.hitobject.time + slider_duration_ms) / speed_multiplier

            start_frame = start_time_ms / get_ms_per_frame() + audio_lead_in_frames
            end_frame = end_time_ms / get_ms_per_frame() + audio_lead_in_frames

            preempt_frames = self.data_manager.calculate_preempt_time(approach_rate) / get_ms_per_frame()
            early_start_frame = start_frame - preempt_frames

            slider_duration_frames = (slider_duration_ms / get_ms_per_frame()) / speed_multiplier

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
                    if segment_type == "L":
                        for point in segment_points:
                            corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                            all_points.append(Vector((corrected_x, corrected_y, corrected_z)))
                    elif segment_type == "P":
                        if len(segment_points) >= 3:
                            spline_points = self.create_perfect_circle_spline(segment_points)
                            for point in spline_points:
                                corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                                all_points.append(Vector((corrected_x, corrected_y, corrected_z)))
                        else:
                            for point in segment_points:
                                corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                                all_points.append(Vector((corrected_x, corrected_y, corrected_z)))
                    elif segment_type == "B":
                        if len(segment_points) < 2:
                            continue
                        control_points = []
                        for point in segment_points:
                            x, y = point
                            corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)
                            control_points.append(Vector((corrected_x, corrected_y, corrected_z)))
                        curve_points = self.evaluate_bezier_curve(control_points)
                        all_points.extend(curve_points)
                    elif segment_type == "C":
                        spline_points = self.create_catmull_rom_spline(segment_points)
                        for point in spline_points:
                            corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                            all_points.append(Vector((corrected_x, corrected_y, corrected_z)))
                    else:
                        for point in segment_points:
                            corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                            all_points.append(Vector((corrected_x, corrected_y, corrected_z)))

                spline.points.add(len(all_points) - 1)
                for i, point in enumerate(all_points):
                    spline.points[i].co = (point.x, point.y, point.z, 1)

                if self.import_type == 'FULL':
                    slider = bpy.data.objects.new(f"{self.global_index:03d}_slider_{self.hitobject.time}_curve", curve_data)
                    curve_data.extrude = osu_radius * SCALE_FACTOR * 2
                elif self.import_type == 'BASE':
                    slider = bpy.data.objects.new(f"{self.global_index:03d}_slider_{self.hitobject.time}_curve",curve_data)

                slider["ar"] = approach_rate
                slider["cs"] = osu_radius * SCALE_FACTOR

                slider["slider_duration_ms"] = slider_duration_ms
                slider["slider_duration_frames"] = (slider_duration_ms / get_ms_per_frame()) / speed_multiplier
                slider["repeat_count"] = repeat_count
                slider["pixel_length"] = pixel_length

                self.sliders_collection.objects.link(slider)
                if slider.users_collection:
                    for col in slider.users_collection:
                        if col != self.sliders_collection:
                            col.objects.unlink(slider)

                create_geometry_nodes_modifier(slider, "slider")

                if self.import_type == 'BASE':
                    frame_values = {
                        "show": [
                            (int(early_start_frame - 1), False),
                            (int(early_start_frame), True),
                            (int(end_frame - 1), True),
                            (int(end_frame), False)
                        ],
                        "was_hit": [
                            (int(start_frame - 1), False),
                            (int(start_frame), self.hitobject.was_hit)
                        ],
                        "was_completed": [
                            (int(end_frame - 1), False),
                            (int(end_frame), self.hitobject.was_completed)
                        ],
                    }

                    fixed_values = {
                        "ar": approach_rate,
                        "cs": 1 + osu_radius * SCALE_FACTOR,
                        "slider_duration_ms": slider_duration_ms,
                        "slider_duration_frames": slider_duration_frames,
                        "repeat_count": repeat_count,
                        "pixel_length": pixel_length
                    }

                    set_modifier_inputs_with_keyframes(slider, {
                        "show": 'BOOLEAN',
                        "slider_duration_ms": 'FLOAT',
                        "slider_duration_frames": 'FLOAT',
                        "ar": 'FLOAT',
                        "cs": 'FLOAT',
                        "was_hit": 'BOOLEAN',
                        "was_completed": 'BOOLEAN',
                        "repeat_count": 'INT',
                        "pixel_length": 'FLOAT',
                    }, frame_values, fixed_values)


                elif self.import_type == 'FULL':
                    frame_values = {
                        "show": [
                            (int(early_start_frame - 1), False),
                            (int(early_start_frame), True),
                            (int(end_frame - 1), True),
                            (int(end_frame), False)  # Set visibility to False after slider duration
                        ],
                        "was_hit": [
                            (int(start_frame - 1), False),
                            (int(start_frame), self.hitobject.was_hit)
                        ],
                        "was_completed": [
                            (int(end_frame - 1), False),
                            (int(end_frame), self.hitobject.was_completed)
                        ]
                    }

                    fixed_values = {
                        "ar": approach_rate,
                        "cs": osu_radius * SCALE_FACTOR,
                        "slider_duration_ms": slider_duration_ms,
                        "slider_duration_frames": slider_duration_frames,
                        "repeat_count": repeat_count,
                        "pixel_length": pixel_length
                    }

                    set_modifier_inputs_with_keyframes(slider, {
                        "show": 'BOOLEAN',
                        "slider_duration_ms": 'FLOAT',
                        "slider_duration_frames": 'FLOAT',
                        "ar": 'FLOAT',
                        "cs": 'FLOAT',
                        "was_hit": 'BOOLEAN',
                        "was_completed": 'BOOLEAN',
                        "repeat_count": 'INT',
                        "pixel_length": 'FLOAT'
                    }, frame_values, fixed_values)

                    slider.hide_viewport = True
                    slider.hide_render = True
                    slider.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame - 1))
                    slider.hide_viewport = False
                    slider.hide_render = False
                    slider.keyframe_insert(data_path="hide_viewport", frame=int(early_start_frame))
                    slider.keyframe_insert(data_path="hide_render", frame=int(early_start_frame))
                    slider.hide_viewport = True
                    slider.hide_render = True
                    slider.keyframe_insert(data_path="hide_viewport", frame=int(end_frame))
                    slider.keyframe_insert(data_path="hide_render", frame=int(end_frame))

                if self.settings.get('import_slider_balls', False):
                    slider_duration_frames = slider["slider_duration_frames"]
                    self.create_slider_ball(slider, start_frame, slider_duration_frames, repeat_count)
                if self.settings.get('import_slider_ticks', False):
                    self.create_slider_ticks(slider, curve_data, slider_duration_ms, repeat_count)

    def evaluate_bezier_curve(self, control_points, num_points=None):
        if num_points is None:
            num_points = self.settings.get('slider_resolution', 100)
        n = len(control_points) - 1
        curve_points = []

        for t in [i / num_points for i in range(num_points + 1)]:
            point = Vector((0.0, 0.0, 0.0))
            for i in range(n + 1):
                bernstein = self.bernstein_polynomial(i, n, t)
                point += bernstein * control_points[i]
            curve_points.append(point)
        return curve_points

    def bernstein_polynomial(self, i, n, t):
        return math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

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
            arc_points.append((x, y))

        return arc_points

    def create_catmull_rom_spline(self, points, tension=0.0):
        if len(points) < 2:
            return points

        spline_points = []
        n = len(points)
        num_points = self.settings.get('slider_resolution', 20)
        for i in range(n - 1):
            p0 = Vector(points[i - 1]) if i > 0 else Vector(points[i])
            p1 = Vector(points[i])
            p2 = Vector(points[i + 1])
            p3 = Vector(points[i + 2]) if i + 2 < n else Vector(points[i + 1])

            for t in [j / num_points for j in range(int(num_points) + 1)]:
                t0 = ((-tension * t + 2 * tension * t ** 2 - tension * t ** 3) / 2)
                t1 = ((1 + (tension - 3) * t ** 2 + (2 - tension) * t ** 3) / 2)
                t2 = ((tension * t + (3 - 2 * tension) * t ** 2 + (tension - 2) * t ** 3) / 2)
                t3 = ((-tension * t ** 2 + tension * t ** 3) / 2)
                point = t0 * p0 + t1 * p1 + t2 * p2 + t3 * p3
                spline_points.append((point.x, point.y))

        return spline_points

    def create_slider_ball(self, slider, start_frame, slider_duration_frames, repeat_count):
        if self.import_type == 'BASE':
            mesh = bpy.data.meshes.new(f"{slider.name}_ball")

            mesh.vertices.add(1)
            mesh.vertices[0].co = (0, 0, 0)

            mesh.use_auto_texspace = True

            slider_ball = bpy.data.objects.new(f"{slider.name}_ball", mesh)
            slider_ball.location = slider.location

        elif self.import_type == 'FULL':
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=slider.location)
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
