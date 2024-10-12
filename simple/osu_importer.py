bl_info = {
    "name": "osu! Beatmap and Replay Importer",
    "author": "wavezz",
    "version": (0, 1),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > osu! Importer",
    "description": "Imports Osu! Beatmaps and Replays into Blender",
    "category": "Import-Export",
}

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup
import os

# Versuche, osrparse zu importieren, und installiere es bei Bedarf
try:
    import osrparse
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "osrparse"])
    import osrparse

# Neue Funktion, um MS_PER_FRAME basierend auf den Blender-Einstellungen zu erhalten
def get_ms_per_frame():
    fps = bpy.context.scene.render.fps
    return 1000 / fps  # Millisekunden pro Frame

# Hilfsfunktionen

def load_hitobject_times(osu_file):
    hitobject_times = []
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
                    if len(parts) >= 3:
                        time = int(parts[2])
                        hitobject_times.append(time)
    except Exception as e:
        print(f"Fehler beim Laden der HitObject-Zeiten: {e}")
    return hitobject_times

def get_first_replay_event_time(replay_data):
    total_time = 0
    for i, event in enumerate(replay_data):
        total_time += event.time_delta
        if event.x != -256 and event.y != -256:
            return total_time
    return total_time  # Falls alle Events bei (-256, -256) sind

def get_audio_lead_in(osu_file):
    audio_lead_in = 0
    try:
        with open(osu_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line.startswith("AudioLeadIn:"):
                    audio_lead_in = int(line.split(':')[1].strip())
                    break
    except Exception as e:
        print(f"Fehler beim Lesen des AudioLeadIns: {e}")
    return audio_lead_in

def create_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection

def create_circle_at_position(x, y, name, start_time_ms, global_index, circles_collection, offset, early_frames=5):
    try:
        start_frame = (start_time_ms + offset) / get_ms_per_frame()
        early_start_frame = start_frame - early_frames

        bpy.ops.mesh.primitive_circle_add(radius=0.5, location=(x * SCALE_FACTOR, -y * SCALE_FACTOR, 0))
        circle = bpy.context.object
        circle.name = f"{global_index:03d}_{name}"

        # Keyframe Sichtbarkeit
        circle.hide_viewport = True
        circle.hide_render = True
        circle.keyframe_insert(data_path="hide_viewport", frame=early_start_frame - 1)
        circle.keyframe_insert(data_path="hide_render", frame=early_start_frame - 1)

        circle.hide_viewport = False
        circle.hide_render = False
        circle.keyframe_insert(data_path="hide_viewport", frame=early_start_frame)
        circle.keyframe_insert(data_path="hide_render", frame=early_start_frame)

        # Link zum gewünschten Collection hinzufügen
        circles_collection.objects.link(circle)
        # Aus anderen Collections entfernen
        for col in circle.users_collection:
            if col != circles_collection:
                col.objects.unlink(circle)

    except Exception as e:
        print(f"Fehler beim Erstellen eines Kreises: {e}")

def create_slider_curve(points, name, start_time_ms, global_index, sliders_collection, offset, early_frames=5):
    try:
        start_frame = (start_time_ms + offset) / get_ms_per_frame()
        early_start_frame = start_frame - early_frames

        curve_data = bpy.data.curves.new(name=f"{global_index:03d}_{name}", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(points) - 1)

        for i, (x, y) in enumerate(points):
            corrected_x = x * SCALE_FACTOR
            corrected_y = -y * SCALE_FACTOR
            spline.points[i].co = (corrected_x, corrected_y, 0, 1)

        slider = bpy.data.objects.new(f"{global_index:03d}_{name}", curve_data)

        # Keyframe Sichtbarkeit
        slider.hide_viewport = True
        slider.hide_render = True
        slider.keyframe_insert(data_path="hide_viewport", frame=early_start_frame - 1)
        slider.keyframe_insert(data_path="hide_render", frame=early_start_frame - 1)

        slider.hide_viewport = False
        slider.hide_render = False
        slider.keyframe_insert(data_path="hide_viewport", frame=early_start_frame)
        slider.keyframe_insert(data_path="hide_render", frame=early_start_frame)

        # Link zum gewünschten Collection hinzufügen
        sliders_collection.objects.link(slider)

    except Exception as e:
        print(f"Fehler beim Erstellen eines Sliders: {e}")

def create_spinner_at_position(x, y, name, start_time_ms, global_index, spinners_collection, offset, early_frames=5):
    try:
        start_frame = (start_time_ms + offset) / get_ms_per_frame()
        early_start_frame = start_frame - early_frames

        bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=0.1, location=(x * SCALE_FACTOR, -y * SCALE_FACTOR, 0))
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
        for col in spinner.users_collection:
            if col != spinners_collection:
                col.objects.unlink(spinner)

    except Exception as e:
        print(f"Fehler beim Erstellen eines Spinners: {e}")

