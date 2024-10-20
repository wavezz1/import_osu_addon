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

    use_auto_offset: BoolProperty(
        name="Automatischen Offset verwenden",
        description="Verwende den automatisch berechneten Offset",
        default=True
    )
    manual_offset: FloatProperty(
        name="Manueller Offset (ms)",
        description="Manuell festgelegter Zeit-Offset in Millisekunden",
        default=0.0
    )

    # Eigenschaften für die erkannten Werte
    detected_first_hitobject_time: FloatProperty(
        name="Erstes HitObject",
        description="Zeit des ersten HitObjects (ms)",
        default=0.0
    )
    detected_first_replay_time: FloatProperty(
        name="Erstes Replay-Event",
        description="Zeit des ersten Replay-Events (ms)",
        default=0.0
    )
    detected_offset: FloatProperty(
        name="Berechneter Offset",
        description="Berechneter Zeit-Offset (ms)",
        default=0.0
    )

    # Neue Properties für die geparsten Informationen
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

        layout.prop(props, "use_auto_offset")
        if not props.use_auto_offset:
            layout.prop(props, "manual_offset")

        layout.operator("osu_importer.import", text="Importieren")

        # Beatmap-Informationen anzeigen
        if props.bpm != 0.0 or props.approach_rate != 0.0 or props.circle_size != 0.0 or props.total_hitobjects != 0:
            beatmap_info = f"BPM: {props.bpm:.2f} | AR: {props.approach_rate} | CS: {props.circle_size} | HitObjects: {props.total_hitobjects}"
            layout.label(text=beatmap_info)

        # Replay-Informationen direkt unter den Beatmap-Informationen anzeigen
        if props.formatted_mods or props.accuracy != 0.0 or props.misses != 0:
            replay_info = f"Mods: {props.formatted_mods} | Acc: {props.accuracy:.2f}% | Misses: {props.misses}"
            layout.label(text=replay_info)

        # Offset-Informationen verbessern
        if props.detected_offset != 0.0 or props.manual_offset != 0.0:
            layout.separator()
            offset_text = f"Verwendeter Offset: {props.detected_offset:.2f} ms" if props.use_auto_offset else f"Manueller Offset: {props.manual_offset:.2f} ms"
            layout.label(text=offset_text)

class OSU_OT_Import(Operator):
    bl_idname = "osu_importer.import"
    bl_label = "Importieren"
    bl_description = "Importiert die ausgewählte Beatmap und Replay"

    def execute(self, context):
        from .exec import main_execution  # Aktualisiert
        result = main_execution(context)
        return result