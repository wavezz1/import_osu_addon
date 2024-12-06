# osu_importer/exec.py

import bpy
import os
from .osu_data_manager import OsuDataManager
from .import_objects import import_hitobjects
from .utils.utils import timeit
from .config import ImportConfig


def main_execution(context):
    props = context.scene.osu_importer_props
    osu_file_path = bpy.path.abspath(props.osu_file)
    osr_file_path = bpy.path.abspath(props.osr_file)

    if not os.path.isfile(osu_file_path) or not os.path.isfile(osr_file_path):
        context.window_manager.popup_menu(
            lambda self, ctx: self.layout.label(text="The specified .osu or .osr file does not exist."),
            title="Error",
            icon='ERROR'
        )
        return {'CANCELLED'}, None

    if props.auto_create_shaders:
        try:
            from .shader_nodes.basic_circle import circles_node_group
            from .shader_nodes.basic_slider import slider_node_group
            from .shader_nodes.basic_slider_ball import slider_balls_node_group
            from .shader_nodes.basic_approach_circle import approach_circles_node_group
            from .shader_nodes.basic_cursor import cursor_node_group
            from .shader_nodes.basic_spinner import spinner_node_group

            circles_node_group()
            slider_node_group()
            slider_balls_node_group()
            approach_circles_node_group()
            cursor_node_group()
            spinner_node_group()

            print("Shaders created successfully.")
        except Exception as e:
            context.window_manager.popup_menu(
                lambda self, ctx: self.layout.label(text=f"Error creating shaders: {str(e)}"),
                title="Shader Error",
                icon='ERROR'
            )
            return {'CANCELLED'}, None

    with timeit("OsuDataManager Initialisierung"):
        data_manager = OsuDataManager(osu_file_path, osr_file_path, props)

    data_manager.print_all_info()

    if props.import_audio:
        with timeit("Audio Importieren"):
            data_manager.import_audio()

    with timeit("Hits Überprüfen"):
        data_manager.check_hits()

    # Erstelle jetzt das zentrale config-Objekt
    config = ImportConfig(props, data_manager)

    with timeit("Hitobjects Importieren"):
        # Statt data_manager, settings, props nun nur noch config
        import_hitobjects(config)

    with timeit("Frame-Range Setzen"):
        scene = bpy.context.scene
        anim_objects = [obj for obj in bpy.data.objects if obj.animation_data and obj.animation_data.action]
        if anim_objects:
            scene.frame_start = int(
                min([action.frame_range[0] for obj in anim_objects for action in [obj.animation_data.action]]))
            scene.frame_end = int(
                max([action.frame_range[1] for obj in anim_objects for action in [obj.animation_data.action]]))

    return {'FINISHED'}, data_manager
