# # osu_importer/ui.py

import bpy
from bpy.types import Panel, PropertyGroup, Operator
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, EnumProperty
from osu_importer.utils.utils import update_quick_load, flip_objects, update_override_mods, update_dev_tools

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
    # Import Type
    import_type: EnumProperty(
        name="Import Type",
        description="Choose the import type:\n- Base: Import minimal data with Geometry Nodes\n- Full: Import complete data with visibility keyframes",
        items=[
            ('BASE', "Base Map/Replay", "Import empty meshes with Geometry Nodes"),
            ('FULL', "Full Map", "Import full meshes with visibility keyframes")
        ],
        default='BASE'
    )
    include_osu_gameplay: BoolProperty(
        name="Include Osu_Gameplay",
        description="Add Osu_Gameplay mesh and Geometry Nodes setup",
        default=True
    )
    # Import Options
    import_approach_circles: BoolProperty(
        name="Approach Circles",
        description="Import approach circles for each hit object",
        default=True
    )
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
    import_slider_heads_tails: BoolProperty(
        name="Slider Heads and Tails",
        description="Import slider head and tail circles for each slider in FULL import",
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
        default=True
    )
    slider_resolution: IntProperty(
        name="Slider Resolution",
        description="Defines the smoothness of sliders (higher values = smoother but more performance intensive)",
        default=12,
        min=4,
        max=50
    )
    approach_circle_bevel_depth: FloatProperty(
        name="Bevel Depth",
        description="Adjust the bevel depth of approach circles in FULL import",
        default=0.02,
        min=0.0,
        max=1.0,
        subtype='NONE',
        step=0.01,
        precision=2
    )
    approach_circle_bevel_resolution: IntProperty(
        name="Bevel Resolution",
        description="Adjust the bevel depth of approach circles in FULL import",
        default=4,
        min=1,
        max=12
    )
    # Replay Options
    import_cursors: BoolProperty(
        name="Cursor Movements",
        description="Import cursor movements from the replay",
        default=True
    )
    cursor_size: FloatProperty(
        name="Cursor Size",
        description="Adjust the size of the cursor",
        default=1.0,
        min=0.1,
        max=10.0,
        step=0.1,
        precision=2
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
    player_name: StringProperty(  # Neue Eigenschaft für den Spielernamen
        name="Player Name",
        default="Unknown"
    )
    dev_tools: BoolProperty(
        name="Enable Dev Tools",
        description="Enable development tools",
        default=False,
        update=update_dev_tools
    )
    quick_load: BoolProperty(
        name="Quick Load",
        description="Automatically load predefined file paths for .osu and .osr files",
        default=False,
        update=lambda self, context: update_quick_load(self)
    )
    auto_create_shaders: BoolProperty(
        name="Auto Create Shaders",
        description="Automatically create basic shaders for imported elements",
        default=False,
    )
    #Override Mods
    override_mods: BoolProperty(
        name="Override Mods",
        description="Manually override the replay's mods with custom settings",
        default=False,
        update = update_override_mods
    )

    # Modifiers aus constants.py
    override_no_fail: BoolProperty(name="No Fail", default=False)
    override_easy: BoolProperty(name="Easy", default=False)
    override_hidden: BoolProperty(name="Hidden", default=False)
    override_hard_rock: BoolProperty(name="Hard Rock", default=False)
    override_sudden_death: BoolProperty(name="Sudden Death", default=False)
    override_double_time: BoolProperty(name="Double Time", default=False)
    override_half_time: BoolProperty(name="Half Time", default=False)
    override_nightcore: BoolProperty(name="Nightcore", default=False)
    override_flashlight: BoolProperty(name="Flashlight", default=False)
    override_perfect: BoolProperty(name="Perfect", default=False)
    override_spun_out: BoolProperty(name="Spun Out", default=False)
    override_autopilot: BoolProperty(name="Autopilot", default=False)
    override_relax: BoolProperty(name="Relax", default=False)
    override_cinema: BoolProperty(name="Cinema", default=False)

    # UI Toggles
    show_beatmap_info: BoolProperty(
        name="Show Beatmap Information",
        description="Toggle visibility of Beatmap Information",
        default=False
    )
    show_replay_info: BoolProperty(
        name="Show Replay Information",
        description="Toggle visibility of Replay Information",
        default=False
    )
    show_tool_info: BoolProperty(
        name="Show Tools",
        description="Toggle visibility of Tools",
        default=False
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
        if props.dev_tools:
            box.label(text="Dev Tools Activated", icon='MODIFIER')
            #Quick Load (Adjust update_dev_tools in utils.py)
            box.prop(props, "osu_file")
            box.prop(props, "osr_file")
        else:
            # Standard File Selection
            box.prop(props, "osu_file")
            box.prop(props, "osr_file")

        box.separator()
        box.operator("osu_importer.import", text="Import", icon='IMPORT')
        box.operator("osu_importer.delete", text="Delete Imported Data", icon='TRASH')

class OSU_PT_SkinPanel(bpy.types.Panel):
    bl_label = "Skin"
    bl_idname = "OSU_PT_skin_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "osu! Importer"

    def draw(self, context):
        layout = self.layout
        props = context.scene.osu_importer_props

        layout.prop(props, "auto_create_shaders", text="Auto Create Shaders", toggle=True)


class OSU_PT_ReplayInfoPanel(Panel):
    bl_label = "Replay Information"
    bl_idname = "OSU_PT_replay_info_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "osu! Importer"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        props = context.scene.osu_importer_props
        # Anzeigen nur, wenn ein Replay importiert wurde
        return props.osr_file and props.player_name != "Unknown"

    def draw(self, context):
        layout = self.layout
        props = context.scene.osu_importer_props

        if props.formatted_mods != "None" or props.accuracy != 0.0 or props.misses != 0:
            col = layout.column(align=True)
            col.label(text=f"Player Name: {props.player_name}")
            col.label(text=f"Mods: {props.formatted_mods}")
            col.label(text=f"Accuracy: {props.accuracy:.2f}%")
            col.label(text=f"Misses: {props.misses}")
            col.label(text=f"Max Combo: {props.max_combo}")
            col.label(text=f"Total Score: {props.total_score}")
        else:
            layout.label(text="No Replay Information Available", icon='INFO')

class OSU_PT_BeatmapInfoPanel(Panel):
    bl_label = "Beatmap Information"
    bl_idname = "OSU_PT_beatmap_info_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "osu! Importer"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        props = context.scene.osu_importer_props
        # Anzeigen nur, wenn eine Beatmap importiert wurde
        return props.osu_file and props.title != ""

    def draw(self, context):
        layout = self.layout
        props = context.scene.osu_importer_props

        if props.bpm != 0.0:
            col = layout.column(align=True)
            col.label(text=f"Title: {props.title}")
            col.label(text=f"Artist: {props.artist}")
            col.label(text=f"Difficulty: {props.difficulty_name}")
            col.separator()
            col.label(text=f"BPM: {props.bpm:.2f}")
            ar_modified = abs(props.base_approach_rate - props.adjusted_approach_rate) > 0.01
            if ar_modified:
                col.label(text=f"AR: {props.base_approach_rate} (Adjusted: {props.adjusted_approach_rate:.1f})")
            else:
                col.label(text=f"AR: {props.base_approach_rate}")
            cs_modified = abs(props.base_circle_size - props.adjusted_circle_size) > 0.01
            if cs_modified:
                col.label(text=f"CS: {props.base_circle_size} (Adjusted: {props.adjusted_circle_size:.1f})")
            else:
                col.label(text=f"CS: {props.base_circle_size}")
            od_modified = abs(props.base_overall_difficulty - props.adjusted_overall_difficulty) > 0.01
            if od_modified:
                col.label(text=f"OD: {props.base_overall_difficulty} (Adjusted: {props.adjusted_overall_difficulty:.1f})")
            else:
                col.label(text=f"OD: {props.base_overall_difficulty}")
            col.label(text=f"Total HitObjects: {props.total_hitobjects}")
        else:
            layout.label(text="No Beatmap Information Available", icon='INFO')


class OSU_PT_ToolsPanel(Panel):
    bl_label = "Tools"
    bl_idname = "OSU_PT_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "osu! Importer"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.osu_importer_props

        # Flip Cursor Position
        col = layout.column(align=True)
        col.label(text="Cursor Transformation:", icon='CURSOR')
        row = col.row(align=True)
        row.operator("osu_importer.flip_cursor_horizontal", text="Flip Cursor Horizontal", icon='ARROW_LEFTRIGHT')
        row.operator("osu_importer.flip_cursor_vertical", text="Flip Cursor Vertical", icon='EVENT_DOWN_ARROW')

        # Flip Map
        col.separator()
        col.label(text="Map Transformation:", icon='MOD_MIRROR')
        row = col.row(align=True)
        row.operator("osu_importer.flip_map_horizontal", text="Flip Map Horizontal", icon='ARROW_LEFTRIGHT')
        row.operator("osu_importer.flip_map_vertical", text="Flip Map Vertical", icon='EVENT_DOWN_ARROW')

        # Dev Tools Toggle
        col.separator()
        col.prop(props, "dev_tools", text="Enable Dev Tools", toggle=True)
        if props.dev_tools:
            dev_box = layout.box()
            dev_box.label(text="Developer Tools", icon='TOOL_SETTINGS')

            # Quick Load Option
            dev_box.prop(props, "quick_load", text="Quick Load", toggle=True)

            # Override Mods Options
            dev_box.label(text="Override Mods", icon='MODIFIER')
            dev_box.prop(props, "override_mods", toggle=True)
            if props.override_mods:
                dev_box.prop(props, "override_no_fail", toggle=True)
                dev_box.prop(props, "override_easy", toggle=True)
                dev_box.prop(props, "override_hidden", toggle=True)
                dev_box.prop(props, "override_hard_rock", toggle=True)
                dev_box.prop(props, "override_sudden_death", toggle=True)
                dev_box.prop(props, "override_double_time", toggle=True)
                dev_box.prop(props, "override_half_time", toggle=True)
                dev_box.prop(props, "override_nightcore", toggle=True)
                dev_box.prop(props, "override_flashlight", toggle=True)
                dev_box.prop(props, "override_perfect", toggle=True)
                dev_box.prop(props, "override_spun_out", toggle=True)
                dev_box.prop(props, "override_autopilot", toggle=True)
                dev_box.prop(props, "override_relax", toggle=True)
                dev_box.prop(props, "override_cinema", toggle=True)

class OSU_PT_ImportOptionsPanel(Panel):
    bl_label = "Import Options"
    bl_idname = "OSU_PT_import_options_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "osu! Importer"

    def draw(self, context):
        layout = self.layout
        props = context.scene.osu_importer_props

        # Import Options
        box = layout.box()

        # Import Type Selection
        box.prop(props, "import_type")

        # import_type 'BASE'
        if props.import_type == 'BASE':
            box.prop(props, "include_osu_gameplay", toggle=True)

        # Hit Objects Import Options
        col = box.column(align=True)
        col.label(text="Hit Objects:", icon='OBJECT_DATA')
        col.prop(props, "import_approach_circles", toggle=True)
        if props.import_type == 'FULL' and props.import_approach_circles:
            col.prop(props, "approach_circle_bevel_depth")
            col.prop(props, "approach_circle_bevel_resolution")
        row = col.row(align=True)
        row.prop(props, "import_circles", toggle=True)
        row.prop(props, "import_sliders", toggle=True)
        row.prop(props, "import_spinners", toggle=True)

        # Slider Options
        if props.import_sliders:
            col.separator()
            col.label(text="Slider Options:", icon='MOD_CURVE')
            col.prop(props, "slider_resolution")
            row = col.row(align=True)
            if props.import_type == 'FULL':
                row.prop(props, "import_slider_heads_tails", toggle=True)

            col.prop(props, "import_slider_balls", toggle=True)
            col.prop(props, "import_slider_ticks", toggle=True)

            if props.import_slider_ticks:
                col.separator()
                warning_box = col.box()
                warning_row = warning_box.row(align=True)
                warning_row.label(text="⚠️  WARNING  ⚠️", icon='NONE')
                warning_row = warning_box.row(align=True)
                warning_row.label(text="Slider Ticks are NOT recommended!", icon='NONE')
                warning_row = warning_box.row(align=True)
                warning_row.label(text="This can lead to too many objects.", icon='NONE')

        # Replay Options
        col.separator()
        col.label(text="Replay Options:", icon='REC')
        col.prop(props, "import_cursors", toggle=True)

        if props.import_cursors:
            col.prop(props, "cursor_size", text="Cursor Size")

        # Audio Options
        col.separator()
        col.label(text="Audio Options:", icon='SPEAKER')
        col.prop(props, "import_audio", toggle=True)

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

            if result != {'FINISHED'} or data_manager is None:
                return {'CANCELLED'}

            props.base_approach_rate = data_manager.base_ar
            props.adjusted_approach_rate = data_manager.adjusted_ar
            props.base_circle_size = data_manager.base_cs
            props.adjusted_circle_size = data_manager.adjusted_cs
            props.base_overall_difficulty = data_manager.base_od
            props.adjusted_overall_difficulty = data_manager.adjusted_od
            props.bpm = data_manager.beatmap_info["bpm"]
            props.total_hitobjects = data_manager.beatmap_info["total_hitobjects"]

            props.title = data_manager.beatmap_info["metadata"].get("Title", "")
            props.artist = data_manager.beatmap_info["metadata"].get("Artist", "")
            props.difficulty_name = data_manager.beatmap_info["metadata"].get("Version", "")

            props.formatted_mods = data_manager.replay_info["mods"]
            props.accuracy = data_manager.replay_info["accuracy"]
            props.misses = data_manager.replay_info["misses"]
            props.max_combo = data_manager.replay_info["max_combo"]
            props.player_name = data_manager.replay_info["username"]
            props.total_score = data_manager.replay_info["total_score"]

            return result

        except Exception as e:
            self.report({'ERROR'}, f"Error during import: {str(e)}")
            return {'CANCELLED'}

class OSU_OT_FlipCursorHorizontal(Operator):
    bl_idname = "osu_importer.flip_cursor_horizontal"
    bl_label = "Flip Cursor Horizontal"
    bl_description = "Spiegelt die Cursor-Positionen horizontal (X-Achse)"

    def execute(self, context):
        flipped_count = flip_objects(["Cursor"], axis="x")
        self.report({'INFO'}, f"Horizontales Spiegeln der {flipped_count} Cursor abgeschlossen.")
        return {'FINISHED'}

class OSU_OT_FlipCursorVertical(Operator):
    bl_idname = "osu_importer.flip_cursor_vertical"
    bl_label = "Flip Cursor Vertical"
    bl_description = "Spiegelt die Cursor-Positionen vertikal (Y-Achse)"

    def execute(self, context):
        flipped_count = flip_objects(["Cursor"], axis="z")
        self.report({'INFO'}, f"Vertikales Spiegeln der {flipped_count} Cursor abgeschlossen.")
        return {'FINISHED'}

class OSU_OT_FlipMapHorizontal(Operator):
    bl_idname = "osu_importer.flip_map_horizontal"
    bl_label = "Flip Map Horizontal"
    bl_description = "Spiegelt die gesamte Karte horizontal (X-Achse)"

    def execute(self, context):
        flipped_count = flip_objects(["Circle", "Slider", "Spinner", "Approach", "Osu_Gameplay", "Slider Heads Tails"], axis="x")
        self.report({'INFO'}, f"Horizontales Spiegeln der {flipped_count} Kartenobjekte abgeschlossen.")
        return {'FINISHED'}

class OSU_OT_FlipMapVertical(Operator):
    bl_idname = "osu_importer.flip_map_vertical"
    bl_label = "Flip Map Vertical"
    bl_description = "Spiegelt die gesamte Karte vertikal (Y-Achse)"

    def execute(self, context):
        flipped_count = flip_objects(["Circle", "Slider", "Spinner", "Approach", "Osu_Gameplay", "Slider Heads Tails"], axis="z")
        self.report({'INFO'}, f"Vertikales Spiegeln der {flipped_count} Kartenobjekte abgeschlossen.")
        return {'FINISHED'}