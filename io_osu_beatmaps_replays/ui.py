# ui.py

import bpy
from bpy.types import Panel, PropertyGroup, Operator
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty

class OSUImporterProperties(PropertyGroup):
    osu_file: StringProperty(name="Beatmap (.osu)", description="Path to .osu Beatmap file", subtype='FILE_PATH')
    osr_file: StringProperty(name="Replay (.osr)", description="Path to .osr Replay file", subtype='FILE_PATH')
    approach_rate: FloatProperty(name="Approach Rate", description="Approach Rate of the Beatmap", default=0.0)
    circle_size: FloatProperty(name="Circle Size", description="Circle Size of the Beatmap", default=0.0)
    bpm: FloatProperty(name="BPM", description="Beats per Minute of the Beatmap", default=0.0)
    total_hitobjects: IntProperty(name="Total HitObjects", description="Total HitObjects in the Beatmap", default=0)
    mods: StringProperty(name="Active Mods", description="List of active mods", default="")
    accuracy: FloatProperty(name="Accuracy", description="Replay accuracy in percent", default=0.0)
    misses: IntProperty(name="Misses", description="Number of missed HitObjects in the Replay", default=0)
    formatted_mods: StringProperty(name="Formatted Mods", description="Formatted list of active mods", default="")
    base_approach_rate: FloatProperty(name="Approach Rate", description="Base Approach Rate of the Beatmap", default=0.0)
    adjusted_approach_rate: FloatProperty(name="Adjusted Approach Rate", description="Adjusted Approach Rate with Mods", default=0.0)
    base_circle_size: FloatProperty(name="Circle Size", description="Base Circle Size of the Beatmap", default=0.0)
    adjusted_circle_size: FloatProperty(name="Adjusted Circle Size", description="Adjusted Circle Size with Mods", default=0.0)
    base_overall_difficulty: FloatProperty(name="Overall Difficulty", description="Base Overall Difficulty of the Beatmap", default=0.0)
    adjusted_overall_difficulty: FloatProperty(name="Adjusted Overall Difficulty", description="Adjusted Overall Difficulty with Mods", default=0.0)
    max_combo: IntProperty(name="Max Combo", description="Maximum Combo in the Replay", default=0)
    total_score: IntProperty(name="Total Score", description="Total Score of the Replay", default=0)
    import_circles: BoolProperty(name="Import Circles", description="Import circles from the Beatmap", default=True)
    import_sliders: BoolProperty(name="Import Sliders", description="Import sliders from the Beatmap", default=True)
    import_spinners: BoolProperty(name="Import Spinners", description="Import spinners from the Beatmap", default=True)
    import_audio: BoolProperty(name="Import Audio", description="Import the Beatmap's audio file", default=True)

class OSU_PT_ImporterPanel(Panel):
    bl_label = "osu! Importer"
    bl_idname = "OSU_PT_importer_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "osu! Importer"

    def draw(self, context):
        layout = self.layout
        props = context.scene.osu_importer_props

        # File Selection
        box = layout.box()
        box.label(text="File Selection", icon='FILE_FOLDER')
        box.prop(props, "osu_file")
        box.prop(props, "osr_file")
        box.operator("osu_importer.import", text="Import", icon='IMPORT')

        # Beatmap Information
        if props.bpm != 0.0:
            box = layout.box()
            box.label(text="Beatmap Information", icon='INFO')
            col = box.column(align=True)
            col.label(text=f"BPM: {props.bpm:.2f}")
            ar_modified = abs(props.base_approach_rate - props.adjusted_approach_rate) > 0.01
            col.label(text=f"AR: {props.base_approach_rate} ({props.adjusted_approach_rate:.1f})" if ar_modified else f"AR: {props.base_approach_rate}")
            cs_modified = abs(props.base_circle_size - props.adjusted_circle_size) > 0.01
            col.label(text=f"CS: {props.base_circle_size} ({props.adjusted_circle_size:.1f})" if cs_modified else f"CS: {props.base_circle_size}")
            od_modified = abs(props.base_overall_difficulty - props.adjusted_overall_difficulty) > 0.01
            col.label(text=f"OD: {props.base_overall_difficulty} ({props.adjusted_overall_difficulty:.1f})" if od_modified else f"OD: {props.base_overall_difficulty}")
            col.label(text=f"HitObjects: {props.total_hitobjects}")

        # Replay Information
        if props.formatted_mods != "None" or props.accuracy != 0.0 or props.misses != 0:
            box = layout.box()
            box.label(text="Replay Information", icon='PLAY')
            col = box.column(align=True)
            col.label(text=f"Mods: {props.formatted_mods}")
            col.label(text=f"Accuracy: {props.accuracy:.2f}%")
            col.label(text=f"Misses: {props.misses}")
            col.label(text=f"Max Combo: {props.max_combo}")
            col.label(text=f"Total Score: {props.total_score}")

        # Settings
        box = layout.box()
        box.label(text="Settings", icon='PREFERENCES')
        col = box.column(align=True)
        col.prop(props, "import_circles")
        col.prop(props, "import_sliders")
        col.prop(props, "import_spinners")
        col.prop(props, "import_audio")

class OSU_OT_Import(Operator):
    bl_idname = "osu_importer.import"
    bl_label = "Import"
    bl_description = "Import selected Beatmap and Replay"

    def execute(self, context):
        from .exec import main_execution

        context.scene.render.fps = 60
        self.report({'INFO'}, "Scene set to 60 FPS")

        result, data_manager = main_execution(context)

        props = context.scene.osu_importer_props
        props.base_approach_rate = data_manager.get_base_ar()
        props.adjusted_approach_rate = data_manager.calculate_adjusted_ar()
        props.base_circle_size = data_manager.get_base_cs()
        props.adjusted_circle_size = data_manager.calculate_adjusted_cs()
        props.base_overall_difficulty = data_manager.get_base_od()
        props.adjusted_overall_difficulty = data_manager.calculate_adjusted_od()
        props.bpm = data_manager.beatmap_info["bpm"]
        props.total_hitobjects = data_manager.beatmap_info["total_hitobjects"]

        # Replay Information
        props.formatted_mods = data_manager.replay_info["mods"]
        props.accuracy = data_manager.replay_info["accuracy"]
        props.misses = data_manager.replay_info["misses"]
        props.max_combo = data_manager.replay_info["max_combo"]
        props.total_score = data_manager.replay_info["total_score"]

        return result
