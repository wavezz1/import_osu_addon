# osu_importer/properties.py

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty
from bpy.types import PropertyGroup

class OSUImporterProperties(PropertyGroup):
    osu_file: StringProperty(
        name="Beatmap (.osu)",
        description="Pfad zur .osu Beatmap-Datei",
        default="",
        subtype='FILE_PATH'
    )
    osr_file: StringProperty(
        name="Replay (.osr)",
        description="Pfad zur .osr Replay-Datei",
        default="",
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
    cursor_offset: FloatProperty(
        name="Cursor Offset (ms)",
        description="Offset zum Verschieben der Cursor-Keyframes",
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
