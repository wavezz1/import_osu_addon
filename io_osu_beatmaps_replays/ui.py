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

        # Zeige die erkannten Werte an
        if props.detected_first_hitobject_time != 0 or props.detected_first_replay_time != 0:
            layout.separator()
            layout.label(text="Erkannte Werte:")

            col = layout.column(align=True)
            col.label(text=f"Erstes HitObject: {props.detected_first_hitobject_time:.2f} ms")
            col.label(text=f"Erstes Replay-Event: {props.detected_first_replay_time:.2f} ms")
            if props.use_auto_offset:
                col.label(text=f"Berechneter Offset: {props.detected_offset:.2f} ms")
            else:
                col.label(text=f"Manueller Offset: {props.manual_offset:.2f} ms")

            layout.separator()
            layout.label(text="Beatmap-Informationen:")

            col = layout.column(align=True)
            col.label(text=f"BPM: {props.bpm:.2f}")
            col.label(text=f"Approach Rate: {props.approach_rate}")
            col.label(text=f"Circle Size: {props.circle_size}")
            col.label(text=f"Anzahl HitObjects: {props.total_hitobjects}")

            layout.separator()
            layout.label(text="Replay-Informationen:")

            col = layout.column(align=True)
            col.label(text=f"Aktive Mods: {props.mods}")