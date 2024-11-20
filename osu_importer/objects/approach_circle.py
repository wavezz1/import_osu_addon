# approach_circle.py

import bpy
from osu_importer.geo_nodes.geometry_nodes import create_geometry_nodes_modifier, set_modifier_inputs_with_keyframes
import math

class ApproachCircleCreator:
    def __init__(self, hitobject, global_index, collection, settings, data_manager, import_type):
        self.hitobject = hitobject
        self.global_index = global_index
        self.collection = collection
        self.settings = settings
        self.data_manager = data_manager
        self.import_type = import_type
        self.name = f"ApproachCircle_{self.global_index}"

        # Attribute: Show, Early Start Frame, Start Frame, Scale
        self.show = True
        self.early_start_frame = int(hitobject.time - self.data_manager.preempt_frames)
        self.start_frame = int(hitobject.time)
        self.scale_initial = 2.0  # Startscale, z.B. doppelt so groß wie der Circle
        self.scale_final = self.data_manager.adjusted_cs  # Circle Size

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

        # Erstellen eines Kreis-Meshes
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.primitive_circle_add(vertices=32, radius=self.data_manager.osu_radius, fill_type='NOTHING')
        bpy.ops.object.mode_set(mode='OBJECT')

        # Hinzufügen des Geometry Nodes Modifiers
        create_geometry_nodes_modifier(obj, obj_type="approach_circle")

        # Definieren der Attribute und Setzen der Keyframes
        attributes = {
            "show": "BOOLEAN",
            "early_start_frame": "INT",
            "start_frame": "INT",
            "scale": "FLOAT",
        }
        frame_values = {
            "show": [
                (self.early_start_frame, True),  # show = True
                (self.start_frame, False),       # show = False
            ],
            "scale": [
                (self.early_start_frame, self.scale_initial),
                (self.start_frame, self.scale_final),
            ]
        }
        fixed_values = {
            "early_start_frame": self.early_start_frame,
            "start_frame": self.start_frame,
        }

        set_modifier_inputs_with_keyframes(obj, attributes, frame_values, fixed_values)

    def create_full_circle(self):
        """Create a curve circle with Geometry Nodes modifier and animate scaling and visibility."""
        # Erstellen des Curve-Circles
        curve_data = bpy.data.curves.new(self.name, type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.resolution_u = 16

        polyline = curve_data.splines.new('POLY')
        polyline.points.add(31)
        for i in range(32):
            angle = (2 * math.pi / 32) * i
            x = self.data_manager.osu_radius * math.cos(angle)
            y = self.data_manager.osu_radius * math.sin(angle)
            polyline.points[i].co = (x, y, 0, 1)

        curve_obj = bpy.data.objects.new(self.name, curve_data)
        self.collection.objects.link(curve_obj)

        # Hinzufügen des Geometry Nodes Modifiers
        create_geometry_nodes_modifier(curve_obj, obj_type="approach_circle")

        # Definieren der Attribute und Setzen der Keyframes
        attributes = {
            "show": "BOOLEAN",
            "early_start_frame": "INT",
            "start_frame": "INT",
            "scale": "FLOAT",
        }
        frame_values = {
            "show": [
                (self.early_start_frame, True),  # show = True
                (self.start_frame, False),       # show = False
            ],
            "scale": [
                (self.early_start_frame, self.scale_initial),
                (self.start_frame, self.scale_final),
            ]
        }
        fixed_values = {
            "early_start_frame": self.early_start_frame,
            "start_frame": self.start_frame,
        }

        set_modifier_inputs_with_keyframes(curve_obj, attributes, frame_values, fixed_values)
