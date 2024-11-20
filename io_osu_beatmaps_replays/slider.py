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
        self.slider_resolution = settings.get('slider_resolution', 100)
        self.import_slider_balls = settings.get('import_slider_balls', False)
        self.import_slider_ticks = settings.get('import_slider_ticks', False)
        self.create_slider()

    def merge_duplicate_points(self, points, tolerance=0.01):
        """Merges duplicate points within a given tolerance."""
        if not points:
            return []

        merged = [points[0]]
        for i in range(1, len(points)):
            if (points[i] - merged[-1]).length > tolerance:
                merged.append(points[i])
        return merged

    def create_slider(self):
        """Main function to create a slider object."""
        with timeit(f"Erstellen von Slider {self.global_index:03d}_slider_{self.hitobject.time}"):
            # Initial Calculations
            start_frame, end_frame, early_start_frame, slider_duration_frames = self._calculate_frames()

            # Prepare Slider Data
            slider_data, repeat_count, pixel_length = self._prepare_slider_data()

            # Generate Curve
            curve_data, all_points = self._generate_slider_curve(slider_data)

            # Create Blender Object
            slider = self._create_slider_object(curve_data, slider_duration_frames, repeat_count, pixel_length)

            # Set Keyframes and Attributes
            self._set_slider_keyframes(slider, start_frame, end_frame, early_start_frame, slider_duration_frames)

            # Optionally Create Additional Features
            if self.import_slider_balls:
                self._create_slider_balls(slider, start_frame, slider_duration_frames, repeat_count, end_frame)

            if self.import_slider_ticks:
                self._create_slider_ticks(slider, curve_data, slider_duration_frames, repeat_count)

    def _calculate_frames(self):
        """Calculate frame-related values."""
        start_time_ms = self.hitobject.time / self.data_manager.speed_multiplier
        slider_duration_ms = self.data_manager.calculate_slider_duration(self.hitobject)
        end_time_ms = (self.hitobject.time + slider_duration_ms) / self.data_manager.speed_multiplier

        start_frame = start_time_ms / self.data_manager.ms_per_frame + self.data_manager.audio_lead_in_frames
        end_frame = end_time_ms / self.data_manager.ms_per_frame + self.data_manager.audio_lead_in_frames
        early_start_frame = start_frame - self.data_manager.preempt_frames

        slider_duration_frames = slider_duration_ms / self.data_manager.ms_per_frame
        return start_frame, end_frame, early_start_frame, slider_duration_frames

    def _prepare_slider_data(self):
        """Extract and prepare slider data."""
        curve_data_str = self.hitobject.extras[0]
        repeat_count = int(self.hitobject.extras[1]) if len(self.hitobject.extras) > 1 else 1
        pixel_length = float(self.hitobject.extras[2]) if len(self.hitobject.extras) > 2 else 100.0

        slider_data = curve_data_str.split('|')
        return slider_data, repeat_count, pixel_length

    def _generate_slider_curve(self, slider_data):
        """Generate curve data for the slider."""
        points = [Vector(map_osu_to_blender(self.hitobject.x, self.hitobject.y))]
        for cp in slider_data[1:]:
            x, y = map(float, cp.split(':'))
            points.append(Vector(map_osu_to_blender(x, y)))

        merged_curve_points = self.merge_duplicate_points(points, tolerance=0.01)

        curve_data = bpy.data.curves.new(
            name=f"{self.global_index:03d}_slider_{self.hitobject.time}_curve", type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.resolution_u = 64

        spline = curve_data.splines.new('POLY')
        spline.points.add(len(merged_curve_points) - 1)
        for i, point in enumerate(merged_curve_points):
            spline.points[i].co = (point.x, point.y, 0.0, 1.0)

        return curve_data, merged_curve_points

    def _create_slider_object(self, curve_data, slider_duration_frames, repeat_count, pixel_length):
        """Create and configure the slider object."""
        slider = bpy.data.objects.new(f"{self.global_index:03d}_slider_{self.hitobject.time}_curve", curve_data)
        self.sliders_collection.objects.link(slider)

        slider["slider_duration_frames"] = slider_duration_frames
        slider["repeat_count"] = repeat_count
        slider["pixel_length"] = pixel_length

        if self.import_type == 'BASE':
            create_geometry_nodes_modifier(slider, "slider")
        elif self.import_type == 'FULL':
            curve_data.extrude = self.data_manager.osu_radius * SCALE_FACTOR * 2

        return slider

    def _set_slider_keyframes(self, slider, start_frame, end_frame, early_start_frame, slider_duration_frames):
        """Set keyframes and attributes for the slider."""
        attributes = {
            "show": 'BOOLEAN',
            "slider_duration_frames": 'FLOAT',
            "repeat_count": 'INT',
            "pixel_length": 'FLOAT',
        }
        frame_values, fixed_values = get_keyframe_values(
            self.hitobject,
            'slider',
            self.import_type,
            start_frame,
            end_frame,
            early_start_frame,
            self.data_manager.adjusted_ar,
            self.data_manager.osu_radius,
            {
                "slider_duration_frames": slider_duration_frames,
                "repeat_count": slider["repeat_count"],
                "pixel_length": slider["pixel_length"]
            }
        )
        set_modifier_inputs_with_keyframes(slider, attributes, frame_values, fixed_values)

    def _create_slider_balls(self, slider, start_frame, slider_duration_frames, repeat_count, end_frame):
        """Create slider balls if enabled."""
        from .slider_balls import SliderBallCreator
        SliderBallCreator(
            slider=slider,
            start_frame=start_frame,
            slider_duration_frames=slider_duration_frames,
            repeat_count=repeat_count,
            end_frame=end_frame,
            slider_balls_collection=self.slider_balls_collection,
            data_manager=self.data_manager,
            import_type=self.import_type,
            slider_time=self.hitobject.time
        ).create()

    def _create_slider_ticks(self, slider, curve_data, slider_duration_frames, repeat_count):
        """Create slider ticks if enabled."""
        tick_interval_ms = 100
        total_ticks = int(slider_duration_frames * self.data_manager.ms_per_frame / tick_interval_ms) * repeat_count

        for tick in range(total_ticks):
            t = (tick * tick_interval_ms) / (slider_duration_frames * repeat_count)
            t = min(max(t, 0.0), 1.0)
            tick_position = evaluate_curve_at_t(slider, t)
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(tick_position.x, tick_position.y, 0.0))
            tick_obj = bpy.context.object
            tick_obj.name = f"{slider.name}_tick_{tick}"
            self.sliders_collection.objects.link(tick_obj)
