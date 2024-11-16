import bpy
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
                    "show": 'BOOLEAN',
                    "was_hit": 'BOOLEAN',
                    "ar": 'FLOAT',
                    "cs": 'FLOAT'
                }
            },
            "slider": {
                "name": "Geometry Nodes Slider",
                "attributes": {
                    "show": 'BOOLEAN',
                    "slider_duration_ms": 'FLOAT',
                    "slider_duration_frames": 'FLOAT',
                    "ar": 'FLOAT',
                    "cs": 'FLOAT',
                    "was_hit": 'BOOLEAN',
                    "was_completed": 'BOOLEAN',
                    "repeat_count": 'INT',
                    "pixel_length": 'FLOAT',
                }
            },
            "spinner": {
                "name": "Geometry Nodes Spinner",
                "attributes": {
                    "show": 'BOOLEAN',
                    "spinner_duration_ms": 'FLOAT',
                    "spinner_duration_frames": 'FLOAT',
                    "was_hit": 'BOOLEAN',
                    "was_completed": 'BOOLEAN'
                }
            },
            "cursor": {
                "name": "Geometry Nodes Cursor",
                "attributes": {
                    "k1": 'BOOLEAN',
                    "k2": 'BOOLEAN',
                    "m1": 'BOOLEAN',
                    "m2": 'BOOLEAN'
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
    :param attributes: Dictionary of attribute names and their data types.
    :return: Created Node Tree.
    """
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]

    group = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    setup_node_group_interface(group, attributes)
    return group


def setup_node_group_interface(group, attributes):
    """
    Set up the input and output sockets for the Geometry Node Tree.

    :param group: The Node Tree to configure.
    :param attributes: Dictionary of attribute names and their data types.
    """
    x_offset = 200

    # Add Geometry input and output sockets
    group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

    input_node = group.nodes.new('NodeGroupInput')
    input_node.location = (0, 0)
    output_node = group.nodes.new('NodeGroupOutput')
    output_node.location = (x_offset * (len(attributes) + 1), 0)

    previous_node_output = input_node.outputs['Geometry']

    socket_map = {
        "BOOLEAN": "NodeSocketBool",
        "FLOAT": "NodeSocketFloat",
        "INT": "NodeSocketInt"
    }

    for i, (attr_name, attr_type) in enumerate(attributes.items()):
        store_node = group.nodes.new('GeometryNodeStoreNamedAttribute')
        store_node.location = (x_offset * (i + 1), 0)
        store_node.inputs['Name'].default_value = attr_name
        store_node.data_type = attr_type
        store_node.domain = 'POINT'

        group.links.new(previous_node_output, store_node.inputs['Geometry'])
        previous_node_output = store_node.outputs['Geometry']

        socket_type = socket_map.get(attr_type.upper(), "NodeSocketFloat")
        new_socket = group.interface.new_socket(name=attr_name, in_out='INPUT', socket_type=socket_type)
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

    for i, (attr_name, attr_type) in enumerate(attributes.items()):
        socket_index = i + 2  # Socket_2 corresponds to the first attribute
        socket_count = f"Socket_{socket_index}"

        if attr_name in frame_values:
            # Set keyframes for this attribute
            for frame, value in frame_values[attr_name]:
                try:
                    if attr_type == 'BOOLEAN':
                        modifier[socket_count] = bool(value)
                    elif attr_type == 'FLOAT':
                        modifier[socket_count] = float(value)
                    elif attr_type == 'INT':
                        modifier[socket_count] = int(value)
                    modifier.keyframe_insert(data_path=f'["{socket_count}"]', frame=frame)
                except Exception as e:
                    print(f"Error setting keyframes for '{attr_name}' on socket '{socket_count}': {e}")
        elif fixed_values and attr_name in fixed_values:
            # Set fixed value for this attribute
            try:
                value = fixed_values[attr_name]
                if attr_type == 'BOOLEAN':
                    modifier[socket_count] = bool(value)
                elif attr_type == 'FLOAT':
                    modifier[socket_count] = float(value)
                elif attr_type == 'INT':
                    modifier[socket_count] = int(value)
                print(f"Set fixed value for '{attr_name}' on socket '{socket_count}' to {value}")
            except Exception as e:
                print(f"Error setting fixed value for '{attr_name}' on socket '{socket_count}': {e}")
        else:
            print(f"No values provided for attribute '{attr_name}'. Skipping.")
