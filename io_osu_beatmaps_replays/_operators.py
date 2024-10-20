# osu_importer/_operators.py

import bpy
from bpy.types import Operator
import os

from .constants import MOD_DOUBLE_TIME, MOD_HALF_TIME
from .utils import get_ms_per_frame, create_collection
from ._io import load_hitobject_times, get_audio_lead_in, get_first_replay_event_time
from .hitobjects import load_and_create_hitobjects
from .cursor import create_animated_cursor, animate_cursor

class OSU_OT_Import(Operator):
    bl_idname = "osu_importer.import"
    bl_label = "Importieren"
    bl_description = "Importiert die ausgewählte Beatmap und Replay"

    def execute(self, context):
        result = self.main(context)
        return result

    def main(self, context):
        try:
            import osrparse
        except ImportError:
            self.report({'ERROR'}, "Das benötigte Modul 'osrparse' ist nicht installiert. Bitte installiere es manuell.")
            return {'CANCELLED'}

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
        offset = adjusted_first_hitobject_time / get_ms_per_frame()
        #adjusted_first_replay_time = first_replay_time

        #offset = adjusted_first_hitobject_time  - adjusted_first_replay_time

        # Speichere die Werte
        props.detected_first_hitobject_time = offset
        props.detected_first_replay_time = first_replay_time
        props.detected_offset = offset

        # Speichere den Cursor-Offset in den Properties
        props.calculated_cursor_offset = offset

        # Verwende automatischen oder manuellen Offset
        if props.use_auto_offset:
            final_offset = offset
        else:
            final_offset = props.manual_offset

        print(f"Verwendeter Zeit-Offset: {final_offset} ms")
        print(f"Geschwindigkeitsmultiplikator: {speed_multiplier}")
        print(f"Erste Hitobject-Zeit: {offset} ms")
        print(f"Erste Replay-Event-Zeit: {first_replay_time} ms")

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
            animate_cursor(cursor, replay.replay_data, final_offset + first_replay_time, speed_multiplier)
            #animate_cursor(cursor, replay.replay_data, adjusted_first_hitobject_time, speed_multiplier)

        else:
            self.report({'WARNING'}, "Cursor konnte nicht erstellt werden.")

        # Setze den Startframe der Szene
        scene_start_time = min(adjusted_first_hitobject_time, first_replay_time)
        bpy.context.scene.frame_start = int(scene_start_time / get_ms_per_frame())

        self.report({'INFO'}, "Import abgeschlossen.")
        return {'FINISHED'}
