# utils.py

import bpy
from mathutils import Vector
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

def evaluate_curve_at_t(curve_object, t):
    spline = curve_object.data.splines[0]
    if spline.type == 'BEZIER':
        # Berechne die Position auf einer Bezier-Kurve
        num_segments = len(spline.bezier_points) - 1
        segment_length = 1.0 / num_segments
        segment_index = min(int(t / segment_length), num_segments - 1)
        local_t = (t - (segment_index * segment_length)) / segment_length

        p0 = spline.bezier_points[segment_index].co.to_3d()
        p1 = spline.bezier_points[segment_index].handle_right.to_3d()
        p2 = spline.bezier_points[segment_index + 1].handle_left.to_3d()
        p3 = spline.bezier_points[segment_index + 1].co.to_3d()

        # Bezier-Kurve Formel
        return ( (1 - local_t)**3 * p0 +
                 3 * (1 - local_t)**2 * local_t * p1 +
                 3 * (1 - local_t) * local_t**2 * p2 +
                 local_t**3 * p3 )
    elif spline.type == 'POLY':
        # Für POLY-Kurven (lineare Segmente)
        num_points = len(spline.points)
        segment_length = 1.0 / (num_points - 1)
        segment_index = min(int(t / segment_length), num_points - 2)
        local_t = (t - (segment_index * segment_length)) / segment_length

        p0 = spline.points[segment_index].co.to_3d()
        p1 = spline.points[segment_index + 1].co.to_3d()

        return p0.lerp(p1, local_t)
    elif spline.type == 'NURBS':
        # Für NURBS-Kurven
        # NURBS-Kurvenberechnung ist komplex; hier eine einfache Approximation
        num_points = len(spline.points)
        segment_length = 1.0 / (num_points - 1)
        segment_index = min(int(t / segment_length), num_points - 2)
        local_t = (t - (segment_index * segment_length)) / segment_length

        p0 = spline.points[segment_index].co.to_3d()
        p1 = spline.points[segment_index + 1].co.to_3d()

        return p0.lerp(p1, local_t)
    return Vector((0, 0, 0))