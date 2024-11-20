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

        # Attribute: Show, Early Start Frame, Start Frame
        self.show = True
        self.early_start_frame = int(hitobject.time - self.data_manager.preempt_frames)
        self.start_frame = int(hitobject.time)

        self.create()

    def create(self):
        """Create the approach circle based on the import type."""
        if self.import_type == 'BASE':
            self.create_base_circle()
        elif self.import_type == 'FULL':
            self.create_full_circle()

    def create_base_circle(self):
        """Create a single vertex with a Geometry Nodes modifier."""
        mesh = bpy.data.meshes.new(self.name)
        obj = bpy.data.objects.new(self.name, mesh)
        mesh.from_pydata([(0, 0, 0)], [], [])  # Single vertex at the origin

        # Add object to the collection
        self.collection.objects.link(obj)

        # Add Geometry Nodes modifier
        create_geometry_nodes_modifier(obj, obj_type="approach_circle")

        # Set modifier inputs and keyframes
        attributes = {
            "show": "BOOLEAN",
            "Early Start Frame": "INT",
            "Start Frame": "INT",
        }
        fixed_values = {
            "show": self.show,
        }
        frame_values = {
            "early_start_frame": [(self.early_start_frame, self.early_start_frame)],
            "start_frame": [(self.start_frame, self.start_frame)],
        }
        set_modifier_inputs_with_keyframes(obj, attributes, frame_values, fixed_values)

    def create_full_circle(self):
        """Create the full animation for the approach circle."""
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        obj = bpy.context.object
        obj.name = self.name

        # Animate scaling from large to circle size
        obj.scale = (3.0, 3.0, 3.0)  # Initial scale
        obj.keyframe_insert(data_path="scale", frame=self.early_start_frame)
        obj.scale = (self.data_manager.osu_radius, self.data_manager.osu_radius, self.data_manager.osu_radius)
        obj.keyframe_insert(data_path="scale", frame=self.start_frame)

        # Add object to the collection
        self.collection.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)

        # Add Geometry Nodes modifier
        create_geometry_nodes_modifier(obj, obj_type="circle")

        # Set modifier inputs and keyframes
        attributes = {
            "show": "BOOLEAN",
            "Early Start Frame": "INT",
            "Start Frame": "INT",
        }
        fixed_values = {
            "show": self.show,
        }
        frame_values = {
            "Early Start Frame": [(self.early_start_frame, self.early_start_frame)],
            "Start Frame": [(self.start_frame, self.start_frame)],
        }
        set_modifier_inputs_with_keyframes(obj, attributes, frame_values, fixed_values)
