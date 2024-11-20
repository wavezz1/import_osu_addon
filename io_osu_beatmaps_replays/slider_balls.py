import bpy
from .geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes
from .constants import SCALE_FACTOR
from mathutils import Vector


class SliderBallCreator:
    def __init__(self, slider, start_frame, slider_duration_frames, repeat_count, end_frame, slider_balls_collection, data_manager, import_type, slider_time):
        self.slider = slider
        self.start_frame = start_frame
        self.slider_duration_frames = slider_duration_frames
        self.repeat_count = repeat_count
        self.end_frame = end_frame
        self.slider_balls_collection = slider_balls_collection
        self.data_manager = data_manager
        self.import_type = import_type
        self.slider_time = slider_time  # Speichert die Zeit des HitObjects

    def create(self):
        if self.import_type == 'BASE':
            slider_ball = self.create_base_slider_ball()
        elif self.import_type == 'FULL':
            slider_ball = self.create_full_slider_ball()
        else:
            print("Unsupported import type for slider ball.")
            return

        self.animate_slider_ball(slider_ball)
        self.link_to_collection(slider_ball)

    def create_base_slider_ball(self):
        # Basis Slider-Ball erstellen
        mesh = bpy.data.meshes.new(f"{self.slider.name}_ball")
        mesh.vertices.add(1)
        mesh.vertices[0].co = (0, 0, 0)
        mesh.use_auto_texspace = True

        slider_ball = bpy.data.objects.new(f"{self.slider.name}_ball", mesh)
        slider_ball.location = self.slider.location

        create_geometry_nodes_modifier(slider_ball, "slider_ball")

        # Keyframes für Geometry Nodes hinzufügen
        frame_values = {
            "show": [
                (int(self.start_frame - 1), False),
                (int(self.start_frame), True),
                (int(self.end_frame), False)
            ]
        }

        set_modifier_inputs_with_keyframes(
            slider_ball,
            {"show": 'BOOLEAN'},
            frame_values,
            fixed_values=None
        )
        return slider_ball

    def create_full_slider_ball(self):
        # Volle Slider-Ball Darstellung erstellen
        circle_size = self.data_manager.calculate_adjusted_cs()
        osu_radius = (54.4 - 4.48 * circle_size) / 2
        bpy.ops.mesh.primitive_uv_sphere_add(radius=osu_radius * SCALE_FACTOR * 2, location=self.slider.location)
        slider_ball = bpy.context.object
        slider_ball.name = f"{self.slider.name}_ball"
        return slider_ball

    def animate_slider_ball(self, slider_ball):
        # Slider Pfadverfolgung konfigurieren
        follow_path = slider_ball.constraints.new(type='FOLLOW_PATH')
        follow_path.target = self.slider
        follow_path.use_fixed_location = True
        follow_path.use_curve_follow = True
        follow_path.forward_axis = 'FORWARD_Y'
        follow_path.up_axis = 'UP_Z'

        # Berechnung von Geschwindigkeit und Frames
        speed_multiplier = self.data_manager.speed_multiplier
        slider_multiplier = float(self.data_manager.osu_parser.difficulty_settings.get("SliderMultiplier", 1.4))
        inherited_multiplier = 1.0

        timing_points = sorted(set(self.data_manager.beatmap_info["timing_points"]), key=lambda tp: tp[0])
        start_time_ms = self.slider_time

        for offset, beat_length in timing_points:
            if start_time_ms >= offset:
                if beat_length < 0:
                    inherited_multiplier = -100 / beat_length
            else:
                break

        effective_speed = slider_multiplier * inherited_multiplier
        adjusted_duration_frames = (self.slider_duration_frames / effective_speed) * speed_multiplier

        self.slider.data.use_path = True
        self.slider.data.path_duration = int(adjusted_duration_frames)

        repeat_duration_frames = adjusted_duration_frames / self.repeat_count if self.repeat_count > 0 else adjusted_duration_frames

        # Animation der Offset-Faktoren für Slider-Ball
        for repeat in range(self.repeat_count):
            repeat_start_frame = self.start_frame + repeat * repeat_duration_frames
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

            # Lineare Interpolation für Animationen setzen
            if slider_ball.animation_data and slider_ball.animation_data.action:
                for fcurve in slider_ball.animation_data.action.fcurves:
                    for keyframe in fcurve.keyframe_points:
                        keyframe.interpolation = 'LINEAR'

        # Sichtbarkeitsanimation nur für FULL Import
        if self.import_type == 'FULL':
            slider_ball.hide_viewport = True
            slider_ball.hide_render = True
            slider_ball.keyframe_insert(data_path="hide_viewport", frame=int(self.start_frame - 1))
            slider_ball.keyframe_insert(data_path="hide_render", frame=int(self.start_frame - 1))

            slider_ball.hide_viewport = False
            slider_ball.hide_render = False
            slider_ball.keyframe_insert(data_path="hide_viewport", frame=int(self.start_frame))
            slider_ball.keyframe_insert(data_path="hide_render", frame=int(self.start_frame))

            slider_ball.hide_viewport = True
            slider_ball.hide_render = True
            slider_ball.keyframe_insert(data_path="hide_viewport", frame=int(self.end_frame))
            slider_ball.keyframe_insert(data_path="hide_render", frame=int(self.end_frame))

    def link_to_collection(self, slider_ball):
        # Slider-Ball zur Sammlung hinzufügen
        self.slider_balls_collection.objects.link(slider_ball)
        if slider_ball.users_collection:
            for col in slider_ball.users_collection:
                if col != self.slider_balls_collection:
                    col.objects.unlink(slider_ball)