def load_and_create_hitobjects(osu_file, circles_collection, sliders_collection, spinners_collection, offset, speed_multiplier):
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
                                slider_data = slider_data[1:]  # Slider-Typ entfernen
                                for point in slider_data:
                                    if ':' in point:
                                        px_str, py_str = point.split(':')
                                        px, py = float(px_str), float(py_str)
                                        slider_points.append((px, py))
                        create_slider_curve(slider_points, f"slider_{time}", start_time_ms, global_index, sliders_collection, offset)
                    elif hit_type & 8:  # Spinner
                        create_spinner_at_position(256, 192, f"spinner_{time}", start_time_ms, global_index, spinners_collection, offset)
                    global_index += 1
    except Exception as e:
        print(f"Fehler beim Laden und Erstellen der HitObjects: {e}")

def create_animated_cursor(cursor_collection):
    try:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, 0))
        cursor = bpy.context.object
        cursor.name = "Cursor"

        # Link zum gewünschten Collection hinzufügen
        cursor_collection.objects.link(cursor)
        # Aus anderen Collections entfernen
        for col in cursor.users_collection:
            if col != cursor_collection:
                col.objects.unlink(cursor)

        return cursor
    except Exception as e:
        print(f"Fehler beim Erstellen des Cursors: {e}")
        return None

def animate_cursor(cursor, replay_data, offset):
    if cursor is None:
        print("Cursor-Objekt ist None, Animation wird übersprungen.")
        return
    total_time = 0
    try:
        for event in replay_data:
            total_time += event.time_delta
            if event.x == -256 and event.y == -256:
                continue  # Cursor ist nicht auf dem Bildschirm
            corrected_x = event.x * SCALE_FACTOR
            corrected_y = -event.y * SCALE_FACTOR
            cursor.location = (corrected_x, corrected_y, 0)
            frame = (total_time + offset) / get_ms_per_frame()
            cursor.keyframe_insert(data_path="location", frame=frame)
    except Exception as e:
        print(f"Fehler beim Animieren des Cursors: {e}")

def shift_cursor_keyframes(cursor_object_name, offset_ms):
    cursor = bpy.data.objects.get(cursor_object_name)
    if cursor is None:
        print(f"Objekt '{cursor_object_name}' nicht gefunden.")
        return

    if cursor.animation_data is None or cursor.animation_data.action is None:
        print(f"Keine Animation gefunden für Objekt '{cursor_object_name}'.")
        return

    action = cursor.animation_data.action
    fcurves = action.fcurves

    frame_offset = offset_ms / get_ms_per_frame()

    for fcurve in fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.co.x += frame_offset
            keyframe.handle_left.x += frame_offset
            keyframe.handle_right.x += frame_offset

        # Aktualisiere die FCurve
        fcurve.update()

# Konstanten
SCALE_FACTOR = 0.05

