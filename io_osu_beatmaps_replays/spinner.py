# spinner.py

import bpy
import math
from .utils import map_osu_to_blender, get_ms_per_frame
from .geometry_nodes import create_geometry_nodes_modifier_spinner
from .constants import SPINNER_CENTER_X, SPINNER_CENTER_Y
from .osu_replay_data_manager import OsuReplayDataManager
from .hitobjects import HitObject

class SpinnerCreator:
    def __init__(self, hitobject: HitObject, global_index: int, spinners_collection, settings: dict, data_manager: OsuReplayDataManager):
        self.hitobject = hitobject
        self.global_index = global_index
        self.spinners_collection = spinners_collection
        self.settings = settings
        self.data_manager = data_manager
        self.create_spinner()

    def create_spinner(self):
        approach_rate = self.data_manager.calculate_approach_rate()
        preempt_ms = self.data_manager.calculate_preempt_time(approach_rate)
        preempt_frames = preempt_ms / get_ms_per_frame()

        audio_lead_in_frames = self.data_manager.beatmap_info["audio_lead_in"] / get_ms_per_frame()

        x = SPINNER_CENTER_X
        y = SPINNER_CENTER_Y
        time_ms = self.hitobject.time
        speed_multiplier = self.settings.get('speed_multiplier', 1.0)
        start_frame = ((time_ms / speed_multiplier) / get_ms_per_frame()) + audio_lead_in_frames
        early_start_frame = start_frame - preempt_frames

        # Endzeit des Spinners ermitteln
        if self.hitobject.extras:
            end_time_ms = int(self.hitobject.extras[0])
            end_frame = ((end_time_ms / speed_multiplier) / get_ms_per_frame())
        else:
            print(f"Keine Endzeit für Spinner bei {time_ms} ms gefunden.")
            return

        corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1,
            depth=0.1,
            location=(corrected_x, corrected_y, corrected_z),
            rotation=(math.radians(90), 0, 0)
        )
        spinner = bpy.context.object
        spinner.name = f"{self.global_index:03d}_spinner_{time_ms}"

        # Spinner-Dauer berechnen
        spinner_duration_ms = end_time_ms - time_ms
        scene_fps = bpy.context.scene.render.fps
        spinner_duration_frames = spinner_duration_ms / (1000 / scene_fps)

        spinner["was_hit"] = False  # Initial value
        spinner.keyframe_insert(data_path='["was_hit"]', frame=start_frame - 1)

        spinner["was_hit"] = self.hitobject.was_hit
        spinner.keyframe_insert(data_path='["was_hit"]', frame=start_frame)

        # Setze 'was_completed' initial auf False und keyframe es vor dem Start
        spinner["was_completed"] = False
        spinner.keyframe_insert(data_path='["was_completed"]', frame=start_frame - 1)

        # Setze 'was_completed' auf den tatsächlichen Wert zum Ende des Spinners
        spinner["was_completed"] = self.hitobject.was_completed
        spinner.keyframe_insert(data_path='["was_completed"]', frame=end_frame)

        # Setzen der Keyframes und Eigenschaften
        spinner["show"] = False  # Startwert: Nicht sichtbar
        spinner.keyframe_insert(data_path='["show"]', frame=(early_start_frame - 1))

        spinner["show"] = True
        spinner.keyframe_insert(data_path='["show"]', frame=early_start_frame)


        # Füge die Spinner-Dauer hinzu
        spinner["spinner_duration_ms"] = spinner_duration_ms
        spinner["spinner_duration_frames"] = spinner_duration_frames

        self.spinners_collection.objects.link(spinner)
        # Aus anderen Collections entfernen
        if spinner.users_collection:
            for col in spinner.users_collection:
                if col != self.spinners_collection:
                    col.objects.unlink(spinner)

        create_geometry_nodes_modifier_spinner(spinner, spinner.name)
