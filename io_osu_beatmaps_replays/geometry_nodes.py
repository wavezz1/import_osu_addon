import bpy

def create_geometry_nodes_modifier(obj, driver_obj_name, attributes):
    modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
    group = bpy.data.node_groups.new(f"Geometry Nodes {obj.name}", 'GeometryNodeTree')
    modifier.node_group = group

    input_node = group.nodes.new('NodeGroupInput')
    output_node = group.nodes.new('NodeGroupOutput')
    input_node.location.x = 0
    output_node.location.x = 1000

    group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

    previous_node = input_node

    for key, data_type in attributes.items():
        store_node = group.nodes.new('GeometryNodeStoreNamedAttribute')
        store_node.location.x = previous_node.location.x + 200
        store_node.inputs['Name'].default_value = key
        store_node.data_type = data_type
        store_node.domain = 'POINT'

        driver = store_node.inputs['Value'].driver_add('default_value').driver
        driver.type = 'AVERAGE'
        var = driver.variables.new()
        var.name = 'var'
        var.targets[0].id_type = 'OBJECT'
        var.targets[0].id = bpy.data.objects[driver_obj_name]
        var.targets[0].data_path = f'["{key}"]'

        group.links.new(previous_node.outputs['Geometry'], store_node.inputs['Geometry'])
        previous_node = store_node

    output_node.location.x = previous_node.location.x + 200
    group.links.new(previous_node.outputs['Geometry'], output_node.inputs['Geometry'])

def create_geometry_nodes_modifier_circle(obj, driver_obj_name):
    attributes = {"show": 'BOOLEAN', "was_hit": 'BOOLEAN', "ar": 'FLOAT', "cs": 'FLOAT'}
    create_geometry_nodes_modifier(obj, driver_obj_name, attributes)

def create_geometry_nodes_modifier_cursor(obj, driver_obj_name):
    attributes = {"k1": 'BOOLEAN', "k2": 'BOOLEAN', "m1": 'BOOLEAN', "m2": 'BOOLEAN'}
    create_geometry_nodes_modifier(obj, driver_obj_name, attributes)

def create_geometry_nodes_modifier_slider(obj, driver_obj_name):
    attributes = {
        "show": 'BOOLEAN', "slider_duration": 'FLOAT', "slider_duration_frames": 'FLOAT', "ar": 'FLOAT', "cs": 'FLOAT',
        "was_hit": 'BOOLEAN', "was_completed": 'BOOLEAN'
    }
    create_geometry_nodes_modifier(obj, driver_obj_name, attributes)

def create_geometry_nodes_modifier_spinner(obj, driver_obj_name):
    attributes = {
        "show": 'BOOLEAN', "spinner_duration_ms": 'FLOAT', "spinner_duration_frames": 'FLOAT', "was_hit": 'BOOLEAN',
        "was_completed": 'BOOLEAN'
    }
    create_geometry_nodes_modifier(obj, driver_obj_name, attributes)
