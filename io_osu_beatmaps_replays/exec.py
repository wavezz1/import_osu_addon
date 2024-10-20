# exec.py

import bpy
import os
from .info_parser import OsuParser, OsrParser
from .import_objects import import_hitobjects
from .cursor import create_cursor, animate_cursor
from .utils import create_collection, get_ms_per_frame
from .offset_calculator import calculate_offsets

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

    # Setze die neuen Eigenschaften für Beatmap-Informationen
    props.approach_rate = float(osu_parser.difficulty_settings.get("ApproachRate", 5))
    props.circle_size = float(osu_parser.difficulty_settings.get("CircleSize", 5))
    props.bpm = osu_parser.bpm
    props.total_hitobjects = osu_parser.total_hitobjects

    # Setze die neuen Eigenschaften für Replay-Informationen
    props.formatted_mods = ','.join(osr_parser.mod_list) if osr_parser.mod_list else "Keine"
    props.accuracy = osr_parser.calculate_accuracy()
    props.misses = osr_parser.calculate_misses()

    # Berechne den Offset und andere notwendige Werte
    try:
        offset_data = calculate_offsets(osu_parser, osr_parser)
    except ValueError as e:
        context.window_manager.popup_menu(
            lambda self, ctx: self.layout.label(text=str(e)),
            title="Fehler",
            icon='ERROR'
        )
        return {'CANCELLED'}

    speed_multiplier = offset_data['speed_multiplier']
    offset_frames = offset_data['offset_frames']
    offset_ms = offset_data['offset_ms']
    first_hitobject_time = offset_data['first_hitobject_time']
    first_replay_time = offset_data['first_replay_time']

    # Speichere die Werte für die Anzeige in der UI
    props.detected_first_hitobject_time = first_hitobject_time
    props.detected_first_replay_time = first_replay_time
    props.detected_offset = offset_ms

    # Verwende automatischen oder manuellen Offset
    if props.use_auto_offset:
        final_offset_frames = offset_frames
    else:
        final_offset_frames = props.manual_offset / get_ms_per_frame()
        props.detected_offset = props.manual_offset  # Aktualisiere den Offset für die UI

    # Verbesserter Offset-Text
    used_offset_ms = final_offset_frames * get_ms_per_frame()
    print(f"Verwendeter Zeit-Offset: {used_offset_ms:.2f} ms")
    print(f"Geschwindigkeitsmultiplikator: {speed_multiplier}")
    print(f"Erste HitObject-Zeit: {first_hitobject_time:.2f} ms")
    print(f"Erste Replay-Event-Zeit: {first_replay_time:.2f} ms")

    # Importiere die HitObjects
    import_hitobjects(osu_parser, final_offset_frames, speed_multiplier)

    # Erstelle und animiere den Cursor
    cursor_collection = create_collection("Cursor")
    cursor = create_cursor(cursor_collection)
    if cursor is not None:
        animate_cursor(cursor, osr_parser.replay_data, final_offset_frames, speed_multiplier)
    else:
        print("Cursor konnte nicht erstellt werden.")

    # Setze den Startframe der Szene
    scene_start_time_ms = min(first_hitobject_time, first_replay_time)
    bpy.context.scene.frame_start = int((scene_start_time_ms / get_ms_per_frame()) + final_offset_frames)

    return {'FINISHED'}
