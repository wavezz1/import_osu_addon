# hitobjects.py

class HitObject:
    def __init__(self, x, y, time, hit_type, hit_sound, extras):
        self.x = x
        self.y = y
        self.time = time
        self.hit_type = hit_type
        self.hit_sound = hit_sound
        self.extras = extras

class HitObjectsProcessor:
    def __init__(self, osu_parser):
        self.osu_parser = osu_parser
        self.circles = []
        self.sliders = []
        self.spinners = []
        self.process_hitobjects()

    def process_hitobjects(self):
        for line in self.osu_parser.hitobjects:
            parts = line.split(',')
            if len(parts) < 5:
                continue
            x = int(parts[0])
            y = int(parts[1])
            time = int(parts[2])
            hit_type = int(parts[3])
            hit_sound = int(parts[4])
            extras = parts[5:]  # Kann Slider-Daten enthalten
            hit_object = HitObject(x, y, time, hit_type, hit_sound, extras)
            if hit_type & 1:  # Circle
                self.circles.append(hit_object)
            elif hit_type & 2:  # Slider
                self.sliders.append(hit_object)
            elif hit_type & 8:  # Spinner
                self.spinners.append(hit_object)












# # osu_importer/hitobjects.py
#
# import bpy
# import math
# from .constants import SPINNER_CENTER_X, SPINNER_CENTER_Y
# from .io import parse_timing_points
# from .utils import get_ms_per_frame, map_osu_to_blender
#
# def create_geometry_nodes_modifier(obj, driver_obj_name):
#     # Geometry Nodes Modifier hinzufügen
#     modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
#
#     # Neuen Geometry Node Tree erstellen
#     group = bpy.data.node_groups.new("Geometry Nodes", 'GeometryNodeTree')
#     modifier.node_group = group
#
#     # Group Input und Group Output Knoten hinzufügen
#     input_node = group.nodes.new('NodeGroupInput')
#     output_node = group.nodes.new('NodeGroupOutput')
#     input_node.location.x = -200 - input_node.width
#     output_node.location.x = 200
#
#     # Store Named Attribute Knoten hinzufügen (für "show")
#     store_attribute_node_show = group.nodes.new('GeometryNodeStoreNamedAttribute')
#     store_attribute_node_show.location.x = 0
#     store_attribute_node_show.inputs['Name'].default_value = "show"
#     store_attribute_node_show.data_type = 'BOOLEAN'
#     store_attribute_node_show.domain = 'POINT'
#
#     # Driver auf Boolean Input setzen (für "show")
#     driver_show = store_attribute_node_show.inputs['Value'].driver_add('default_value').driver
#     driver_show.type = 'AVERAGE'
#     var_show = driver_show.variables.new()
#     var_show.name = 'var'
#     var_show.targets[0].id_type = 'OBJECT'
#     var_show.targets[0].id = bpy.data.objects[driver_obj_name]
#     var_show.targets[0].data_path = '["show"]'
#
#     # Store Named Attribute Knoten hinzufügen (für "time_ms")
#     store_attribute_node_time = group.nodes.new('GeometryNodeStoreNamedAttribute')
#     store_attribute_node_time.location.x = 200
#     store_attribute_node_time.inputs['Name'].default_value = "time_ms"
#     store_attribute_node_time.data_type = 'FLOAT'
#     store_attribute_node_time.domain = 'POINT'
#
#     # Driver auf Float Input setzen (für "time_ms")
#     driver_time = store_attribute_node_time.inputs['Value'].driver_add('default_value').driver
#     driver_time.type = 'AVERAGE'
#     var_time = driver_time.variables.new()
#     var_time.name = 'var'
#     var_time.targets[0].id_type = 'OBJECT'
#     var_time.targets[0].id = bpy.data.objects[driver_obj_name]
#     var_time.targets[0].data_path = '["time_ms"]'
#
#     # Geometrie-Sockets für Input und Output hinzufügen
#     group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
#     group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
#
#     # Verbindungen zwischen den Knoten erstellen
#     group.links.new(input_node.outputs['Geometry'], store_attribute_node_show.inputs['Geometry'])
#     group.links.new(store_attribute_node_show.outputs['Geometry'], store_attribute_node_time.inputs['Geometry'])
#     group.links.new(store_attribute_node_time.outputs['Geometry'], output_node.inputs['Geometry'])
#
# def create_circle_at_position(x, y, name, start_time_ms, global_index, circles_collection, offset, early_frames=5, end_time_ms=None, hitobject_times=None, time_property_name='time_ms'):
#     try:
#         start_frame = (start_time_ms + offset) / get_ms_per_frame()
#         early_start_frame = start_frame - early_frames
#
#         corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)
#         bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=0.5,
#             location=(corrected_x, corrected_y, corrected_z),
#             rotation=(math.radians(90), 0, 0)
#         )
#         circle = bpy.context.object
#         circle.name = f"{global_index:03d}_{name}"
#         circle[time_property_name] = start_time_ms
#         if hitobject_times is not None:
#             hitobject_times.append(start_time_ms)
#
#         # Benutzerdefiniertes Attribut "show" hinzufügen
#         circle["show"] = False
#         circle.keyframe_insert(data_path='["show"]', frame=early_start_frame - 1)
#
#         circle["show"] = True
#         circle.keyframe_insert(data_path='["show"]', frame=early_start_frame)
#
#         circle["show"] = False
#         circle.keyframe_insert(data_path='["show"]', frame=early_start_frame + 1)
#
#         circles_collection.objects.link(circle)
#         if circle.users_collection:
#             for col in circle.users_collection:
#                 if col != circles_collection:
#                     col.objects.unlink(circle)
#
#         # Geometry Nodes Modifier erstellen
#         create_geometry_nodes_modifier(circle, circle.name)
#     except Exception as e:
#         print(f"Fehler beim Erstellen eines Kreises: {e}")
#
# def create_slider_curve(points, name, start_time_ms, end_time_ms, repeats, global_index, sliders_collection, offset, early_frames=5):
#     try:
#         start_frame = (start_time_ms + offset) / get_ms_per_frame()
#         early_start_frame = start_frame - early_frames
#         end_frame = (end_time_ms + offset) / get_ms_per_frame()
#
#         # Erstelle die Kurve
#         curve_data = bpy.data.curves.new(name=f"{global_index:03d}_{name}_curve", type='CURVE')
#         curve_data.dimensions = '3D'
#         spline = curve_data.splines.new('BEZIER')
#         spline.bezier_points.add(len(points) - 1)
#
#         for i, (x, y) in enumerate(points):
#             corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)
#             bp = spline.bezier_points[i]
#             bp.co = (corrected_x, corrected_y, corrected_z)
#             # Optional: Handle-Typen setzen
#             bp.handle_left_type = 'AUTO'
#             bp.handle_right_type = 'AUTO'
#
#         slider = bpy.data.objects.new(f"{global_index:03d}_{name}_curve", curve_data)
#
#         # Benutzerdefiniertes Attribut "show" hinzufügen
#         slider["show"] = False  # Startwert: Nicht sichtbar
#         slider.keyframe_insert(data_path='["show"]', frame=early_start_frame - 1)
#
#         slider["show"] = True
#         slider.keyframe_insert(data_path='["show"]', frame=early_start_frame)
#
#         # Optional: Ausblenden am Ende
#         slider["show"] = True
#         slider.keyframe_insert(data_path='["show"]', frame=end_frame - 1)
#
#         slider["show"] = False
#         slider.keyframe_insert(data_path='["show"]', frame=end_frame)
#
#         sliders_collection.objects.link(slider)
#         # Aus anderen Collections entfernen
#         if slider.users_collection:
#             for col in slider.users_collection:
#                 if col != sliders_collection:
#                     col.objects.unlink(slider)
#
#         # Slider-Kopf und -Ende erstellen (ggf. auch anpassen)
#         create_circle_at_position(points[0][0], points[0][1], f"{name}_head", start_time_ms, global_index,
#                                   sliders_collection, offset)
#
#         if repeats % 2 == 0:
#             end_x, end_y = points[0]
#         else:
#             end_x, end_y = points[-1]
#
#         create_circle_at_position(end_x, end_y, f"{name}_tail", start_time_ms, global_index, sliders_collection, offset)
#
#     except Exception as e:
#         print(f"Fehler beim Erstellen eines Sliders: {e}")
#
# def calculate_slider_duration(osu_file, start_time_ms, repeat_count, pixel_length, speed_multiplier):
#     # Parsen der Timing-Punkte und Berechnung der Slider-Geschwindigkeit
#     timing_points = parse_timing_points(osu_file)
#     # Standardwerte
#     beat_duration = 500  # Fallback-Wert
#     slider_multiplier = 1.4  # Standardwert, sollte aus [Difficulty] Abschnitt gelesen werden
#     try:
#         with open(osu_file, 'r', encoding='utf-8') as file:
#             difficulty_section = False
#             for line in file:
#                 line = line.strip()
#                 if line == '[Difficulty]':
#                     difficulty_section = True
#                     continue
#                 if difficulty_section:
#                     if line == '':
#                         break  # Ende der Difficulty-Sektion
#                     if line.startswith("SliderMultiplier:"):
#                         slider_multiplier = float(line.split(':')[1].strip())
#                         break
#     except Exception as e:
#         print(f"Fehler beim Lesen des SliderMultipliers: {e}")
#
#     # Finden des passenden Timing Points
#     current_beat_length = None
#     for offset, beat_length in timing_points:
#         if start_time_ms >= offset:
#             current_beat_length = beat_length
#         else:
#             break
#     if current_beat_length is not None:
#         beat_duration = current_beat_length
#
#     slider_duration = (pixel_length / (slider_multiplier * 100)) * beat_duration * repeat_count
#     slider_duration /= speed_multiplier  # Anpassung an Mods wie DT oder HT
#     return slider_duration
#
# def create_spinner_at_position(x, y, name, start_time_ms, global_index, spinners_collection, offset, early_frames=5):
#     try:
#         start_frame = (start_time_ms + offset) / get_ms_per_frame()
#         early_start_frame = start_frame - early_frames
#
#         corrected_x, corrected_y, corrected_z = map_osu_to_blender(x, y)
#         bpy.ops.mesh.primitive_cylinder_add(
#             radius=1,
#             depth=0.1,
#             location=(corrected_x, corrected_y, corrected_z),
#             rotation=(math.radians(90), 0, 0)  # Drehung um 90 Grad um die X-Achse
#         )
#         spinner = bpy.context.object
#         spinner.name = f"{global_index:03d}_{name}"
#
#         # Benutzerdefiniertes Attribut "show" hinzufügen
#         spinner["show"] = False  # Startwert: Nicht sichtbar
#         spinner.keyframe_insert(data_path='["show"]', frame=early_start_frame - 1)
#
#         spinner["show"] = True
#         spinner.keyframe_insert(data_path='["show"]', frame=early_start_frame)
#
#         # Optional: Ausblenden am Ende (falls gewünscht)
#         # Hier müssten Sie die Endzeit des Spinners kennen und entsprechend keyframen
#
#         # Objekt zur gewünschten Collection hinzufügen
#         spinners_collection.objects.link(spinner)
#         # Aus anderen Collections entfernen
#         if spinner.users_collection:
#             for col in spinner.users_collection:
#                 if col != spinners_collection:
#                     col.objects.unlink(spinner)
#
#     except Exception as e:
#         print(f"Fehler beim Erstellen eines Spinners: {e}")
#
# def load_and_create_hitobjects(osu_file, circles_collection, sliders_collection, spinners_collection, offset, speed_multiplier):
#     global_index = 1
#     try:
#         with open(osu_file, 'r', encoding='utf-8') as file:
#             hit_objects_section = False
#             for line in file:
#                 line = line.strip()
#                 if line == '[HitObjects]':
#                     hit_objects_section = True
#                     continue
#                 if hit_objects_section and line:
#                     parts = line.split(',')
#                     if len(parts) < 5:
#                         continue  # Nicht genügend Daten
#                     x, y, time, hit_type = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
#                     start_time_ms = time / speed_multiplier
#                     if hit_type & 1:  # Circle
#                         create_circle_at_position(x, y, f"circle_{time}", start_time_ms, global_index, circles_collection, offset)
#                     elif hit_type & 2:  # Slider
#                         slider_points = [(x, y)]
#                         if len(parts) > 5:
#                             slider_data = parts[5].split('|')
#                             if len(slider_data) > 1:
#                                 slider_type = slider_data[0]
#                                 slider_control_points = slider_data[1:]
#                                 for point in slider_control_points:
#                                     if ':' in point:
#                                         px_str, py_str = point.split(':')
#                                         px, py = float(px_str), float(py_str)
#                                         slider_points.append((px, py))
#                         else:
#                             continue
#
#                         # Wiederholungen und Pixel-Länge ermitteln
#                         #??
#                         repeat_count = int(parts[6]) if len(parts) > 6 else 1
#                         pixel_length = float(parts[7]) if len(parts) > 7 else 100
#
#                         # Slider-Dauer berechnen
#                         slider_duration = calculate_slider_duration(osu_file, start_time_ms, repeat_count, pixel_length, speed_multiplier)
#
#                         end_time_ms = start_time_ms + slider_duration
#
#                         create_slider_curve(
#                             slider_points,
#                             f"slider_{time}",
#                             start_time_ms,
#                             end_time_ms,
#                             repeat_count,
#                             global_index,
#                             sliders_collection,
#                             offset
#                         )
#                     elif hit_type & 8:  # Spinner
#                         create_spinner_at_position(SPINNER_CENTER_X, SPINNER_CENTER_Y, f"spinner_{time}", start_time_ms, global_index, spinners_collection, offset)
#                     global_index += 1
#     except Exception as e:
#         print(f"Fehler beim Laden und Erstellen der HitObjects: {e}")
