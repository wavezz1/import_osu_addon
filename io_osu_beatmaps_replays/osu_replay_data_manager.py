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
        print(self.hitobjects[:10])

        print("\n--- Replay Data (First 10 Events) ---")
        print(self.replay_data[:10])

        print("\n--- Key Presses (First 10 Presses) ---")
        print(self.key_presses[:10])

    def import_audio(self):
        audio_filename = self.beatmap_info['general_settings'].get("AudioFilename")
        if not audio_filename:
            print("No audio file found in general settings.")
            return

        osu_file_dir = os.path.dirname(self.osu_parser.osu_file_path)
        audio_path = os.path.join(osu_file_dir, audio_filename)

        if not os.path.isfile(audio_path):
            print(f"Audio file '{audio_filename}' not found in directory: {osu_file_dir}")
            return

        bpy.ops.object.speaker_add(location=(0, 0, 0))
        speaker = bpy.context.object
        speaker.name = "OsuAudioSpeaker"

        sound = bpy.data.sounds.load(filepath=audio_path, check_existing=True)
        speaker.data.sound = sound

        pitch = 1.5 if self.mods & MOD_DOUBLE_TIME else 0.75 if self.mods & MOD_HALF_TIME else 1.0
        speaker.data.pitch = pitch
        print(f"Audio file '{audio_filename}' imported with {pitch}x pitch.")

    def calculate_hit_windows(self):
        od = self.calculate_adjusted_od()

        hit_window_300 = max(80 - (6 * od), 0)
        hit_window_100 = max(140 - (8 * od), 0)
        hit_window_50 = max(200 - (10 * od), 0)

        speed_multiplier = calculate_speed_multiplier(self.mods)
        return (
            hit_window_300 / speed_multiplier,
            hit_window_100 / speed_multiplier,
            hit_window_50 / speed_multiplier,
        )

    def check_hits(self):
        hit_window_300, hit_window_100, hit_window_50 = self.calculate_hit_windows()
        hit_window = hit_window_50

        speed_multiplier = calculate_speed_multiplier(self.mods)
        audio_lead_in = self.beatmap_info['audio_lead_in']

        key_press_times = [
            (kp['time'] / speed_multiplier) + audio_lead_in for kp in self.key_presses
        ]

        for hitobject in self.hitobjects:
            hitobject_time = (hitobject.time / speed_multiplier) + audio_lead_in
            was_hit = False

            if hitobject.hit_type & 1:
                window_start = hitobject_time - hit_window
                window_end = hitobject_time + hit_window

                for idx, kp_time in enumerate(key_press_times):
                    if window_start <= kp_time <= window_end:
                        if any([self.key_presses[idx][k] for k in ('k1', 'k2', 'm1', 'm2')]):
                            was_hit = True
                            break
                    elif kp_time > window_end:
                        break

                hitobject.was_hit = was_hit

            elif hitobject.hit_type & 2:
                slider_duration_ms = self.calculate_slider_duration(hitobject)
                slider_end_time = (hitobject.time + slider_duration_ms) / speed_multiplier + audio_lead_in

                window_start = hitobject_time - hit_window
                window_end = slider_end_time + hit_window

                for idx, kp_time in enumerate(key_press_times):
                    if window_start <= kp_time <= window_end:
                        if any([self.key_presses[idx][k] for k in ('k1', 'k2', 'm1', 'm2')]):
                            was_hit = True
                            break
                    elif kp_time > window_end:
                        break

                hitobject.was_hit = was_hit
                hitobject.was_completed = was_hit and all(
                    any(self.key_presses[idx][k] for k in ('k1', 'k2', 'm1', 'm2'))
                    for idx, kp_time in enumerate(key_press_times)
                    if hitobject_time <= kp_time <= slider_end_time
                )

            elif hitobject.hit_type & 8:
                spinner_duration_ms = self.calculate_spinner_duration(hitobject)
                spinner_end_time = (hitobject.time + spinner_duration_ms) / speed_multiplier + audio_lead_in

                window_start = hitobject_time - hit_window
                window_end = spinner_end_time + hit_window

                for idx, kp_time in enumerate(key_press_times):
                    if window_start <= kp_time <= window_end:
                        if any([self.key_presses[idx][k] for k in ('k1', 'k2', 'm1', 'm2')]):
                            was_hit = True
                            break
                    elif kp_time > window_end:
                        break

                hitobject.was_hit = was_hit
                hitobject.was_completed = was_hit and all(
                    any(self.key_presses[idx][k] for k in ('k1', 'k2', 'm1', 'm2'))
                    for idx, kp_time in enumerate(key_press_times)
                    if hitobject_time <= kp_time <= spinner_end_time
                )
    def calculate_slider_duration(self, hitobject):
        start_time_ms = hitobject.time
        repeat_count = int(hitobject.extras[1]) if len(hitobject.extras) > 1 else 1
        pixel_length = float(hitobject.extras[2]) if len(hitobject.extras) > 2 else 100.0
        speed_multiplier = calculate_speed_multiplier(self.mods)
        slider_multiplier = float(self.osu_parser.difficulty_settings.get("SliderMultiplier", 1.4))
        timing_points = self.osu_parser.timing_points

        beat_duration = 500
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
            spinner_duration_ms = (end_time_ms - start_time_ms) / calculate_speed_multiplier(self.mods)
            return spinner_duration_ms
        return 0

    def get_base_ar(self):
        return float(self.osu_parser.difficulty_settings.get("ApproachRate", 5.0))

    def get_base_cs(self):
        return float(self.osu_parser.difficulty_settings.get("CircleSize", 5.0))

    def get_base_od(self):
        return float(self.osu_parser.difficulty_settings.get("OverallDifficulty", 5.0))

    def calculate_adjusted_od(self):
        od = self.get_base_od()
        if self.mods & MOD_HARD_ROCK:
            od = min(10, od * 1.4)
        elif self.mods & MOD_EASY:
            od = od * 0.5
        return od

    def calculate_adjusted_ar(self):
        ar = self.get_base_ar()
        if self.mods & MOD_HARD_ROCK:
            ar = min(10, ar * 1.4)
        elif self.mods & MOD_EASY:
            ar *= 0.5

        preempt = 1800 - (120 * ar) if ar < 5 else 1200 - (150 * (ar - 5))
        preempt /= calculate_speed_multiplier(self.mods)

        ar = (1800 - preempt) / 120 if preempt > 1200 else (1200 - preempt) / 150 + 5
        return max(0, min(11, ar))

    def calculate_adjusted_cs(self):
        cs = self.get_base_cs()
        if self.mods & MOD_HARD_ROCK:
            cs = min(10, cs * 1.3)
        elif self.mods & MOD_EASY:
            cs = cs * 0.5
        return cs

    def calculate_preempt_time(self, ar):
        preempt = 1800 - (120 * ar) if ar < 5 else 1200 - (150 * (ar - 5))
        return preempt / calculate_speed_multiplier(self.mods)