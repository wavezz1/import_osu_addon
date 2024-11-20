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
        self.slider_time = slider_time

    def create(self):
        slider_ball = (
            self.create_base_slider_ball() if self.import_type == 'BASE' else
            self.create_full_slider_ball() if self.import_type == 'FULL' else
            None
        )

        if slider_ball:
            self.animate_slider_ball(slider_ball)
            self.link_to_collection(slider_ball)

    def create_base_slider_ball(self):
        """Erstellt einen Slider-Ball im BASE-Modus mit Geometry Nodes."""
        mesh = self._create_empty_mesh(f"{self.slider.name}_ball")
        slider_ball = bpy.data.objects.new(f"{self.slider.name}_ball", mesh)
        slider_ball.location = self.slider.location

        create_geometry_nodes_modifier(slider_ball, "slider_ball")
        self._set_geometry_node_keyframes(slider_ball)
        return slider_ball

    def create_full_slider_ball(self):
        """Erstellt einen Slider-Ball im FULL-Modus als UV-Sphäre."""
        radius = self._calculate_osu_radius()
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=self.slider.location)
        slider_ball = bpy.context.object
        slider_ball.name = f"{self.slider.name}_ball"
        return slider_ball

    def animate_slider_ball(self, slider_ball):
        """Animiert den Slider-Ball entlang des Pfads und setzt Viewport-Sichtbarkeit für FULL-Import."""
        self._apply_follow_path_constraint(slider_ball)
        self._set_follow_path_keyframes(slider_ball)

        if self.import_type == 'FULL':
            self._set_visibility_keyframes(slider_ball)

    def link_to_collection(self, slider_ball):
        """Verlinkt den Slider-Ball zur vorgesehenen Sammlung."""
        self.slider_balls_collection.objects.link(slider_ball)
        self._remove_from_other_collections(slider_ball)

    # Hilfsfunktionen

    def _create_empty_mesh(self, name):
        """Erstellt ein leeres Mesh mit einem einzelnen Vertex."""
        mesh = bpy.data.meshes.new(name)
        mesh.vertices.add(1)
        mesh.vertices[0].co = (0, 0, 0)
        mesh.use_auto_texspace = True
        return mesh

    def _set_geometry_node_keyframes(self, slider_ball):
        """Setzt Keyframes für Geometry Nodes-Attribute."""
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

    def _calculate_osu_radius(self):
        """Berechnet den osu!-Radius basierend auf der Circle Size (CS)."""
        circle_size = self.data_manager.calculate_adjusted_cs()
        return (54.4 - 4.48 * circle_size) / 2 * SCALE_FACTOR * 2

    def _apply_follow_path_constraint(self, slider_ball):
        """Wendet den Follow-Path-Constraint an den Slider-Ball an."""
        follow_path = slider_ball.constraints.new(type='FOLLOW_PATH')
        follow_path.target = self.slider
        follow_path.use_fixed_location = True
        follow_path.use_curve_follow = True
        follow_path.forward_axis = 'FORWARD_Y'
        follow_path.up_axis = 'UP_Z'

    def _set_follow_path_keyframes(self, slider_ball):
        """Setzt Keyframes für die Offset-Animation des Follow-Path-Constraints."""
        speed_multiplier = self.data_manager.speed_multiplier
        slider_multiplier = float(self.data_manager.osu_parser.difficulty_settings.get("SliderMultiplier", 1.4))
        inherited_multiplier = self._get_inherited_multiplier()
        effective_speed = slider_multiplier * inherited_multiplier
        adjusted_duration_frames = (self.slider_duration_frames / effective_speed) * speed_multiplier

        self.slider.data.use_path = True
        self.slider.data.path_duration = int(adjusted_duration_frames)

        repeat_duration_frames = adjusted_duration_frames / self.repeat_count if self.repeat_count > 0 else adjusted_duration_frames

        for repeat in range(self.repeat_count):
            repeat_start_frame = self.start_frame + repeat * repeat_duration_frames
            offset_start, offset_end = (0.0, 1.0) if repeat % 2 == 0 else (1.0, 0.0)

            self._set_keyframe(slider_ball, "offset_factor", repeat_start_frame, offset_start)
            self._set_keyframe(slider_ball, "offset_factor", repeat_start_frame + repeat_duration_frames, offset_end)

    def _set_visibility_keyframes(self, slider_ball):
        """Setzt Keyframes für die Viewport- und Render-Sichtbarkeit."""
        slider_ball.hide_viewport = True
        slider_ball.hide_render = True
        self._set_keyframe(slider_ball, "hide_viewport", self.start_frame - 1, True)
        self._set_keyframe(slider_ball, "hide_render", self.start_frame - 1, True)

        slider_ball.hide_viewport = False
        slider_ball.hide_render = False
        self._set_keyframe(slider_ball, "hide_viewport", self.start_frame, False)
        self._set_keyframe(slider_ball, "hide_render", self.start_frame, False)

        slider_ball.hide_viewport = True
        slider_ball.hide_render = True
        self._set_keyframe(slider_ball, "hide_viewport", self.end_frame, True)
        self._set_keyframe(slider_ball, "hide_render", self.end_frame, True)

    def _get_inherited_multiplier(self):
        """Berechnet den geerbten Geschwindigkeitsmultiplikator basierend auf Timing-Punkten."""
        timing_points = sorted(set(self.data_manager.beatmap_info["timing_points"]), key=lambda tp: tp[0])
        for offset, beat_length in timing_points:
            if self.slider_time >= offset and beat_length < 0:
                return -100 / beat_length
        return 1.0

    def _set_keyframe(self, obj, data_path, frame, value):
        """Hilfsfunktion zum Setzen eines Keyframes."""
        setattr(obj, data_path, value)
        obj.keyframe_insert(data_path=data_path, frame=int(frame))

    def _remove_from_other_collections(self, slider_ball):
        """Entfernt das Objekt aus allen anderen Sammlungen außer der vorgesehenen."""
        if slider_ball.users_collection:
            for col in slider_ball.users_collection:
                if col != self.slider_balls_collection:
                    col.objects.unlink(slider_ball)
