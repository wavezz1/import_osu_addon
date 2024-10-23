# geometry_nodes.py

import bpy

def create_geometry_nodes_modifier(obj, driver_obj_name):
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

    # Store Named Attribute Knoten hinzufügen (für "show")
    store_attribute_node_show = group.nodes.new('GeometryNodeStoreNamedAttribute')

    store_attribute_node_show.location.x = 150

    store_attribute_node_show.inputs['Name'].default_value = "show"
    store_attribute_node_show.data_type = 'BOOLEAN'
    store_attribute_node_show.domain = 'POINT'

    # Driver auf Boolean Input setzen (für "show")
    driver_show = store_attribute_node_show.inputs['Value'].driver_add('default_value').driver
    driver_show.type = 'AVERAGE'
    var_show = driver_show.variables.new()
    var_show.name = 'var'
    var_show.targets[0].id_type = 'OBJECT'
    var_show.targets[0].id = bpy.data.objects[driver_obj_name]
    var_show.targets[0].data_path = '["show"]'

    # Store Named Attribute Knoten hinzufügen (für "time_ms")
    store_attribute_node_time = group.nodes.new('GeometryNodeStoreNamedAttribute')

    store_attribute_node_time.location.x = 300

    store_attribute_node_time.inputs['Name'].default_value = "time_ms"
    store_attribute_node_time.data_type = 'FLOAT'
    store_attribute_node_time.domain = 'POINT'

    # Driver auf Float Input setzen (für "time_ms")
    driver_time = store_attribute_node_time.inputs['Value'].driver_add('default_value').driver
    driver_time.type = 'AVERAGE'
    var_time = driver_time.variables.new()
    var_time.name = 'var'
    var_time.targets[0].id_type = 'OBJECT'
    var_time.targets[0].id = bpy.data.objects[driver_obj_name]
    var_time.targets[0].data_path = '["time_ms"]'

    # Verbindungen zwischen den Knoten erstellen
    group.links.new(input_node.outputs['Geometry'], store_attribute_node_show.inputs['Geometry'])
    group.links.new(store_attribute_node_show.outputs['Geometry'], store_attribute_node_time.inputs['Geometry'])
    group.links.new(store_attribute_node_time.outputs['Geometry'], output_node.inputs['Geometry'])

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

    # Erstelle die Attribute für "k1", "k2", "m1", "m2"
    previous_node = input_node  # Start mit Input-Node

    for key in ["k1", "k2", "m1", "m2"]:
        store_attribute_node_key = group.nodes.new('GeometryNodeStoreNamedAttribute')
        store_attribute_node_key.location.x = previous_node.location.x + 200
        store_attribute_node_key.inputs['Name'].default_value = key
        store_attribute_node_key.data_type = 'BOOLEAN'
        store_attribute_node_key.domain = 'POINT'

        # Driver auf Boolean Input setzen (für die Tasten)
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

    # Attribute für "show" und "slider_duration" hinzufügen
    for key in ["show", "slider_duration"]:
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
