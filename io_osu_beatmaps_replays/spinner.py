# spinner.py

import bpy
import math
from .utils import map_osu_to_blender, get_ms_per_frame
from .geometry_nodes import create_geometry_nodes_modifier_spinner
from .constants import SPINNER_CENTER_X, SPINNER_CENTER_Y
from .hitobjects import HitObject

class SpinnerCreator:
    def __init__(self, hitobject: HitObject, global_index: int, spinners_collection, settings: dict):
        self.hitobject = hitobject
        self.global_index = global_index
        self.spinners_collection = spinners_collection
        self.settings = settings
        self.create_spinner()

    def create_spinner(self):
        x = SPINNER_CENTER_X
        y = SPINNER_CENTER_Y
        time_ms = self.hitobject.time
        speed_multiplier = self.settings.get('speed_multiplier', 1.0)
        start_frame = ((time_ms / speed_multiplier) / get_ms_per_frame())
        early_start_frame = start_frame - self.settings.get('early_frames', 5)

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
            rotation=(math.radians(90), 0, 0)  # Drehung um 90 Grad um die X-Achse
        )
        spinner = bpy.context.object
        spinner.name = f"{self.global_index:03d}_spinner_{time_ms}"

        # Spinner-Dauer berechnen
        spinner_duration_ms = end_time_ms - time_ms
        scene_fps = bpy.context.scene.render.fps
        spinner_duration_frames = spinner_duration_ms / (1000 / scene_fps)

        # Setzen der Keyframes und Eigenschaften
        spinner["show"] = False  # Startwert: Nicht sichtbar
        spinner.keyframe_insert(data_path='["show"]', frame=(early_start_frame - 1))

        spinner["show"] = True
        spinner.keyframe_insert(data_path='["show"]', frame=early_start_frame)

        # Ausblenden am Ende
        spinner["show"] = True
        spinner.keyframe_insert(data_path='["show"]', frame=(end_frame - 1))

        spinner["show"] = False
        spinner.keyframe_insert(data_path='["show"]', frame=end_frame)

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