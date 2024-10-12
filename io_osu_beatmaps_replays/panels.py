# osu_importer/panels.py

import bpy
from bpy.types import Panel

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
            layout.label(text="Erkannte Werte:")
            col = layout.column(align=True)
            col.label(text=f"Erstes HitObject: {props.detected_first_hitobject_time:.2f} ms")
            col.label(text=f"Erstes Replay-Event: {props.detected_first_replay_time:.2f} ms")
            col.label(text=f"Berechneter Cursor-Offset: {props.calculated_cursor_offset:.2f} ms")
            if props.use_auto_offset:
                col.label(text=f"Berechneter Offset: {props.detected_offset:.2f} ms")
            else:
                col.label(text=f"Manueller Offset: {props.manual_offset:.2f} ms")

