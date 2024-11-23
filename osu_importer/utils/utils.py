# # osu_importer/utils/utils.py

import time
import bpy
import mathutils
from osu_importer.utils.constants import SCALE_FACTOR

def update_dev_tools(self, context):
    if not self.dev_tools:
        self.quick_load = False

def update_quick_load(props):
    if props.quick_load:
        # .osu Path for Quick Load
        props.osu_file = r""
        # .osr Path for Quick Load
        props.osr_file = r""
    else:
        props.osu_file = ""
        props.osr_file = ""
        print("Quick Load deactivated: File paths cleared.")

def timeit(label):
    class Timer:
        def __init__(self, label):
            self.label = label
            self.start = None
            self.end = None
            self.duration = None

        def __enter__(self):
            self.start = time.perf_counter()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.end = time.perf_counter()
            self.duration = self.end - self.start
            print(f"[osu! Importer] {self.label}: {self.duration:.4f} Sekunden")

    return Timer(label)

def create_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection

def map_osu_to_blender(x, y):
    if not hasattr(map_osu_to_blender, 'cache'):
        map_osu_to_blender.cache = {}
    key = (x, y)
    if key in map_osu_to_blender.cache:
        return map_osu_to_blender.cache[key]
    corrected_x = (x - 256) * SCALE_FACTOR  # Centering on zero
    corrected_y = 0
    corrected_z = (192 - y) * SCALE_FACTOR  # Invert and center
    map_osu_to_blender.cache[key] = (corrected_x, corrected_y, corrected_z)
    return corrected_x, corrected_y, corrected_z

def evaluate_curve_at_t(curve_object, t):
    t = max(0.0, min(1.0, t))

    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_curve_object = curve_object.evaluated_get(depsgraph)
    eval_curve = eval_curve_object.data

    spline = eval_curve.splines[0]

    spline_length = spline.calc_length()

    desired_length = t * spline_length

    accumulated_length = 0.0

    points = []
    if spline.type == 'BEZIER':
        bezier_points = spline.bezier_points
        num_segments = len(bezier_points) - 1
        for i in range(num_segments):
            bp0 = bezier_points[i]
            bp1 = bezier_points[i + 1]

            p0 = bp0.co.xyz
            p1 = bp0.handle_right.xyz
            p2 = bp1.handle_left.xyz
            p3 = bp1.co.xyz

            segment_samples = 10
            for j in range(segment_samples):
                s = j / segment_samples
                point = mathutils.geometry.interpolate_bezier(p0, p1, p2, p3, s)
                points.append(point)
    else:
        spline_points = spline.points
        points = [p.co.xyz for p in spline_points]

    for i in range(len(points) - 1):
        p0 = points[i]
        p1 = points[i + 1]
        segment_length = (p1 - p0).length
        if accumulated_length + segment_length >= desired_length:
            remaining_length = desired_length - accumulated_length
            local_t = remaining_length / segment_length
            position = p0.lerp(p1, local_t)
            return curve_object.matrix_world @ position
        accumulated_length += segment_length

    last_point = points[-1]
    return curve_object.matrix_world @ last_point

def get_keyframe_values(hitobject, object_type, import_type, start_frame, end_frame, early_start_frame, approach_rate,
                        osu_radius, extra_params=None, ms_per_frame=None, audio_lead_in_frames=None):
    frame_values = {}
    fixed_values = {}

    frame_values["show"] = [
        (int(early_start_frame - 1), False),
        (int(early_start_frame), True),
    ]
    frame_values["was_hit"] = [
        (int(start_frame - 1), False),
        (int(start_frame), hitobject.was_hit)
    ]

    fixed_values["ar"] = approach_rate
    fixed_values["cs"] = osu_radius * SCALE_FACTOR * (2 if import_type == 'BASE' else 1)

    if object_type == 'circle':
        if import_type == 'FULL':
            frame_values["show"].append((int(start_frame + 1), False))
    elif object_type == 'slider':
        frame_values["show"].extend([
            (int(end_frame - 1), True),
            (int(end_frame), False)
        ])
        slider_end_frame = (hitobject.slider_end_time / ms_per_frame) + audio_lead_in_frames
        frame_values["was_completed"] = [
            (int(slider_end_frame - 1), False),
            (int(slider_end_frame), True)
        ]
        if extra_params:
            fixed_values.update(extra_params)
    elif object_type == 'spinner':
        frame_values["was_completed"] = [
            (int(end_frame - 1), False),
            (int(end_frame), True)
        ]
        if extra_params:
            fixed_values.update(extra_params)

    if import_type == 'BASE' and object_type != 'circle':
        frame_values["show"] = [
            (int(early_start_frame - 1), False),
            (int(early_start_frame), True),
            (int(end_frame - 1), True),
            (int(end_frame), False)
        ]

    return frame_values, fixed_values

def tag_imported(obj, tag="osu_imported", value=True):
    obj[tag] = value

def flip_objects(prefixes, axis, invert_location=True, invert_scale=True):
    flipped_count = 0
    objects_to_flip = [obj for obj in bpy.data.objects if any(obj.name.startswith(prefix) for prefix in prefixes)]

    for obj in objects_to_flip:
        if invert_location:
            setattr(obj.location, axis, getattr(obj.location, axis) * -1)
        if invert_scale:
            setattr(obj.scale, axis, getattr(obj.scale, axis) * -1)

        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                if fcurve.data_path in ["location", "scale"] and fcurve.array_index == "xyz".index(axis):
                    for keyframe in fcurve.keyframe_points:
                        keyframe.co.y *= -1
                        keyframe.handle_left.y *= -1
                        keyframe.handle_right.y *= -1
        flipped_count += 1

    return flipped_count

def update_override_mods(self, context):
    for prop_name in dir(self):
        if prop_name.startswith("override_") and prop_name != "override_mods":
            setattr(self, prop_name, False)