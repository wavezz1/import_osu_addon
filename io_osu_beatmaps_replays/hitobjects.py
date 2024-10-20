# hitobjects.py

class HitObject:
    def __init__(self, x, y, time, hit_type, hit_sound, extras):
        self.x = x
        self.y = y
        self.time = time
        self.hit_type = hit_type
        self.hit_sound = hit_sound
        self.extras = extras

class HitObjectsProcessor:
    def __init__(self, osu_parser):
        self.osu_parser = osu_parser
        self.circles = []
        self.sliders = []
        self.spinners = []
        self.process_hitobjects()

    def process_hitobjects(self):
        for line in self.osu_parser.hitobjects:
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