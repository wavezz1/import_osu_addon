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
    # Festlegen der Position der Nodes
    x_offset = 200

    # Füge einen Geometry Eingang und Ausgang hinzu
    group_input = group.nodes.new('NodeGroupInput')
    group_input.location = (0, 0)
    group_output = group.nodes.new('NodeGroupOutput')
    group_output.location = (x_offset * (len(attributes) + 1), 0)

    # Verlinke direkt Geometry Input mit dem ersten Store Node
    previous_node_output = group_input.outputs['Geometry']

    # Definiere eine Map für die Socket-Typen
    socket_map = {
        "BOOLEAN": "NodeSocketBool",
        "FLOAT": "NodeSocketFloat",
        "INT": "NodeSocketInt"
    }

    # Füge für jedes Attribut einen Store Named Attribute Knoten hinzu
    for i, (attr_name, attr_type) in enumerate(attributes.items()):
        store_node = group.nodes.new('GeometryNodeStoreNamedAttribute')
        store_node.location = (x_offset * (i + 1), 0)  # Nur entlang der x-Achse verschoben
        store_node.inputs['Name'].default_value = attr_name
        store_node.data_type = attr_type
        store_node.domain = 'POINT'

        # Verlinken des vorherigen Knotens mit dem aktuellen Store Node
        group.links.new(previous_node_output, store_node.inputs['Geometry'])
        previous_node_output = store_node.outputs['Geometry']

        # Erstelle einen Group Input Socket für jeden Wert
        socket_type = socket_map.get(attr_type.upper(), "NodeSocketFloat")  # Fallback auf Float
        new_socket = group.interface.new_socket(name=attr_name, in_out='INPUT', socket_type=socket_type)
        group.links.new(group_input.outputs[new_socket.name], store_node.inputs['Value'])

    # Verlinke den letzten Store Node mit dem Group Output
    group.links.new(previous_node_output, group_output.inputs['Geometry'])

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
        if attr_name in obj:
            modifier = obj.modifiers.get("GeometryNodes")
            if not modifier:
                continue
            node_group = modifier.node_group
            if not node_group:
                continue

            store_node = next(
                (node for node in node_group.nodes if isinstance(node, bpy.types.GeometryNodeStoreNamedAttribute)
                 and node.inputs['Name'].default_value == attr_name), None)
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
