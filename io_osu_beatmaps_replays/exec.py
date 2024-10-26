# exec.py

import bpy
import os
from .osu_replay_data_manager import OsuReplayDataManager
from .import_objects import import_hitobjects
from .cursor import create_cursor, animate_cursor
from .utils import create_collection
from .mod_functions import calculate_speed_multiplier

def main_execution(context):
    props = context.scene.osu_importer_props
    osu_file_path = bpy.path.abspath(props.osu_file)
    osr_file_path = bpy.path.abspath(props.osr_file)

    if not os.path.isfile(osu_file_path) or not os.path.isfile(osr_file_path):
        context.window_manager.popup_menu(
            lambda self, ctx: self.layout.label(text="Die angegebene .osu- oder .osr-Datei existiert nicht."),
            title="Fehler",
            icon='ERROR'
        )
        return {'CANCELLED'}

    # Erstelle eine zentrale Instanz für osu! und Replay-Daten
    data_manager = OsuReplayDataManager(osu_file_path, osr_file_path)

    # Setze die neuen Eigenschaften für Beatmap- und Replay-Informationen
    beatmap_info = data_manager.beatmap_info
    props.approach_rate = beatmap_info["approach_rate"]
    props.circle_size = beatmap_info["circle_size"]
    props.bpm = beatmap_info["bpm"]
    props.total_hitobjects = beatmap_info["total_hitobjects"]

    replay_info = data_manager.replay_info
    props.formatted_mods = replay_info["mods"]
    props.accuracy = replay_info["accuracy"]
    props.misses = replay_info["misses"]

    speed_multiplier = calculate_speed_multiplier(data_manager.mods)

    # Importiere die HitObjects
    import_hitobjects(data_manager, speed_multiplier)

    # Erstelle und animiere den Cursor
    cursor_collection = create_collection("Cursor")
    cursor = create_cursor(cursor_collection, data_manager)
    if cursor:
        animate_cursor(cursor, data_manager.replay_data, data_manager.key_presses, speed_multiplier)
    else:
        print("Cursor konnte nicht erstellt werden.")

    # Setze Frame Start und End basierend auf Animation
    scene = bpy.context.scene
    scene.frame_start = int(min([obj.animation_data.action.frame_range[0] for obj in bpy.data.objects if
                                 obj.animation_data and obj.animation_data.action]))
    scene.frame_end = int(max([obj.animation_data.action.frame_range[1] for obj in bpy.data.objects if
                               obj.animation_data and obj.animation_data.action]))

    return {'FINISHED'}
