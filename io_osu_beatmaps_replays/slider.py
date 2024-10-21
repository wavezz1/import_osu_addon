# slider.py

import bpy
import math
from .utils import map_osu_to_blender, get_ms_per_frame
from .geometry_nodes import create_geometry_nodes_modifier
from .constants import SCALE_FACTOR
from .info_parser import OsuParser
from .hitobjects import HitObject

class SliderCreator:
    def __init__(self, hitobject: HitObject, global_index: int, sliders_collection, offset_frames: float, settings: dict, osu_parser: OsuParser):
        self.hitobject = hitobject
        self.global_index = global_index
        self.sliders_collection = sliders_collection
        self.offset_frames = offset_frames
        self.settings = settings  # Enthält Slider-Multiplier usw.
        self.osu_parser = osu_parser
        self.create_slider()

    def create_slider(self):
        x = self.hitobject.x
        y = self.hitobject.y
        time_ms = self.hitobject.time
        speed_multiplier = self.settings.get('speed_multiplier', 1.0)
        start_frame = ((time_ms / speed_multiplier) / get_ms_per_frame()) + self.offset_frames
        early_start_frame = start_frame - self.settings.get('early_frames', 5)

        # Slider-Daten aus den Extras extrahieren
        if self.hitobject.extras:
            slider_data = self.hitobject.extras[0].split('|')
            if len(slider_data) > 1:
                slider_type = slider_data[0]
                slider_control_points = slider_data[1:]
                points = [(x, y)]
                for point in slider_control_points:
                    if ':' in point:
                        px_str, py_str = point.split(':')
                        px, py = float(px_str), float(py_str)
                        points.append((px, py))
            else:
                print(f"Ungültige Slider-Daten für HitObject bei {time_ms} ms")
                return
        else:
            print(f"Keine Slider-Daten für HitObject bei {time_ms} ms")
            return

        # Wiederholungen und Pixel-Länge ermitteln
        repeat_count = int(self.hitobject.extras[1]) if len(self.hitobject.extras) > 1 else 1
        pixel_length = float(self.hitobject.extras[2]) if len(self.hitobject.extras) > 2 else 100

        # Slider-Dauer berechnen
        slider_duration_ms = self.calculate_slider_duration(time_ms, repeat_count, pixel_length, speed_multiplier)
        end_time_ms = time_ms + slider_duration_ms
        end_frame = ((end_time_ms / speed_multiplier) / get_ms_per_frame()) + self.offset_frames

        # Erstelle die Kurve
        curve_data = bpy.data.curves.new(name=f"{self.global_index:03d}_slider_{time_ms}_curve", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(len(points) - 1)

        for i, (px, py) in enumerate(points):
            corrected_x, corrected_y, corrected_z = map_osu_to_blender(px, py)
            bp = spline.bezier_points[i]
            bp.co = (corrected_x, corrected_y, corrected_z)
            # Optional: Handle-Typen setzen
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'

        slider = bpy.data.objects.new(f"{self.global_index:03d}_slider_{time_ms}", curve_data)

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

        self.sliders_collection.objects.link(slider)
        # Aus anderen Collections entfernen
        if slider.users_collection:
            for col in slider.users_collection:
                if col != self.sliders_collection:
                    col.objects.unlink(slider)

        # Slider-Kopf und -Ende erstellen (optional)
        #self.create_slider_endpoints(points, time_ms, start_frame, end_frame)

        create_geometry_nodes_modifier(slider, slider.name)

    def calculate_slider_duration(self, start_time_ms, repeat_count, pixel_length, speed_multiplier):
        # Parsen der Timing-Punkte und Berechnung der Slider-Geschwindigkeit
        timing_points = self.osu_parser.timing_points
        beat_duration = 500  # Fallback-Wert
        slider_multiplier = float(self.osu_parser.difficulty_settings.get("SliderMultiplier", 1.4))

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

    # def create_slider_endpoints(self, points, time_ms, early_start_frame, end_frame):
    #     # Slider-Kopf erstellen
    #     head_x, head_y = points[0]
    #     self.create_slider_endpoint(head_x, head_y, f"slider_head_{time_ms}", early_start_frame, end_frame)
    #
    #     # Slider-Ende erstellen (abhängig von der Anzahl der Wiederholungen)
    #     repeats = int(self.hitobject.extras[1]) if len(self.hitobject.extras) > 1 else 1
    #     if repeats % 2 == 0:
    #         end_x, end_y = points[0]
    #     else:
    #         end_x, end_y = points[-1]
    #     self.create_slider_endpoint(end_x, end_y, f"slider_tail_{time_ms}", early_start_frame, end_frame)
    #
    # def create_slider_endpoint(self, x, y, name, early_start_frame, end_frame):
    #     corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)
    #     bpy.ops.mesh.primitive_circle_add(
    #         fill_type='NGON',
    #         radius=0.5,
    #         location=(corrected_x, corrected_y, corrected_z),
    #         rotation=(math.radians(90), 0, 0)
    #     )
    #     endpoint = bpy.context.object
    #     endpoint.name = f"{self.global_index:03d}_{name}"
    #
    #     # Benutzerdefiniertes Attribut "show" hinzufügen
    #     endpoint["show"] = False
    #     endpoint.keyframe_insert(data_path='["show"]', frame=(early_start_frame - 1))
    #
    #     endpoint["show"] = True
    #     endpoint.keyframe_insert(data_path='["show"]', frame=early_start_frame)
    #
    #     # Objekt bleibt sichtbar bis zum Endframe
    #     endpoint["show"] = True
    #     endpoint.keyframe_insert(data_path='["show"]', frame=(end_frame - 1))
    #
    #     endpoint["show"] = False
    #     endpoint.keyframe_insert(data_path='["show"]', frame=end_frame)
    #
    #     self.sliders_collection.objects.link(endpoint)
    #     if endpoint.users_collection:
    #         for col in endpoint.users_collection:
    #             if col != self.sliders_collection:
    #                 col.objects.unlink(endpoint)

        # Geometry Nodes Modifier hinzufügen
        create_geometry_nodes_modifier(endpoint, endpoint.name)
