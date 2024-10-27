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
            od = od * 1.4
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
        hit_window = hit_window_50  # Größtes Hit-Fenster

        speed_multiplier = calculate_speed_multiplier(self.mods)
        audio_lead_in = self.beatmap_info['audio_lead_in']

        key_presses = self.key_presses
        # Berechne die tatsächlichen Zeiten der Keypresses unter Berücksichtigung von Mods und Audio Lead-In
        key_press_times = [(kp['time'] / speed_multiplier) + audio_lead_in for kp in key_presses]

        for hitobject in self.hitobjects:
            hitobject_time = (hitobject.time / speed_multiplier) + audio_lead_in
            was_hit = False

            if hitobject.hit_type & 1:  # Kreis
                window_start = hitobject_time - hit_window
                window_end = hitobject_time + hit_window

                # Durchsuche die Keypresses innerhalb des Hit-Fensters
                for idx, kp_time in enumerate(key_press_times):
                    if window_start <= kp_time <= window_end:
                        kp = key_presses[idx]
                        if any([kp['k1'], kp['k2'], kp['m1'], kp['m2']]):
                            was_hit = True
                            break
                    elif kp_time > window_end:
                        break

                hitobject.was_hit = was_hit

            elif hitobject.hit_type & 2:  # Slider
                # Berechne die Slider-Dauer
                slider_duration_ms = self.calculate_slider_duration(hitobject)
                slider_end_time = (hitobject.time + slider_duration_ms) / speed_multiplier + audio_lead_in

                # Wir prüfen, ob während der Slider-Dauer eine Taste gedrückt wurde
                window_start = hitobject_time - hit_window
                window_end = slider_end_time + hit_window  # Etwas Puffer am Ende

                for idx, kp_time in enumerate(key_press_times):
                    if window_start <= kp_time <= window_end:
                        kp = key_presses[idx]
                        if any([kp['k1'], kp['k2'], kp['m1'], kp['m2']]):
                            was_hit = True
                            break
                    elif kp_time > window_end:
                        break

                # hitobject.was_hit = was_hit

                # Füge 'was_completed' hinzu
                was_completed = False
                if was_hit:
                    # Prüfe, ob während der gesamten Slider-Dauer die Tasten gehalten wurden
                    slider_window_start = hitobject_time
                    slider_window_end = slider_end_time
                    keys_held = True
                    for idx, kp_time in enumerate(key_press_times):
                        if slider_window_start <= kp_time <= slider_window_end:
                            kp = key_presses[idx]
                            if not any([kp['k1'], kp['k2'], kp['m1'], kp['m2']]):
                                keys_held = False
                                break
                        elif kp_time > slider_window_end:
                            break
                    was_completed = keys_held
                hitobject.was_hit = was_hit
                hitobject.was_completed = was_completed

            elif hitobject.hit_type & 8:  # Spinner
                # Berechne die Spinner-Dauer
                spinner_duration_ms = self.calculate_spinner_duration(hitobject)
                spinner_end_time = (hitobject.time + spinner_duration_ms) / speed_multiplier + audio_lead_in

                # Wir prüfen, ob der Spinner gestartet wurde
                window_start = hitobject_time - hit_window
                window_end = spinner_end_time + hit_window  # Etwas Puffer am Ende

                for idx, kp_time in enumerate(key_press_times):
                    if window_start <= kp_time <= window_end:
                        kp = key_presses[idx]
                        if any([kp['k1'], kp['k2'], kp['m1'], kp['m2']]):
                            was_hit = True
                            break
                    elif kp_time > window_end:
                        break

                # Füge 'was_completed' hinzu
                was_completed = False
                if was_hit:
                    # Prüfe, ob während der gesamten Spinner-Dauer die Tasten gehalten wurden
                    spinner_window_start = hitobject_time
                    spinner_window_end = spinner_end_time
                    keys_held = True
                    for idx, kp_time in enumerate(key_press_times):
                        if kp_time > spinner_window_end:
                            break
                        if spinner_window_start <= kp_time <= spinner_window_end:
                            kp = key_presses[idx]
                            if not any([kp['k1'], kp['k2'], kp['m1'], kp['m2']]):
                                keys_held = False
                                break
                    was_completed = keys_held
                hitobject.was_hit = was_hit
                hitobject.was_completed = was_completed

            else:
                # Andere HitObject-Typen können ähnlich behandelt werden
                hitobject.was_hit = False  # Standardmäßig False setzen

            # Debug-Ausgabe für jedes HitObject
            if hitobject.hit_type & 1:
                print(f"HitObject at time {hitobject.time} was_hit: {hitobject.was_hit}")
            elif hitobject.hit_type & 2:
                print(
                    f"HitObject at time {hitobject.time} was_hit: {hitobject.was_hit}, was_completed: {hitobject.was_completed}")
            elif hitobject.hit_type & 8:
                print(
                    f"HitObject at time {hitobject.time} was_hit: {hitobject.was_hit}, was_completed: {hitobject.was_completed}")
            else:
                print(f"HitObject at time {hitobject.time} was_hit: {hitobject.was_hit}")

    def calculate_slider_duration(self, hitobject):
        start_time_ms = hitobject.time
        repeat_count = int(hitobject.extras[1]) if len(hitobject.extras) > 1 else 1
        pixel_length = float(hitobject.extras[2]) if len(hitobject.extras) > 2 else 100.0
        speed_multiplier = calculate_speed_multiplier(self.mods)
        slider_multiplier = float(self.osu_parser.difficulty_settings.get("SliderMultiplier", 1.4))
        timing_points = self.osu_parser.timing_points

        beat_duration = 500  # Standardwert
        inherited_multiplier = 1.0
        current_beat_length = None

        for offset, beat_length in timing_points:
            if start_time_ms >= offset:
                if beat_length < 0:
                    inherited_multiplier = -100 / beat_length
                else:
                    current_beat_length = beat_length
            else:
                break

        if current_beat_length is not None and current_beat_length > 0:
            beat_duration = current_beat_length

        slider_duration_ms = (pixel_length / (
                    slider_multiplier * 100)) * beat_duration * repeat_count * inherited_multiplier
        slider_duration_ms /= speed_multiplier

        return slider_duration_ms

    def calculate_spinner_duration(self, hitobject):
        start_time_ms = hitobject.time
        if hitobject.extras:
            end_time_ms = int(hitobject.extras[0])
            spinner_duration_ms = (end_time_ms - start_time_ms)
            speed_multiplier = calculate_speed_multiplier(self.mods)
            spinner_duration_ms /= speed_multiplier
            return spinner_duration_ms
        else:
            print(f"Keine Endzeit für Spinner bei {start_time_ms} ms gefunden.")
            return 0  # Keine Dauer berechenbar

    def calculate_approach_rate(self):
        ar = float(self.osu_parser.difficulty_settings.get("ApproachRate", 5.0))
        original_ar = ar  # Speichere die ursprüngliche AR für Debugging

        # Mods berücksichtigen
        if self.mods & MOD_HARD_ROCK:
            ar = ar * 1.4
            print(f"[Debug] Hard Rock Mod aktiviert. Original AR: {original_ar}, Angepasste AR: {ar}")
        elif self.mods & MOD_EASY:
            ar = ar * 0.5
            print(f"[Debug] Easy Mod aktiviert. Original AR: {original_ar}, Angepasste AR: {ar}")
        else:
            print(f"[Debug] Keine AR-beeinflussenden Mods aktiviert. AR bleibt bei: {ar}")

        return ar

    def calculate_preempt_time(self, ar):
        if ar < 5:
            preempt = 1800 - (120 * ar)
            print(f"[Debug] AR < 5. Berechnete Preempt-Zeit: {preempt} ms für AR: {ar}")
        else:
            preempt = 1200 - (150 * (ar - 5))
            print(f"[Debug] AR >= 5. Berechnete Preempt-Zeit: {preempt} ms für AR: {ar}")
        return preempt  # in Millisekunden