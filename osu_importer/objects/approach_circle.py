# approach_circle.py

import bpy
from osu_importer.geo_nodes.geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes


class ApproachCircleCreator:
    def __init__(self, hitobject, global_index, collection, settings, data_manager, import_type):
        self.hitobject = hitobject
        self.global_index = global_index
        self.collection = collection
        self.settings = settings
        self.data_manager = data_manager
        self.import_type = import_type
        self.name = f"ApproachCircle_{self.global_index}"

        # Attribute: Show, Start Frame, Scale
        self.show = True
        self.start_frame = int(hitobject.frame)  # Start frame vom hitobject
        self.scale_initial = 2.0  # Startskalierung, z.B. doppelt so groß wie der Circle
        self.scale_final = self.data_manager.adjusted_cs  # Final Scale entspricht cs Größe

        self.create()

    def create(self):
        """Create the approach circle based on the import type."""
        if self.import_type == 'BASE':
            self.create_base_circle()
        elif self.import_type == 'FULL':
            self.create_full_circle()

    def create_base_circle(self):
        """Create a mesh circle with Geometry Nodes modifier."""
        # Erstellen des Mesh-Circles
        mesh = bpy.data.meshes.new(self.name)
        obj = bpy.data.objects.new(self.name, mesh)

        # Link das Objekt zur Sammlung
        self.collection.objects.link(obj)

        # Erstellen eines Kreis-Meshes ohne Füllung
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.primitive_circle_add(vertices=32, radius=self.data_manager.osu_radius, fill_type='NOTHING')
        bpy.ops.object.mode_set(mode='OBJECT')

        # Hinzufügen des Geometry Nodes Modifiers
        create_geometry_nodes_modifier(obj, obj_type="approach_circle")

        # Definieren der Attribute und Setzen der Keyframes
        attributes = {
            "show": "BOOLEAN",
            "start_frame": "INT",
            "scale": "FLOAT",
        }
        frame_values = {
            "show": [
                (self.start_frame, True),   # Sichtbar ab Start Frame
                (self.start_frame + 10, False),  # Unsichtbar nach kurzer Zeit (angepasst nach Bedarf)
            ],
            "scale": [
                (self.start_frame, self.scale_initial),
                (self.start_frame, self.scale_final),
            ]
        }
        fixed_values = {
            "start_frame": self.start_frame,
        }

        set_modifier_inputs_with_keyframes(obj, attributes, frame_values, fixed_values)

    def create_full_circle(self):
        """Create a curve circle with direct scaling and visibility animation."""
        # Erstellen des Curve-Circles
        curve_data = bpy.data.curves.new(self.name, type='CURVE')
        curve_data.dimensions = '3D'

        # Verwenden von 'CIRCLE' als Spline-Typ für einen geschlossenen Kreis
        circle_spline = curve_data.splines.new('CIRCLE')
        circle_spline.radius = self.data_manager.osu_radius

        curve_obj = bpy.data.objects.new(self.name, curve_data)
        self.collection.objects.link(curve_obj)

        # Animieren der Skalierung
        curve_obj.scale = (self.scale_initial, self.scale_initial, self.scale_initial)
        curve_obj.keyframe_insert(data_path="scale", frame=self.start_frame)
        curve_obj.scale = (self.scale_final, self.scale_final, self.scale_final)
        curve_obj.keyframe_insert(data_path="scale", frame=self.start_frame + 30)  # Dauer der Animation anpassen

        # Animieren der Sichtbarkeit (sichtbar -> unsichtbar)
        curve_obj.hide_viewport = False
        curve_obj.hide_render = False
        curve_obj.keyframe_insert(data_path="hide_viewport", frame=self.start_frame)
        curve_obj.keyframe_insert(data_path="hide_render", frame=self.start_frame)

        curve_obj.hide_viewport = True
        curve_obj.hide_render = True
        curve_obj.keyframe_insert(data_path="hide_viewport", frame=self.start_frame + 30)
        curve_obj.keyframe_insert(data_path="hide_render", frame=self.start_frame + 30)
