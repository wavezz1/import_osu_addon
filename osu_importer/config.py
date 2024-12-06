# osu_importer/config.py

class ImportConfig:
    def __init__(self, props, data_manager):
        # Aus props (Benutzereinstellungen)
        self.import_type = props.import_type
        self.include_osu_gameplay = props.include_osu_gameplay
        self.import_approach_circles = props.import_approach_circles
        self.import_circles = props.import_circles
        self.import_sliders = props.import_sliders
        self.import_spinners = props.import_spinners
        self.import_slider_heads_tails = props.import_slider_heads_tails
        self.import_slider_balls = props.import_slider_balls
        self.import_slider_ticks = props.import_slider_ticks
        self.import_cursors = props.import_cursors
        self.import_audio = props.import_audio
        self.slider_resolution = props.slider_resolution
        self.cursor_size = props.cursor_size
        self.cursor_shape = props.cursor_shape
        self.approach_circle_bevel_depth = props.approach_circle_bevel_depth
        self.approach_circle_bevel_resolution = props.approach_circle_bevel_resolution

        # Aus data_manager (berechnete Werte und Beatmap-Infos)
        self.audio_lead_in = data_manager.audio_lead_in
        self.audio_lead_in_frames = data_manager.audio_lead_in_frames
        self.adjusted_ar = data_manager.adjusted_ar
        self.adjusted_cs = data_manager.adjusted_cs
        self.adjusted_od = data_manager.adjusted_od
        self.base_ar = data_manager.base_ar
        self.base_cs = data_manager.base_cs
        self.base_od = data_manager.base_od
        self.osu_radius = data_manager.osu_radius
        self.ms_per_frame = data_manager.ms_per_frame
        self.speed_multiplier = data_manager.speed_multiplier

        # Beatmap- und Replay-Informationen (falls benötigt)
        self.beatmap_info = data_manager.beatmap_info
        self.replay_info = data_manager.replay_info

        # Da data_manager selbst auch häufig für den Zugriff auf die Hitobjects genutzt wird,
        # können wir ihn optional direkt referenzieren, falls notwendig:
        self.data_manager = data_manager
