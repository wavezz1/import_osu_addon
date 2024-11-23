# osu_importer/parsers/hitobjects.py

class HitObject:
    def __init__(self, x, y, time, hit_type, hit_sound, extras):
        self.x = x
        self.y = y
        self.time = time
        self.hit_type = hit_type
        self.hit_sound = hit_sound
        self.extras = extras
        self.frame = None
        self.start_frame = None
        self.end_frame = None
        self.duration_frames = None
        self.was_hit = False
        self.was_completed = False

class HitObjectsProcessor:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.circles = []
        self.sliders = []
        self.spinners = []
        self.process_hitobjects()

    def process_hitobjects(self):
        hitobjects = self.data_manager.osu_parser.hitobjects

        for line in hitobjects:
            parts = line.split(',')
            if len(parts) < 5:
                continue
            x, y, time = int(parts[0]), int(parts[1]), int(parts[2])
            hit_type, hit_sound = int(parts[3]), int(parts[4])
            extras = parts[5:]

            hit_object = HitObject(x, y, time, hit_type, hit_sound, extras)
            if hit_type & 1:  # Circle
                self.circles.append(hit_object)
            elif hit_type & 2:  # Slider
                self.sliders.append(hit_object)
            elif hit_type & 8:  # Spinner
                self.spinners.append(hit_object)
