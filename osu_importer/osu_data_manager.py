# osu_importer/osu_data_manager.py

import bpy
import os
import bisect
from osu_importer.parsers.osu_parser import OsuParser, OsrParser
from osu_importer.utils.constants import MOD_DOUBLE_TIME, MOD_HALF_TIME, MOD_HARD_ROCK, MOD_EASY
from osu_importer.utils.mod_functions import calculate_speed_multiplier
from osu_importer.parsers.hitobjects import HitObjectsProcessor


class OsuDataManager:
    def __init__(self, osu_file_path, osr_file_path):
        self.osu_parser = OsuParser(osu_file_path)
        self.osr_parser = OsrParser(osr_file_path)
        self.hitobjects_processor = HitObjectsProcessor(self)
        #self.mods = self.osr_parser.mods  # Sicherstellen, dass self.mods definiert ist
        self.speed_multiplier = calculate_speed_multiplier(self.mods)
        self.ms_per_frame = self.get_ms_per_frame()

        self.audio_lead_in = self.osu_parser.audio_lead_in
        self.adjusted_ar = None
        self.adjusted_cs = None
        self.adjusted_od = None
        self.preempt_ms = None
        self.preempt_frames = None
        self.osu_radius = None
        self.audio_lead_in_frames = None

        self.base_ar = float(self.osu_parser.difficulty_settings.get("ApproachRate", 5.0))
        self.base_cs = float(self.osu_parser.difficulty_settings.get("CircleSize", 5.0))
        self.base_od = float(self.osu_parser.difficulty_settings.get("OverallDifficulty", 5.0))

        self.calculate_adjusted_values()
        self.calculate_hit_objects_frames()  # Neue Methode aufrufen

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
            "username": self.osr_parser.username,
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

    def get_ms_per_frame(self):
        fps = bpy.context.scene.render.fps
        return 1000 / fps  # Millisekunden pro Frame

    def calculate_adjusted_values(self):
        self.adjusted_ar = self.calculate_adjusted_ar()
        self.adjusted_cs = self.calculate_adjusted_cs()
        self.adjusted_od = self.calculate_adjusted_od()
        self.preempt_ms = self.calculate_preempt_time(self.adjusted_ar)
        self.preempt_frames = self.preempt_ms / self.ms_per_frame
        self.osu_radius = (54.4 - 4.48 * self.adjusted_cs) / 2
        self.audio_lead_in_frames = self.audio_lead_in / self.ms_per_frame

    def calculate_hit_objects_frames(self):
        for hitobject in self.hitobjects:
            # Berechnung der tatsächlichen HitObject-Zeit unter Berücksichtigung des Speed Multipliers und Audio-Lead-In
            hitobject_time = (hitobject.time / self.speed_multiplier)

            # Startframe berechnen unter Berücksichtigung der Preempt-Zeit
            hitobject.start_frame = int(hitobject_time / self.ms_per_frame) + self.audio_lead_in

            if hitobject.hit_type & 2:  # Slider
                slider_duration_ms = self.calculate_slider_duration(hitobject)
                hitobject.duration_frames = int(slider_duration_ms / self.ms_per_frame)
                hitobject.end_frame = hitobject.start_frame + hitobject.duration_frames
                hitobject.slider_end_time = hitobject_time + slider_duration_ms
            elif hitobject.hit_type & 8:  # Spinner
                spinner_duration_ms = self.calculate_spinner_duration(hitobject)
                hitobject.duration_frames = int(spinner_duration_ms / self.ms_per_frame)
                hitobject.end_frame = hitobject.start_frame + hitobject.duration_frames
                hitobject.slider_end_time = hitobject_time + spinner_duration_ms
            else:  # Circle
                hitobject.duration_frames = 0
                hitobject.end_frame = hitobject.start_frame
                # Für Kreise ist slider_end_time nicht relevant
                hitobject.slider_end_time = hitobject_time

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
        od = self.adjusted_od

        hit_window_300 = max(80 - (6 * od), 0)
        hit_window_100 = max(140 - (8 * od), 0)
        hit_window_50 = max(200 - (10 * od), 0)

        return (
            hit_window_300 / self.speed_multiplier,
            hit_window_100 / self.speed_multiplier,
            hit_window_50 / self.speed_multiplier,
        )

    def check_hits(self):
        hit_window_300, hit_window_100, hit_window_50 = self.calculate_hit_windows()
        hit_window = hit_window_50

        speed_multiplier = self.speed_multiplier
        audio_lead_in = self.audio_lead_in

        key_press_times = [
            (kp['time'] / speed_multiplier) + audio_lead_in for kp in self.key_presses
        ]

        if not key_press_times:
            print("No key presses found.")
            return

        key_press_times, key_presses = zip(*sorted(zip(key_press_times, self.key_presses), key=lambda x: x[0]))

        for hitobject in self.hitobjects:
            hitobject_time = (hitobject.time / speed_multiplier) + audio_lead_in

            window_start = hitobject_time - hit_window
            window_end = hitobject_time + hit_window

            start_idx = bisect.bisect_left(key_press_times, window_start)
            end_idx = bisect.bisect_right(key_press_times, window_end)

            was_hit = False

            if hitobject.hit_type & 1:  # Circle
                for idx in range(start_idx, end_idx):
                    if any(key_presses[idx][k] for k in ('k1', 'k2', 'm1', 'm2')):
                        was_hit = True
                        break
                hitobject.was_hit = was_hit

            elif hitobject.hit_type & 2:  # Slider
                slider_end_time = hitobject.slider_end_time  # Bereits im check_hits gesetzt
                window_end = slider_end_time + hit_window
                end_idx = bisect.bisect_right(key_press_times, window_end)
                was_hit = False
                for idx in range(start_idx, end_idx):
                    if any(key_presses[idx][k] for k in ('k1', 'k2', 'm1', 'm2')):
                        was_hit = True
                        break
                hitobject.was_hit = was_hit
                hitobject.was_completed = False  # Wir setzen es später basierend auf der Slider-Dauer
                # slider_end_time wurde bereits gesetzt

            elif hitobject.hit_type & 8:  # Spinner
                spinner_end_time = hitobject.slider_end_time  # Nutzen des gleichen Attributes für Spinner-Endzeit
                window_end = spinner_end_time + hit_window

                end_idx = bisect.bisect_right(key_press_times, window_end)

                for idx in range(start_idx, end_idx):
                    if any(key_presses[idx][k] for k in ('k1', 'k2', 'm1', 'm2')):
                        was_hit = True
                        break
                hitobject.was_hit = was_hit

                if was_hit:
                    end_press_idx = bisect.bisect_left(key_press_times, spinner_end_time)
                    was_completed = False
                    if end_press_idx < len(key_press_times):
                        if any(key_presses[end_press_idx - 1][k] for k in ('k1', 'k2', 'm1', 'm2')):
                            was_completed = True
                    hitobject.was_completed = was_completed
                else:
                    hitobject.was_completed = False

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
                slider_multiplier * 100)) * beat_duration * repeat_count * inherited_multiplier / speed_multiplier
        # slider_duration_ms /= speed_multiplier

        return slider_duration_ms

    def calculate_spinner_duration(self, hitobject):
        start_time_ms = hitobject.time
        if hitobject.extras:
            end_time_ms = int(hitobject.extras[0])
            spinner_duration_ms = (end_time_ms - start_time_ms) / calculate_speed_multiplier(self.mods)
            return spinner_duration_ms
        return 0

    def get_base_ar(self):
        return self.base_ar

    def get_base_cs(self):
        return self.base_cs

    def get_base_od(self):
        return self.base_od

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
