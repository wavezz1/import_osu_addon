# geometry_nodes.py

import bpy
from bpy.types import GeometryNodeTree
from .utils import timeit

node_groups = {}

def setup_geometry_node_trees():
    """
    Set up all required Geometry Node Trees. Re-creates any missing Node Trees dynamically.
    """
    global node_groups
    with timeit("Einrichten der Geometry Node Trees"):
        # Node tree definitions
        node_definitions = {
            "circle": {
                "name": "Geometry Nodes Circle",
                "attributes": {
                    "show": 'NodeSocketBool',
                    "was_hit": 'NodeSocketBool',
                    "ar": 'NodeSocketFloat',
                    "cs": 'NodeSocketFloat'
                }
            },
            "slider": {
                "name": "Geometry Nodes Slider",
                "attributes": {
                    "show": 'NodeSocketBool',
                    "slider_duration_ms": 'NodeSocketFloat',
                    "slider_duration_frames": 'NodeSocketFloat',
                    "ar": 'NodeSocketFloat',
                    "cs": 'NodeSocketFloat',
                    "was_hit": 'NodeSocketBool',
                    "was_completed": 'NodeSocketBool',
                    "repeat_count": 'NodeSocketInt',
                    "pixel_length": 'NodeSocketFloat',
                }
            },
            "spinner": {
                "name": "Geometry Nodes Spinner",
                "attributes": {
                    "show": 'NodeSocketBool',
                    "spinner_duration_ms": 'NodeSocketFloat',
                    "spinner_duration_frames": 'NodeSocketFloat',
                    "was_hit": 'NodeSocketBool',
                    "was_completed": 'NodeSocketBool'
                }
            },
            "cursor": {
                "name": "Geometry Nodes Cursor",
                "attributes": {
                    "k1": 'NodeSocketBool',
                    "k2": 'NodeSocketBool',
                    "m1": 'NodeSocketBool',
                    "m2": 'NodeSocketBool'
                }
            },
        }

        # Create or reassign Node Trees
        for key, node_def in node_definitions.items():
            name = node_def["name"]
            attributes = node_def["attributes"]
            if name not in bpy.data.node_groups:
                # Create Node Tree if missing
                node_groups[key] = create_geometry_nodes_tree(name, attributes)
            else:
                # Reassign existing Node Tree
                node_groups[key] = bpy.data.node_groups[name]


def create_geometry_nodes_tree(name, attributes):
    """
    Create a new Geometry Node Tree with the specified attributes.

    :param name: Name of the Node Tree.
    :param attributes: Dictionary of attribute names and their socket types.
    :return: Created Node Tree.
    """
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]

    group = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    setup_node_group_interface(group, attributes)
    return group


def setup_node_group_interface(group, attributes):
    """
    Set up the input and output sockets for the Geometry Node Tree using new_socket.

    :param group: The Node Tree to configure.
    :param attributes: Dictionary of attribute names and their socket types.
    """
    x_offset = 200

    # Add Geometry input and output sockets
    group.interface.new_socket('NodeSocketGeometry', name='Geometry')
    group.interface.new_socket('NodeSocketGeometry', name='Geometry')

    input_node = group.nodes.new('NodeGroupInput')
    input_node.location = (0, 0)
    output_node = group.nodes.new('NodeGroupOutput')
    output_node.location = (x_offset * (len(attributes) + 1), 0)

    previous_node_output = input_node.outputs['Geometry']

    for i, (attr_name, attr_type) in enumerate(attributes.items()):
        store_node = group.nodes.new('GeometryNodeStoreNamedAttribute')
        store_node.location = (x_offset * (i + 1), 0)
        store_node.inputs['Name'].default_value = attr_name
        store_node.data_type = attr_type
        store_node.domain = 'POINT'

        group.links.new(previous_node_output, store_node.inputs['Geometry'])
        previous_node_output = store_node.outputs['Geometry']

        # Add new socket to the group interface
        new_socket = group.interface.new_socket(attr_type, name=attr_name)
        group.links.new(input_node.outputs[new_socket.name], store_node.inputs['Value'])

    group.links.new(previous_node_output, output_node.inputs['Geometry'])


def create_geometry_nodes_modifier(obj, obj_type):
    """
    Add a Geometry Nodes modifier to the specified object.

    :param obj: The Blender object to add the modifier to.
    :param obj_type: The type of Geometry Node Tree to use (e.g., 'circle', 'slider').
    """
    setup_geometry_node_trees()

    node_group = node_groups.get(obj_type)
    if not node_group:
        print(f"Unrecognized object type for {obj_type}. Skipping modifier setup.")
        return

    modifier = obj.modifiers.get("GeometryNodes")
    if not modifier:
        modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
    modifier.node_group = node_group


def set_modifier_inputs_with_keyframes(obj, attributes, frame_values, fixed_values=None):
    """
    Set the modifier's inputs and insert keyframes only for attributes in frame_values.
    Attributes not in frame_values are set to fixed_values if provided.

    :param obj: The Blender object.
    :param attributes: Dict of attribute names and their types.
    :param frame_values: Dict of attribute names and list of (frame, value) tuples.
    :param fixed_values: Optional dict of attribute names and fixed values.
    """
    modifier = obj.modifiers.get("GeometryNodes")
    if not modifier:
        print(f"No GeometryNodes modifier found on object '{obj.name}'.")
        return

    for attr_name, attr_type in attributes.items():
        if attr_name in frame_values:
            # Set keyframes for this attribute
            for frame, value in frame_values[attr_name]:
                try:
                    modifier[attr_name] = value
                    modifier.keyframe_insert(data_path=f'["{attr_name}"]', frame=frame)
                except Exception as e:
                    print(f"Error setting keyframes for '{attr_name}' on object '{obj.name}': {e}")
        elif fixed_values and attr_name in fixed_values:
            # Set fixed value for this attribute
            try:
                value = fixed_values[attr_name]
                modifier[attr_name] = value
                print(f"Set fixed value for '{attr_name}' on object '{obj.name}' to {value}")
            except Exception as e:
                print(f"Error setting fixed value for '{attr_name}' on object '{obj.name}': {e}")
        else:
            print(f"No values provided for attribute '{attr_name}'. Skipping.")
