# osu_parser.py

import osrparse

class OsuParser:
    _cache = {}

    def __new__(cls, osu_file_path):
        if osu_file_path in cls._cache:
            return cls._cache[osu_file_path]
        else:
            instance = super(OsuParser, cls).__new__(cls)
            cls._cache[osu_file_path] = instance
            return instance

    def __init__(self, osu_file_path):
        if hasattr(self, 'initialized'):
            return
        self.initialized = True

        self.osu_file_path = osu_file_path
        self.audio_lead_in = 0
        self.timing_points = []
        self.hitobjects = []
        self.difficulty_settings = {}
        self.general_settings = {}
        self.metadata = {}
        self.events = []
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
                            offset, beat_length = float(parts[0]), float(parts[1])
                            self.timing_points.append((offset, beat_length))
                    elif section == 'HitObjects':
                        self.hitobjects.append(line)
                    elif section == 'Events':
                        self.events.append(line)
        except Exception as e:
            print(f"Error parsing .osu file: {e}")

    def calculate_bpm(self):
        min_beat_length = min((beat_length for _, beat_length in self.timing_points if beat_length > 0), default=None)
        return 60000 / min_beat_length if min_beat_length else 0.0

class OsrParser:
    def __init__(self, osr_file_path):
        self.osr_file_path = osr_file_path
        self.replay_data = None
        self.mods = 0
        self.mod_list = []
        self.key_presses = []
        self.number_300s = 0
        self.number_100s = 0
        self.number_50s = 0
        self.misses = 0
        self.score = 0
        self.max_combo = 0
        self.username = "Unknown"
        self.parse_osr_file()

    def parse_osr_file(self):
        try:
            replay = osrparse.Replay.from_path(self.osr_file_path)
            self.replay_data = replay.replay_data
            self.mods = replay.mods
            self.mod_list = self.get_mods_list(self.mods)
            self.number_300s = replay.count_300
            self.number_100s = replay.count_100
            self.number_50s = replay.count_50
            self.misses = replay.count_miss
            self.max_combo = replay.max_combo
            self.score = replay.score
            self.username = replay.username
            self.key_presses = self.parse_key_presses()
        except Exception as e:
            print(f"Error parsing .osr file: {e}")

    def calculate_accuracy(self):
        total_hits = self.number_300s + self.number_100s + self.number_50s + self.misses
        return ((self.number_50s * 50 + self.number_100s * 100 + self.number_300s * 300) / (total_hits * 300)) * 100 if total_hits else 0.0

    def get_mods_list(self, mods):
        mod_constants = {
            1 << 0: "NF",
            1 << 1: "EZ",
            1 << 3: "HD",
            1 << 4: "HR",
            1 << 5: "SD",
            1 << 6: "DT",
            1 << 8: "HT",
        }
        return [name for val, name in mod_constants.items() if mods & val]

    def parse_key_presses(self):
        key_presses = []
        total_time = 0
        for frame in self.replay_data:
            total_time += frame.time_delta
            key_presses.append({
                'time': total_time,
                'time_delta': frame.time_delta,
                'k1': bool(frame.keys & osrparse.utils.Key.K1),
                'k2': bool(frame.keys & osrparse.utils.Key.K2),
                'm1': bool(frame.keys & osrparse.utils.Key.M1),
                'm2': bool(frame.keys & osrparse.utils.Key.M2),
            })
        return key_presses
