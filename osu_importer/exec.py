# osu_importer/exec.py

import bpy
import os
from .osu_data_manager import OsuDataManager
from .import_objects import import_hitobjects
from .utils.utils import timeit


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

    with timeit("OsuDataManager Initialisierung"):
        data_manager = OsuDataManager(osu_file_path, osr_file_path, props)

    data_manager.print_all_info()

    if props.import_audio:
        with timeit("Audio Importieren"):
            data_manager.import_audio()

    with timeit("Hits Überprüfen"):
        data_manager.check_hits()

    settings = {
        'audio_lead_in': data_manager.audio_lead_in,
        'import_slider_balls': props.import_slider_balls,
        'import_slider_ticks': props.import_slider_ticks,
        'slider_resolution': props.slider_resolution,
        'import_type': props.import_type
    }

    with timeit("Hitobjects Importieren"):
        import_hitobjects(data_manager, settings, props)

    with timeit("Frame-Range Setzen"):
        scene = bpy.context.scene
        anim_objects = [obj for obj in bpy.data.objects if obj.animation_data and obj.animation_data.action]
        if anim_objects:
            scene.frame_start = int(
                min([action.frame_range[0] for obj in anim_objects for action in [obj.animation_data.action]]))
            scene.frame_end = int(
                max([action.frame_range[1] for obj in anim_objects for action in [obj.animation_data.action]]))

    return {'FINISHED'}, data_manager
