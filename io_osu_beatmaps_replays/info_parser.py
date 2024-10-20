# info_parser.py

import osrparse

class OsuParser:
    def __init__(self, osu_file_path):
        self.osu_file_path = osu_file_path
        self.audio_lead_in = 0
        self.timing_points = []
        self.hitobjects = []
        self.difficulty_settings = {}
        self.general_settings = {}
        self.metadata = {}
        self.parse_osu_file()
        self.bpm = self.calculate_bpm()
        self.total_hitobjects = len(self.hitobjects)

    def parse_osu_file(self):
        try:
            with open(self.osu_file_path, 'r', encoding='utf-8') as file:
                section = None
                for line in file:
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        section = line[1:-1]
                        continue
                    if not line or line.startswith('//'):
                        continue
                    if section == 'General':
                        key, value = line.split(':', 1)
                        self.general_settings[key.strip()] = value.strip()
                        if key.strip() == "AudioLeadIn":
                            self.audio_lead_in = int(value.strip())
                    elif section == 'Metadata':
                        key, value = line.split(':', 1)
                        self.metadata[key.strip()] = value.strip()
                    elif section == 'Difficulty':
                        key, value = line.split(':', 1)
                        self.difficulty_settings[key.strip()] = value.strip()
                    elif section == 'TimingPoints':
                        parts = line.split(',')
                        if len(parts) >= 2:
                            offset = float(parts[0])
                            beat_length = float(parts[1])
                            self.timing_points.append((offset, beat_length))
                    elif section == 'HitObjects':
                        self.hitobjects.append(line)
        except Exception as e:
            print(f"Fehler beim Parsen der .osu-Datei: {e}")

    def calculate_bpm(self):
        bpm = 0.0
        # Suche nach dem Timing Point mit dem minimalen beat_length (wird als BPM verwendet)
        min_beat_length = None
        for _, beat_length in self.timing_points:
            if beat_length > 0 and (min_beat_length is None or beat_length < min_beat_length):
                min_beat_length = beat_length
        if min_beat_length:
            bpm = 60000 / min_beat_length
        return bpm

class OsrParser:
    def __init__(self, osr_file_path):
        self.osr_file_path = osr_file_path
        self.replay_data = None
        self.mods = 0
        self.mod_list = []
        self.player_name = ""
        self.misses = 0
        self.parse_osr_file()

    def parse_osr_file(self):
        try:
            replay = osrparse.parse_replay_file(self.osr_file_path)
            self.replay_data = replay.play_data
            self.mods = replay.mod_combination
            self.mod_list = self.get_mods_list(self.mods)
            self.player_name = replay.player_name
            self.misses = replay.number_misses
        except Exception as e:
            print(f"Fehler beim Parsen der .osr-Datei: {e}")

    def get_mods_list(self, mods):
        mod_names = []
        mod_constants = {
            1: "NoFail",
            2: "Easy",
            8: "Hidden",
            16: "HardRock",
            32: "SuddenDeath",
            64: "DoubleTime",
            128: "Relax",
            256: "HalfTime",
            576: "Perfect",
            1024: "Nightcore",
            2048: "Flashlight",
            4096: "Autoplay",
            8192: "SpunOut",
            16384: "Autopilot",
            32768: "Target",
            65536: "Mirror",
        }
        for mod_value, mod_name in mod_constants.items():
            if mods & mod_value:
                mod_names.append(mod_name)
        return mod_names

def get_first_replay_event_time(replay_data):
    total_time = 0
    for event in replay_data:
        total_time += event.time_since_previous_action
        if event.x != -256 and event.y != -256:
            return total_time
    return total_time  # Falls alle Events bei (-256, -256) sind
