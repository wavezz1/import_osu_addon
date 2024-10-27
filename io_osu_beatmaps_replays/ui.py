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

class OSU_PT_ImporterPanel(Panel):
    bl_label = "osu! Importer"
    bl_idname = "OSU_PT_importer_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "osu! Importer"

    def draw(self, context):
        layout = self.layout
        props = context.scene.osu_importer_props

        layout.prop(props, "osu_file")
        layout.prop(props, "osr_file")

        layout.operator("osu_importer.import", text="Importieren")

        # Beatmap-Informationen anzeigen
        if props.bpm != 0.0 or props.base_approach_rate != 0.0 or props.base_circle_size != 0.0 or props.total_hitobjects != 0:
            # Prüfen, ob Mods aktiv sind, die AR oder CS beeinflussen
            ar_modified = abs(props.base_approach_rate - props.adjusted_approach_rate) > 0.01
            cs_modified = abs(props.base_circle_size - props.adjusted_circle_size) > 0.01

            # AR anzeigen
            if ar_modified:
                ar_display = f"AR: {props.base_approach_rate} ({props.adjusted_approach_rate:.1f})"
            else:
                ar_display = f"AR: {props.base_approach_rate}"

            # CS anzeigen
            if cs_modified:
                cs_display = f"CS: {props.base_circle_size} ({props.adjusted_circle_size:.1f})"
            else:
                cs_display = f"CS: {props.base_circle_size}"

            beatmap_info = f"BPM: {props.bpm:.2f} | {ar_display} | {cs_display} | HitObjects: {props.total_hitobjects}"
            layout.label(text=beatmap_info)

        # Replay-Informationen anzeigen
        if props.formatted_mods != "Keine" or props.accuracy != 0.0 or props.misses != 0:
            replay_info = f"Mods: {props.formatted_mods} | Acc: {props.accuracy:.2f}% | Misses: {props.misses}"
            layout.label(text=replay_info)

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