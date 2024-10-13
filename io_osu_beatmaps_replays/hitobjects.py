# osu_importer/hitobjects.py

import bpy
import math  # Importiere das math Modul
from .constants import SPINNER_CENTER_X, SPINNER_CENTER_Y
from .io import parse_timing_points
from .utils import get_ms_per_frame, map_osu_to_blender

def create_circle_at_position(x, y, name, start_time_ms, global_index, circles_collection, offset, early_frames=5, end_time_ms=None):
    """
    Erstellt einen Circle (HitObject) an der angegebenen Position und fügt ihn der entsprechenden Collection hinzu.
    """
    try:
        start_frame = (start_time_ms + offset) / get_ms_per_frame()
        early_start_frame = start_frame - early_frames

        corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)
        bpy.ops.mesh.primitive_circle_add(
            radius=0.5,
            location=(corrected_x, corrected_y, corrected_z),
            rotation=(math.radians(90), 0, 0)  # Drehung um 90 Grad um die Y-Achse
        )
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
    """
    Erstellt einen Slider als Kurve basierend auf den gegebenen Punkten und fügt ihn der entsprechenden Collection hinzu.
    """
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

def calculate_slider_duration(osu_file, start_time_ms, repeat_count, pixel_length, speed_multiplier):
    """
    Berechnet die Dauer eines Sliders basierend auf der Beatmap-Information.
    """
    # Parsen der Timing-Punkte und Berechnung der Slider-Geschwindigkeit
    timing_points = parse_timing_points(osu_file)
    # Standardwerte
    beat_duration = 500  # Fallback-Wert
    slider_multiplier = 1.4  # Standardwert, sollte aus [Difficulty] Abschnitt gelesen werden
    try:
        with open(osu_file, 'r', encoding='utf-8') as file:
            difficulty_section = False
            for line in file:
                line = line.strip()
                if line == '[Difficulty]':
                    difficulty_section = True
                    continue
                if difficulty_section:
                    if line == '':
                        break  # Ende der Difficulty-Sektion
                    if line.startswith("SliderMultiplier:"):
                        slider_multiplier = float(line.split(':')[1].strip())
                        break
    except Exception as e:
        print(f"Fehler beim Lesen des SliderMultipliers: {e}")

    # Finden des passenden Timing Points
    current_beat_length = None
    for offset, beat_length in timing_points:
        if start_time_ms >= offset:
            current_beat_length = beat_length
        else:
            break
    if current_beat_length is not None:
        beat_duration = current_beat_length

    slider_duration = (pixel_length / (slider_multiplier * 100)) * beat_duration * repeat_count
    slider_duration /= speed_multiplier  # Anpassung an Mods wie DT oder HT
    return slider_duration

def create_spinner_at_position(x, y, name, start_time_ms, global_index, spinners_collection, offset, early_frames=5):
    """
    Erstellt einen Spinner an der angegebenen Position und fügt ihn der entsprechenden Collection hinzu.
    """
    try:
        start_frame = (start_time_ms + offset) / get_ms_per_frame()
        early_start_frame = start_frame - early_frames

        corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1,
            depth=0.1,
            location=(corrected_x, corrected_y, corrected_z),
            rotation=(math.radians(90), 0, 0)  # Drehung um 90 Grad um die Y-Achse
        )
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

def load_and_create_hitobjects(osu_file, circles_collection, sliders_collection, spinners_collection, offset, speed_multiplier):
    """
    Lädt die HitObjects aus der .osu-Datei und erstellt sie in Blender.
    """
    global_index = 1
    try:
        with open(osu_file, 'r', encoding='utf-8') as file:
            hit_objects_section = False
            for line in file:
                line = line.strip()
                if line == '[HitObjects]':
                    hit_objects_section = True
                    continue
                if hit_objects_section and line:
                    parts = line.split(',')
                    if len(parts) < 5:
                        continue  # Nicht genügend Daten
                    x, y, time, hit_type = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                    start_time_ms = time / speed_multiplier  # Anpassung hier

                    if hit_type & 1:  # Circle
                        create_circle_at_position(x, y, f"circle_{time}", start_time_ms, global_index, circles_collection, offset)
                    elif hit_type & 2:  # Slider
                        slider_points = [(x, y)]
                        if len(parts) > 5:
                            slider_data = parts[5].split('|')
                            if len(slider_data) > 1:
                                slider_type = slider_data[0]
                                slider_control_points = slider_data[1:]
                                for point in slider_control_points:
                                    if ':' in point:
                                        px_str, py_str = point.split(':')
                                        px, py = float(px_str), float(py_str)
                                        slider_points.append((px, py))
                        else:
                            continue  # Keine Slider-Daten

                        # Wiederholungen und Pixel-Länge ermitteln
                        repeat_count = int(parts[6]) if len(parts) > 6 else 1
                        pixel_length = float(parts[7]) if len(parts) > 7 else 100

                        # Slider-Dauer berechnen
                        slider_duration = calculate_slider_duration(osu_file, start_time_ms, repeat_count, pixel_length, speed_multiplier)

                        end_time_ms = start_time_ms + slider_duration

                        create_slider_curve(
                            slider_points,
                            f"slider_{time}",
                            start_time_ms,
                            end_time_ms,
                            repeat_count,
                            global_index,
                            sliders_collection,
                            offset
                        )
                    elif hit_type & 8:  # Spinner
                        create_spinner_at_position(SPINNER_CENTER_X, SPINNER_CENTER_Y, f"spinner_{time}", start_time_ms, global_index, spinners_collection, offset)
                    global_index += 1
    except Exception as e:
        print(f"Fehler beim Laden und Erstellen der HitObjects: {e}")
