# offset_calculator.py

import os
from .constants import MOD_DOUBLE_TIME, MOD_HALF_TIME
from .utils import get_ms_per_frame

def calculate_speed_multiplier(mods):
    speed_multiplier = 1.0
    if mods & MOD_DOUBLE_TIME:
        speed_multiplier = 1.5
    elif mods & MOD_HALF_TIME:
        speed_multiplier = 0.75
    return speed_multiplier

def calculate_offsets(osu_parser, osr_parser):
    # Lade den AudioLeadIn-Wert
    audio_lead_in = osu_parser.audio_lead_in

    # Bestimme den Geschwindigkeitsmultiplikator basierend auf den Mods
    mods = osr_parser.mods
    speed_multiplier = calculate_speed_multiplier(mods)

    # Lade die HitObject-Zeiten
    hitobject_times = [obj.time for obj in osu_parser.hitobjects]
    if not hitobject_times:
        raise ValueError("Keine HitObjects in der .osu-Datei gefunden.")

    first_hitobject_time = hitobject_times[0]
    first_replay_time = get_first_replay_event_time(osr_parser.replay_data)

    # Berechne die angepassten Zeiten
    adjusted_first_hitobject_time = (first_hitobject_time + audio_lead_in) / speed_multiplier

    # Berechne den Offset in Millisekunden
    offset_ms = adjusted_first_hitobject_time - first_replay_time

    # Berechne den Offset in Frames
    offset_frames = offset_ms / get_ms_per_frame()

    # Rückgabe aller relevanten Werte
    return {
        'speed_multiplier': speed_multiplier,
        'offset_ms': offset_ms,
        'offset_frames': offset_frames,
        'first_hitobject_time': adjusted_first_hitobject_time,
        'first_replay_time': first_replay_time,
    }

def get_first_replay_event_time(replay_data):
    total_time = 0
    for event in replay_data:
        total_time += event.time_delta
        if event.x != -256 and event.y != -256:
            return total_time
    return total_time  # Falls alle Events bei (-256, -256) sind
