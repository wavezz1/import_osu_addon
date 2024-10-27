# osu_replay_data_manager.py

import bpy
import os
from .info_parser import OsuParser, OsrParser
from .constants import MOD_DOUBLE_TIME, MOD_HALF_TIME, MOD_HARD_ROCK, MOD_EASY
from .mod_functions import calculate_speed_multiplier
from .hitobjects import HitObjectsProcessor

class OsuReplayDataManager:
    def __init__(self, osu_file_path, osr_file_path):
        self.osu_parser = OsuParser(osu_file_path)
        self.osr_parser = OsrParser(osr_file_path)
        self.hitobjects_processor = HitObjectsProcessor(self)

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
        # Kombiniere alle verarbeiteten HitObjects aus dem HitObjectsProcessor
        return (
                self.hitobjects_processor.circles +
                self.hitobjects_processor.sliders +
                self.hitobjects_processor.spinners
        )
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
        speaker.data.attenuation = 0.0  # Keine Distanz-Dämpfung
        speaker.data.distance_max = 10000.0  # Hoher Wert für maximale Reichweite
        speaker.data.distance_reference = 0.1  # Geringer Wert für gleichbleibende Lautstärke

        # Playback Geschwindigkeit (Pitch) entsprechend Modifikatoren anpassen
        pitch = 1.0
        if self.mods & MOD_DOUBLE_TIME:
            pitch = 1.5
        elif self.mods & MOD_HALF_TIME:
            pitch = 0.75
        speaker.data.pitch = pitch

        print(f"Audio-Datei '{audio_filename}' erfolgreich importiert und mit {pitch}x Pitch dem Speaker hinzugefügt.")

    def calculate_hit_windows(self):
        od = float(self.osu_parser.difficulty_settings.get("OverallDifficulty", 5.0))

        # Mods berücksichtigen
        if self.mods & MOD_HARD_ROCK:
            od = min(10, od * 1.4)
        elif self.mods & MOD_EASY:
            od = od * 0.5

        # Hit Windows berechnen
        hit_window_300 = 80 - (6 * od)
        hit_window_100 = 140 - (8 * od)
        hit_window_50 = 200 - (10 * od)

        # Negative Werte vermeiden
        hit_window_300 = max(hit_window_300, 0)
        hit_window_100 = max(hit_window_100, 0)
        hit_window_50 = max(hit_window_50, 0)

        return hit_window_300, hit_window_100, hit_window_50

    def check_hits(self):
        hit_window_300, hit_window_100, hit_window_50 = self.calculate_hit_windows()
        hit_window = hit_window_50  # Wir verwenden das größte Fenster für die Treffererkennung

        speed_multiplier = calculate_speed_multiplier(self.mods)
        audio_lead_in = self.beatmap_info['audio_lead_in']

        key_presses = self.key_presses
        current_time = 0
        event_index = 0
        key_state = {'k1': False, 'k2': False, 'm1': False, 'm2': False}

        for hitobject in self.hitobjects:
            # Entferne die Bedingung, die nur Kreise berücksichtigt
            # if not (hitobject.hit_type & 1):  # Nur Kreise
            #     continue

            hitobject_time = (hitobject.time / speed_multiplier) + audio_lead_in
            window_start = hitobject_time - hit_window
            window_end = hitobject_time + hit_window
            was_hit = False

            while event_index < len(key_presses) and current_time <= window_end:
                kp = key_presses[event_index]
                time_delta = kp['time'] / speed_multiplier
                current_time += time_delta

                # Tastenzustände aktualisieren
                key_state['k1'] = kp['k1']
                key_state['k2'] = kp['k2']
                key_state['m1'] = kp['m1']
                key_state['m2'] = kp['m2']

                if window_start <= current_time <= window_end:
                    if any(key_state.values()):
                        was_hit = True
                        break
                elif current_time > window_end:
                    break

                event_index += 1

            hitobject.was_hit = was_hit