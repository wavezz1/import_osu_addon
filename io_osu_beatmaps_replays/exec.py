# exec.py

import bpy
import os
from .osu_replay_data_manager import OsuReplayDataManager
from .import_objects import import_hitobjects
from .cursor import create_cursor, animate_cursor
from .utils import create_collection
from .mod_functions import calculate_speed_multiplier

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

    data_manager = OsuReplayDataManager(osu_file_path, osr_file_path)
    data_manager.print_all_info()
    if props.import_audio:
        data_manager.import_audio()

    data_manager.check_hits()
    speed_multiplier = calculate_speed_multiplier(data_manager.mods)

    settings = {
        'speed_multiplier': speed_multiplier,
        'audio_lead_in': data_manager.beatmap_info.get("audio_lead_in", 0),
        'early_frames': 5,  # if needed
    }

    import_hitobjects(data_manager, settings, props)

    cursor_collection = create_collection("Cursor")
    cursor = create_cursor(cursor_collection, data_manager)
    if cursor:
        animate_cursor(cursor, data_manager.replay_data, data_manager.key_presses, calculate_speed_multiplier(data_manager.mods))
    else:
        print("Cursor could not be created.")

    # Set frame start and end based on animation
    scene = bpy.context.scene
    scene.frame_start = int(min([obj.animation_data.action.frame_range[0] for obj in bpy.data.objects if
                                 obj.animation_data and obj.animation_data.action]))
    scene.frame_end = int(max([obj.animation_data.action.frame_range[1] for obj in bpy.data.objects if
                               obj.animation_data and obj.animation_data.action]))

    return {'FINISHED'}, data_manager

def connect_attributes_with_drivers(obj, attributes):
    for attr_name, attr_type in attributes.items():
        # Überprüfen, ob das Objekt die Property besitzt
        if attr_name in obj:
            # Erstellen eines Fahrers für das entsprechende Attribut im Node Group Input
            modifier = obj.modifiers.get("GeometryNodes")
            if not modifier:
                continue
            node_group = modifier.node_group
            if not node_group:
                continue

            # Finden des entsprechenden Store Nodes
            store_node = None
            for node in node_group.nodes:
                if isinstance(node, bpy.types.GeometryNodeStoreNamedAttribute) and node.inputs['Name'].default_value == attr_name:
                    store_node = node
                    break
            if not store_node:
                continue

            # Hinzufügen des Fahrers
            driver = store_node.inputs['Value'].driver_add('default_value').driver
            driver.type = 'AVERAGE'
            var = driver.variables.new()
            var.name = 'var'
            var.targets[0].id_type = 'OBJECT'
            var.targets[0].id = obj
            var.targets[0].data_path = f'["{attr_name}"]'
