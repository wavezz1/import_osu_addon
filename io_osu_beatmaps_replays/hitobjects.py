# osu_importer/hitobjects.py

import bpy
from .utils import get_ms_per_frame, map_osu_to_blender
from .constants import SCALE_FACTOR
from .io import parse_timing_points

def create_circle_at_position(x, y, name, start_time_ms, global_index, circles_collection, offset, early_frames=5, end_time_ms=None):
    corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)
    try:
        start_frame = (start_time_ms + offset) / get_ms_per_frame()
        early_start_frame = start_frame - early_frames

        bpy.ops.mesh.primitive_circle_add(radius=0.5, location=(corrected_x, corrected_y, corrected_z))
        circle = bpy.context.object
        circle.name = f"{global_index:03d}_{name}"

        # Keyframe zum Einblenden
        circle.hide_viewport = True
        circle.hide_render = True
        circle.keyframe_insert(data_path="hide_viewport", frame=early_start_frame - 1)
        circle.keyframe_insert(data_path="hide_render", frame=early_start_frame - 1)

        circle.hide_viewport = False
        circle.hide_render = False
        circle.keyframe_insert(data_path="hide_viewport", frame=early_start_frame)
        circle.keyframe_insert(data_path="hide_render", frame=early_start_frame)

        # Optional: Keyframe zum Ausblenden
        if end_time_ms is not None:
            end_frame = (end_time_ms + offset) / get_ms_per_frame()
            circle.hide_viewport = False
            circle.hide_render = False
            circle.keyframe_insert(data_path="hide_viewport", frame=end_frame - 1)
            circle.keyframe_insert(data_path="hide_render", frame=end_frame - 1)

            circle.hide_viewport = True
            circle.hide_render = True
            circle.keyframe_insert(data_path="hide_viewport", frame=end_frame)
            circle.keyframe_insert(data_path="hide_render", frame=end_frame)

        # Objekt zur gewünschten Collection hinzufügen
        circles_collection.objects.link(circle)
        # Aus anderen Collections entfernen
        if circle.users_collection:
            for col in circle.users_collection:
                if col != circles_collection:
                    col.objects.unlink(circle)

    except Exception as e:
        print(f"Fehler beim Erstellen eines Kreises: {e}")

def create_slider_curve(points, name, start_time_ms, end_time_ms, repeats, global_index, sliders_collection, offset,
                        early_frames=5):
    try:
        start_frame = (start_time_ms + offset) / get_ms_per_frame()
        early_start_frame = start_frame - early_frames
        end_frame = (end_time_ms + offset) / get_ms_per_frame()

        # Erstelle die Kurve
        curve_data = bpy.data.curves.new(name=f"{global_index:03d}_{name}_curve", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(len(points) - 1)

        for i, (x, y) in enumerate(points):
            corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)
            bp = spline.bezier_points[i]
            bp.co = (corrected_x, corrected_y, corrected_z)
            # Optional: Handle-Typen setzen
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'

        slider = bpy.data.objects.new(f"{global_index:03d}_{name}_curve", curve_data)

        # Keyframe Sichtbarkeit für die Kurve
        slider.hide_viewport = True
        slider.hide_render = True
        slider.keyframe_insert(data_path="hide_viewport", frame=early_start_frame - 1)
        slider.keyframe_insert(data_path="hide_render", frame=early_start_frame - 1)

        slider.hide_viewport = False
        slider.hide_render = False
        slider.keyframe_insert(data_path="hide_viewport", frame=early_start_frame)
        slider.keyframe_insert(data_path="hide_render", frame=early_start_frame)

        sliders_collection.objects.link(slider)
        # Aus anderen Collections entfernen
        if slider.users_collection:
            for col in slider.users_collection:
                if col != sliders_collection:
                    col.objects.unlink(slider)

        # Slider-Kopf und -Ende erstellen
        create_circle_at_position(points[0][0], points[0][1], f"{name}_head", start_time_ms, global_index,
                                  sliders_collection, offset)

        if repeats % 2 == 0:
            end_x, end_y = points[0]
        else:
            end_x, end_y = points[-1]

        create_circle_at_position(end_x, end_y, f"{name}_tail", start_time_ms, global_index, sliders_collection, offset)

    except Exception as e:
        print(f"Fehler beim Erstellen eines Sliders: {e}")

def create_spinner_at_position(x, y, name, start_time_ms, global_index, spinners_collection, offset, early_frames=5):
    corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)
    try:
        start_frame = (start_time_ms + offset) / get_ms_per_frame()
        early_start_frame = start_frame - early_frames

        bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=0.1, location=(corrected_x, corrected_y, corrected_z))
        spinner = bpy.context.object
        spinner.name = f"{global_index:03d}_{name}"

        # Keyframe Sichtbarkeit
        spinner.hide_viewport = True
        spinner.hide_render = True
        spinner.keyframe_insert(data_path="hide_viewport", frame=early_start_frame - 1)
        spinner.keyframe_insert(data_path="hide_render", frame=early_start_frame - 1)

        spinner.hide_viewport = False
        spinner.hide_render = False
        spinner.keyframe_insert(data_path="hide_viewport", frame=early_start_frame)
        spinner.keyframe_insert(data_path="hide_render", frame=early_start_frame)

        # Link zum gewünschten Collection hinzufügen
        spinners_collection.objects.link(spinner)
        # Aus anderen Collections entfernen
        if spinner.users_collection:
            for col in spinner.users_collection:
                if col != spinners_collection:
                    col.objects.unlink(spinner)

    except Exception as e:
        print(f"Fehler beim Erstellen eines Spinners: {e}")
