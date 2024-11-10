# ui.py

import bpy
from bpy.types import Panel, PropertyGroup, Operator
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty


class OSUImporterProperties(PropertyGroup):
    # File Paths
    osu_file: StringProperty(
        name="Beatmap (.osu) File",
        description="Path to the .osu beatmap file",
        default="",
        subtype='FILE_PATH'
    )
    osr_file: StringProperty(
        name="Replay (.osr) File",
        description="Path to the .osr replay file",
        default="",
        subtype='FILE_PATH'
    )
    # Import Options
    import_circles: BoolProperty(
        name="Circles",
        description="Import circle hit objects",
        default=True
    )
    import_sliders: BoolProperty(
        name="Sliders",
        description="Import slider hit objects",
        default=True
    )
    import_spinners: BoolProperty(
        name="Spinners",
        description="Import spinner hit objects",
        default=True
    )
    # Slider Options
    import_slider_ticks: BoolProperty(
        name="Slider Ticks",
        description="Import slider ticks",
        default=False
    )
    import_slider_balls: BoolProperty(
        name="Slider Balls",
        description="Import slider balls",
        default=False
    )
    slider_resolution: IntProperty(
        name="Slider Resolution",
        description="Defines the smoothness of sliders (higher values = smoother but more performance intensive)",
        default=12,
        min=4,
        max=50
    )
    # Replay Options
    import_cursors: BoolProperty(
        name="Cursor Movements",
        description="Import cursor movements from the replay",
        default=True
    )
    # Audio Options
    import_audio: BoolProperty(
        name="Audio Track",
        description="Import the audio track associated with the beatmap",
        default=True
    )
    # Beatmap Information
    title: StringProperty(
        name="Title",
        default=""
    )
    artist: StringProperty(
        name="Artist",
        default=""
    )
    difficulty_name: StringProperty(
        name="Difficulty",
        default=""
    )
    bpm: FloatProperty(
        name="BPM",
        default=0.0
    )
    base_approach_rate: FloatProperty(
        name="Base AR",
        default=0.0
    )
    adjusted_approach_rate: FloatProperty(
        name="Adjusted AR",
        default=0.0
    )
    base_circle_size: FloatProperty(
        name="Base CS",
        default=0.0
    )
    adjusted_circle_size: FloatProperty(
        name="Adjusted CS",
        default=0.0
    )
    base_overall_difficulty: FloatProperty(
        name="Base OD",
        default=0.0
    )
    adjusted_overall_difficulty: FloatProperty(
        name="Adjusted OD",
        default=0.0
    )
    total_hitobjects: IntProperty(
        name="Total HitObjects",
        default=0
    )
    # Replay Information
    formatted_mods: StringProperty(
        name="Mods",
        default="None"
    )
    accuracy: FloatProperty(
        name="Accuracy",
        default=0.0
    )
    misses: IntProperty(
        name="Misses",
        default=0
    )
    max_combo: IntProperty(
        name="Max Combo",
        default=0
    )
    total_score: IntProperty(
        name="Total Score",
        default=0
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

        # File Selection
        box = layout.box()
        box.label(text="File Selection", icon='FILE_FOLDER')
        box.prop(props, "osu_file")
        box.prop(props, "osr_file")
        box.operator("osu_importer.import", text="Import", icon='IMPORT')

        # Import Options
        box = layout.box()
        box.label(text="Import Options", icon='IMPORT')

        # Hit Objects Import Options
        col = box.column(align=True)
        col.label(text="Hit Objects:", icon='OBJECT_DATA')
        row = col.row(align=True)
        row.prop(props, "import_circles", toggle=True)
        row.prop(props, "import_sliders", toggle=True)
        row.prop(props, "import_spinners", toggle=True)

        # Slider Options (only visible if sliders are imported)
        if props.import_sliders:
            col.separator()
            col.label(text="Slider Options:", icon='MOD_CURVE')
            col.prop(props, "import_slider_ticks")
            col.prop(props, "import_slider_balls")
            col.prop(props, "slider_resolution")

        # Replay Options
        col.separator()
        col.label(text="Replay Options:", icon='REC')
        col.prop(props, "import_cursors")

        # Audio Options
        col.separator()
        col.label(text="Audio Options:", icon='SPEAKER')
        col.prop(props, "import_audio")

        # Beatmap Information
        if props.bpm != 0.0:
            box = layout.box()
            box.label(text="Beatmap Information", icon='INFO')
            col = box.column(align=True)
            col.label(text=f"Title: {props.title}")
            col.label(text=f"Artist: {props.artist}")
            col.label(text=f"Difficulty: {props.difficulty_name}")
            col.separator()
            col.label(text=f"BPM: {props.bpm:.2f}")
            ar_modified = abs(props.base_approach_rate - props.adjusted_approach_rate) > 0.01
            col.label(text=f"AR: {props.base_approach_rate} (Adjusted: {props.adjusted_approach_rate:.1f})" if ar_modified else f"AR: {props.base_approach_rate}")
            cs_modified = abs(props.base_circle_size - props.adjusted_circle_size) > 0.01
            col.label(text=f"CS: {props.base_circle_size} (Adjusted: {props.adjusted_circle_size:.1f})" if cs_modified else f"CS: {props.base_circle_size}")
            od_modified = abs(props.base_overall_difficulty - props.adjusted_overall_difficulty) > 0.01
            col.label(text=f"OD: {props.base_overall_difficulty} (Adjusted: {props.adjusted_overall_difficulty:.1f})" if od_modified else f"OD: {props.base_overall_difficulty}")
            col.label(text=f"Total HitObjects: {props.total_hitobjects}")

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


class OSU_OT_Import(Operator):
    bl_idname = "osu_importer.import"
    bl_label = "Import"
    bl_description = "Import selected Beatmap and Replay"

    def execute(self, context):
        from .exec import main_execution
        props = context.scene.osu_importer_props

        try:
            if not (props.osu_file and props.osr_file):
                self.report({'ERROR'}, "Please specify both .osu and .osr files.")
                return {'CANCELLED'}

            context.scene.render.fps = 60
            self.report({'INFO'}, "Scene set to 60 FPS")

            result, data_manager = main_execution(context)

            props.base_approach_rate = data_manager.get_base_ar()
            props.adjusted_approach_rate = data_manager.calculate_adjusted_ar()
            props.base_circle_size = data_manager.get_base_cs()
            props.adjusted_circle_size = data_manager.calculate_adjusted_cs()
            props.base_overall_difficulty = data_manager.get_base_od()
            props.adjusted_overall_difficulty = data_manager.calculate_adjusted_od()
            props.bpm = data_manager.beatmap_info["bpm"]
            props.total_hitobjects = data_manager.beatmap_info["total_hitobjects"]

            props.title = data_manager.beatmap_info["metadata"].get("Title", "")
            props.artist = data_manager.beatmap_info["metadata"].get("Artist", "")
            props.difficulty_name = data_manager.beatmap_info["metadata"].get("Version", "")

            props.formatted_mods = data_manager.replay_info["mods"]
            props.accuracy = data_manager.replay_info["accuracy"]
            props.misses = data_manager.replay_info["misses"]
            props.max_combo = data_manager.replay_info["max_combo"]
            props.total_score = data_manager.replay_info["total_score"]

            return result

        except Exception as e:
            self.report({'ERROR'}, f"Error during import: {str(e)}")
            return {'CANCELLED'}
