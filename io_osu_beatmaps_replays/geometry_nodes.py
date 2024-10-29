import bpy

# Speichere die Node Groups in einem Dictionary, damit sie nur einmal erstellt werden
node_groups = {}


def setup_geometry_node_trees():
    """
    Initialisiert die vier Node Trees, falls sie noch nicht existieren.
    """
    global node_groups
    if not node_groups:
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
    """
    Erstellt einen Geometry Node Tree, falls er noch nicht existiert, und fügt die erforderlichen Sockets hinzu.
    """
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]

    group = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    setup_node_group_interface(group, attributes)
    return group


def setup_node_group_interface(group, attributes):
    """
    Erstellt die Sockets für die Geometry Node Group und verbindet die Attribute.
    """
    x_offset = 200
    # Füge einen Geometry Eingang und Ausgang hinzu
    group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

    input_node = group.nodes.new('NodeGroupInput')
    input_node.location = (0, 0)
    output_node = group.nodes.new('NodeGroupOutput')
    output_node.location = (x_offset * (len(attributes) + 1), 0)

    # Verlinke direkt Geometry Input mit dem ersten Store Node
    previous_node_output = input_node.outputs['Geometry']

    # Mapping für Socket-Typen
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

        # Verbinde den vorherigen Knoten mit dem aktuellen Store Node
        group.links.new(previous_node_output, store_node.inputs['Geometry'])
        previous_node_output = store_node.outputs['Geometry']

        # Erstelle den richtigen Socket und verbinde ihn
        socket_type = socket_map.get(attr_type.upper(), "NodeSocketFloat")
        new_socket = group.interface.new_socket(name=attr_name, in_out='INPUT', socket_type=socket_type)
        group.links.new(input_node.outputs[new_socket.name], store_node.inputs['Value'])

    # Verbinde den letzten Store Node mit dem Output
    group.links.new(previous_node_output, output_node.inputs['Geometry'])


def create_geometry_nodes_modifier(obj, obj_type):
    """
    Weist dem Objekt den entsprechenden Geometry Node Tree basierend auf dem Objekttyp zu.
    """
    # Initialisiere die Node Trees einmalig
    setup_geometry_node_trees()

    # Hole die passende Node Group für den gegebenen Objekttyp
    node_group = node_groups.get(obj_type)
    if not node_group:
        print(f"Unrecognized object type for {obj_type}. Skipping modifier setup.")
        return

    # Erstelle den Modifier und weise die Node Group zu, falls sie nicht schon zugewiesen ist
    modifier = obj.modifiers.get("GeometryNodes")
    if not modifier:
        modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
    modifier.node_group = node_group


def connect_attributes_with_drivers(obj, attributes):
    """
    Verbindet die Objekt-Properties mit den Geometry Node Tree-Sockets mittels Treibern.
    """
    modifier = obj.modifiers.get("GeometryNodes")
    if not modifier:
        return

    # Definiere die Socket-Zuordnungen je nach Objekttyp
    socket_mapping = {
        "circle": {
            "ar": "Socket_4",
            "cs": "Socket_5",
            "show": "Socket_2",
            "was_hit": "Socket_3"
        },
        "slider": {
            "ar": "Socket_5",
            "cs": "Socket_6",
            "show": "Socket_2",
            "slider_duration_frames": "Socket_4",
            "slider_duration_ms": "Socket_3",
            "was_completed": "Socket_8",
            "was_hit": "Socket_7"
        },
        "spinner": {
            "show": "Socket_2",
            "spinner_duration_frames": "Socket_4",
            "spinner_duration_ms": "Socket_3",
            "was_completed": "Socket_6",
            "was_hit": "Socket_5"
        },
        "cursor": {
            "k1": "k1",
            "k2": "k2",
            "m1": "m1",
            "m2": "m2"
        }
    }

    # Bestimme den Objekttyp und die zugehörige Socket-Zuordnung
    if "circle" in obj.name.lower():
        sockets = socket_mapping["circle"]
    elif "slider" in obj.name.lower():
        sockets = socket_mapping["slider"]
    elif "spinner" in obj.name.lower():
        sockets = socket_mapping["spinner"]
    elif "cursor" in obj.name.lower():
        sockets = socket_mapping["cursor"]
    else:
        print(f"Unrecognized object type for {obj.name}. Skipping driver setup.")
        return

    # Füge die Driver für jedes Attribut entsprechend der Socket-Zuordnung hinzu
    for attr_name, socket_name in sockets.items():
        # Überprüfen, ob die Objekt-Property für das Attribut existiert
        if attr_name not in obj:
            continue

        try:
            # Füge den Driver hinzu, der den Object-Property-Wert an den Socket-Wert bindet
            driver = modifier.driver_add(f'["{socket_name}"]').driver
            driver.type = 'AVERAGE'
            var = driver.variables.new()
            var.name = 'var'
            var.targets[0].id_type = 'OBJECT'
            var.targets[0].id = obj
            var.targets[0].data_path = f'["{attr_name}"]'
        except Exception as e:
            print(f"Could not set driver for {attr_name} on {socket_name}: {e}")
