# osu_importer/operators.py

import bpy
from bpy.types import Operator
from .properties import OSUImporterProperties
from .utils import (
    create_collection,
    get_audio_lead_in,
    get_first_replay_event_time,
    load_hitobject_times,
    shift_cursor_keyframes,
    SCALE_FACTOR,
    get_ms_per_frame
)
import os

# Versuche, osrparse zu importieren, und installiere es bei Bedarf
try:
    import osrparse
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "osrparse"])
    import osrparse

class OSU_OT_Import(Operator):
    bl_idname = "osu_importer.import"
    bl_label = "Importieren"
    bl_description = "Importiert die ausgewählte Beatmap und Replay"

    def execute(self, context):
        result = self.main(context)
        return result

    def main(self, context):
        from .utils import (
            load_and_create_hitobjects,
            create_circle_at_position,
            create_slider_curve,
            create_spinner_at_position,
            create_animated_cursor,
            animate_cursor
        )
        props = context.scene.osu_importer_props
        osu_file_path = bpy.path.abspath(props.osu_file)
        osr_file_path = bpy.path.abspath(props.osr_file)

        if not os.path.isfile(osu_file_path):
            self.report({'ERROR'}, "Die angegebene .osu-Datei existiert nicht.")
            return {'CANCELLED'}
        if not os.path.isfile(osr_file_path):
            self.report({'ERROR'}, "Die angegebene .osr-Datei existiert nicht.")
            return {'CANCELLED'}

        # Lade das Replay
        try:
            replay = osrparse.Replay.from_path(osr_file_path)
        except Exception as e:
            self.report({'ERROR'}, f"Fehler beim Laden des Replays: {e}")
            return {'CANCELLED'}

        # Lade den AudioLeadIn-Wert
        audio_lead_in = get_audio_lead_in(osu_file_path)

        # Bestimme den Geschwindigkeitsmultiplikator basierend auf den Mods
        mods = replay.mods
        speed_multiplier = 1.0

        # Definiere die Mod-Konstanten
        MOD_DOUBLE_TIME = 64
        MOD_HALF_TIME = 256

        if mods & MOD_DOUBLE_TIME:
            speed_multiplier = 1.5
        elif mods & MOD_HALF_TIME:
            speed_multiplier = 0.75

        # Berechne den Offset
        hitobject_times = load_hitobject_times(osu_file_path)
        if not hitobject_times:
            self.report({'ERROR'}, "Keine HitObjects in der .osu-Datei gefunden.")
            return {'CANCELLED'}

        first_hitobject_time = hitobject_times[0]
        first_replay_time = get_first_replay_event_time(replay.replay_data)

        # Berechne die angepassten Zeiten
        adjusted_first_hitobject_time = (first_hitobject_time + audio_lead_in) / speed_multiplier
        adjusted_first_replay_time = first_replay_time  # Entferne - standard_replay_lead_in

        offset = adjusted_first_hitobject_time - adjusted_first_replay_time

        # Speichere die Werte
        props.detected_first_hitobject_time = adjusted_first_hitobject_time
        props.detected_first_replay_time = adjusted_first_replay_time
        props.detected_offset = offset

        # Berechne den Cursor-Offset (Hälfte der Zeit des ersten HitObjects)
        cursor_offset = adjusted_first_hitobject_time / 2

        # Speichere den Cursor-Offset in den Properties (optional)
        props.cursor_offset = cursor_offset

        # Verwende automatischen oder manuellen Offset
        if props.use_auto_offset:
            final_offset = offset
        else:
            final_offset = props.manual_offset

        print(f"Verwendeter Zeit-Offset: {final_offset} ms")
        print(f"Geschwindigkeitsmultiplikator: {speed_multiplier}")
        print(f"Erste Hitobject-Zeit: {adjusted_first_hitobject_time} ms")
        print(f"Erste Replay-Event-Zeit: {adjusted_first_replay_time} ms")
        print(f"Berechneter Cursor-Offset: {cursor_offset} ms")

        # Erstelle Collections
        circles_collection = create_collection("Circles")
        sliders_collection = create_collection("Sliders")
        spinners_collection = create_collection("Spinners")
        cursor_collection = create_collection("Cursor")

        # Lade und erstelle Hitobjects
        load_and_create_hitobjects(
            osu_file_path,
            circles_collection,
            sliders_collection,
            spinners_collection,
            final_offset,
            speed_multiplier
        )

        # Erstelle und animiere den Cursor
        cursor = create_animated_cursor(cursor_collection)
        if cursor is not None:
            animate_cursor(cursor, replay.replay_data, final_offset + cursor_offset)
        else:
            self.report({'WARNING'}, "Cursor konnte nicht erstellt werden.")

        # Setze den Startframe der Szene
        scene_start_time = min(adjusted_first_hitobject_time, adjusted_first_replay_time)
        bpy.context.scene.frame_start = int(scene_start_time / get_ms_per_frame())

        self.report({'INFO'}, "Import abgeschlossen.")
        return {'FINISHED'}

class OSU_OT_AdjustCursorOffset(Operator):
    bl_idname = "osu_importer.adjust_cursor_offset"
    bl_label = "Cursor Offset Anwenden"
    bl_description = "Verschiebt die Cursor-Keyframes um den angegebenen Offset"

    def execute(self, context):
        from .properties import OSUImporterProperties
        from .utils import shift_cursor_keyframes

        props = context.scene.osu_importer_props
        cursor_offset = props.cursor_offset
        shift_cursor_keyframes("Cursor", cursor_offset)
        self.report({'INFO'}, f"Cursor-Keyframes um {cursor_offset} ms verschoben.")
        return {'FINISHED'}
