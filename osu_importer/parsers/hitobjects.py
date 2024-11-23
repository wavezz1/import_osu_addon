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
        self.combo_number = 0
        self.is_new_combo = False
        self.combo_color = None

class HitObjectsProcessor:
    COMBO_COLORS = [
        "Blue",
        "Red",
        "Green",
        "Yellow",
        "Purple",
        "Orange",
        "Pink",
        "Brown",
        "Grey",
        "Cyan",
    ]
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.circles = []
        self.sliders = []
        self.spinners = []
        self.process_hitobjects()

    def process_hitobjects(self):
        hitobjects = self.data_manager.osu_parser.hitobjects
        current_combo = 0
        combo_color_index = 0

        for line in hitobjects:
            parts = line.split(',')
            if len(parts) < 5:
                continue
            x, y, time = int(parts[0]), int(parts[1]), int(parts[2])
            hit_type, hit_sound = int(parts[3]), int(parts[4])
            extras = parts[5:]

            hit_object = HitObject(x, y, time, hit_type, hit_sound, extras)

            # Prüfen auf New Combo-Flag
            NEW_COMBO_FLAG = 4  # Bit 2 (0-indexed) repräsentiert New Combo in osu! Standard
            is_new_combo = hit_type & NEW_COMBO_FLAG
            hit_object.is_new_combo = bool(is_new_combo)

            if is_new_combo:
                current_combo = 1
                combo_color_index = (combo_color_index + 1) % len(self.COMBO_COLORS)
            else:
                current_combo += 1

            hit_object.combo_number = current_combo
            #hit_object.combo_color = self.COMBO_COLORS[combo_color_index]
            hit_object.combo_color = combo_color_index

            # Einteilen in Typen
            if hit_type & 1:  # Circle
                self.circles.append(hit_object)
            elif hit_type & 2:  # Slider
                self.sliders.append(hit_object)
            elif hit_type & 8:  # Spinner
                self.spinners.append(hit_object)