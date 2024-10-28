# spinner.py

import bpy
import math
from .utils import map_osu_to_blender, get_ms_per_frame
from .geometry_nodes import create_geometry_nodes_modifier_spinner
from .constants import SPINNER_CENTER_X, SPINNER_CENTER_Y
from .osu_replay_data_manager import OsuReplayDataManager
from .hitobjects import HitObject
from .exec import connect_attributes_with_drivers

class SpinnerCreator:
    def __init__(self, hitobject: HitObject, global_index: int, spinners_collection, settings: dict, data_manager: OsuReplayDataManager):
        self.hitobject = hitobject
        self.global_index = global_index
        self.spinners_collection = spinners_collection
        self.settings = settings
        self.data_manager = data_manager
        self.create_spinner()

    def create_spinner(self):
        approach_rate = self.data_manager.calculate_adjusted_ar()
        preempt_frames = self.data_manager.calculate_preempt_time(approach_rate) / get_ms_per_frame()
        audio_lead_in_frames = self.data_manager.beatmap_info["audio_lead_in"] / get_ms_per_frame()

        start_frame = (self.hitobject.time / self.settings.get('speed_multiplier', 1.0)) / get_ms_per_frame() + audio_lead_in_frames
        early_start_frame = start_frame - preempt_frames

        if self.hitobject.extras:
            end_time_ms = int(self.hitobject.extras[0])
            end_frame = end_time_ms / self.settings.get('speed_multiplier', 1.0) / get_ms_per_frame()
        else:
            print(f"No end time found for spinner at {self.hitobject.time} ms.")
            return

        corrected_x, corrected_y, corrected_z = map_osu_to_blender(SPINNER_CENTER_X, SPINNER_CENTER_Y)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1,
            depth=0.1,
            location=(corrected_x, corrected_y, corrected_z),
            rotation=(math.radians(90), 0, 0)
        )
        spinner = bpy.context.object
        spinner.name = f"{self.global_index:03d}_spinner_{self.hitobject.time}"

        spinner_duration_ms = end_time_ms - self.hitobject.time
        scene_fps = bpy.context.scene.render.fps
        spinner_duration_frames = spinner_duration_ms / (1000 / scene_fps)

        spinner["was_hit"] = self.hitobject.was_hit
        spinner.keyframe_insert(data_path='["was_hit"]', frame=start_frame)

        spinner["was_completed"] = self.hitobject.was_completed
        spinner.keyframe_insert(data_path='["was_completed"]', frame=end_frame)

        spinner["show"] = True
        spinner.keyframe_insert(data_path='["show"]', frame=early_start_frame)

        spinner["spinner_duration_ms"] = spinner_duration_ms
        spinner["spinner_duration_frames"] = spinner_duration_frames

        self.spinners_collection.objects.link(spinner)
        if spinner.users_collection:
            for col in spinner.users_collection:
                if col != self.spinners_collection:
                    col.objects.unlink(spinner)

        # Geometry Nodes Modifier hinzufügen
        node_group_name = f"Geometry Nodes Spinner {self.global_index:03d}"
        create_geometry_nodes_modifier_spinner(spinner, node_group_name)

        # Fahrer (Drivers) verbinden
        connect_attributes_with_drivers(spinner, {
            "show": 'BOOLEAN',
            "spinner_duration_ms": 'FLOAT',
            "spinner_duration_frames": 'FLOAT',
            "was_hit": 'BOOLEAN',
            "was_completed": 'BOOLEAN'
        })