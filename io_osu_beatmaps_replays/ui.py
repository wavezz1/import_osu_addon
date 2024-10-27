# ui.py

import bpy
from bpy.types import Panel, PropertyGroup, Operator
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, CollectionProperty

class OSUImporterProperties(PropertyGroup):
    osu_file: StringProperty(
        name="Beatmap (.osu)",
        description="Pfad zur .osu Beatmap-Datei",
        subtype='FILE_PATH'
    )
    osr_file: StringProperty(
        name="Replay (.osr)",
        description="Pfad zur .osr Replay-Datei",
        subtype='FILE_PATH'
    )
    approach_rate: FloatProperty(
        name="Approach Rate",
        description="Approach Rate der Beatmap",
        default=0.0
    )
    circle_size: FloatProperty(
        name="Circle Size",
        description="Circle Size der Beatmap",
        default=0.0
    )
    bpm: FloatProperty(
        name="BPM",
        description="Beats per Minute der Beatmap",
        default=0.0
    )
    total_hitobjects: IntProperty(
        name="Anzahl HitObjects",
        description="Gesamtzahl der HitObjects in der Beatmap",
        default=0
    )
    mods: StringProperty(
        name="Aktive Mods",
        description="Liste der aktiven Mods",
        default=""
    )
    accuracy: FloatProperty(
        name="Accuracy",
        description="Genauigkeit des Replays in Prozent",
        default=0.0
    )
    misses: IntProperty(
        name="Misses",
        description="Anzahl der verpassten HitObjects im Replay",
        default=0
    )
    formatted_mods: StringProperty(
        name="Aktive Mods (Formatiert)",
        description="Liste der aktiven Mods im Format DT,HD",
        default=""
    )
    base_approach_rate: FloatProperty(
        name="Approach Rate",
        description="Base Approach Rate der Beatmap",
        default=0.0
    )
    adjusted_approach_rate: FloatProperty(
        name="Adjusted Approach Rate",
        description="Adjusted Approach Rate der Beatmap mit Mods",
        default=0.0
    )
    base_circle_size: FloatProperty(
        name="Circle Size",
        description="Base Circle Size der Beatmap",
        default=0.0
    )
    adjusted_circle_size: FloatProperty(
        name="Adjusted Circle Size",
        description="Adjusted Circle Size der Beatmap mit Mods",
        default=0.0
    )
    import_circles: BoolProperty(
        name="Kreise importieren",
        description="Importiert Kreise aus der Beatmap",
        default=True
    )
    import_sliders: BoolProperty(
        name="Slider importieren",
        description="Importiert Slider aus der Beatmap",
        default=True
    )
    import_spinners: BoolProperty(
        name="Spinner importieren",
        description="Importiert Spinner aus der Beatmap",
        default=True
    )
    import_audio: BoolProperty(
        name="Audio importieren",
        description="Importiert die Audio-Datei der Beatmap",
        default=True
    )
    custom_speed_multiplier: FloatProperty(
        name="Geschwindigkeitsmultiplikator",
        description="Passt die Geschwindigkeit des Replays an",
        default=1.0,
        min=0.1,
        max=3.0
    )

class OSU_PT_ImporterPanel(Panel):
    bl_label = "osu! Importer"
    bl_idname = "OSU_PT_importer_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "osu! Importer"

    def draw(self, context):
        layout = self.layout
        props = context.scene.osu_importer_props

        # Dateiauswahl
        box = layout.box()
        box.label(text="Dateiauswahl", icon='FILE_FOLDER')
        box.prop(props, "osu_file")
        box.prop(props, "osr_file")
        box.operator("osu_importer.import", text="Importieren", icon='IMPORT')

        # Beatmap-Informationen
        if props.bpm != 0.0:
            box = layout.box()
            box.label(text="Beatmap-Informationen", icon='INFO')
            col = box.column(align=True)
            col.label(text=f"BPM: {props.bpm:.2f}")
            # AR
            ar_modified = abs(props.base_approach_rate - props.adjusted_approach_rate) > 0.01
            if ar_modified:
                col.label(text=f"AR: {props.base_approach_rate} ({props.adjusted_approach_rate:.1f})")
            else:
                col.label(text=f"AR: {props.base_approach_rate}")
            # CS
            cs_modified = abs(props.base_circle_size - props.adjusted_circle_size) > 0.01
            if cs_modified:
                col.label(text=f"CS: {props.base_circle_size} ({props.adjusted_circle_size:.1f})")
            else:
                col.label(text=f"CS: {props.base_circle_size}")
            # OD
            od_modified = abs(props.base_overall_difficulty - props.adjusted_overall_difficulty) > 0.01
            if od_modified:
                col.label(text=f"OD: {props.base_overall_difficulty} ({props.adjusted_overall_difficulty:.1f})")
            else:
                col.label(text=f"OD: {props.base_overall_difficulty}")
            col.label(text=f"HitObjects: {props.total_hitobjects}")

        # Replay-Informationen
        if props.formatted_mods or props.accuracy != 0.0:
            box = layout.box()
            box.label(text="Replay-Informationen", icon='PLAY')
            col = box.column(align=True)
            col.label(text=f"Mods: {props.formatted_mods}")
            col.label(text=f"Accuracy: {props.accuracy:.2f}%")
            col.label(text=f"Misses: {props.misses}")
            col.label(text=f"Max Combo: {props.max_combo}")
            col.label(text=f"Total Score: {props.total_score}")

        # Erweiterte Einstellungen
        box = layout.box()
        box.label(text="Einstellungen", icon='PREFERENCES')
        col = box.column(align=True)
        col.prop(props, "import_circles")
        col.prop(props, "import_sliders")
        col.prop(props, "import_spinners")
        col.prop(props, "import_audio")
        col.prop(props, "custom_speed_multiplier")

class OSU_OT_Import(Operator):
    bl_idname = "osu_importer.import"
    bl_label = "Importieren"
    bl_description = "Importiert die ausgewählte Beatmap und Replay"

    def execute(self, context):
        from .exec import main_execution

        # Setze die Szene auf 60 FPS
        context.scene.render.fps = 60
        self.report({'INFO'}, "Szene auf 60 FPS gesetzt")

        # Importiere die Daten und erhalte das Ergebnis von main_execution
        result, data_manager = main_execution(context)

        # Aktualisiere die UI-Properties mit den Daten aus data_manager
        props = context.scene.osu_importer_props
        props.base_approach_rate = data_manager.get_base_ar()
        props.adjusted_approach_rate = data_manager.calculate_adjusted_ar()
        props.base_circle_size = data_manager.get_base_cs()
        props.adjusted_circle_size = data_manager.calculate_adjusted_cs()
        props.bpm = data_manager.beatmap_info["bpm"]
        props.total_hitobjects = data_manager.beatmap_info["total_hitobjects"]

        # Replay-Informationen
        props.formatted_mods = data_manager.replay_info["mods"]
        props.accuracy = data_manager.replay_info["accuracy"]
        props.misses = data_manager.replay_info["misses"]

        return result