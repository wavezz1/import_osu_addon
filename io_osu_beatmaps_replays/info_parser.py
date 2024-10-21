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

    def get_first_hitobject_time(self):
        if not self.hitobjects:
            return 0.0
        first_hitobject = self.hitobjects[0]
        parts = first_hitobject.split(',')
        if len(parts) >= 3:
            time = int(parts[2])
            return time
        return 0.0

class OsrParser:
    def __init__(self, osr_file_path):
        self.osr_file_path = osr_file_path
        self.replay_data = None
        self.mods = 0
        self.mod_list = []
        self.parse_osr_file()

    def parse_osr_file(self):
        try:
            replay = osrparse.Replay.from_path(self.osr_file_path)
            print(str(replay.replay_data[:5]))
            self.replay_data = replay.replay_data
            self.mods = replay.mods
            self.mod_list = self.get_mods_list(self.mods)
            self.number_300s = replay.count_300
            self.number_100s = replay.count_100
            self.number_50s = replay.count_50
            self.misses = replay.count_miss
        except Exception as e:
            print(f"Fehler beim Parsen der .osr-Datei: {e}")

    def calculate_accuracy(self):
        total_hits = self.number_300s + self.number_100s + self.number_50s + self.misses
        if total_hits == 0:
            return 0.0
        accuracy = ((self.number_50s * 50 + self.number_100s * 100 + self.number_300s * 300) / (total_hits * 300)) * 100
        return accuracy

    def calculate_misses(self):
        return self.misses

    def get_mods_list(self, mods):
        mod_names = []
        mod_constants = {
            1 << 0: "NF",
            1 << 1: "EZ",
            1 << 2: "TD",
            1 << 3: "HD",
            1 << 4: "HR",
            1 << 5: "SD",
            1 << 6: "DT",
            1 << 7: "RX",
            1 << 8: "HT",
            1 << 9: "NC",  # Wird als DT + NC behandelt
            1 << 10: "FL",
            1 << 11: "AP",
            1 << 12: "SO",
            1 << 13: "AO",
            1 << 14: "PF",
            1 << 15: "4K",
            1 << 16: "5K",
            1 << 17: "6K",
            1 << 18: "7K",
            1 << 19: "8K",
            1 << 20: "FI",
            1 << 21: "RN",
            1 << 22: "CN",
            1 << 23: "TP",
            1 << 24: "9K",
            1 << 25: "CO",
            1 << 26: "1K",
            1 << 27: "3K",
            1 << 28: "2K",
            1 << 29: "V2",
            1 << 30: "MR",
        }
        for mod_value, mod_name in mod_constants.items():
            if mods & mod_value:
                mod_names.append(mod_name)
        return mod_names


    def get_first_replay_event_time(self):
        total_time = 0
        for event in self.replay_data:
            total_time += event.time_delta
            if event.x != -256 and event.y != -256:
                return total_time
        return total_time