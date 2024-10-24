# slider.py

import bpy
from mathutils import Vector
from .utils import map_osu_to_blender, get_ms_per_frame
from .geometry_nodes import create_geometry_nodes_modifier_slider
from .info_parser import OsuParser
from .hitobjects import HitObject

class SliderCreator:
    def __init__(self, hitobject: HitObject, global_index: int, sliders_collection, settings: dict, osu_parser: OsuParser):
        self.hitobject = hitobject
        self.global_index = global_index
        self.sliders_collection = sliders_collection
        self.settings = settings
        self.osu_parser = osu_parser
        self.create_slider()

    def vector_lerp(self, p0, p1, t):
        p0 = Vector(p0)
        p1 = Vector(p1)
        return p0.lerp(p1, t)

    def create_catmull_rom_spline(self, points):
        spline_points = []
        n = len(points)
        if n < 2:
            return points  # Nicht genug Punkte für eine Kurve

        for i in range(n - 1):
            # Verwende Vector für die Punkte
            p0 = Vector(points[i - 1]) if i > 0 else Vector(points[i])
            p1 = Vector(points[i])
            p2 = Vector(points[i + 1])
            p3 = Vector(points[i + 2]) if i < n - 2 else Vector(points[i + 1])

            # Interpolation zwischen den Punkten
            for t in [j / 10.0 for j in range(11)]:
                t2 = t * t
                t3 = t2 * t
                spline_point = 0.5 * (
                        (2 * p1) +
                        (-p0 + p2) * t +
                        (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                        (-p0 + 3 * p1 - 3 * p2 + p3) * t3
                )
                spline_points.append(spline_point)

        return spline_points
    def create_linear_spline(self, points):
        return points  # Lineare Spline

    def create_bezier_spline(self, points):
        bezier_points = []
        n = len(points)

        # Wenn nur 2 Punkte vorhanden sind, wechsle auf eine lineare Bezier-Kurve
        if n == 2:
            p0, p1 = Vector(points[0]), Vector(points[1])
            for t in [j / 10.0 for j in range(11)]:
                bezier_point = self.vector_lerp(p0, p1, t)  # Lineare Interpolation
                bezier_points.append(bezier_point)
            return bezier_points

        # Wenn 3 oder mehr Punkte vorhanden sind, benutze die quadratische oder kubische Bezier-Kurve
        if n >= 3:
            current_curve = []
            for i, point in enumerate(points):
                current_curve.append(Vector(point))

                # Wenn wir eine Gruppe von 3 Punkten haben, berechne die quadratische Bezier-Kurve
                if len(current_curve) == 3:
                    p0, p1, p2 = current_curve
                    for t in [j / 10.0 for j in range(11)]:
                        bezier_point = ((1 - t) ** 2 * p0 +
                                        2 * (1 - t) * t * p1 +
                                        t ** 2 * p2)
                        bezier_points.append(bezier_point)
                    current_curve = [p2]  # Setze den letzten Punkt als Startpunkt der nächsten Gruppe

            # Falls am Ende nur noch 2 Punkte übrig sind, lineare Interpolation für den letzten Abschnitt
            if len(current_curve) == 2:
                p0, p1 = current_curve
                for t in [j / 10.0 for j in range(11)]:
                    bezier_point = self.vector_lerp(p0, p1, t)
                    bezier_points.append(bezier_point)

        return bezier_points

    def create_slider(self):
        approach_rate = float(self.osu_parser.difficulty_settings.get("ApproachRate", 5.0))
        circle_size = float(self.osu_parser.difficulty_settings.get("CircleSize", 5.0))
        x = self.hitobject.x
        y = self.hitobject.y
        time_ms = self.hitobject.time
        speed_multiplier = self.settings.get('speed_multiplier', 1.0)
        start_frame = ((time_ms / speed_multiplier) / get_ms_per_frame())
        early_start_frame = start_frame - self.settings.get('early_frames', 5)

        if self.hitobject.extras:
            slider_data = self.hitobject.extras[0].split('|')
            if len(slider_data) > 1:
                slider_type = slider_data[0]
                slider_control_points = slider_data[1:]
                points = [(self.hitobject.x, self.hitobject.y)]
                for point in slider_control_points:
                    if ':' in point:
                        px_str, py_str = point.split(':')
                        px, py = float(px_str), float(py_str)
                        points.append((px, py))

                # Flexibler Umgang mit der Anzahl der Punkte
                if slider_type == "B":
                    if len(points) < 3:
                        print(
                            f"Nicht genügend Punkte für quadratische Bezier-Kurve, verwende lineare Interpolation: {points}")
                        points = self.create_linear_spline(points)  # Verwende lineare Spline
                    else:
                        points = self.create_bezier_spline(points)  # Quadratische Bezier-Spline

                # Erstelle die Kurve in Blender
                curve_data = bpy.data.curves.new(name=f"{self.global_index:03d}_slider_{time_ms}_{slider_type}_curve",
                                                 type='CURVE')
                curve_data.dimensions = '3D'
                spline = curve_data.splines.new('BEZIER')
                spline.bezier_points.add(len(points) - 1)

                # Verwende die Punkte zur Erstellung der Spline in Blender
                for i, point in enumerate(points):
                    bp = spline.bezier_points[i]
                    corrected_x, corrected_y, corrected_z = map_osu_to_blender(point[0], point[1])
                    bp.co = (corrected_x, corrected_y, corrected_z)
                    bp.handle_left_type = 'AUTO'
                    bp.handle_right_type = 'AUTO'

                slider = bpy.data.objects.new(f"{self.global_index:03d}_slider_{time_ms}_{slider_type}", curve_data)

                slider["ar"] = approach_rate
                slider["cs"] = circle_size

        # Wiederholungen und Pixel-Länge ermitteln
        repeat_count = int(self.hitobject.extras[1]) if len(self.hitobject.extras) > 1 else 1
        pixel_length = float(self.hitobject.extras[2]) if len(self.hitobject.extras) > 2 else 100

                 # Slider-Dauer berechnen
        slider_duration_ms = self.calculate_slider_duration(time_ms, repeat_count, pixel_length, speed_multiplier)
        end_time_ms = time_ms + slider_duration_ms
        end_frame = ((end_time_ms / speed_multiplier) / get_ms_per_frame())


        # Benutzerdefiniertes Attribut "show" hinzufügen
        slider["show"] = False  # Startwert: Nicht sichtbar
        slider.keyframe_insert(data_path='["show"]', frame=(early_start_frame - 1))

        slider["show"] = True
        slider.keyframe_insert(data_path='["show"]', frame=early_start_frame)

        # Optional: Ausblenden am Ende
        slider["show"] = True
        slider.keyframe_insert(data_path='["show"]', frame=(end_frame - 1))

        slider["show"] = False
        slider.keyframe_insert(data_path='["show"]', frame=end_frame)

        # Füge "slider_duration_ms" und "slider_duration_frames" hinzu (ohne Keyframe)
        slider["slider_duration_ms"] = slider_duration_ms

        # Berechne slider_duration in Frames basierend auf der Szenen-FPS
        scene_fps = bpy.context.scene.render.fps
        slider_duration_frames = slider_duration_ms / (1000 / scene_fps)
        slider["slider_duration_frames"] = slider_duration_frames

        self.sliders_collection.objects.link(slider)
        # Aus anderen Collections entfernen
        if slider.users_collection:
            for col in slider.users_collection:
                if col != self.sliders_collection:
                    col.objects.unlink(slider)
                    
        create_geometry_nodes_modifier_slider(slider, slider.name)

    def calculate_slider_duration(self, start_time_ms, repeat_count, pixel_length, speed_multiplier):
        # Defaultwerte für den Fall, dass keine Timing Points gefunden werden
        beat_duration = 500  # Fallback-Wert
        slider_multiplier = float(self.osu_parser.difficulty_settings.get("SliderMultiplier", 1.4))
        inherited_multiplier = 1.0  # Wird für inherited Timing Points verwendet

        # Timing Points aus der osu-Datei
        timing_points = self.osu_parser.timing_points
        current_beat_length = None

        # Finde den gültigen Timing Point, der vor oder bei der Startzeit des Sliders liegt
        for offset, beat_length in timing_points:
            if start_time_ms >= offset:
                if beat_length < 0:  # Inherited Timing Point (negativer BeatLength)
                    inherited_multiplier = -100 / beat_length  # Berechne den Inherited Multiplier
                else:  # Normaler Timing Point
                    current_beat_length = beat_length
            else:
                break  # Kein weiterer gültiger Timing Point nach der Startzeit gefunden

        # Prüfen, ob ein gültiger Timing Point gefunden wurde
        if current_beat_length is not None and current_beat_length > 0:
            beat_duration = current_beat_length
        else:
            print(
                f"Warnung: Kein gültiger Beat Length für Startzeit {start_time_ms}. Fallback-Wert {beat_duration} wird verwendet.")

        # Slider-Dauer in Millisekunden berechnen
        slider_duration_ms = (pixel_length / (
                    slider_multiplier * 100)) * beat_duration * repeat_count * inherited_multiplier

        # Anpassung der Slider-Dauer für Mods wie Double Time (DT) oder Half Time (HT)
        slider_duration_ms /= speed_multiplier

        return slider_duration_ms
