# osu_importer/utils.py

import bpy

from .constants import SCALE_FACTOR

def get_ms_per_frame():
    fps = bpy.context.scene.render.fps
    return 1000 / fps  # Millisekunden pro Frame

def create_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection

def shift_cursor_keyframes(cursor_object_name, offset_ms):
    cursor = bpy.data.objects.get(cursor_object_name)
    if cursor is None:
        print(f"Objekt '{cursor_object_name}' nicht gefunden.")
        return

    if cursor.animation_data is None or cursor.animation_data.action is None:
        print(f"Keine Animation gefunden für Objekt '{cursor_object_name}'.")
        return

    action = cursor.animation_data.action
    fcurves = action.fcurves

    frame_offset = offset_ms / get_ms_per_frame()

    for fcurve in fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.co.x += frame_offset
            keyframe.handle_left.x += frame_offset
            keyframe.handle_right.x += frame_offset

        fcurve.update()

def map_osu_to_blender(x, y):
    corrected_x = (x - 256) * SCALE_FACTOR  # Zentrieren auf 0
    corrected_y = 0
    corrected_z = (192 - y) * SCALE_FACTOR  # Invertieren und zentrieren
    return corrected_x, corrected_y, corrected_z