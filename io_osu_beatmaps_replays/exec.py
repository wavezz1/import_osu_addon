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
        return {'CANCELLED'}, None

    # Erstelle eine zentrale Instanz für osu! und Replay-Daten
    data_manager = OsuReplayDataManager(osu_file_path, osr_file_path)
    data_manager.print_all_info()
    data_manager.import_audio()

    # Importiere die HitObjects
    import_hitobjects(data_manager, calculate_speed_multiplier(data_manager.mods))

    # Erstelle und animiere den Cursor
    cursor_collection = create_collection("Cursor")
    cursor = create_cursor(cursor_collection, data_manager)
    if cursor is not None:
        animate_cursor(cursor, data_manager.replay_data, data_manager.key_presses, calculate_speed_multiplier(data_manager.mods))
    else:
        print("Cursor konnte nicht erstellt werden.")

    # Setze Frame Start und End basierend auf Animation
    scene = bpy.context.scene
    scene.frame_start = int(min([obj.animation_data.action.frame_range[0] for obj in bpy.data.objects if
                                 obj.animation_data and obj.animation_data.action]))
    scene.frame_end = int(max([obj.animation_data.action.frame_range[1] for obj in bpy.data.objects if
                               obj.animation_data and obj.animation_data.action]))

    # Erzwinge ein Update des View Layers, um alle Änderungen anzuwenden
    bpy.context.view_layer.update()

    return {'FINISHED'}, data_manager