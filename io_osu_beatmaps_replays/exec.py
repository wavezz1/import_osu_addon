# exec.py

import bpy
import os
from .info_parser import OsuParser, OsrParser
from .import_objects import import_hitobjects
from .cursor import create_cursor, animate_cursor

from .utils import create_collection
from .mod_functions import calculate_speed_multiplier

def main_execution(context):
    props = context.scene.osu_importer_props
    osu_file_path = bpy.path.abspath(props.osu_file)
    osr_file_path = bpy.path.abspath(props.osr_file)

    if not os.path.isfile(osu_file_path):
        context.window_manager.popup_menu(
            lambda self, ctx: self.layout.label(text="Die angegebene .osu-Datei existiert nicht."),
            title="Fehler",
            icon='ERROR'
        )
        return {'CANCELLED'}
    if not os.path.isfile(osr_file_path):
        context.window_manager.popup_menu(
            lambda self, ctx: self.layout.label(text="Die angegebene .osr-Datei existiert nicht."),
            title="Fehler",
            icon='ERROR'
        )
        return {'CANCELLED'}

    osu_parser = OsuParser(osu_file_path)
    osr_parser = OsrParser(osr_file_path)

    # Keypresses aus dem Replay extrahieren
    key_presses = osr_parser.parse_key_presses()

    # Setze die neuen Eigenschaften für Beatmap-Informationen

    props.approach_rate = float(osu_parser.difficulty_settings.get("ApproachRate", 5))
    props.circle_size = float(osu_parser.difficulty_settings.get("CircleSize", 5))
    props.bpm = osu_parser.bpm
    props.total_hitobjects = osu_parser.total_hitobjects


    # Setze die neuen Eigenschaften für Replay-Informationen
    props.formatted_mods = ','.join(osr_parser.mod_list) if osr_parser.mod_list else "Keine"
    props.accuracy = osr_parser.calculate_accuracy()
    props.misses = osr_parser.calculate_misses()

    speed_multiplier = calculate_speed_multiplier(osr_parser.mods)

    # Importiere die HitObjects
    import_hitobjects(osu_parser, speed_multiplier)

    # Erstelle und animiere den Cursor
    cursor_collection = create_collection("Cursor")
    cursor = create_cursor(cursor_collection)
    if cursor is not None:
        animate_cursor(cursor, osr_parser.replay_data, key_presses, speed_multiplier)  # Übergabe von key_presses
    else:
        print("Cursor konnte nicht erstellt werden.")

    return {'FINISHED'}
