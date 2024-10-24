# geometry_nodes.py

import bpy

def create_geometry_nodes_modifier_cursor(obj, driver_obj_name):
    # Geometry Nodes Modifier hinzufügen
    modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')

    # Neuen Geometry Node Tree erstellen
    node_group_name = f"Geometry Nodes {obj.name}"
    group = bpy.data.node_groups.new(node_group_name, 'GeometryNodeTree')
    modifier.node_group = group

    # Group Input und Group Output Knoten hinzufügen
    input_node = group.nodes.new('NodeGroupInput')
    output_node = group.nodes.new('NodeGroupOutput')

    input_node.location.x = 0
    output_node.location.x = 1000

    # Geometrie-Sockets für Input und Output hinzufügen
    group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # Erstelle die Attribute für "k1", "k2", "m1", "m2", "ar", "cs"
    previous_node = input_node  # Start mit Input-Node

    for key in ["k1", "k2", "m1", "m2", "ar", "cs"]:
        store_attribute_node_key = group.nodes.new('GeometryNodeStoreNamedAttribute')
        store_attribute_node_key.location.x = previous_node.location.x + 200
        store_attribute_node_key.inputs['Name'].default_value = key
        store_attribute_node_key.data_type = 'FLOAT' if key in ["ar", "cs"] else 'BOOLEAN'
        store_attribute_node_key.domain = 'POINT'

        # Driver auf Input setzen
        driver_key = store_attribute_node_key.inputs['Value'].driver_add('default_value').driver
        driver_key.type = 'AVERAGE'
        var_key = driver_key.variables.new()
        var_key.name = 'var'
        var_key.targets[0].id_type = 'OBJECT'
        var_key.targets[0].id = bpy.data.objects[driver_obj_name]
        var_key.targets[0].data_path = f'["{key}"]'

        # Verknüpfungen zwischen vorherigem Knoten und dem aktuellen Knoten
        group.links.new(previous_node.outputs['Geometry'], store_attribute_node_key.inputs['Geometry'])

        # Aktuellen Knoten als vorherigen für die nächste Iteration setzen
        previous_node = store_attribute_node_key

    # Letzte Verbindung zum Output-Knoten
    group.links.new(previous_node.outputs['Geometry'], output_node.inputs['Geometry'])

def create_geometry_nodes_modifier_circle(obj, driver_obj_name):
    # Geometry Nodes Modifier hinzufügen
    modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')

    # Neuen Geometry Node Tree erstellen
    node_group_name = f"Geometry Nodes {obj.name}"
    group = bpy.data.node_groups.new(node_group_name, 'GeometryNodeTree')
    modifier.node_group = group

    # Group Input und Group Output Knoten hinzufügen
    input_node = group.nodes.new('NodeGroupInput')
    output_node = group.nodes.new('NodeGroupOutput')

    input_node.location.x = 0
    output_node.location.x = 500

    # Geometrie-Sockets für Input und Output hinzufügen
    group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # Store Named Attribute Knoten hinzufügen (für "show", "ar", "cs")
    for key in ["show", "ar", "cs"]:
        store_attribute_node = group.nodes.new('GeometryNodeStoreNamedAttribute')
        store_attribute_node.location.x = input_node.location.x + 200
        store_attribute_node.inputs['Name'].default_value = key
        store_attribute_node.data_type = 'BOOLEAN' if key == "show" else 'FLOAT'
        store_attribute_node.domain = 'POINT'

        # Driver auf Input setzen
        driver = store_attribute_node.inputs['Value'].driver_add('default_value').driver
        driver.type = 'AVERAGE'
        var = driver.variables.new()
        var.name = 'var'
        var.targets[0].id_type = 'OBJECT'
        var.targets[0].id = bpy.data.objects[driver_obj_name]
        var.targets[0].data_path = f'["{key}"]'

        # Verknüpfungen erstellen
        group.links.new(input_node.outputs['Geometry'], store_attribute_node.inputs['Geometry'])
        input_node = store_attribute_node

    # Verbindung zum Output-Knoten
    group.links.new(input_node.outputs['Geometry'], output_node.inputs['Geometry'])

