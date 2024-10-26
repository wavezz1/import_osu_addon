# hitobjects.py

from .osu_replay_data_manager import OsuReplayDataManager


class HitObject:
    def __init__(self, x, y, time, hit_type, hit_sound, extras):
        self.x = x
        self.y = y
        self.time = time
        self.hit_type = hit_type
        self.hit_sound = hit_sound
        self.extras = extras


class HitObjectsProcessor:
    def __init__(self, data_manager: OsuReplayDataManager):
        self.data_manager = data_manager
        self.circles = []
        self.sliders = []
        self.spinners = []
        self.process_hitobjects()

    def process_hitobjects(self):
        # Greife auf die hitobjects-Liste über data_manager zu
        hitobjects = self.data_manager.hitobjects
        print(str(hitobjects[:10]))

        for line in hitobjects:
            parts = line.split(',')
            if len(parts) < 5:
                continue
            x = int(parts[0])
            y = int(parts[1])
            time = int(parts[2])
            hit_type = int(parts[3])
            hit_sound = int(parts[4])
            extras = parts[5:]  # Kann Slider-Daten enthalten
            hit_object = HitObject(x, y, time, hit_type, hit_sound, extras)
            if hit_type & 1:  # Circle
                self.circles.append(hit_object)
            elif hit_type & 2:  # Slider
                self.sliders.append(hit_object)
            elif hit_type & 8:  # Spinner
                self.spinners.append(hit_object)
