# geometry_nodes.py

import bpy


def create_geometry_nodes_modifier(obj, node_group_name, attributes):
    # Überprüfen, ob die Node Group bereits existiert, sonst erstellen
    if node_group_name in bpy.data.node_groups:
        group = bpy.data.node_groups[node_group_name]
    else:
        group = bpy.data.node_groups.new(node_group_name, 'GeometryNodeTree')
        setup_node_group_interface(group, attributes)

    # Modifier hinzufügen und Node Group zuweisen
    modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
    modifier.node_group = group


def setup_node_group_interface(group, attributes):
    # Löschen Sie alle Standard-Sockets
    group.inputs.clear()
    group.outputs.clear()

    # Füge einen Geometry Eingang und Ausgang hinzu
    group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

    previous_node = group.nodes.new('NodeGroupInput')
    previous_node.location = (0, 0)
    output_node = group.nodes.new('NodeGroupOutput')
    output_node.location = (400, 0)

    group.links.new(previous_node.outputs['Geometry'], output_node.inputs['Geometry'])

    # Für jedes Attribut einen Store Named Attribute Knoten hinzufügen
    for i, (attr_name, attr_type) in enumerate(attributes.items()):
        store_node = group.nodes.new('GeometryNodeStoreNamedAttribute')
        store_node.location = (200, -100 * i)
        store_node.inputs['Name'].default_value = attr_name
        store_node.data_type = attr_type
        store_node.domain = 'POINT'

        # Verbinden des vorherigen Knotens mit dem aktuellen Store Node
        group.links.new(previous_node.outputs['Geometry'], store_node.inputs['Geometry'])
        group.links.new(store_node.outputs['Geometry'], output_node.inputs['Geometry'])


def create_geometry_nodes_modifier_circle(obj, node_group_name):
    attributes = {"show": 'BOOLEAN', "was_hit": 'BOOLEAN', "ar": 'FLOAT', "cs": 'FLOAT'}
    create_geometry_nodes_modifier(obj, node_group_name, attributes)


def create_geometry_nodes_modifier_slider(obj, node_group_name):
    attributes = {
        "show": 'BOOLEAN',
        "slider_duration": 'FLOAT',
        "slider_duration_frames": 'FLOAT',
        "ar": 'FLOAT',
        "cs": 'FLOAT',
        "was_hit": 'BOOLEAN',
        "was_completed": 'BOOLEAN'
    }
    create_geometry_nodes_modifier(obj, node_group_name, attributes)


def create_geometry_nodes_modifier_spinner(obj, node_group_name):
    attributes = {
        "show": 'BOOLEAN',
        "spinner_duration_ms": 'FLOAT',
        "spinner_duration_frames": 'FLOAT',
        "was_hit": 'BOOLEAN',
        "was_completed": 'BOOLEAN'
    }
    create_geometry_nodes_modifier(obj, node_group_name, attributes)


def create_geometry_nodes_modifier_cursor(obj, node_group_name):
    attributes = {"k1": 'BOOLEAN', "k2": 'BOOLEAN', "m1": 'BOOLEAN', "m2": 'BOOLEAN'}
    create_geometry_nodes_modifier(obj, node_group_name, attributes)

def connect_attributes_with_drivers(obj, attributes):
    for attr_name, attr_type in attributes.items():
        # Überprüfen, ob das Objekt die Property besitzt
        if attr_name in obj:
            # Erstellen eines Fahrers für das entsprechende Attribut im Node Group Input
            modifier = obj.modifiers.get("GeometryNodes")
            if not modifier:
                continue
            node_group = modifier.node_group
            if not node_group:
                continue

            # Finden des entsprechenden Store Nodes
            store_node = None
            for node in node_group.nodes:
                if isinstance(node, bpy.types.GeometryNodeStoreNamedAttribute) and node.inputs['Name'].default_value == attr_name:
                    store_node = node
                    break
            if not store_node:
                continue

            # Hinzufügen des Fahrers
            driver = store_node.inputs['Value'].driver_add('default_value').driver
            driver.type = 'AVERAGE'
            var = driver.variables.new()
            var.name = 'var'
            var.targets[0].id_type = 'OBJECT'
            var.targets[0].id = obj
            var.targets[0].data_path = f'["{attr_name}"]'
