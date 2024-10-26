# osu_replay_data_manager.py

import bpy
import os
from .info_parser import OsuParser, OsrParser

class OsuReplayDataManager:
    def __init__(self, osu_file_path, osr_file_path):
        self.osu_parser = OsuParser(osu_file_path)
        self.osr_parser = OsrParser(osr_file_path)

    @property
    def beatmap_info(self):
        return {
            "approach_rate": float(self.osu_parser.difficulty_settings.get("ApproachRate", 5.0)),
            "circle_size": float(self.osu_parser.difficulty_settings.get("CircleSize", 5.0)),
            "bpm": self.osu_parser.bpm,
            "total_hitobjects": self.osu_parser.total_hitobjects,
            "audio_lead_in": self.osu_parser.audio_lead_in,
            "timing_points": self.osu_parser.timing_points,
            "general_settings": self.osu_parser.general_settings,
            "metadata": self.osu_parser.metadata,
            "events": self.osu_parser.events,
        }

    @property
    def replay_info(self):
        return {
            "mods": ','.join(self.osr_parser.mod_list) if self.osr_parser.mod_list else "Keine",
            "accuracy": self.osr_parser.calculate_accuracy(),
            "misses": self.osr_parser.misses,
            "max_combo": self.osr_parser.max_combo,
            "total_score": self.osr_parser.score,
        }

    @property
    def hitobjects(self):
        return self.osu_parser.hitobjects

    @property
    def replay_data(self):
        return self.osr_parser.replay_data

    @property
    def key_presses(self):
        return self.osr_parser.key_presses

    @property
    def mods(self):
        return self.osr_parser.mods

    def print_all_info(self):
        print("\n--- Beatmap Information ---")
        for key, value in self.beatmap_info.items():
            print(f"{key}: {value}")

        print("\n--- Replay Information ---")
        for key, value in self.replay_info.items():
            print(f"{key}: {value}")

        print("\n--- Hit Objects ---")
        print(self.hitobjects[:10])  # Nur die ersten 10 HitObjects zur Übersicht

        print("\n--- Replay Data (First 10 Events) ---")
        print(self.replay_data[:10])  # Nur die ersten 10 Replay-Events zur Übersicht

        print("\n--- Key Presses (First 10 Presses) ---")
        print(self.key_presses[:10])  # Nur die ersten 10 Tastendrücke zur Übersicht

    def import_audio(self):
        # Prüfen, ob der Audio-Dateiname in den General Settings existiert
        audio_filename = self.beatmap_info['general_settings'].get("AudioFilename")
        if not audio_filename:
            print("Keine Audio-Datei in den General Settings gefunden.")
            return

        # Vollständigen Pfad zur Audio-Datei erstellen
        osu_file_dir = os.path.dirname(self.osu_parser.osu_file_path)
        audio_path = os.path.join(osu_file_dir, audio_filename)

        # Überprüfen, ob die Datei existiert
        if not os.path.isfile(audio_path):
            print(f"Audio-Datei '{audio_filename}' nicht gefunden im Verzeichnis: {osu_file_dir}")
            return

        # Speaker-Objekt hinzufügen
        bpy.ops.object.speaker_add(location=(0, 0, 0))
        speaker = bpy.context.object
        speaker.name = "OsuAudioSpeaker"

        # Sound-Datei laden und dem Speaker-Objekt zuweisen
        sound = bpy.data.sounds.load(filepath=audio_path, check_existing=True)
        speaker.data.sound = sound

        # Playback einstellen (optional)
        speaker.data.volume = 1.0  # Lautstärke
        speaker.data.pitch = 1.0  # Playback-Geschwindigkeit
        print(f"Audio-Datei '{audio_filename}' erfolgreich importiert und dem Speaker hinzugefügt.")