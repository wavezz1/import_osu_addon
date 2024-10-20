# utils.py

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

def map_osu_to_blender(x, y):
    corrected_x = (x - 256) * SCALE_FACTOR  # Zentrieren auf 0
    corrected_y = 0
    corrected_z = (192 - y) * SCALE_FACTOR  # Invertieren und zentrieren
    return corrected_x, corrected_y, corrected_z