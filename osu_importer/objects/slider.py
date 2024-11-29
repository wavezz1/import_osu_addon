# osu_importer/objects/slider.py

import bpy
import math
from mathutils import Vector
from osu_importer.utils.constants import SCALE_FACTOR
from osu_importer.utils.utils import map_osu_to_blender, timeit, get_keyframe_values, tag_imported
from osu_importer.geo_nodes.geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes
from osu_importer.osu_data_manager import OsuDataManager
from osu_importer.parsers.hitobjects import HitObject

class SliderCreator:
    def __init__(self, hitobject: HitObject, global_index: int, sliders_collection, slider_balls_collection, settings: dict,
                 data_manager: OsuDataManager, import_type):
        self.hitobject = hitobject
        self.global_index = global_index
        self.sliders_collection = sliders_collection
        self.slider_balls_collection = slider_balls_collection
        self.settings = settings
        self.data_manager = data_manager
        self.import_type = import_type
        self.slider_resolution = settings.get('slider_resolution', 100)
        self.import_slider_balls = settings.get('import_slider_balls', False)
        self.import_slider_ticks = settings.get('import_slider_ticks', False)
        self.create_slider()

    def merge_duplicate_points(self, points, tolerance=0.01):
        if not points:
            print("Keine Punkte zum Mergen vorhanden.")
            return [], []

        merged = []
        i = 0
        while i < len(points):
            if i < len(points) - 1:
                p1 = points[i]
                p2 = points[i + 1]
                if (abs(p1.x - p2.x) <= tolerance) and (abs(p1.y - p2.y) <= tolerance):
                    print(f"merged doubles {p1} und {p2} zu {p1}")
                    merged.append(p1)
                    i += 2
                    continue
            merged.append(points[i])
            i += 1
        print(f"Merge Result: {merged}")
        return merged

    def create_slider(self):
        with timeit(f"Create Slider {self.global_index:03d}_slider_{self.hitobject.time}"):
            data_manager = self.data_manager

            approach_rate = data_manager.adjusted_ar
            osu_radius = data_manager.osu_radius

            start_frame = int(self.hitobject.start_frame)
            end_frame = int(self.hitobject.end_frame)
            early_start_frame = int(start_frame - data_manager.preempt_frames)

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

                merged_curve_points = self.merge_duplicate_points(all_points, tolerance=0.01)

                if merged_curve_points:
                    start_pos = merged_curve_points[0]
                    end_pos = merged_curve_points[-1]
                    self.hitobject.start_pos = start_pos
                    self.hitobject.end_pos = end_pos
                else:
                    start_pos = Vector(map_osu_to_blender(self.hitobject.x, self.hitobject.y))
                    end_pos = start_pos
                    self.hitobject.start_pos = start_pos
                    self.hitobject.end_pos = end_pos

                spline.points.add(len(merged_curve_points) - 1)
                for i, point in enumerate(merged_curve_points):
                    spline.points[i].co = (point.x, point.y, point.z, 1)

                if self.import_type == 'FULL':
                    slider = bpy.data.objects.new(f"{self.global_index:03d}_slider_{self.hitobject.time}_curve", curve_data)
                    curve_data.extrude = osu_radius * SCALE_FACTOR * 2
                elif self.import_type == 'BASE':
                    slider = bpy.data.objects.new(f"{self.global_index:03d}_slider_{self.hitobject.time}_curve", curve_data)

                tag_imported(slider)

                slider["ar"] = approach_rate
                slider["cs"] = osu_radius * SCALE_FACTOR

                slider_duration_frames = self.hitobject.duration_frames
                slider_duration_ms = slider_duration_frames * data_manager.ms_per_frame
                slider["slider_duration_ms"] = slider_duration_ms
                slider["slider_duration_frames"] = slider_duration_frames
                slider["repeat_count"] = repeat_count
                slider["pixel_length"] = pixel_length

                reverse_frames = []
                for i in range(1, repeat_count):
                    reverse_frame = int(self.hitobject.start_frame + (slider_duration_frames / repeat_count) * i)
                    reverse_frames.append(reverse_frame)

                self.sliders_collection.objects.link(slider)
                if slider.users_collection:
                    for col in slider.users_collection:
                        if col != self.sliders_collection:
                            col.objects.unlink(slider)
                if self.import_type == 'BASE':
                    create_geometry_nodes_modifier(slider, "slider")

                frame_values, fixed_values = get_keyframe_values(
                    self.hitobject,
                    'slider',
                    self.import_type,
                    start_frame,
                    end_frame,
                    early_start_frame,
                    approach_rate,
                    osu_radius,
                    extra_params={
                        "slider_duration_ms": slider_duration_ms,
                        "slider_duration_frames": slider_duration_frames,
                        "repeat_count": repeat_count,
                        "pixel_length": pixel_length
                    },
                    ms_per_frame=data_manager.ms_per_frame,
                    audio_lead_in_frames=data_manager.audio_lead_in_frames
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
                    "pixel_length": 'FLOAT',
                    "combo": 'INT',
                    "combo_color_idx": 'INT',
                    "combo_color": 'FLOAT_VECTOR',
                    "reverse_head": 'BOOLEAN',
                    "reverse_tail": 'BOOLEAN',
                }

                if self.hitobject.combo_number is not None:
                    fixed_values['combo'] = self.hitobject.combo_number
                    fixed_values['combo_color'] = self.hitobject.combo_color
                    fixed_values['combo_color_idx'] = self.hitobject.combo_color_idx

                reverse_head_frames = [
                    int((time + data_manager.audio_lead_in) / data_manager.ms_per_frame)
                    for time in self.hitobject.reverse_arrow_keyframes_head
                ]
                reverse_tail_frames = [
                    int((time + data_manager.audio_lead_in) / data_manager.ms_per_frame)
                    for time in self.hitobject.reverse_arrow_keyframes_tail
                ]

                # reverse_head und reverse_tail unter frame_values setzen
                for frame in reverse_head_frames:
                    if frame not in frame_values:
                        frame_values[frame] = {}
                    frame_values[frame]['reverse_head'] = True

                for frame in reverse_tail_frames:
                    if frame not in frame_values:
                        frame_values[frame] = {}
                    frame_values[frame]['reverse_tail'] = True

                set_modifier_inputs_with_keyframes(slider, attributes, frame_values, fixed_values)

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

                if self.import_slider_balls:
                    from .slider_balls import SliderBallCreator
                    slider_ball_creator = SliderBallCreator(
                        slider=slider,
                        start_frame=start_frame,
                        slider_duration_frames=self.hitobject.duration_frames,
                        repeat_count=repeat_count,
                        end_frame=end_frame,
                        slider_balls_collection=self.slider_balls_collection,
                        data_manager=self.data_manager,
                        import_type=self.import_type,
                        slider_time=self.hitobject.time
                    )
                    slider_ball_creator.create()

                if self.import_slider_ticks:
                    from .slider_ticks import SliderTicksCreator
                    slider_ticks_creator = SliderTicksCreator(
                        slider=slider,
                        slider_duration_ms=slider_duration_ms,
                        repeat_count=repeat_count,
                        sliders_collection=self.sliders_collection,
                        settings=self.settings,
                        import_type=self.import_type
                    )
                    slider_ticks_creator.create()

    def evaluate_curve(self, segment_type, segment_points):
        if segment_type == "L":
            return [Vector(map_osu_to_blender(point[0], point[1])) for point in segment_points]
        elif segment_type == "P":
            return self.evaluate_perfect_circle(segment_points)
        elif segment_type == "B":
            return self.evaluate_bezier_curve(segment_points)
        elif segment_type == "C":
            return self.evaluate_catmull_rom_spline(segment_points)
        else:
            return [Vector(map_osu_to_blender(point[0], point[1])) for point in segment_points]

    def evaluate_bezier_curve(self, control_points_osu, num_points=None):
        if num_points is None:
            num_points = self.slider_resolution
        n = len(control_points_osu) - 1
        curve_points = []

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
