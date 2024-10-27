# utils.py

import bpy
from .constants import SCALE_FACTOR

def get_ms_per_frame():
    fps = bpy.context.scene.render.fps
    return 1000 / fps  # Milliseconds per frame

def create_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection

def map_osu_to_blender(x, y):
    corrected_x = (x - 256) * SCALE_FACTOR  # Centering on zero
    corrected_y = 0
    corrected_z = (192 - y) * SCALE_FACTOR  # Invert and center
    return corrected_x, corrected_y, corrected_z
