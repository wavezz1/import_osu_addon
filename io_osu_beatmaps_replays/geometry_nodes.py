import bpy
from .utils import timeit
import time

node_groups = {}

def setup_geometry_node_trees():
    global node_groups
    if not node_groups:
        with timeit("Einrichten der Geometry Node Trees"):
            node_groups = {
                "circle": create_geometry_nodes_tree("Geometry Nodes Circle", {
                    "show": 'BOOLEAN',
                    "was_hit": 'BOOLEAN',
                    "ar": 'FLOAT',
                    "cs": 'FLOAT'
                }),
                "slider": create_geometry_nodes_tree("Geometry Nodes Slider", {
                    "show": 'BOOLEAN',
                    "slider_duration": 'FLOAT',
                    "slider_duration_frames": 'FLOAT',
                    "ar": 'FLOAT',
                    "cs": 'FLOAT',
                    "was_hit": 'BOOLEAN',
                    "was_completed": 'BOOLEAN'
                }),
                "spinner": create_geometry_nodes_tree("Geometry Nodes Spinner", {
                    "show": 'BOOLEAN',
                    "spinner_duration_ms": 'FLOAT',
                    "spinner_duration_frames": 'FLOAT',
                    "was_hit": 'BOOLEAN',
                    "was_completed": 'BOOLEAN'
                }),
                "cursor": create_geometry_nodes_tree("Geometry Nodes Cursor", {
                    "k1": 'BOOLEAN',
                    "k2": 'BOOLEAN',
                    "m1": 'BOOLEAN',
                    "m2": 'BOOLEAN'
                })
            }

def create_geometry_nodes_tree(name, attributes):
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]

    group = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    setup_node_group_interface(group, attributes)
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
    setup_geometry_node_trees()

    node_group = node_groups.get(obj_type)
    if not node_group:
        print(f"Unrecognized object type for {obj_type}. Skipping modifier setup.")
        return

    modifier = obj.modifiers.get("GeometryNodes")
    if not modifier:
        modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
    modifier.node_group = node_group


def connect_attributes_with_drivers(obj, attributes):
    modifier = obj.modifiers.get("GeometryNodes")
    if not modifier:
        return

    # Zugriff auf die Node Group des Modifiers
    node_group = modifier.node_group
    if not node_group:
        print(f"Keine Node Group für Modifier 'GeometryNodes' auf Objekt '{obj.name}' gefunden.")
        return

    for attr_name, attr_type in attributes.items():
        socket_name = attr_name  # Sockets sind nach Attributnamen benannt

        # Überprüfen, ob der Socket existiert
        if socket_name not in node_group.interface.inputs:
            print(f"Socket '{socket_name}' nicht in der Geometry Nodes Gruppe gefunden.")
            continue

        try:
            # Treiber hinzufügen
            driver = modifier.driver_add(f'["{socket_name}"]').driver
            driver.type = 'AVERAGE'

            # Variable für den Treiber erstellen
            var = driver.variables.new()
            var.name = 'var'
            var.type = 'SINGLE_PROP'

            # Ziel des Treibers setzen
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = obj
            target.data_path = f'["{attr_name}"]'

        except Exception as e:
            print(f"Fehler beim Setzen des Treibers für Attribut '{attr_name}' auf Socket '{socket_name}': {e}")

# def connect_cursor_attributes_with_drivers(cursor):
#     modifier = cursor.modifiers.get("GeometryNodes")
#     if not modifier:
#         return
#
#     socket_mapping = {
#         "k1": "Socket_2",
#         "k2": "Socket_3",
#         "m1": "Socket_4",
#         "m2": "Socket_5"
#     }
#
#     for attr_name, socket_name in socket_mapping.items():
#         if attr_name not in cursor:
#             continue
#
#         try:
#             driver = modifier.driver_add(f'["{socket_name}"]').driver
#             driver.type = 'AVERAGE'
#             var = driver.variables.new()
#             var.name = 'var'
#             var.targets[0].id_type = 'OBJECT'
#             var.targets[0].id = cursor
#             var.targets[0].data_path = f'["{attr_name}"]'
#         except Exception as e:
#             print(f"Could not set driver for {attr_name} on {socket_name}: {e}")