def create_geometry_nodes_modifier_slider(obj, driver_obj_name):
    # Geometry Nodes Modifier hinzufügen
    modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')

    # Neuen Geometry Node Tree erstellen
    node_group_name = f"Geometry Nodes {obj.name}"
    group = bpy.data.node_groups.new(node_group_name, 'GeometryNodeTree')
    modifier.node_group = group

    # Group Input und Group Output Knoten hinzufügen
    input_node = group.nodes.new('NodeGroupInput')
    output_node = group.nodes.new('NodeGroupOutput')

    input_node.location.x = 0
    output_node.location.x = 1000

    # Geometrie-Sockets für Input und Output hinzufügen
    group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # Attribute für "show", "slider_duration", "slider_duration_frames", "ar", "cs", und "is_anchor" hinzufügen
    for key in ["show", "slider_duration", "slider_duration_frames", "ar", "cs"]:
        store_attribute_node_key = group.nodes.new('GeometryNodeStoreNamedAttribute')
        store_attribute_node_key.location.x = input_node.location.x + 200 + (len(key) * 50)
        store_attribute_node_key.inputs['Name'].default_value = key
        store_attribute_node_key.data_type = 'BOOLEAN' if key in ["show"] else 'FLOAT'
        store_attribute_node_key.domain = 'POINT'

        driver_key = store_attribute_node_key.inputs['Value'].driver_add('default_value').driver
        driver_key.type = 'AVERAGE'
        var_key = driver_key.variables.new()
        var_key.name = 'var'
        var_key.targets[0].id_type = 'OBJECT'
        var_key.targets[0].id = bpy.data.objects[driver_obj_name]
        var_key.targets[0].data_path = f'["{key}"]'

        # Verknüpfungen erstellen
        group.links.new(input_node.outputs['Geometry'], store_attribute_node_key.inputs['Geometry'])
        input_node = store_attribute_node_key  # Verkette die Nodes nacheinander

    # Letzte Verbindung zum Output-Knoten
    group.links.new(input_node.outputs['Geometry'], output_node.inputs['Geometry'])

def create_geometry_nodes_modifier_spinner(obj, driver_obj_name):
    # Geometry Nodes Modifier hinzufügen
    modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')

    # Neuen Geometry Node Tree erstellen
    node_group_name = f"Geometry Nodes {obj.name}"
    group = bpy.data.node_groups.new(node_group_name, 'GeometryNodeTree')
    modifier.node_group = group

    # Group Input und Group Output Knoten hinzufügen
    input_node = group.nodes.new('NodeGroupInput')
    output_node = group.nodes.new('NodeGroupOutput')

    input_node.location.x = 0
    output_node.location.x = 1000

    # Geometrie-Sockets für Input und Output hinzufügen
    group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # Attribute für "show", "spinner_duration_ms", und "spinner_duration_frames" hinzufügen
    for key in ["show", "spinner_duration_ms", "spinner_duration_frames"]:
        store_attribute_node_key = group.nodes.new('GeometryNodeStoreNamedAttribute')
        store_attribute_node_key.location.x = 150 + (len(key) * 50)
        store_attribute_node_key.inputs['Name'].default_value = key
        store_attribute_node_key.data_type = 'BOOLEAN' if key == "show" else 'FLOAT'
        store_attribute_node_key.domain = 'POINT'

        # Driver auf Input setzen
        driver_key = store_attribute_node_key.inputs['Value'].driver_add('default_value').driver
        driver_key.type = 'AVERAGE'
        var_key = driver_key.variables.new()
        var_key.name = 'var'
        var_key.targets[0].id_type = 'OBJECT'
        var_key.targets[0].id = bpy.data.objects[driver_obj_name]
        var_key.targets[0].data_path = f'["{key}"]'

        # Verknüpfungen erstellen
        group.links.new(input_node.outputs['Geometry'], store_attribute_node_key.inputs['Geometry'])
        input_node = store_attribute_node_key  # Verkette die Nodes nacheinander

    # Letzte Verbindung zum Output-Knoten
    group.links.new(input_node.outputs['Geometry'], output_node.inputs['Geometry'])
