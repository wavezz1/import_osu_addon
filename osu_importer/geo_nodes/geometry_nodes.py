# osu_importer/geo_nodes/geometry_nodes.py

import bpy
from osu_importer.utils.utils import timeit, tag_imported

node_groups = {}

def setup_geometry_node_trees():
    global node_groups
    with timeit("Setup Geometry Node Trees"):
        node_definitions = {
            "circle": {
                "name": "Geometry Nodes Circle",
                "attributes": {
                    "show": 'BOOLEAN',
                    "was_hit": 'BOOLEAN',
                    "ar": 'FLOAT',
                    "cs": 'FLOAT',
                    "combo": 'INT',
                    "combo_color_idx": 'INT',
                    "combo_color": 'FLOAT_VECTOR'
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
                    "combo": 'INT',
                    "combo_color_idx": 'INT',
                    "combo_color": 'FLOAT_VECTOR'
                }
            },
            "slider_head_tail": {
                "name": "Geometry Nodes Head Tail",
                "attributes": {
                    "show": 'BOOLEAN',
                    "scale": 'FLOAT',
                    "cs": 'FLOAT',
                    "combo": 'INT',
                    "combo_color_idx": 'INT',
                    "combo_color": 'FLOAT_VECTOR',
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
                    "m2": 'BOOLEAN',
                    "cursor_size": 'FLOAT'
                }
            },
            "slider_ball": {
                "name": "Geometry Nodes Slider Ball",
                "attributes": {
                    "show": 'BOOLEAN'
                }
            },
            "approach_circle": {
                "name": "Geometry Nodes Approach Circle",
                "attributes": {
                    "show": 'BOOLEAN',
                    "scale": 'FLOAT',
                    "cs": 'FLOAT'
                }
            },
        }

        for key, node_def in node_definitions.items():
            name = node_def["name"]
            attributes = node_def["attributes"]
            node_group = bpy.data.node_groups.get(name)
            if node_group is None:
                node_group = create_geometry_nodes_tree(name, attributes)
            node_groups[key] = node_group

def create_geometry_nodes_tree(name, attributes):
    # if name in bpy.data.node_groups:
    #     return bpy.data.node_groups[name]

    group = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    setup_node_group_interface(group, attributes)
    tag_imported(group)
    return group

def setup_node_group_interface(group, attributes):
    x_offset = 200

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
        "INT": "NodeSocketInt",
        "FLOAT_VECTOR": "NodeSocketVector"
    }

    for i, (attr_name, attr_type) in enumerate(attributes.items()):
        store_node = group.nodes.new('GeometryNodeStoreNamedAttribute')
        store_node.location = (x_offset * (i + 1), 0)
        store_node.inputs['Name'].default_value = attr_name
        store_node.data_type = attr_type
        store_node.domain = 'SPLINE'

        group.links.new(previous_node_output, store_node.inputs['Geometry'])
        previous_node_output = store_node.outputs['Geometry']

        socket_type = socket_map.get(attr_type.upper(), "NodeSocketFloat")
        new_socket = group.interface.new_socket(name=attr_name, in_out='INPUT', socket_type=socket_type)
        group.links.new(input_node.outputs[new_socket.name], store_node.inputs['Value'])

    group.links.new(previous_node_output, output_node.inputs['Geometry'])


def create_geometry_nodes_modifier(obj, obj_type):
    setup_geometry_node_trees()

    node_group = node_groups.get(obj_type)
    if not node_group:
        print(f"Unrecognized object type for {obj_type}. Skipping modifier setup.")
        return

    try:
        modifier = add_geometry_nodes_modifier(obj, node_group.name)
        tag_imported(modifier)
    except ValueError as e:
        print(f"Error creating Geometry Nodes modifier: {e}")

def set_modifier_inputs_with_keyframes(obj, attributes, frame_values, fixed_values=None):
    modifier = obj.modifiers.get("GeometryNodes")
    if not modifier:
        print(f"No GeometryNodes modifier found on object '{obj.name}'.")
        return

    for i, (attr_name, attr_type) in enumerate(attributes.items()):
        socket_index = i + 2
        socket_count = f"Socket_{socket_index}"

        if attr_name in frame_values:
            for frame, value in frame_values[attr_name]:
                try:
                    if attr_type == 'BOOLEAN':
                        modifier[socket_count] = bool(value)
                    elif attr_type == 'FLOAT':
                        modifier[socket_count] = float(value)
                    elif attr_type == 'INT':
                        modifier[socket_count] = int(value)
                    elif attr_type == 'FLOAT_VECTOR':
                        modifier[socket_count] = tuple(float(v) for v in value)
                    modifier.keyframe_insert(data_path=f'["{socket_count}"]', frame=frame)
                except Exception as e:
                    print(f"Error setting keyframes for '{attr_name}' on socket '{socket_count}': {e}")
        elif fixed_values and attr_name in fixed_values:
            try:
                value = fixed_values[attr_name]
                if attr_type == 'BOOLEAN':
                    modifier[socket_count] = bool(value)
                elif attr_type == 'FLOAT':
                    modifier[socket_count] = float(value)
                elif attr_type == 'INT':
                    modifier[socket_count] = int(value)
                elif attr_type == 'FLOAT_VECTOR':
                    modifier[socket_count] = tuple(float(v) for v in value)
                print(f"Set fixed value for '{attr_name}' on socket '{socket_count}' to {value}")
            except Exception as e:
                print(f"Error setting fixed value for '{attr_name}' on socket '{socket_count}': {e}")
        else:
            print(f"No values provided for attribute '{attr_name}'. Skipping.")

def assign_collections_to_sockets(obj, socket_to_collection, operator=None):
    modifier = obj.modifiers.get("GeometryNodes")
    if not modifier:
        error_message = f"No GeometryNodes modifier found on object '{obj.name}'."
        if operator:
            operator.report({'ERROR'}, error_message)
        print(error_message)
        return

    for socket_name, collection in socket_to_collection.items():
        try:
            if socket_name in modifier:
                modifier[socket_name] = collection
                print(f"Assigned collection '{collection.name}' to '{socket_name}'.")
            else:
                error_message = f"Socket '{socket_name}' not found in modifier 'GeometryNodes'."
                if operator:
                    operator.report({'ERROR'}, error_message)
                print(error_message)
        except Exception as e:
            error_message = f"Error assigning collection '{collection.name}' to '{socket_name}': {e}"
            if operator:
                operator.report({'ERROR'}, error_message)
            print(error_message)

def add_geometry_nodes_modifier(obj, node_group_name):
    node_group = bpy.data.node_groups.get(node_group_name)
    if not node_group:
        raise ValueError(f"Node Group '{node_group_name}' not found.")
    modifier = obj.modifiers.new(name="GeometryNodes", type='NODES') if not obj.modifiers.get("GeometryNodes") else obj.modifiers.get("GeometryNodes")
    modifier.node_group = node_group
    return modifier