# Property Group für die Add-on-Einstellungen
class OSUImporterProperties(PropertyGroup):
    osu_file: StringProperty(
        name="Beatmap (.osu)",
        description="Pfad zur .osu Beatmap-Datei",
        default="",
        subtype='FILE_PATH'
    )
    osr_file: StringProperty(
        name="Replay (.osr)",
        description="Pfad zur .osr Replay-Datei",
        default="",
        subtype='FILE_PATH'
    )
    use_auto_offset: BoolProperty(
        name="Automatischen Offset verwenden",
        description="Verwende den automatisch berechneten Offset",
        default=True
    )
    manual_offset: FloatProperty(
        name="Manueller Offset (ms)",
        description="Manuell festgelegter Zeit-Offset in Millisekunden",
        default=0.0
    )
    cursor_offset: FloatProperty(
        name="Cursor Offset (ms)",
        description="Offset zum Verschieben der Cursor-Keyframes",
        default=0.0
    )
    # Eigenschaften für die erkannten Werte
    detected_first_hitobject_time: FloatProperty(
        name="Erstes HitObject",
        description="Zeit des ersten HitObjects (ms)",
        default=0.0
    )
    detected_first_replay_time: FloatProperty(
        name="Erstes Replay-Event",
        description="Zeit des ersten Replay-Events (ms)",
        default=0.0
    )
    detected_offset: FloatProperty(
        name="Berechneter Offset",
        description="Berechneter Zeit-Offset (ms)",
        default=0.0
    )

# Operator zum Importieren der Dateien
class OSU_OT_Import(Operator):
    bl_idname = "osu_importer.import"
    bl_label = "Importieren"
    bl_description = "Importiert die ausgewählte Beatmap und Replay"

    def execute(self, context):
        result = self.main(context)
        return result

    def main(self, context):
        props = context.scene.osu_importer_props
        osu_file_path = bpy.path.abspath(props.osu_file)
        osr_file_path = bpy.path.abspath(props.osr_file)

        if not os.path.isfile(osu_file_path):
            self.report({'ERROR'}, "Die angegebene .osu-Datei existiert nicht.")
            return {'CANCELLED'}
        if not os.path.isfile(osr_file_path):
            self.report({'ERROR'}, "Die angegebene .osr-Datei existiert nicht.")
            return {'CANCELLED'}

        # Lade das Replay
        try:
            replay = osrparse.Replay.from_path(osr_file_path)
        except Exception as e:
            self.report({'ERROR'}, f"Fehler beim Laden des Replays: {e}")
            return {'CANCELLED'}

        # Lade den AudioLeadIn-Wert
        audio_lead_in = get_audio_lead_in(osu_file_path)

        # Bestimme den Geschwindigkeitsmultiplikator basierend auf den Mods
        mods = replay.mods
        speed_multiplier = 1.0

        # Definiere die Mod-Konstanten
        MOD_DOUBLE_TIME = 64
        MOD_HALF_TIME = 256

        if mods & MOD_DOUBLE_TIME:
            speed_multiplier = 1.5
        elif mods & MOD_HALF_TIME:
            speed_multiplier = 0.75

        # Berechne den Offset
        hitobject_times = load_hitobject_times(osu_file_path)
        if not hitobject_times:
            self.report({'ERROR'}, "Keine HitObjects in der .osu-Datei gefunden.")
            return {'CANCELLED'}

        first_hitobject_time = hitobject_times[0]
        first_replay_time = get_first_replay_event_time(replay.replay_data)

        # Annahme: Standard-Lead-In im Replay ist 2000 ms
        standard_replay_lead_in = 2000

        # Berechne die angepassten Zeiten
        adjusted_first_hitobject_time = (first_hitobject_time + audio_lead_in) / speed_multiplier
        adjusted_first_replay_time = first_replay_time - standard_replay_lead_in

        offset = adjusted_first_hitobject_time - adjusted_first_replay_time

        # Speichere die Werte
        props.detected_first_hitobject_time = adjusted_first_hitobject_time
        props.detected_first_replay_time = adjusted_first_replay_time
        props.detected_offset = offset

        # Verwende automatischen oder manuellen Offset
        if props.use_auto_offset:
            final_offset = offset
        else:
            final_offset = props.manual_offset

        print(f"Verwendeter Zeit-Offset: {final_offset} ms")
        print(f"Geschwindigkeitsmultiplikator: {speed_multiplier}")
        print(f"Erste Hitobject-Zeit: {adjusted_first_hitobject_time} ms")
        print(f"Erste Replay-Event-Zeit: {adjusted_first_replay_time} ms")

        # Erstelle Collections
        circles_collection = create_collection("Circles")
        sliders_collection = create_collection("Sliders")
        spinners_collection = create_collection("Spinners")
        cursor_collection = create_collection("Cursor")

        # Lade und erstelle Hitobjects
        load_and_create_hitobjects(osu_file_path, circles_collection, sliders_collection, spinners_collection, final_offset, speed_multiplier)

        # Erstelle und animiere den Cursor
        cursor = create_animated_cursor(cursor_collection)
        if cursor is not None:
            animate_cursor(cursor, replay.replay_data, final_offset)
        else:
            self.report({'WARNING'}, "Cursor konnte nicht erstellt werden.")

        # Setze den Startframe der Szene
        scene_start_time = min(adjusted_first_hitobject_time, adjusted_first_replay_time)
        bpy.context.scene.frame_start = int(scene_start_time / get_ms_per_frame())

        self.report({'INFO'}, "Import abgeschlossen.")
        return {'FINISHED'}

