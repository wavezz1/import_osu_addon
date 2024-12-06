# osu_importer/objects/slider_balls.py

import bpy
from osu_importer.geo_nodes.geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes
from osu_importer.utils.constants import SCALE_FACTOR
from osu_importer.utils.utils import tag_imported
from osu_importer.osu_data_manager import OsuDataManager

class SliderBallCreator:
    def __init__(self, slider, start_frame, slider_duration_frames, repeat_count, end_frame,
                 slider_balls_collection, data_manager: OsuDataManager, config, slider_time):
        self.slider = slider
        self.start_frame = start_frame
        self.slider_duration_frames = slider_duration_frames
        self.repeat_count = repeat_count
        self.end_frame = end_frame
        self.slider_balls_collection = slider_balls_collection
        self.data_manager = data_manager
        self.config = config
        self.slider_time = slider_time
        self.import_type = self.config.import_type

    def create(self):
        if self.import_type == 'BASE':
            slider_ball = self.create_base_slider_ball()
        elif self.import_type == 'FULL':
            slider_ball = self.create_full_slider_ball()
        else:
            print("Unsupported import type for slider ball.")
            return

        tag_imported(slider_ball)

        self.animate_slider_ball(slider_ball)
        self.link_to_collection(slider_ball)

    def create_base_slider_ball(self):
        mesh = bpy.data.meshes.new(f"{self.slider.name}_ball_mesh")
        mesh.from_pydata([(0, 0, 0)], [], [])
        mesh.update()

        slider_ball = bpy.data.objects.new(f"{self.slider.name}_ball", mesh)
        slider_ball.location = self.slider.location

        create_geometry_nodes_modifier(slider_ball, "slider_ball")

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
        osu_radius = self.data_manager.osu_radius

        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=osu_radius * SCALE_FACTOR * 2,
            location=self.slider.location
        )
        slider_ball = bpy.context.object
        slider_ball.name = f"{self.slider.name}_ball"

        return slider_ball

    def animate_slider_ball(self, slider_ball):
        follow_path = slider_ball.constraints.new(type='FOLLOW_PATH')
        follow_path.target = self.slider
        follow_path.use_fixed_location = True
        follow_path.use_curve_follow = True
        follow_path.forward_axis = 'FORWARD_Y'
        follow_path.up_axis = 'UP_Z'

        if self.repeat_count > 0:
            repeat_duration_frames = self.slider_duration_frames / self.repeat_count
        else:
            repeat_duration_frames = self.slider_duration_frames

        self.slider.data.use_path = True
        self.slider.data.path_duration = int(repeat_duration_frames)

        for repeat in range(self.repeat_count):
            repeat_start_frame = self.start_frame + int(repeat * repeat_duration_frames)
            repeat_end_frame = repeat_start_frame + int(repeat_duration_frames)

            if repeat % 2 == 0:
                follow_path.offset_factor = 0.0
                follow_path.keyframe_insert(data_path="offset_factor", frame=int(repeat_start_frame))
                follow_path.offset_factor = 1.0
                follow_path.keyframe_insert(data_path="offset_factor", frame=int(repeat_end_frame))
            else:
                follow_path.offset_factor = 1.0
                follow_path.keyframe_insert(data_path="offset_factor", frame=int(repeat_start_frame))
                follow_path.offset_factor = 0.0
                follow_path.keyframe_insert(data_path="offset_factor", frame=int(repeat_end_frame))

            if slider_ball.animation_data and slider_ball.animation_data.action:
                for fcurve in slider_ball.animation_data.action.fcurves:
                    for keyframe in fcurve.keyframe_points:
                        keyframe.interpolation = 'LINEAR'

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
        self.slider_balls_collection.objects.link(slider_ball)
        if slider_ball.users_collection:
            for col in slider_ball.users_collection:
                if col != self.slider_balls_collection:
                    col.objects.unlink(slider_ball)
