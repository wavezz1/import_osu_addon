# osu_importer/sliders.py

import bpy
from .utils import get_ms_per_frame, SCALE_FACTOR
from .circles import create_circle_at_position

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
            corrected_x = x * SCALE_FACTOR
            corrected_y = -y * SCALE_FACTOR
            bp = spline.bezier_points[i]
            bp.co = (corrected_x, corrected_y, 0)
            # Optional: Handle-Typen setzen
            # bp.handle_left_type = 'AUTO'
            # bp.handle_right_type = 'AUTO'

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

def calculate_slider_duration(osu_file, start_time_ms, repeat_count, pixel_length, speed_multiplier):
    # Ihre bestehende Implementierung
    slider_multiplier = 1.4  # Standard-Slider-Multiplikator, kann aus der .osu-Datei gelesen werden
    beat_duration = 500  # Annahme eines Standard-Beat-Durationswertes in ms

    slider_duration = (pixel_length / (slider_multiplier * 100)) * beat_duration * repeat_count
    slider_duration /= speed_multiplier  # Anpassung an Mods wie DT oder HT
    return slider_duration