# Operator zum Verschieben der Cursor-Keyframes
class OSU_OT_AdjustCursorOffset(Operator):
    bl_idname = "osu_importer.adjust_cursor_offset"
    bl_label = "Cursor Offset Anwenden"
    bl_description = "Verschiebt die Cursor-Keyframes um den angegebenen Offset"

    def execute(self, context):
        props = context.scene.osu_importer_props
        cursor_offset = props.cursor_offset
        shift_cursor_keyframes("Cursor", cursor_offset)
        self.report({'INFO'}, f"Cursor-Keyframes um {cursor_offset} ms verschoben.")
        return {'FINISHED'}

# Panel in der Sidebar
class OSU_PT_ImporterPanel(Panel):
    bl_label = "osu! Importer"
    bl_idname = "OSU_PT_importer_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "osu! Importer"

    def draw(self, context):
        layout = self.layout
        props = context.scene.osu_importer_props

        layout.prop(props, "osu_file")
        layout.prop(props, "osr_file")

        layout.prop(props, "use_auto_offset")
        if not props.use_auto_offset:
            layout.prop(props, "manual_offset")

        layout.operator("osu_importer.import", text="Importieren")

        # Zeige die erkannten Werte an
        if props.detected_first_hitobject_time != 0 or props.detected_first_replay_time != 0:
            layout.label(text="Erkannte Werte:")
            col = layout.column(align=True)
            col.label(text=f"Erstes HitObject: {props.detected_first_hitobject_time:.2f} ms")
            col.label(text=f"Erstes Replay-Event: {props.detected_first_replay_time:.2f} ms")
            if props.use_auto_offset:
                col.label(text=f"Berechneter Offset: {props.detected_offset:.2f} ms")
            else:
                col.label(text=f"Manueller Offset: {props.manual_offset:.2f} ms")

        layout.separator()
        layout.prop(props, "cursor_offset")
        layout.operator("osu_importer.adjust_cursor_offset", text="Cursor Offset Anwenden")

# Registrierungsfunktionen
classes = (
    OSUImporterProperties,
    OSU_OT_Import,
    OSU_OT_AdjustCursorOffset,
    OSU_PT_ImporterPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.osu_importer_props = PointerProperty(type=OSUImporterProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.osu_importer_props

if __name__ == "__main__":
    register()
