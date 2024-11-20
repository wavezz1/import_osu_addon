import bpy, mathutils


def circle_sim_group_node_group():
    circle_sim_group = bpy.data.node_groups.new(type='GeometryNodeTree', name="Circle Sim Group")

    circle_sim_group.color_tag = 'NONE'
    circle_sim_group.description = ""

    # circle_sim_group interface
    # Socket Circles
    circles_socket = circle_sim_group.interface.new_socket(name="Circles", in_out='OUTPUT',
                                                           socket_type='NodeSocketGeometry')
    circles_socket.attribute_domain = 'POINT'

    # Socket Circle Mesh
    circle_mesh_socket = circle_sim_group.interface.new_socket(name="Circle Mesh", in_out='OUTPUT',
                                                               socket_type='NodeSocketGeometry')
    circle_mesh_socket.attribute_domain = 'POINT'

    # Socket Geometry
    geometry_socket = circle_sim_group.interface.new_socket(name="Geometry", in_out='INPUT',
                                                            socket_type='NodeSocketGeometry')
    geometry_socket.attribute_domain = 'POINT'

    # Socket Circle Material
    circle_material_socket = circle_sim_group.interface.new_socket(name="Circle Material", in_out='INPUT',
                                                                   socket_type='NodeSocketMaterial')
    circle_material_socket.attribute_domain = 'POINT'

    # Socket Y Offset
    y_offset_socket = circle_sim_group.interface.new_socket(name="Y Offset", in_out='INPUT',
                                                            socket_type='NodeSocketFloat')
    y_offset_socket.default_value = 0.0
    y_offset_socket.min_value = -10000.0
    y_offset_socket.max_value = 10000.0
    y_offset_socket.subtype = 'NONE'
    y_offset_socket.attribute_domain = 'POINT'

    # initialize circle_sim_group nodes
    # node Group Output
    group_output = circle_sim_group.nodes.new("NodeGroupOutput")
    group_output.name = "Group Output"
    group_output.is_active_output = True

    # node Group Input
    group_input = circle_sim_group.nodes.new("NodeGroupInput")
    group_input.name = "Group Input"
    group_input.outputs[1].hide = True
    group_input.outputs[2].hide = True
    group_input.outputs[3].hide = True

    # node Realize Instances
    realize_instances = circle_sim_group.nodes.new("GeometryNodeRealizeInstances")
    realize_instances.name = "Realize Instances"
    # Selection
    realize_instances.inputs[1].default_value = True
    # Realize All
    realize_instances.inputs[2].default_value = True
    # Depth
    realize_instances.inputs[3].default_value = 0

    # node Delete Geometry
    delete_geometry = circle_sim_group.nodes.new("GeometryNodeDeleteGeometry")
    delete_geometry.name = "Delete Geometry"
    delete_geometry.domain = 'POINT'
    delete_geometry.mode = 'ALL'

    # node Named Attribute
    named_attribute = circle_sim_group.nodes.new("GeometryNodeInputNamedAttribute")
    named_attribute.name = "Named Attribute"
    named_attribute.data_type = 'FLOAT'
    # Name
    named_attribute.inputs[0].default_value = "show"

    # node Boolean Math
    boolean_math = circle_sim_group.nodes.new("FunctionNodeBooleanMath")
    boolean_math.name = "Boolean Math"
    boolean_math.hide = True
    boolean_math.operation = 'NOT'

    # node Delete Geometry.001
    delete_geometry_001 = circle_sim_group.nodes.new("GeometryNodeDeleteGeometry")
    delete_geometry_001.name = "Delete Geometry.001"
    delete_geometry_001.domain = 'POINT'
    delete_geometry_001.mode = 'ALL'

    # node Named Attribute.001
    named_attribute_001 = circle_sim_group.nodes.new("GeometryNodeInputNamedAttribute")
    named_attribute_001.name = "Named Attribute.001"
    named_attribute_001.data_type = 'BOOLEAN'
    # Name
    named_attribute_001.inputs[0].default_value = "was_hit"

    # node Instance on Points
    instance_on_points = circle_sim_group.nodes.new("GeometryNodeInstanceOnPoints")
    instance_on_points.name = "Instance on Points"
    instance_on_points.inputs[1].hide = True
    instance_on_points.inputs[3].hide = True
    instance_on_points.inputs[4].hide = True
    instance_on_points.inputs[5].hide = True
    instance_on_points.inputs[6].hide = True
    # Selection
    instance_on_points.inputs[1].default_value = True
    # Pick Instance
    instance_on_points.inputs[3].default_value = False
    # Instance Index
    instance_on_points.inputs[4].default_value = 0
    # Rotation
    instance_on_points.inputs[5].default_value = (0.0, 0.0, 0.0)
    # Scale
    instance_on_points.inputs[6].default_value = (1.0, 1.0, 1.0)

    # node Mesh Circle
    mesh_circle = circle_sim_group.nodes.new("GeometryNodeMeshCircle")
    mesh_circle.name = "Mesh Circle"
    mesh_circle.fill_type = 'NGON'
    # Vertices
    mesh_circle.inputs[0].default_value = 32
    # Radius
    mesh_circle.inputs[1].default_value = 1.0

    # node Transform Geometry
    transform_geometry = circle_sim_group.nodes.new("GeometryNodeTransform")
    transform_geometry.name = "Transform Geometry"
    transform_geometry.mode = 'COMPONENTS'
    transform_geometry.inputs[2].hide = True
    transform_geometry.inputs[4].hide = True
    # Rotation
    transform_geometry.inputs[2].default_value = (1.5707963705062866, 0.0, 0.0)

    # node Named Attribute.003
    named_attribute_003 = circle_sim_group.nodes.new("GeometryNodeInputNamedAttribute")
    named_attribute_003.name = "Named Attribute.003"
    named_attribute_003.data_type = 'FLOAT'
    # Name
    named_attribute_003.inputs[0].default_value = "cs"

    # node Attribute Statistic
    attribute_statistic = circle_sim_group.nodes.new("GeometryNodeAttributeStatistic")
    attribute_statistic.name = "Attribute Statistic"
    attribute_statistic.data_type = 'FLOAT'
    attribute_statistic.domain = 'POINT'
    attribute_statistic.inputs[1].hide = True
    attribute_statistic.outputs[1].hide = True
    attribute_statistic.outputs[2].hide = True
    attribute_statistic.outputs[3].hide = True
    attribute_statistic.outputs[4].hide = True
    attribute_statistic.outputs[5].hide = True
    attribute_statistic.outputs[6].hide = True
    attribute_statistic.outputs[7].hide = True
    # Selection
    attribute_statistic.inputs[1].default_value = True

    # node Set Material
    set_material = circle_sim_group.nodes.new("GeometryNodeSetMaterial")
    set_material.name = "Set Material"
    # Selection
    set_material.inputs[1].default_value = True

    # node Transform Geometry.001
    transform_geometry_001 = circle_sim_group.nodes.new("GeometryNodeTransform")
    transform_geometry_001.name = "Transform Geometry.001"
    transform_geometry_001.mode = 'COMPONENTS'
    transform_geometry_001.inputs[1].hide = True
    transform_geometry_001.inputs[2].hide = True
    transform_geometry_001.inputs[4].hide = True
    # Translation
    transform_geometry_001.inputs[1].default_value = (0.0, 0.0, 0.0)
    # Rotation
    transform_geometry_001.inputs[2].default_value = (1.5707963705062866, 0.0, 0.0)

    # node Attribute Statistic.001
    attribute_statistic_001 = circle_sim_group.nodes.new("GeometryNodeAttributeStatistic")
    attribute_statistic_001.name = "Attribute Statistic.001"
    attribute_statistic_001.data_type = 'FLOAT'
    attribute_statistic_001.domain = 'POINT'
    attribute_statistic_001.inputs[1].hide = True
    attribute_statistic_001.outputs[1].hide = True
    attribute_statistic_001.outputs[2].hide = True
    attribute_statistic_001.outputs[3].hide = True
    attribute_statistic_001.outputs[4].hide = True
    attribute_statistic_001.outputs[5].hide = True
    attribute_statistic_001.outputs[6].hide = True
    attribute_statistic_001.outputs[7].hide = True
    # Selection
    attribute_statistic_001.inputs[1].default_value = True

    # node Reroute
    reroute = circle_sim_group.nodes.new("NodeReroute")
    reroute.name = "Reroute"
    # node Reroute.001
    reroute_001 = circle_sim_group.nodes.new("NodeReroute")
    reroute_001.name = "Reroute.001"
    # node Combine XYZ
    combine_xyz = circle_sim_group.nodes.new("ShaderNodeCombineXYZ")
    combine_xyz.name = "Combine XYZ"
    combine_xyz.inputs[0].hide = True
    combine_xyz.inputs[2].hide = True
    # X
    combine_xyz.inputs[0].default_value = 0.0
    # Z
    combine_xyz.inputs[2].default_value = 0.0

    # node UV Unwrap
    uv_unwrap = circle_sim_group.nodes.new("GeometryNodeUVUnwrap")
    uv_unwrap.name = "UV Unwrap"
    uv_unwrap.method = 'ANGLE_BASED'
    uv_unwrap.inputs[0].hide = True
    uv_unwrap.inputs[2].hide = True
    uv_unwrap.inputs[3].hide = True
    # Selection
    uv_unwrap.inputs[0].default_value = True
    # Margin
    uv_unwrap.inputs[2].default_value = 0.0010000000474974513
    # Fill Holes
    uv_unwrap.inputs[3].default_value = True

    # node Boolean
    boolean = circle_sim_group.nodes.new("FunctionNodeInputBool")
    boolean.name = "Boolean"
    boolean.boolean = True

    # node Pack UV Islands
    pack_uv_islands = circle_sim_group.nodes.new("GeometryNodeUVPackIslands")
    pack_uv_islands.name = "Pack UV Islands"
    pack_uv_islands.inputs[1].hide = True
    pack_uv_islands.inputs[2].hide = True
    pack_uv_islands.inputs[3].hide = True
    # Selection
    pack_uv_islands.inputs[1].default_value = True
    # Margin
    pack_uv_islands.inputs[2].default_value = 0.0010000000474974513
    # Rotate
    pack_uv_islands.inputs[3].default_value = True

    # node Reroute.002
    reroute_002 = circle_sim_group.nodes.new("NodeReroute")
    reroute_002.name = "Reroute.002"
    # node Store Named Attribute
    store_named_attribute = circle_sim_group.nodes.new("GeometryNodeStoreNamedAttribute")
    store_named_attribute.name = "Store Named Attribute"
    store_named_attribute.data_type = 'FLOAT_VECTOR'
    store_named_attribute.domain = 'CORNER'
    store_named_attribute.inputs[1].hide = True
    store_named_attribute.inputs[2].hide = True
    # Selection
    store_named_attribute.inputs[1].default_value = True
    # Name
    store_named_attribute.inputs[2].default_value = "UVMap"

    # node Reroute.003
    reroute_003 = circle_sim_group.nodes.new("NodeReroute")
    reroute_003.name = "Reroute.003"
    # node Reroute.004
    reroute_004 = circle_sim_group.nodes.new("NodeReroute")
    reroute_004.name = "Reroute.004"
    # node Reroute.005
    reroute_005 = circle_sim_group.nodes.new("NodeReroute")
    reroute_005.name = "Reroute.005"
    # node Reroute.006
    reroute_006 = circle_sim_group.nodes.new("NodeReroute")
    reroute_006.name = "Reroute.006"
    # node Reroute.007
    reroute_007 = circle_sim_group.nodes.new("NodeReroute")
    reroute_007.name = "Reroute.007"
    # node Reroute.008
    reroute_008 = circle_sim_group.nodes.new("NodeReroute")
    reroute_008.name = "Reroute.008"
    # node Group Input.001
    group_input_001 = circle_sim_group.nodes.new("NodeGroupInput")
    group_input_001.name = "Group Input.001"
    group_input_001.outputs[0].hide = True
    group_input_001.outputs[1].hide = True
    group_input_001.outputs[3].hide = True

    # node Group Input.002
    group_input_002 = circle_sim_group.nodes.new("NodeGroupInput")
    group_input_002.name = "Group Input.002"
    group_input_002.outputs[0].hide = True
    group_input_002.outputs[2].hide = True
    group_input_002.outputs[3].hide = True

    # node Reroute.010
    reroute_010 = circle_sim_group.nodes.new("NodeReroute")
    reroute_010.name = "Reroute.010"
    # node Reroute.011
    reroute_011 = circle_sim_group.nodes.new("NodeReroute")
    reroute_011.name = "Reroute.011"
    # node Reroute.012
    reroute_012 = circle_sim_group.nodes.new("NodeReroute")
    reroute_012.name = "Reroute.012"
    # node Reroute.013
    reroute_013 = circle_sim_group.nodes.new("NodeReroute")
    reroute_013.name = "Reroute.013"
    # node Reroute.009
    reroute_009 = circle_sim_group.nodes.new("NodeReroute")
    reroute_009.name = "Reroute.009"
    # node Reroute.014
    reroute_014 = circle_sim_group.nodes.new("NodeReroute")
    reroute_014.name = "Reroute.014"

    # Set locations
    group_output.location = (920.0, -40.0)
    group_input.location = (-1000.0, -80.0)
    realize_instances.location = (-840.0, -80.0)
    delete_geometry.location = (-660.0, -80.0)
    named_attribute.location = (-660.0, -280.0)
    boolean_math.location = (-660.0, -240.0)
    delete_geometry_001.location = (-480.0, -80.0)
    named_attribute_001.location = (-480.0, -240.0)
    instance_on_points.location = (500.0, 120.0)
    mesh_circle.location = (-320.0, -240.0)
    transform_geometry.location = (340.0, 20.0)
    named_attribute_003.location = (0.0, -580.0)
    attribute_statistic.location = (180.0, -80.0)
    set_material.location = (660.0, 120.0)
    transform_geometry_001.location = (340.0, -380.0)
    attribute_statistic_001.location = (180.0, -480.0)
    reroute.location = (-680.0, -120.0)
    reroute_001.location = (-680.0, -600.0)
    combine_xyz.location = (180.0, 20.0)
    uv_unwrap.location = (-160.0, -480.0)
    boolean.location = (-160.0, -580.0)
    pack_uv_islands.location = (-160.0, -400.0)
    reroute_002.location = (40.0, -280.0)
    store_named_attribute.location = (-160.0, -240.0)
    reroute_003.location = (40.0, -60.0)
    reroute_004.location = (40.0, -460.0)
    reroute_005.location = (860.0, 80.0)
    reroute_006.location = (860.0, -60.0)
    reroute_007.location = (860.0, -100.0)
    reroute_008.location = (860.0, -420.0)
    group_input_001.location = (20.0, 20.0)
    group_input_002.location = (500.0, 0.0)
    reroute_010.location = (160.0, -620.0)
    reroute_011.location = (160.0, -220.0)
    reroute_012.location = (-240.0, -120.0)
    reroute_013.location = (-240.0, 60.0)
    reroute_009.location = (-680.0, -180.0)
    reroute_014.location = (-240.0, -200.0)

    # Set dimensions
    group_output.width, group_output.height = 140.0, 100.0
    group_input.width, group_input.height = 140.0, 100.0
    realize_instances.width, realize_instances.height = 140.0, 100.0
    delete_geometry.width, delete_geometry.height = 140.0, 100.0
    named_attribute.width, named_attribute.height = 140.0, 100.0
    boolean_math.width, boolean_math.height = 140.0, 100.0
    delete_geometry_001.width, delete_geometry_001.height = 140.0, 100.0
    named_attribute_001.width, named_attribute_001.height = 140.0, 100.0
    instance_on_points.width, instance_on_points.height = 140.0, 100.0
    mesh_circle.width, mesh_circle.height = 140.0, 100.0
    transform_geometry.width, transform_geometry.height = 140.0, 100.0
    named_attribute_003.width, named_attribute_003.height = 140.0, 100.0
    attribute_statistic.width, attribute_statistic.height = 140.0, 100.0
    set_material.width, set_material.height = 140.0, 100.0
    transform_geometry_001.width, transform_geometry_001.height = 140.0, 100.0
    attribute_statistic_001.width, attribute_statistic_001.height = 140.0, 100.0
    reroute.width, reroute.height = 16.0, 100.0
    reroute_001.width, reroute_001.height = 16.0, 100.0
    combine_xyz.width, combine_xyz.height = 140.0, 100.0
    uv_unwrap.width, uv_unwrap.height = 140.0, 100.0
    boolean.width, boolean.height = 140.0, 100.0
    pack_uv_islands.width, pack_uv_islands.height = 140.0, 100.0
    reroute_002.width, reroute_002.height = 16.0, 100.0
    store_named_attribute.width, store_named_attribute.height = 140.0, 100.0
    reroute_003.width, reroute_003.height = 16.0, 100.0
    reroute_004.width, reroute_004.height = 16.0, 100.0
    reroute_005.width, reroute_005.height = 16.0, 100.0
    reroute_006.width, reroute_006.height = 16.0, 100.0
    reroute_007.width, reroute_007.height = 16.0, 100.0
    reroute_008.width, reroute_008.height = 16.0, 100.0
    group_input_001.width, group_input_001.height = 140.0, 100.0
    group_input_002.width, group_input_002.height = 140.0, 100.0
    reroute_010.width, reroute_010.height = 16.0, 100.0
    reroute_011.width, reroute_011.height = 16.0, 100.0
    reroute_012.width, reroute_012.height = 16.0, 100.0
    reroute_013.width, reroute_013.height = 16.0, 100.0
    reroute_009.width, reroute_009.height = 16.0, 100.0
    reroute_014.width, reroute_014.height = 16.0, 100.0

    # initialize circle_sim_group links
    # named_attribute.Attribute -> boolean_math.Boolean
    circle_sim_group.links.new(named_attribute.outputs[0], boolean_math.inputs[0])
    # group_input.Geometry -> realize_instances.Geometry
    circle_sim_group.links.new(group_input.outputs[0], realize_instances.inputs[0])
    # reroute_009.Output -> delete_geometry.Geometry
    circle_sim_group.links.new(reroute_009.outputs[0], delete_geometry.inputs[0])
    # delete_geometry.Geometry -> delete_geometry_001.Geometry
    circle_sim_group.links.new(delete_geometry.outputs[0], delete_geometry_001.inputs[0])
    # named_attribute_001.Attribute -> delete_geometry_001.Selection
    circle_sim_group.links.new(named_attribute_001.outputs[0], delete_geometry_001.inputs[1])
    # reroute_013.Output -> instance_on_points.Points
    circle_sim_group.links.new(reroute_013.outputs[0], instance_on_points.inputs[0])
    # reroute_006.Output -> group_output.Circles
    circle_sim_group.links.new(reroute_006.outputs[0], group_output.inputs[0])
    # reroute_003.Output -> transform_geometry.Geometry
    circle_sim_group.links.new(reroute_003.outputs[0], transform_geometry.inputs[0])
    # transform_geometry.Geometry -> instance_on_points.Instance
    circle_sim_group.links.new(transform_geometry.outputs[0], instance_on_points.inputs[2])
    # reroute_014.Output -> attribute_statistic.Geometry
    circle_sim_group.links.new(reroute_014.outputs[0], attribute_statistic.inputs[0])
    # attribute_statistic.Mean -> transform_geometry.Scale
    circle_sim_group.links.new(attribute_statistic.outputs[0], transform_geometry.inputs[3])
    # reroute_011.Output -> attribute_statistic.Attribute
    circle_sim_group.links.new(reroute_011.outputs[0], attribute_statistic.inputs[2])
    # instance_on_points.Instances -> set_material.Geometry
    circle_sim_group.links.new(instance_on_points.outputs[0], set_material.inputs[0])
    # attribute_statistic_001.Mean -> transform_geometry_001.Scale
    circle_sim_group.links.new(attribute_statistic_001.outputs[0], transform_geometry_001.inputs[3])
    # reroute_004.Output -> transform_geometry_001.Geometry
    circle_sim_group.links.new(reroute_004.outputs[0], transform_geometry_001.inputs[0])
    # reroute_001.Output -> attribute_statistic_001.Geometry
    circle_sim_group.links.new(reroute_001.outputs[0], attribute_statistic_001.inputs[0])
    # reroute_010.Output -> attribute_statistic_001.Attribute
    circle_sim_group.links.new(reroute_010.outputs[0], attribute_statistic_001.inputs[2])
    # reroute_007.Output -> group_output.Circle Mesh
    circle_sim_group.links.new(reroute_007.outputs[0], group_output.inputs[1])
    # realize_instances.Geometry -> reroute.Input
    circle_sim_group.links.new(realize_instances.outputs[0], reroute.inputs[0])
    # reroute_009.Output -> reroute_001.Input
    circle_sim_group.links.new(reroute_009.outputs[0], reroute_001.inputs[0])
    # combine_xyz.Vector -> transform_geometry.Translation
    circle_sim_group.links.new(combine_xyz.outputs[0], transform_geometry.inputs[1])
    # boolean.Boolean -> uv_unwrap.Seam
    circle_sim_group.links.new(boolean.outputs[0], uv_unwrap.inputs[1])
    # uv_unwrap.UV -> pack_uv_islands.UV
    circle_sim_group.links.new(uv_unwrap.outputs[0], pack_uv_islands.inputs[0])
    # store_named_attribute.Geometry -> reroute_002.Input
    circle_sim_group.links.new(store_named_attribute.outputs[0], reroute_002.inputs[0])
    # mesh_circle.Mesh -> store_named_attribute.Geometry
    circle_sim_group.links.new(mesh_circle.outputs[0], store_named_attribute.inputs[0])
    # pack_uv_islands.UV -> store_named_attribute.Value
    circle_sim_group.links.new(pack_uv_islands.outputs[0], store_named_attribute.inputs[3])
    # reroute_002.Output -> reroute_003.Input
    circle_sim_group.links.new(reroute_002.outputs[0], reroute_003.inputs[0])
    # reroute_002.Output -> reroute_004.Input
    circle_sim_group.links.new(reroute_002.outputs[0], reroute_004.inputs[0])
    # set_material.Geometry -> reroute_005.Input
    circle_sim_group.links.new(set_material.outputs[0], reroute_005.inputs[0])
    # reroute_005.Output -> reroute_006.Input
    circle_sim_group.links.new(reroute_005.outputs[0], reroute_006.inputs[0])
    # reroute_008.Output -> reroute_007.Input
    circle_sim_group.links.new(reroute_008.outputs[0], reroute_007.inputs[0])
    # transform_geometry_001.Geometry -> reroute_008.Input
    circle_sim_group.links.new(transform_geometry_001.outputs[0], reroute_008.inputs[0])
    # group_input_001.Y Offset -> combine_xyz.Y
    circle_sim_group.links.new(group_input_001.outputs[2], combine_xyz.inputs[1])
    # group_input_002.Circle Material -> set_material.Material
    circle_sim_group.links.new(group_input_002.outputs[1], set_material.inputs[2])
    # named_attribute_003.Attribute -> reroute_010.Input
    circle_sim_group.links.new(named_attribute_003.outputs[0], reroute_010.inputs[0])
    # reroute_010.Output -> reroute_011.Input
    circle_sim_group.links.new(reroute_010.outputs[0], reroute_011.inputs[0])
    # delete_geometry_001.Geometry -> reroute_012.Input
    circle_sim_group.links.new(delete_geometry_001.outputs[0], reroute_012.inputs[0])
    # reroute_012.Output -> reroute_013.Input
    circle_sim_group.links.new(reroute_012.outputs[0], reroute_013.inputs[0])
    # boolean_math.Boolean -> delete_geometry.Selection
    circle_sim_group.links.new(boolean_math.outputs[0], delete_geometry.inputs[1])
    # reroute.Output -> reroute_009.Input
    circle_sim_group.links.new(reroute.outputs[0], reroute_009.inputs[0])
    # reroute_012.Output -> reroute_014.Input
    circle_sim_group.links.new(reroute_012.outputs[0], reroute_014.inputs[0])
    return circle_sim_group




# initialize slider_sim_group node group
def slider_sim_group_node_group():
    slider_sim_group = bpy.data.node_groups.new(type='GeometryNodeTree', name="Slider Sim Group")

    slider_sim_group.color_tag = 'NONE'
    slider_sim_group.description = ""

    # slider_sim_group interface
    # Socket Geometry
    geometry_socket_1 = slider_sim_group.interface.new_socket(name="Geometry", in_out='OUTPUT',
                                                              socket_type='NodeSocketGeometry')
    geometry_socket_1.attribute_domain = 'POINT'

    # Socket Geometry
    geometry_socket_2 = slider_sim_group.interface.new_socket(name="Geometry", in_out='INPUT',
                                                              socket_type='NodeSocketGeometry')
    geometry_socket_2.attribute_domain = 'POINT'

    # Socket Circle Mesh
    circle_mesh_socket_1 = slider_sim_group.interface.new_socket(name="Circle Mesh", in_out='INPUT',
                                                                 socket_type='NodeSocketGeometry')
    circle_mesh_socket_1.attribute_domain = 'POINT'

    # Socket Slider Material
    slider_material_socket = slider_sim_group.interface.new_socket(name="Slider Material", in_out='INPUT',
                                                                   socket_type='NodeSocketMaterial')
    slider_material_socket.attribute_domain = 'POINT'

    # Socket Slider Head/Tail Y Offset
    slider_head_tail_y_offset_socket = slider_sim_group.interface.new_socket(name="Slider Head/Tail Y Offset",
                                                                             in_out='INPUT',
                                                                             socket_type='NodeSocketFloat')
    slider_head_tail_y_offset_socket.default_value = 0.0
    slider_head_tail_y_offset_socket.min_value = -10000.0
    slider_head_tail_y_offset_socket.max_value = 10000.0
    slider_head_tail_y_offset_socket.subtype = 'NONE'
    slider_head_tail_y_offset_socket.attribute_domain = 'POINT'

    # Socket Slider Curve Y Offset
    slider_curve_y_offset_socket = slider_sim_group.interface.new_socket(name="Slider Curve Y Offset", in_out='INPUT',
                                                                         socket_type='NodeSocketFloat')
    slider_curve_y_offset_socket.default_value = 0.0
    slider_curve_y_offset_socket.min_value = -10000.0
    slider_curve_y_offset_socket.max_value = 10000.0
    slider_curve_y_offset_socket.subtype = 'NONE'
    slider_curve_y_offset_socket.attribute_domain = 'POINT'

    # Socket Enable Slider Balls
    enable_slider_balls_socket = slider_sim_group.interface.new_socket(name="Enable Slider Balls", in_out='INPUT',
                                                                       socket_type='NodeSocketBool')
    enable_slider_balls_socket.default_value = True
    enable_slider_balls_socket.attribute_domain = 'POINT'

    # Socket Slider Balls
    slider_balls_socket = slider_sim_group.interface.new_socket(name="Slider Balls", in_out='INPUT',
                                                                socket_type='NodeSocketCollection')
    slider_balls_socket.attribute_domain = 'POINT'

    # Socket Slider Balls Material
    slider_balls_material_socket = slider_sim_group.interface.new_socket(name="Slider Balls Material", in_out='INPUT',
                                                                         socket_type='NodeSocketMaterial')
    slider_balls_material_socket.attribute_domain = 'POINT'

    # Socket Slider Balls Y Offset
    slider_balls_y_offset__socket = slider_sim_group.interface.new_socket(name="Slider Balls Y Offset ", in_out='INPUT',
                                                                          socket_type='NodeSocketFloat')
    slider_balls_y_offset__socket.default_value = 0.0
    slider_balls_y_offset__socket.min_value = -10000.0
    slider_balls_y_offset__socket.max_value = 10000.0
    slider_balls_y_offset__socket.subtype = 'NONE'
    slider_balls_y_offset__socket.attribute_domain = 'POINT'

    # Socket Slider Headt/Tail Material
    slider_headt_tail_material_socket = slider_sim_group.interface.new_socket(name="Slider Headt/Tail Material",
                                                                              in_out='INPUT',
                                                                              socket_type='NodeSocketMaterial')
    slider_headt_tail_material_socket.attribute_domain = 'POINT'

    # initialize slider_sim_group nodes
    # node Group Output
    group_output_1 = slider_sim_group.nodes.new("NodeGroupOutput")
    group_output_1.name = "Group Output"
    group_output_1.is_active_output = True

    # node Group Input
    group_input_1 = slider_sim_group.nodes.new("NodeGroupInput")
    group_input_1.name = "Group Input"
    group_input_1.outputs[1].hide = True
    group_input_1.outputs[2].hide = True
    group_input_1.outputs[3].hide = True
    group_input_1.outputs[4].hide = True
    group_input_1.outputs[5].hide = True
    group_input_1.outputs[6].hide = True
    group_input_1.outputs[7].hide = True
    group_input_1.outputs[8].hide = True
    group_input_1.outputs[9].hide = True
    group_input_1.outputs[10].hide = True

    # node Realize Instances
    realize_instances_1 = slider_sim_group.nodes.new("GeometryNodeRealizeInstances")
    realize_instances_1.name = "Realize Instances"
    # Selection
    realize_instances_1.inputs[1].default_value = True
    # Realize All
    realize_instances_1.inputs[2].default_value = True
    # Depth
    realize_instances_1.inputs[3].default_value = 0

    # node Delete Geometry
    delete_geometry_1 = slider_sim_group.nodes.new("GeometryNodeDeleteGeometry")
    delete_geometry_1.name = "Delete Geometry"
    delete_geometry_1.domain = 'POINT'
    delete_geometry_1.mode = 'ALL'

    # node Named Attribute
    named_attribute_1 = slider_sim_group.nodes.new("GeometryNodeInputNamedAttribute")
    named_attribute_1.name = "Named Attribute"
    named_attribute_1.data_type = 'FLOAT'
    # Name
    named_attribute_1.inputs[0].default_value = "show"

    # node Boolean Math
    boolean_math_1 = slider_sim_group.nodes.new("FunctionNodeBooleanMath")
    boolean_math_1.name = "Boolean Math"
    boolean_math_1.hide = True
    boolean_math_1.operation = 'NOT'

    # node Endpoint Selection.004
    endpoint_selection_004 = slider_sim_group.nodes.new("GeometryNodeCurveEndpointSelection")
    endpoint_selection_004.name = "Endpoint Selection.004"
    # Start Size
    endpoint_selection_004.inputs[0].default_value = 0
    # End Size
    endpoint_selection_004.inputs[1].default_value = 1

    # node Endpoint Selection.005
    endpoint_selection_005 = slider_sim_group.nodes.new("GeometryNodeCurveEndpointSelection")
    endpoint_selection_005.name = "Endpoint Selection.005"
    # Start Size
    endpoint_selection_005.inputs[0].default_value = 1
    # End Size
    endpoint_selection_005.inputs[1].default_value = 0

    # node Instance on Points.002
    instance_on_points_002 = slider_sim_group.nodes.new("GeometryNodeInstanceOnPoints")
    instance_on_points_002.name = "Instance on Points.002"
    instance_on_points_002.inputs[3].hide = True
    instance_on_points_002.inputs[4].hide = True
    instance_on_points_002.inputs[5].hide = True
    instance_on_points_002.inputs[6].hide = True
    # Pick Instance
    instance_on_points_002.inputs[3].default_value = False
    # Instance Index
    instance_on_points_002.inputs[4].default_value = 0
    # Rotation
    instance_on_points_002.inputs[5].default_value = (0.0, 0.0, 0.0)
    # Scale
    instance_on_points_002.inputs[6].default_value = (1.0, 1.0, 1.0)

    # node Boolean Math.003
    boolean_math_003 = slider_sim_group.nodes.new("FunctionNodeBooleanMath")
    boolean_math_003.name = "Boolean Math.003"
    boolean_math_003.operation = 'OR'

    # node Curve to Mesh
    curve_to_mesh = slider_sim_group.nodes.new("GeometryNodeCurveToMesh")
    curve_to_mesh.name = "Curve to Mesh"
    curve_to_mesh.inputs[2].hide = True
    # Fill Caps
    curve_to_mesh.inputs[2].default_value = False

    # node Curve Line
    curve_line = slider_sim_group.nodes.new("GeometryNodeCurvePrimitiveLine")
    curve_line.name = "Curve Line"
    curve_line.mode = 'POINTS'

    # node Value
    value = slider_sim_group.nodes.new("ShaderNodeValue")
    value.name = "Value"

    value.outputs[0].default_value = 1.0
    # node Combine XYZ
    combine_xyz_1 = slider_sim_group.nodes.new("ShaderNodeCombineXYZ")
    combine_xyz_1.name = "Combine XYZ"
    combine_xyz_1.hide = True
    # X
    combine_xyz_1.inputs[0].default_value = 0.0
    # Z
    combine_xyz_1.inputs[2].default_value = 0.0

    # node Combine XYZ.001
    combine_xyz_001 = slider_sim_group.nodes.new("ShaderNodeCombineXYZ")
    combine_xyz_001.name = "Combine XYZ.001"
    combine_xyz_001.hide = True
    # X
    combine_xyz_001.inputs[0].default_value = 0.0
    # Z
    combine_xyz_001.inputs[2].default_value = 0.0

    # node Math.001
    math_001 = slider_sim_group.nodes.new("ShaderNodeMath")
    math_001.name = "Math.001"
    math_001.operation = 'MULTIPLY'
    math_001.use_clamp = False
    # Value_001
    math_001.inputs[1].default_value = -1.0

    # node Frame
    frame = slider_sim_group.nodes.new("NodeFrame")
    frame.label = "Init Splines"
    frame.name = "Frame"
    frame.label_size = 20
    frame.shrink = True

    # node Frame.003
    frame_003 = slider_sim_group.nodes.new("NodeFrame")
    frame_003.label = "Instance Head and Tail on Slider"
    frame_003.name = "Frame.003"
    frame_003.label_size = 20
    frame_003.shrink = True

    # node Frame.004
    frame_004 = slider_sim_group.nodes.new("NodeFrame")
    frame_004.label = "Create Curve Path"
    frame_004.name = "Frame.004"
    frame_004.label_size = 20
    frame_004.shrink = True

    # node Named Attribute.003
    named_attribute_003_1 = slider_sim_group.nodes.new("GeometryNodeInputNamedAttribute")
    named_attribute_003_1.name = "Named Attribute.003"
    named_attribute_003_1.data_type = 'FLOAT'
    # Name
    named_attribute_003_1.inputs[0].default_value = "cs"

    # node Set Curve Radius
    set_curve_radius = slider_sim_group.nodes.new("GeometryNodeSetCurveRadius")
    set_curve_radius.name = "Set Curve Radius"
    set_curve_radius.inputs[1].hide = True
    # Selection
    set_curve_radius.inputs[1].default_value = True

    # node Math.003
    math_003 = slider_sim_group.nodes.new("ShaderNodeMath")
    math_003.name = "Math.003"
    math_003.operation = 'ADD'
    math_003.use_clamp = False
    # Value_001
    math_003.inputs[1].default_value = 1.0

    # node Reroute.001
    reroute_001_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_001_1.name = "Reroute.001"
    # node Delete Geometry.001
    delete_geometry_001_1 = slider_sim_group.nodes.new("GeometryNodeDeleteGeometry")
    delete_geometry_001_1.name = "Delete Geometry.001"
    delete_geometry_001_1.domain = 'CURVE'
    delete_geometry_001_1.mode = 'ALL'

    # node Named Attribute.001
    named_attribute_001_1 = slider_sim_group.nodes.new("GeometryNodeInputNamedAttribute")
    named_attribute_001_1.name = "Named Attribute.001"
    named_attribute_001_1.data_type = 'BOOLEAN'
    # Name
    named_attribute_001_1.inputs[0].default_value = "was_completed"

    # node Reroute.002
    reroute_002_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_002_1.name = "Reroute.002"
    # node Reroute.003
    reroute_003_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_003_1.name = "Reroute.003"
    # node Frame.001
    frame_001 = slider_sim_group.nodes.new("NodeFrame")
    frame_001.label = "normalize to 1 unit"
    frame_001.name = "Frame.001"
    frame_001.label_size = 20
    frame_001.shrink = True

    # node Math
    math = slider_sim_group.nodes.new("ShaderNodeMath")
    math.name = "Math"
    math.operation = 'DIVIDE'
    math.use_clamp = False
    # Value_001
    math.inputs[1].default_value = 2.0

    # node Set Material
    set_material_1 = slider_sim_group.nodes.new("GeometryNodeSetMaterial")
    set_material_1.name = "Set Material"
    # Selection
    set_material_1.inputs[1].default_value = True

    # node Spline Parameter
    spline_parameter = slider_sim_group.nodes.new("GeometryNodeSplineParameter")
    spline_parameter.name = "Spline Parameter"
    spline_parameter.outputs[1].hide = True
    spline_parameter.outputs[2].hide = True

    # node Capture Attribute
    capture_attribute = slider_sim_group.nodes.new("GeometryNodeCaptureAttribute")
    capture_attribute.name = "Capture Attribute"
    capture_attribute.active_index = 0
    capture_attribute.capture_items.clear()
    capture_attribute.capture_items.new('FLOAT', "Factor")
    capture_attribute.capture_items["Factor"].data_type = 'FLOAT'
    capture_attribute.domain = 'POINT'

    # node Store Named Attribute
    store_named_attribute_1 = slider_sim_group.nodes.new("GeometryNodeStoreNamedAttribute")
    store_named_attribute_1.name = "Store Named Attribute"
    store_named_attribute_1.data_type = 'FLOAT_VECTOR'
    store_named_attribute_1.domain = 'CORNER'
    # Selection
    store_named_attribute_1.inputs[1].default_value = True
    # Name
    store_named_attribute_1.inputs[2].default_value = "UVMap"

    # node Combine XYZ.002
    combine_xyz_002 = slider_sim_group.nodes.new("ShaderNodeCombineXYZ")
    combine_xyz_002.name = "Combine XYZ.002"
    combine_xyz_002.inputs[2].hide = True
    # Z
    combine_xyz_002.inputs[2].default_value = 0.0

    # node Capture Attribute.001
    capture_attribute_001 = slider_sim_group.nodes.new("GeometryNodeCaptureAttribute")
    capture_attribute_001.name = "Capture Attribute.001"
    capture_attribute_001.active_index = 0
    capture_attribute_001.capture_items.clear()
    capture_attribute_001.capture_items.new('FLOAT', "Factor")
    capture_attribute_001.capture_items["Factor"].data_type = 'FLOAT'
    capture_attribute_001.domain = 'POINT'

    # node Position.001
    position_001 = slider_sim_group.nodes.new("GeometryNodeInputPosition")
    position_001.name = "Position.001"

    # node Capture Attribute.002
    capture_attribute_002 = slider_sim_group.nodes.new("GeometryNodeCaptureAttribute")
    capture_attribute_002.name = "Capture Attribute.002"
    capture_attribute_002.active_index = 0
    capture_attribute_002.capture_items.clear()
    capture_attribute_002.capture_items.new('FLOAT', "Position")
    capture_attribute_002.capture_items["Position"].data_type = 'FLOAT_VECTOR'
    capture_attribute_002.domain = 'CURVE'

    # node Resample Curve.001
    resample_curve_001 = slider_sim_group.nodes.new("GeometryNodeResampleCurve")
    resample_curve_001.name = "Resample Curve.001"
    resample_curve_001.mode = 'COUNT'
    # Selection
    resample_curve_001.inputs[1].default_value = True
    # Count
    resample_curve_001.inputs[2].default_value = 12

    # node Collection Info
    collection_info = slider_sim_group.nodes.new("GeometryNodeCollectionInfo")
    collection_info.name = "Collection Info"
    collection_info.transform_space = 'ORIGINAL'
    collection_info.inputs[1].hide = True
    collection_info.inputs[2].hide = True
    # Separate Children
    collection_info.inputs[1].default_value = False
    # Reset Children
    collection_info.inputs[2].default_value = False

    # node Realize Instances.001
    realize_instances_001 = slider_sim_group.nodes.new("GeometryNodeRealizeInstances")
    realize_instances_001.name = "Realize Instances.001"
    realize_instances_001.inputs[1].hide = True
    realize_instances_001.inputs[2].hide = True
    realize_instances_001.inputs[3].hide = True
    # Selection
    realize_instances_001.inputs[1].default_value = True
    # Realize All
    realize_instances_001.inputs[2].default_value = True
    # Depth
    realize_instances_001.inputs[3].default_value = 0

    # node Delete Geometry.002
    delete_geometry_002 = slider_sim_group.nodes.new("GeometryNodeDeleteGeometry")
    delete_geometry_002.name = "Delete Geometry.002"
    delete_geometry_002.domain = 'POINT'
    delete_geometry_002.mode = 'ALL'

    # node Named Attribute.002
    named_attribute_002 = slider_sim_group.nodes.new("GeometryNodeInputNamedAttribute")
    named_attribute_002.name = "Named Attribute.002"
    named_attribute_002.data_type = 'FLOAT'
    # Name
    named_attribute_002.inputs[0].default_value = "show"

    # node Boolean Math.001
    boolean_math_001 = slider_sim_group.nodes.new("FunctionNodeBooleanMath")
    boolean_math_001.name = "Boolean Math.001"
    boolean_math_001.hide = True
    boolean_math_001.operation = 'NOT'

    # node Delete Geometry.003
    delete_geometry_003 = slider_sim_group.nodes.new("GeometryNodeDeleteGeometry")
    delete_geometry_003.name = "Delete Geometry.003"
    delete_geometry_003.domain = 'POINT'
    delete_geometry_003.mode = 'ALL'

    # node Named Attribute.005
    named_attribute_005 = slider_sim_group.nodes.new("GeometryNodeInputNamedAttribute")
    named_attribute_005.name = "Named Attribute.005"
    named_attribute_005.data_type = 'BOOLEAN'
    # Name
    named_attribute_005.inputs[0].default_value = "was_completed"

    # node Switch
    switch = slider_sim_group.nodes.new("GeometryNodeSwitch")
    switch.name = "Switch"
    switch.input_type = 'GEOMETRY'

    # node Instance on Points
    instance_on_points_1 = slider_sim_group.nodes.new("GeometryNodeInstanceOnPoints")
    instance_on_points_1.name = "Instance on Points"
    instance_on_points_1.inputs[1].hide = True
    instance_on_points_1.inputs[3].hide = True
    instance_on_points_1.inputs[4].hide = True
    instance_on_points_1.inputs[5].hide = True
    instance_on_points_1.inputs[6].hide = True
    # Selection
    instance_on_points_1.inputs[1].default_value = True
    # Pick Instance
    instance_on_points_1.inputs[3].default_value = False
    # Instance Index
    instance_on_points_1.inputs[4].default_value = 0
    # Rotation
    instance_on_points_1.inputs[5].default_value = (0.0, 0.0, 0.0)
    # Scale
    instance_on_points_1.inputs[6].default_value = (1.0, 1.0, 1.0)

    # node Math.004
    math_004 = slider_sim_group.nodes.new("ShaderNodeMath")
    math_004.name = "Math.004"
    math_004.operation = 'DIVIDE'
    math_004.use_clamp = False
    # Value_001
    math_004.inputs[1].default_value = 2.0

    # node Set Position
    set_position = slider_sim_group.nodes.new("GeometryNodeSetPosition")
    set_position.name = "Set Position"
    # Selection
    set_position.inputs[1].default_value = True
    # Position
    set_position.inputs[2].default_value = (0.0, 0.0, 0.0)

    # node Combine XYZ.003
    combine_xyz_003 = slider_sim_group.nodes.new("ShaderNodeCombineXYZ")
    combine_xyz_003.name = "Combine XYZ.003"
    combine_xyz_003.inputs[0].hide = True
    combine_xyz_003.inputs[2].hide = True
    # X
    combine_xyz_003.inputs[0].default_value = 0.0
    # Z
    combine_xyz_003.inputs[2].default_value = 0.0

    # node Set Position.001
    set_position_001 = slider_sim_group.nodes.new("GeometryNodeSetPosition")
    set_position_001.name = "Set Position.001"
    # Selection
    set_position_001.inputs[1].default_value = True
    # Position
    set_position_001.inputs[2].default_value = (0.0, 0.0, 0.0)

    # node Combine XYZ.004
    combine_xyz_004 = slider_sim_group.nodes.new("ShaderNodeCombineXYZ")
    combine_xyz_004.name = "Combine XYZ.004"
    combine_xyz_004.inputs[0].hide = True
    combine_xyz_004.inputs[2].hide = True
    # X
    combine_xyz_004.inputs[0].default_value = 0.0
    # Z
    combine_xyz_004.inputs[2].default_value = 0.0

    # node Set Position.002
    set_position_002 = slider_sim_group.nodes.new("GeometryNodeSetPosition")
    set_position_002.name = "Set Position.002"
    # Selection
    set_position_002.inputs[1].default_value = True
    # Position
    set_position_002.inputs[2].default_value = (0.0, 0.0, 0.0)

    # node Combine XYZ.005
    combine_xyz_005 = slider_sim_group.nodes.new("ShaderNodeCombineXYZ")
    combine_xyz_005.name = "Combine XYZ.005"
    combine_xyz_005.inputs[0].hide = True
    combine_xyz_005.inputs[2].hide = True
    # X
    combine_xyz_005.inputs[0].default_value = 0.0
    # Z
    combine_xyz_005.inputs[2].default_value = 0.0

    # node Set Material.001
    set_material_001 = slider_sim_group.nodes.new("GeometryNodeSetMaterial")
    set_material_001.name = "Set Material.001"
    # Selection
    set_material_001.inputs[1].default_value = True

    # node Group Input.001
    group_input_001_1 = slider_sim_group.nodes.new("NodeGroupInput")
    group_input_001_1.name = "Group Input.001"
    group_input_001_1.outputs[0].hide = True
    group_input_001_1.outputs[1].hide = True
    group_input_001_1.outputs[2].hide = True
    group_input_001_1.outputs[3].hide = True
    group_input_001_1.outputs[4].hide = True
    group_input_001_1.outputs[5].hide = True
    group_input_001_1.outputs[6].hide = True
    group_input_001_1.outputs[7].hide = True
    group_input_001_1.outputs[8].hide = True
    group_input_001_1.outputs[10].hide = True

    # node Group Input.002
    group_input_002_1 = slider_sim_group.nodes.new("NodeGroupInput")
    group_input_002_1.name = "Group Input.002"
    group_input_002_1.outputs[0].hide = True
    group_input_002_1.outputs[1].hide = True
    group_input_002_1.outputs[2].hide = True
    group_input_002_1.outputs[3].hide = True
    group_input_002_1.outputs[4].hide = True
    group_input_002_1.outputs[5].hide = True
    group_input_002_1.outputs[6].hide = True
    group_input_002_1.outputs[7].hide = True
    group_input_002_1.outputs[9].hide = True
    group_input_002_1.outputs[10].hide = True

    # node Group Input.004
    group_input_004 = slider_sim_group.nodes.new("NodeGroupInput")
    group_input_004.name = "Group Input.004"
    group_input_004.outputs[0].hide = True
    group_input_004.outputs[1].hide = True
    group_input_004.outputs[2].hide = True
    group_input_004.outputs[3].hide = True
    group_input_004.outputs[4].hide = True
    group_input_004.outputs[5].hide = True
    group_input_004.outputs[7].hide = True
    group_input_004.outputs[8].hide = True
    group_input_004.outputs[9].hide = True
    group_input_004.outputs[10].hide = True

    # node Group Input.005
    group_input_005 = slider_sim_group.nodes.new("NodeGroupInput")
    group_input_005.name = "Group Input.005"
    group_input_005.outputs[0].hide = True
    group_input_005.outputs[1].hide = True
    group_input_005.outputs[2].hide = True
    group_input_005.outputs[3].hide = True
    group_input_005.outputs[4].hide = True
    group_input_005.outputs[6].hide = True
    group_input_005.outputs[7].hide = True
    group_input_005.outputs[8].hide = True
    group_input_005.outputs[9].hide = True
    group_input_005.outputs[10].hide = True

    # node Group Input.006
    group_input_006 = slider_sim_group.nodes.new("NodeGroupInput")
    group_input_006.name = "Group Input.006"
    group_input_006.outputs[0].hide = True
    group_input_006.outputs[1].hide = True
    group_input_006.outputs[2].hide = True
    group_input_006.outputs[3].hide = True
    group_input_006.outputs[5].hide = True
    group_input_006.outputs[6].hide = True
    group_input_006.outputs[7].hide = True
    group_input_006.outputs[8].hide = True
    group_input_006.outputs[9].hide = True
    group_input_006.outputs[10].hide = True

    # node Group Input.007
    group_input_007 = slider_sim_group.nodes.new("NodeGroupInput")
    group_input_007.name = "Group Input.007"
    group_input_007.outputs[0].hide = True
    group_input_007.outputs[1].hide = True
    group_input_007.outputs[2].hide = True
    group_input_007.outputs[4].hide = True
    group_input_007.outputs[5].hide = True
    group_input_007.outputs[6].hide = True
    group_input_007.outputs[7].hide = True
    group_input_007.outputs[8].hide = True
    group_input_007.outputs[9].hide = True
    group_input_007.outputs[10].hide = True

    # node Group Input.009
    group_input_009 = slider_sim_group.nodes.new("NodeGroupInput")
    group_input_009.name = "Group Input.009"
    group_input_009.outputs[0].hide = True
    group_input_009.outputs[2].hide = True
    group_input_009.outputs[3].hide = True
    group_input_009.outputs[4].hide = True
    group_input_009.outputs[5].hide = True
    group_input_009.outputs[6].hide = True
    group_input_009.outputs[7].hide = True
    group_input_009.outputs[8].hide = True
    group_input_009.outputs[9].hide = True
    group_input_009.outputs[10].hide = True

    # node Group Input.010
    group_input_010 = slider_sim_group.nodes.new("NodeGroupInput")
    group_input_010.name = "Group Input.010"
    group_input_010.outputs[0].hide = True
    group_input_010.outputs[1].hide = True
    group_input_010.outputs[3].hide = True
    group_input_010.outputs[4].hide = True
    group_input_010.outputs[5].hide = True
    group_input_010.outputs[6].hide = True
    group_input_010.outputs[7].hide = True
    group_input_010.outputs[8].hide = True
    group_input_010.outputs[9].hide = True
    group_input_010.outputs[10].hide = True

    # node Reroute
    reroute_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_1.name = "Reroute"
    # node Reroute.004
    reroute_004_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_004_1.name = "Reroute.004"
    # node Reroute.005
    reroute_005_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_005_1.name = "Reroute.005"
    # node Frame.002
    frame_002 = slider_sim_group.nodes.new("NodeFrame")
    frame_002.label = "Instance Slider Balls"
    frame_002.name = "Frame.002"
    frame_002.label_size = 20
    frame_002.shrink = True

    # node Set Material.005
    set_material_005 = slider_sim_group.nodes.new("GeometryNodeSetMaterial")
    set_material_005.name = "Set Material.005"
    # Selection
    set_material_005.inputs[1].default_value = True

    # node Group Input.008
    group_input_008 = slider_sim_group.nodes.new("NodeGroupInput")
    group_input_008.name = "Group Input.008"
    group_input_008.outputs[0].hide = True
    group_input_008.outputs[1].hide = True
    group_input_008.outputs[2].hide = True
    group_input_008.outputs[3].hide = True
    group_input_008.outputs[4].hide = True
    group_input_008.outputs[5].hide = True
    group_input_008.outputs[6].hide = True
    group_input_008.outputs[8].hide = True
    group_input_008.outputs[9].hide = True
    group_input_008.outputs[10].hide = True

    # node Reroute.006
    reroute_006_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_006_1.name = "Reroute.006"
    # node Reroute.007
    reroute_007_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_007_1.name = "Reroute.007"
    # node Reroute.008
    reroute_008_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_008_1.name = "Reroute.008"
    # node Spline Parameter.001
    spline_parameter_001 = slider_sim_group.nodes.new("GeometryNodeSplineParameter")
    spline_parameter_001.name = "Spline Parameter.001"
    spline_parameter_001.outputs[1].hide = True
    spline_parameter_001.outputs[2].hide = True

    # node Reroute.009
    reroute_009_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_009_1.name = "Reroute.009"
    # node Reroute.010
    reroute_010_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_010_1.name = "Reroute.010"
    # node Reroute.011
    reroute_011_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_011_1.name = "Reroute.011"
    # node Join Geometry.002
    join_geometry_002 = slider_sim_group.nodes.new("GeometryNodeJoinGeometry")
    join_geometry_002.name = "Join Geometry.002"

    # node Join Geometry.003
    join_geometry_003 = slider_sim_group.nodes.new("GeometryNodeJoinGeometry")
    join_geometry_003.name = "Join Geometry.003"

    # node Reroute.012
    reroute_012_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_012_1.name = "Reroute.012"
    # node Reroute.013
    reroute_013_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_013_1.name = "Reroute.013"
    # node Reroute.014
    reroute_014_1 = slider_sim_group.nodes.new("NodeReroute")
    reroute_014_1.name = "Reroute.014"
    # node Reroute.015
    reroute_015 = slider_sim_group.nodes.new("NodeReroute")
    reroute_015.name = "Reroute.015"
    # node Reroute.016
    reroute_016 = slider_sim_group.nodes.new("NodeReroute")
    reroute_016.name = "Reroute.016"
    # node Reroute.017
    reroute_017 = slider_sim_group.nodes.new("NodeReroute")
    reroute_017.name = "Reroute.017"
    # node Merge by Distance
    merge_by_distance = slider_sim_group.nodes.new("GeometryNodeMergeByDistance")
    merge_by_distance.name = "Merge by Distance"
    merge_by_distance.mode = 'ALL'
    # Selection
    merge_by_distance.inputs[1].default_value = True
    # Distance
    merge_by_distance.inputs[2].default_value = 0.0010000000474974513

    # node Curve to Mesh.001
    curve_to_mesh_001 = slider_sim_group.nodes.new("GeometryNodeCurveToMesh")
    curve_to_mesh_001.name = "Curve to Mesh.001"
    # Fill Caps
    curve_to_mesh_001.inputs[2].default_value = False

    # node Mesh to Curve
    mesh_to_curve = slider_sim_group.nodes.new("GeometryNodeMeshToCurve")
    mesh_to_curve.name = "Mesh to Curve"
    # Selection
    mesh_to_curve.inputs[1].default_value = True

    # node Fillet Curve
    fillet_curve = slider_sim_group.nodes.new("GeometryNodeFilletCurve")
    fillet_curve.name = "Fillet Curve"
    fillet_curve.mode = 'POLY'
    # Count
    fillet_curve.inputs[1].default_value = 6
    # Radius
    fillet_curve.inputs[2].default_value = 30.149999618530273
    # Limit Radius
    fillet_curve.inputs[3].default_value = True

    # node Viewer
    viewer = slider_sim_group.nodes.new("GeometryNodeViewer")
    viewer.name = "Viewer"
    viewer.data_type = 'FLOAT'
    viewer.domain = 'AUTO'
    # Value
    viewer.inputs[1].default_value = 0.0

    # Set parents
    group_input_1.parent = frame
    realize_instances_1.parent = frame
    delete_geometry_1.parent = frame
    named_attribute_1.parent = frame
    boolean_math_1.parent = frame
    endpoint_selection_004.parent = frame_003
    endpoint_selection_005.parent = frame_003
    instance_on_points_002.parent = frame_003
    boolean_math_003.parent = frame_003
    curve_to_mesh.parent = frame_004
    curve_line.parent = frame_004
    value.parent = frame_001
    combine_xyz_1.parent = frame_004
    combine_xyz_001.parent = frame_004
    math_001.parent = frame_004
    named_attribute_003_1.parent = frame_004
    set_curve_radius.parent = frame_004
    math_003.parent = frame_004
    delete_geometry_001_1.parent = frame
    named_attribute_001_1.parent = frame
    frame_001.parent = frame_004
    math.parent = frame_001
    set_material_1.parent = frame_004
    spline_parameter.parent = frame_004
    capture_attribute.parent = frame_004
    store_named_attribute_1.parent = frame_004
    combine_xyz_002.parent = frame_004
    capture_attribute_001.parent = frame_004
    position_001.parent = frame_004
    capture_attribute_002.parent = frame_004
    resample_curve_001.parent = frame_004
    collection_info.parent = frame_002
    realize_instances_001.parent = frame_002
    delete_geometry_002.parent = frame_002
    named_attribute_002.parent = frame_002
    boolean_math_001.parent = frame_002
    delete_geometry_003.parent = frame_002
    named_attribute_005.parent = frame_002
    switch.parent = frame_002
    instance_on_points_1.parent = frame_002
    math_004.parent = frame_004
    set_position.parent = frame_002
    combine_xyz_003.parent = frame_002
    set_position_001.parent = frame_003
    combine_xyz_004.parent = frame_003
    set_position_002.parent = frame_004
    combine_xyz_005.parent = frame_004
    set_material_001.parent = frame_003
    group_input_001_1.parent = frame_003
    group_input_002_1.parent = frame_002
    group_input_004.parent = frame_002
    group_input_005.parent = frame_002
    group_input_006.parent = frame_004
    group_input_007.parent = frame_003
    group_input_009.parent = frame_003
    group_input_010.parent = frame_004
    reroute_004_1.parent = frame_003
    set_material_005.parent = frame_002
    group_input_008.parent = frame_002
    reroute_006_1.parent = frame_002
    reroute_007_1.parent = frame_004
    reroute_008_1.parent = frame_004
    spline_parameter_001.parent = frame_004
    reroute_009_1.parent = frame_004
    reroute_010_1.parent = frame_004
    reroute_011_1.parent = frame_004
    reroute_014_1.parent = frame_002
    merge_by_distance.parent = frame
    curve_to_mesh_001.parent = frame
    mesh_to_curve.parent = frame
    fillet_curve.parent = frame

    # Set locations
    group_output_1.location = (2460.0, -260.0)
    group_input_1.location = (-1330.0, -40.0)
    realize_instances_1.location = (-1170.0, -40.0)
    delete_geometry_1.location = (-370.0, -40.0)
    named_attribute_1.location = (-371.4922180175781, -240.92755126953125)
    boolean_math_1.location = (-371.4922180175781, -202.42237854003906)
    endpoint_selection_004.location = (1680.0, -340.0)
    endpoint_selection_005.location = (1680.0, -220.0)
    instance_on_points_002.location = (2080.0, -400.0)
    boolean_math_003.location = (1840.0, -260.0)
    curve_to_mesh.location = (3660.75439453125, 386.0)
    curve_line.location = (3140.75439453125, 66.0)
    value.location = (292.0, -426.0)
    combine_xyz_1.location = (2980.75439453125, 6.0)
    combine_xyz_001.location = (2980.75439453125, -34.0)
    math_001.location = (2980.75439453125, -74.0)
    frame.location = (230.0, -20.0)
    frame_003.location = (-590.0, -100.0)
    frame_004.location = (-2241.0, 34.0)
    named_attribute_003_1.location = (3140.75439453125, 266.0)
    set_curve_radius.location = (3460.75439453125, 386.0)
    math_003.location = (3460.75439453125, 266.0)
    reroute_001_1.location = (280.0, -100.0)
    delete_geometry_001_1.location = (-210.0, -40.0)
    named_attribute_001_1.location = (-210.0, -180.0)
    reroute_002_1.location = (280.0, 360.0)
    reroute_003_1.location = (280.0, -540.0)
    frame_001.location = (2308.75439453125, 352.0)
    math.location = (452.0, -426.0)
    set_material_1.location = (4140.75439453125, 386.0)
    spline_parameter.location = (2980.75439453125, 246.0)
    capture_attribute.location = (2980.75439453125, 386.0)
    store_named_attribute_1.location = (3820.75439453125, 386.0)
    combine_xyz_002.location = (3820.75439453125, 186.0)
    capture_attribute_001.location = (3460.75439453125, 66.0)
    position_001.location = (2821.0, 246.0)
    capture_attribute_002.location = (2820.75439453125, 386.0)
    resample_curve_001.location = (3300.75439453125, 66.0)
    collection_info.location = (1060.0, -660.0)
    realize_instances_001.location = (1200.0, -660.0)
    delete_geometry_002.location = (1360.0, -660.0)
    named_attribute_002.location = (1360.0, -860.0)
    boolean_math_001.location = (1360.0, -820.0)
    delete_geometry_003.location = (1510.0, -660.0)
    named_attribute_005.location = (1510.0, -820.0)
    switch.location = (2170.0, -660.0)
    instance_on_points_1.location = (1690.0, -660.0)
    math_004.location = (3300.75439453125, 266.0)
    set_position.location = (2010.0, -660.0)
    combine_xyz_003.location = (2010.0, -820.0)
    set_position_001.location = (2320.0, -200.0)
    combine_xyz_004.location = (2320.0, -360.0)
    set_position_002.location = (3980.75439453125, 386.0)
    combine_xyz_005.location = (3980.75439453125, 226.0)
    set_material_001.location = (2470.0, -200.0)
    group_input_001_1.location = (2470.0, -320.0)
    group_input_002_1.location = (2010.0, -900.0)
    group_input_004.location = (1060.0, -800.0)
    group_input_005.location = (2170.0, -820.0)
    group_input_006.location = (3980.75439453125, 126.0)
    group_input_007.location = (2320.0, -440.0)
    group_input_009.location = (1680.0, -460.0)
    group_input_010.location = (4140.75439453125, 266.0)
    reroute_1.location = (1700.0, -660.0)
    reroute_004_1.location = (2030.0, -500.0)
    reroute_005_1.location = (1440.0, -660.0)
    frame_002.location = (30.0, -40.0)
    set_material_005.location = (1850.0, -660.0)
    group_input_008.location = (1690.0, -780.0)
    reroute_006_1.location = (1670.0, -740.0)
    reroute_007_1.location = (3620.75439453125, 6.0)
    reroute_008_1.location = (3620.75439453125, 306.0)
    spline_parameter_001.location = (3460.75439453125, -74.0)
    reroute_009_1.location = (2940.75439453125, -114.0)
    reroute_010_1.location = (2940.75439453125, 6.0)
    reroute_011_1.location = (2939.34765625, -180.73318481445312)
    join_geometry_002.location = (2120.0, -260.0)
    join_geometry_003.location = (2300.0, -260.0)
    reroute_012_1.location = (2100.0, 380.0)
    reroute_013_1.location = (2100.0, -320.0)
    reroute_014_1.location = (2230.0, -700.0)
    reroute_015.location = (2280.0, -320.0)
    reroute_016.location = (2100.0, -340.0)
    reroute_017.location = (2280.0, -300.0)
    merge_by_distance.location = (-850.0, -40.0)
    curve_to_mesh_001.location = (-1010.0, -40.0)
    mesh_to_curve.location = (-690.0, -40.0)
    fillet_curve.location = (-530.0, -40.0)
    viewer.location = (350.0, 370.0)

    # Set dimensions
    group_output_1.width, group_output_1.height = 140.0, 100.0
    group_input_1.width, group_input_1.height = 140.0, 100.0
    realize_instances_1.width, realize_instances_1.height = 140.0, 100.0
    delete_geometry_1.width, delete_geometry_1.height = 140.0, 100.0
    named_attribute_1.width, named_attribute_1.height = 140.0, 100.0
    boolean_math_1.width, boolean_math_1.height = 140.0, 100.0
    endpoint_selection_004.width, endpoint_selection_004.height = 140.0, 100.0
    endpoint_selection_005.width, endpoint_selection_005.height = 140.0, 100.0
    instance_on_points_002.width, instance_on_points_002.height = 140.0, 100.0
    boolean_math_003.width, boolean_math_003.height = 140.0, 100.0
    curve_to_mesh.width, curve_to_mesh.height = 140.0, 100.0
    curve_line.width, curve_line.height = 140.0, 100.0
    value.width, value.height = 140.0, 100.0
    combine_xyz_1.width, combine_xyz_1.height = 140.0, 100.0
    combine_xyz_001.width, combine_xyz_001.height = 140.0, 100.0
    math_001.width, math_001.height = 140.0, 100.0
    frame.width, frame.height = 1320.0, 392.0
    frame_003.width, frame_003.height = 990.0, 391.0
    frame_004.width, frame_004.height = 1770.0, 708.0
    named_attribute_003_1.width, named_attribute_003_1.height = 140.0, 100.0
    set_curve_radius.width, set_curve_radius.height = 140.0, 100.0
    math_003.width, math_003.height = 140.0, 100.0
    reroute_001_1.width, reroute_001_1.height = 16.0, 100.0
    delete_geometry_001_1.width, delete_geometry_001_1.height = 140.0, 100.0
    named_attribute_001_1.width, named_attribute_001_1.height = 140.0, 100.0
    reroute_002_1.width, reroute_002_1.height = 16.0, 100.0
    reroute_003_1.width, reroute_003_1.height = 16.0, 100.0
    frame_001.width, frame_001.height = 360.0, 218.0
    math.width, math.height = 140.0, 100.0
    set_material_1.width, set_material_1.height = 140.0, 100.0
    spline_parameter.width, spline_parameter.height = 140.0, 100.0
    capture_attribute.width, capture_attribute.height = 140.0, 100.0
    store_named_attribute_1.width, store_named_attribute_1.height = 140.0, 100.0
    combine_xyz_002.width, combine_xyz_002.height = 140.0, 100.0
    capture_attribute_001.width, capture_attribute_001.height = 140.0, 100.0
    position_001.width, position_001.height = 140.0, 100.0
    capture_attribute_002.width, capture_attribute_002.height = 140.0, 100.0
    resample_curve_001.width, resample_curve_001.height = 140.0, 100.0
    collection_info.width, collection_info.height = 140.0, 100.0
    realize_instances_001.width, realize_instances_001.height = 140.0, 100.0
    delete_geometry_002.width, delete_geometry_002.height = 140.0, 100.0
    named_attribute_002.width, named_attribute_002.height = 140.0, 100.0
    boolean_math_001.width, boolean_math_001.height = 140.0, 100.0
    delete_geometry_003.width, delete_geometry_003.height = 140.0, 100.0
    named_attribute_005.width, named_attribute_005.height = 140.0, 100.0
    switch.width, switch.height = 140.0, 100.0
    instance_on_points_1.width, instance_on_points_1.height = 140.0, 100.0
    math_004.width, math_004.height = 140.0, 100.0
    set_position.width, set_position.height = 140.0, 100.0
    combine_xyz_003.width, combine_xyz_003.height = 140.0, 100.0
    set_position_001.width, set_position_001.height = 140.0, 100.0
    combine_xyz_004.width, combine_xyz_004.height = 140.0, 100.0
    set_position_002.width, set_position_002.height = 140.0, 100.0
    combine_xyz_005.width, combine_xyz_005.height = 140.0, 100.0
    set_material_001.width, set_material_001.height = 140.0, 100.0
    group_input_001_1.width, group_input_001_1.height = 140.0, 100.0
    group_input_002_1.width, group_input_002_1.height = 140.0, 100.0
    group_input_004.width, group_input_004.height = 140.0, 100.0
    group_input_005.width, group_input_005.height = 140.0, 100.0
    group_input_006.width, group_input_006.height = 140.0, 100.0
    group_input_007.width, group_input_007.height = 140.0, 100.0
    group_input_009.width, group_input_009.height = 140.0, 100.0
    group_input_010.width, group_input_010.height = 140.0, 100.0
    reroute_1.width, reroute_1.height = 16.0, 100.0
    reroute_004_1.width, reroute_004_1.height = 16.0, 100.0
    reroute_005_1.width, reroute_005_1.height = 16.0, 100.0
    frame_002.width, frame_002.height = 1310.0, 391.0
    set_material_005.width, set_material_005.height = 140.0, 100.0
    group_input_008.width, group_input_008.height = 140.0, 100.0
    reroute_006_1.width, reroute_006_1.height = 16.0, 100.0
    reroute_007_1.width, reroute_007_1.height = 16.0, 100.0
    reroute_008_1.width, reroute_008_1.height = 16.0, 100.0
    spline_parameter_001.width, spline_parameter_001.height = 140.0, 100.0
    reroute_009_1.width, reroute_009_1.height = 16.0, 100.0
    reroute_010_1.width, reroute_010_1.height = 16.0, 100.0
    reroute_011_1.width, reroute_011_1.height = 16.0, 100.0
    join_geometry_002.width, join_geometry_002.height = 140.0, 100.0
    join_geometry_003.width, join_geometry_003.height = 140.0, 100.0
    reroute_012_1.width, reroute_012_1.height = 16.0, 100.0
    reroute_013_1.width, reroute_013_1.height = 16.0, 100.0
    reroute_014_1.width, reroute_014_1.height = 16.0, 100.0
    reroute_015.width, reroute_015.height = 16.0, 100.0
    reroute_016.width, reroute_016.height = 16.0, 100.0
    reroute_017.width, reroute_017.height = 16.0, 100.0
    merge_by_distance.width, merge_by_distance.height = 140.0, 100.0
    curve_to_mesh_001.width, curve_to_mesh_001.height = 140.0, 100.0
    mesh_to_curve.width, mesh_to_curve.height = 140.0, 100.0
    fillet_curve.width, fillet_curve.height = 140.0, 100.0
    viewer.width, viewer.height = 140.0, 100.0

    # initialize slider_sim_group links
    # boolean_math_1.Boolean -> delete_geometry_1.Selection
    slider_sim_group.links.new(boolean_math_1.outputs[0], delete_geometry_1.inputs[1])
    # named_attribute_1.Attribute -> boolean_math_1.Boolean
    slider_sim_group.links.new(named_attribute_1.outputs[0], boolean_math_1.inputs[0])
    # group_input_1.Geometry -> realize_instances_1.Geometry
    slider_sim_group.links.new(group_input_1.outputs[0], realize_instances_1.inputs[0])
    # endpoint_selection_005.Selection -> boolean_math_003.Boolean
    slider_sim_group.links.new(endpoint_selection_005.outputs[0], boolean_math_003.inputs[0])
    # endpoint_selection_004.Selection -> boolean_math_003.Boolean
    slider_sim_group.links.new(endpoint_selection_004.outputs[0], boolean_math_003.inputs[1])
    # boolean_math_003.Boolean -> instance_on_points_002.Selection
    slider_sim_group.links.new(boolean_math_003.outputs[0], instance_on_points_002.inputs[1])
    # reroute_003_1.Output -> instance_on_points_002.Points
    slider_sim_group.links.new(reroute_003_1.outputs[0], instance_on_points_002.inputs[0])
    # join_geometry_003.Geometry -> group_output_1.Geometry
    slider_sim_group.links.new(join_geometry_003.outputs[0], group_output_1.inputs[0])
    # set_curve_radius.Curve -> curve_to_mesh.Curve
    slider_sim_group.links.new(set_curve_radius.outputs[0], curve_to_mesh.inputs[0])
    # reroute_010_1.Output -> combine_xyz_1.Y
    slider_sim_group.links.new(reroute_010_1.outputs[0], combine_xyz_1.inputs[1])
    # reroute_011_1.Output -> math_001.Value
    slider_sim_group.links.new(reroute_011_1.outputs[0], math_001.inputs[0])
    # math_001.Value -> combine_xyz_001.Y
    slider_sim_group.links.new(math_001.outputs[0], combine_xyz_001.inputs[1])
    # reroute_008_1.Output -> curve_to_mesh.Profile Curve
    slider_sim_group.links.new(reroute_008_1.outputs[0], curve_to_mesh.inputs[1])
    # capture_attribute.Geometry -> set_curve_radius.Curve
    slider_sim_group.links.new(capture_attribute.outputs[0], set_curve_radius.inputs[0])
    # math_003.Value -> set_curve_radius.Radius
    slider_sim_group.links.new(math_003.outputs[0], set_curve_radius.inputs[2])
    # delete_geometry_1.Geometry -> delete_geometry_001_1.Geometry
    slider_sim_group.links.new(delete_geometry_1.outputs[0], delete_geometry_001_1.inputs[0])
    # named_attribute_001_1.Attribute -> delete_geometry_001_1.Selection
    slider_sim_group.links.new(named_attribute_001_1.outputs[0], delete_geometry_001_1.inputs[1])
    # reroute_001_1.Output -> reroute_002_1.Input
    slider_sim_group.links.new(reroute_001_1.outputs[0], reroute_002_1.inputs[0])
    # reroute_001_1.Output -> reroute_003_1.Input
    slider_sim_group.links.new(reroute_001_1.outputs[0], reroute_003_1.inputs[0])
    # value.Value -> math.Value
    slider_sim_group.links.new(value.outputs[0], math.inputs[0])
    # combine_xyz_1.Vector -> curve_line.Start
    slider_sim_group.links.new(combine_xyz_1.outputs[0], curve_line.inputs[0])
    # combine_xyz_001.Vector -> curve_line.End
    slider_sim_group.links.new(combine_xyz_001.outputs[0], curve_line.inputs[1])
    # set_position_002.Geometry -> set_material_1.Geometry
    slider_sim_group.links.new(set_position_002.outputs[0], set_material_1.inputs[0])
    # spline_parameter.Factor -> capture_attribute.Factor
    slider_sim_group.links.new(spline_parameter.outputs[0], capture_attribute.inputs[1])
    # curve_to_mesh.Mesh -> store_named_attribute_1.Geometry
    slider_sim_group.links.new(curve_to_mesh.outputs[0], store_named_attribute_1.inputs[0])
    # capture_attribute.Factor -> combine_xyz_002.X
    slider_sim_group.links.new(capture_attribute.outputs[1], combine_xyz_002.inputs[0])
    # resample_curve_001.Curve -> capture_attribute_001.Geometry
    slider_sim_group.links.new(resample_curve_001.outputs[0], capture_attribute_001.inputs[0])
    # capture_attribute_001.Factor -> combine_xyz_002.Y
    slider_sim_group.links.new(capture_attribute_001.outputs[1], combine_xyz_002.inputs[1])
    # combine_xyz_002.Vector -> store_named_attribute_1.Value
    slider_sim_group.links.new(combine_xyz_002.outputs[0], store_named_attribute_1.inputs[3])
    # capture_attribute_002.Geometry -> capture_attribute.Geometry
    slider_sim_group.links.new(capture_attribute_002.outputs[0], capture_attribute.inputs[0])
    # delete_geometry_001_1.Geometry -> reroute_001_1.Input
    slider_sim_group.links.new(delete_geometry_001_1.outputs[0], reroute_001_1.inputs[0])
    # reroute_002_1.Output -> capture_attribute_002.Geometry
    slider_sim_group.links.new(reroute_002_1.outputs[0], capture_attribute_002.inputs[0])
    # position_001.Position -> capture_attribute_002.Position
    slider_sim_group.links.new(position_001.outputs[0], capture_attribute_002.inputs[1])
    # curve_line.Curve -> resample_curve_001.Curve
    slider_sim_group.links.new(curve_line.outputs[0], resample_curve_001.inputs[0])
    # boolean_math_001.Boolean -> delete_geometry_002.Selection
    slider_sim_group.links.new(boolean_math_001.outputs[0], delete_geometry_002.inputs[1])
    # named_attribute_002.Attribute -> boolean_math_001.Boolean
    slider_sim_group.links.new(named_attribute_002.outputs[0], boolean_math_001.inputs[0])
    # realize_instances_001.Geometry -> delete_geometry_002.Geometry
    slider_sim_group.links.new(realize_instances_001.outputs[0], delete_geometry_002.inputs[0])
    # delete_geometry_002.Geometry -> delete_geometry_003.Geometry
    slider_sim_group.links.new(delete_geometry_002.outputs[0], delete_geometry_003.inputs[0])
    # named_attribute_005.Attribute -> delete_geometry_003.Selection
    slider_sim_group.links.new(named_attribute_005.outputs[0], delete_geometry_003.inputs[1])
    # set_position.Geometry -> switch.True
    slider_sim_group.links.new(set_position.outputs[0], switch.inputs[2])
    # collection_info.Instances -> realize_instances_001.Geometry
    slider_sim_group.links.new(collection_info.outputs[0], realize_instances_001.inputs[0])
    # reroute_004_1.Output -> instance_on_points_002.Instance
    slider_sim_group.links.new(reroute_004_1.outputs[0], instance_on_points_002.inputs[2])
    # delete_geometry_003.Geometry -> instance_on_points_1.Points
    slider_sim_group.links.new(delete_geometry_003.outputs[0], instance_on_points_1.inputs[0])
    # named_attribute_003_1.Attribute -> math_004.Value
    slider_sim_group.links.new(named_attribute_003_1.outputs[0], math_004.inputs[0])
    # math_004.Value -> math_003.Value
    slider_sim_group.links.new(math_004.outputs[0], math_003.inputs[0])
    # set_material_005.Geometry -> set_position.Geometry
    slider_sim_group.links.new(set_material_005.outputs[0], set_position.inputs[0])
    # combine_xyz_003.Vector -> set_position.Offset
    slider_sim_group.links.new(combine_xyz_003.outputs[0], set_position.inputs[3])
    # instance_on_points_002.Instances -> set_position_001.Geometry
    slider_sim_group.links.new(instance_on_points_002.outputs[0], set_position_001.inputs[0])
    # combine_xyz_004.Vector -> set_position_001.Offset
    slider_sim_group.links.new(combine_xyz_004.outputs[0], set_position_001.inputs[3])
    # store_named_attribute_1.Geometry -> set_position_002.Geometry
    slider_sim_group.links.new(store_named_attribute_1.outputs[0], set_position_002.inputs[0])
    # combine_xyz_005.Vector -> set_position_002.Offset
    slider_sim_group.links.new(combine_xyz_005.outputs[0], set_position_002.inputs[3])
    # reroute_006_1.Output -> instance_on_points_1.Instance
    slider_sim_group.links.new(reroute_006_1.outputs[0], instance_on_points_1.inputs[2])
    # set_position_001.Geometry -> set_material_001.Geometry
    slider_sim_group.links.new(set_position_001.outputs[0], set_material_001.inputs[0])
    # group_input_001_1.Slider Headt/Tail Material -> set_material_001.Material
    slider_sim_group.links.new(group_input_001_1.outputs[9], set_material_001.inputs[2])
    # group_input_002_1.Slider Balls Y Offset  -> combine_xyz_003.Y
    slider_sim_group.links.new(group_input_002_1.outputs[8], combine_xyz_003.inputs[1])
    # group_input_004.Slider Balls -> collection_info.Collection
    slider_sim_group.links.new(group_input_004.outputs[6], collection_info.inputs[0])
    # group_input_005.Enable Slider Balls -> switch.Switch
    slider_sim_group.links.new(group_input_005.outputs[5], switch.inputs[0])
    # group_input_006.Slider Curve Y Offset -> combine_xyz_005.Y
    slider_sim_group.links.new(group_input_006.outputs[4], combine_xyz_005.inputs[1])
    # group_input_007.Slider Head/Tail Y Offset -> combine_xyz_004.Y
    slider_sim_group.links.new(group_input_007.outputs[3], combine_xyz_004.inputs[1])
    # group_input_010.Slider Material -> set_material_1.Material
    slider_sim_group.links.new(group_input_010.outputs[2], set_material_1.inputs[2])
    # reroute_005_1.Output -> reroute_1.Input
    slider_sim_group.links.new(reroute_005_1.outputs[0], reroute_1.inputs[0])
    # reroute_004_1.Output -> reroute_005_1.Input
    slider_sim_group.links.new(reroute_004_1.outputs[0], reroute_005_1.inputs[0])
    # group_input_009.Circle Mesh -> reroute_004_1.Input
    slider_sim_group.links.new(group_input_009.outputs[1], reroute_004_1.inputs[0])
    # instance_on_points_1.Instances -> set_material_005.Geometry
    slider_sim_group.links.new(instance_on_points_1.outputs[0], set_material_005.inputs[0])
    # group_input_008.Slider Balls Material -> set_material_005.Material
    slider_sim_group.links.new(group_input_008.outputs[7], set_material_005.inputs[2])
    # reroute_1.Output -> reroute_006_1.Input
    slider_sim_group.links.new(reroute_1.outputs[0], reroute_006_1.inputs[0])
    # capture_attribute_001.Geometry -> reroute_007_1.Input
    slider_sim_group.links.new(capture_attribute_001.outputs[0], reroute_007_1.inputs[0])
    # reroute_007_1.Output -> reroute_008_1.Input
    slider_sim_group.links.new(reroute_007_1.outputs[0], reroute_008_1.inputs[0])
    # spline_parameter_001.Factor -> capture_attribute_001.Factor
    slider_sim_group.links.new(spline_parameter_001.outputs[0], capture_attribute_001.inputs[1])
    # math.Value -> reroute_009_1.Input
    slider_sim_group.links.new(math.outputs[0], reroute_009_1.inputs[0])
    # reroute_009_1.Output -> reroute_010_1.Input
    slider_sim_group.links.new(reroute_009_1.outputs[0], reroute_010_1.inputs[0])
    # reroute_009_1.Output -> reroute_011_1.Input
    slider_sim_group.links.new(reroute_009_1.outputs[0], reroute_011_1.inputs[0])
    # reroute_016.Output -> join_geometry_002.Geometry
    slider_sim_group.links.new(reroute_016.outputs[0], join_geometry_002.inputs[0])
    # reroute_015.Output -> join_geometry_003.Geometry
    slider_sim_group.links.new(reroute_015.outputs[0], join_geometry_003.inputs[0])
    # set_material_1.Geometry -> reroute_012_1.Input
    slider_sim_group.links.new(set_material_1.outputs[0], reroute_012_1.inputs[0])
    # reroute_012_1.Output -> reroute_013_1.Input
    slider_sim_group.links.new(reroute_012_1.outputs[0], reroute_013_1.inputs[0])
    # switch.Output -> reroute_014_1.Input
    slider_sim_group.links.new(switch.outputs[0], reroute_014_1.inputs[0])
    # reroute_014_1.Output -> reroute_015.Input
    slider_sim_group.links.new(reroute_014_1.outputs[0], reroute_015.inputs[0])
    # set_material_001.Geometry -> reroute_016.Input
    slider_sim_group.links.new(set_material_001.outputs[0], reroute_016.inputs[0])
    # join_geometry_002.Geometry -> reroute_017.Input
    slider_sim_group.links.new(join_geometry_002.outputs[0], reroute_017.inputs[0])
    # curve_to_mesh_001.Mesh -> merge_by_distance.Geometry
    slider_sim_group.links.new(curve_to_mesh_001.outputs[0], merge_by_distance.inputs[0])
    # realize_instances_1.Geometry -> curve_to_mesh_001.Curve
    slider_sim_group.links.new(realize_instances_1.outputs[0], curve_to_mesh_001.inputs[0])
    # merge_by_distance.Geometry -> mesh_to_curve.Mesh
    slider_sim_group.links.new(merge_by_distance.outputs[0], mesh_to_curve.inputs[0])
    # mesh_to_curve.Curve -> fillet_curve.Curve
    slider_sim_group.links.new(mesh_to_curve.outputs[0], fillet_curve.inputs[0])
    # fillet_curve.Curve -> delete_geometry_1.Geometry
    slider_sim_group.links.new(fillet_curve.outputs[0], delete_geometry_1.inputs[0])
    # reroute_002_1.Output -> viewer.Geometry
    slider_sim_group.links.new(reroute_002_1.outputs[0], viewer.inputs[0])
    # reroute_013_1.Output -> join_geometry_002.Geometry
    slider_sim_group.links.new(reroute_013_1.outputs[0], join_geometry_002.inputs[0])
    # reroute_017.Output -> join_geometry_003.Geometry
    slider_sim_group.links.new(reroute_017.outputs[0], join_geometry_003.inputs[0])
    return slider_sim_group




# initialize spinner_sim_group node group
def spinner_sim_group_node_group():
    spinner_sim_group = bpy.data.node_groups.new(type='GeometryNodeTree', name="Spinner Sim Group")

    spinner_sim_group.color_tag = 'NONE'
    spinner_sim_group.description = ""

    # spinner_sim_group interface
    # Socket Geometry
    geometry_socket_3 = spinner_sim_group.interface.new_socket(name="Geometry", in_out='OUTPUT',
                                                               socket_type='NodeSocketGeometry')
    geometry_socket_3.attribute_domain = 'POINT'

    # Socket Geometry
    geometry_socket_4 = spinner_sim_group.interface.new_socket(name="Geometry", in_out='INPUT',
                                                               socket_type='NodeSocketGeometry')
    geometry_socket_4.attribute_domain = 'POINT'

    # Socket Scale
    scale_socket = spinner_sim_group.interface.new_socket(name="Scale", in_out='INPUT', socket_type='NodeSocketFloat')
    scale_socket.default_value = 1.0
    scale_socket.min_value = 0.0
    scale_socket.max_value = 3.4028234663852886e+38
    scale_socket.subtype = 'NONE'
    scale_socket.attribute_domain = 'POINT'

    # Socket Spinner Material
    spinner_material_socket = spinner_sim_group.interface.new_socket(name="Spinner Material", in_out='INPUT',
                                                                     socket_type='NodeSocketMaterial')
    spinner_material_socket.attribute_domain = 'POINT'

    # Socket Y Offset
    y_offset_socket_1 = spinner_sim_group.interface.new_socket(name="Y Offset", in_out='INPUT',
                                                               socket_type='NodeSocketFloat')
    y_offset_socket_1.default_value = 0.0
    y_offset_socket_1.min_value = -10000.0
    y_offset_socket_1.max_value = 10000.0
    y_offset_socket_1.subtype = 'NONE'
    y_offset_socket_1.attribute_domain = 'POINT'

    # initialize spinner_sim_group nodes
    # node Group Output
    group_output_2 = spinner_sim_group.nodes.new("NodeGroupOutput")
    group_output_2.name = "Group Output"
    group_output_2.is_active_output = True

    # node Group Input
    group_input_2 = spinner_sim_group.nodes.new("NodeGroupInput")
    group_input_2.name = "Group Input"

    # node Realize Instances
    realize_instances_2 = spinner_sim_group.nodes.new("GeometryNodeRealizeInstances")
    realize_instances_2.name = "Realize Instances"
    # Selection
    realize_instances_2.inputs[1].default_value = True
    # Realize All
    realize_instances_2.inputs[2].default_value = True
    # Depth
    realize_instances_2.inputs[3].default_value = 0

    # node Delete Geometry
    delete_geometry_2 = spinner_sim_group.nodes.new("GeometryNodeDeleteGeometry")
    delete_geometry_2.name = "Delete Geometry"
    delete_geometry_2.domain = 'POINT'
    delete_geometry_2.mode = 'ALL'

    # node Named Attribute
    named_attribute_2 = spinner_sim_group.nodes.new("GeometryNodeInputNamedAttribute")
    named_attribute_2.name = "Named Attribute"
    named_attribute_2.data_type = 'FLOAT'
    # Name
    named_attribute_2.inputs[0].default_value = "show"

    # node Boolean Math
    boolean_math_2 = spinner_sim_group.nodes.new("FunctionNodeBooleanMath")
    boolean_math_2.name = "Boolean Math"
    boolean_math_2.hide = True
    boolean_math_2.operation = 'NOT'

    # node Delete Geometry.001
    delete_geometry_001_2 = spinner_sim_group.nodes.new("GeometryNodeDeleteGeometry")
    delete_geometry_001_2.name = "Delete Geometry.001"
    delete_geometry_001_2.domain = 'POINT'
    delete_geometry_001_2.mode = 'ALL'

    # node Named Attribute.001
    named_attribute_001_2 = spinner_sim_group.nodes.new("GeometryNodeInputNamedAttribute")
    named_attribute_001_2.name = "Named Attribute.001"
    named_attribute_001_2.data_type = 'BOOLEAN'
    # Name
    named_attribute_001_2.inputs[0].default_value = "was_completed"

    # node Set Material
    set_material_2 = spinner_sim_group.nodes.new("GeometryNodeSetMaterial")
    set_material_2.name = "Set Material"
    set_material_2.inputs[1].hide = True
    # Selection
    set_material_2.inputs[1].default_value = True

    # node Instance on Points
    instance_on_points_2 = spinner_sim_group.nodes.new("GeometryNodeInstanceOnPoints")
    instance_on_points_2.name = "Instance on Points"
    instance_on_points_2.inputs[1].hide = True
    instance_on_points_2.inputs[3].hide = True
    instance_on_points_2.inputs[4].hide = True
    instance_on_points_2.inputs[5].hide = True
    instance_on_points_2.inputs[6].hide = True
    # Selection
    instance_on_points_2.inputs[1].default_value = True
    # Pick Instance
    instance_on_points_2.inputs[3].default_value = False
    # Instance Index
    instance_on_points_2.inputs[4].default_value = 0
    # Rotation
    instance_on_points_2.inputs[5].default_value = (1.5707963705062866, 0.0, 0.0)
    # Scale
    instance_on_points_2.inputs[6].default_value = (1.0, 1.0, 1.0)

    # node Mesh Circle
    mesh_circle_1 = spinner_sim_group.nodes.new("GeometryNodeMeshCircle")
    mesh_circle_1.name = "Mesh Circle"
    mesh_circle_1.fill_type = 'NGON'
    # Vertices
    mesh_circle_1.inputs[0].default_value = 32

    # node Set Position
    set_position_1 = spinner_sim_group.nodes.new("GeometryNodeSetPosition")
    set_position_1.name = "Set Position"
    set_position_1.inputs[1].hide = True
    set_position_1.inputs[2].hide = True
    # Selection
    set_position_1.inputs[1].default_value = True
    # Position
    set_position_1.inputs[2].default_value = (0.0, 0.0, 0.0)

    # node Combine XYZ
    combine_xyz_2 = spinner_sim_group.nodes.new("ShaderNodeCombineXYZ")
    combine_xyz_2.name = "Combine XYZ"
    combine_xyz_2.inputs[0].hide = True
    combine_xyz_2.inputs[2].hide = True
    # X
    combine_xyz_2.inputs[0].default_value = 0.0
    # Z
    combine_xyz_2.inputs[2].default_value = 0.0

    # node Group Input.001
    group_input_001_2 = spinner_sim_group.nodes.new("NodeGroupInput")
    group_input_001_2.name = "Group Input.001"
    group_input_001_2.outputs[0].hide = True
    group_input_001_2.outputs[1].hide = True
    group_input_001_2.outputs[2].hide = True
    group_input_001_2.outputs[4].hide = True

    # node Group Input.002
    group_input_002_2 = spinner_sim_group.nodes.new("NodeGroupInput")
    group_input_002_2.name = "Group Input.002"
    group_input_002_2.outputs[0].hide = True
    group_input_002_2.outputs[1].hide = True
    group_input_002_2.outputs[3].hide = True
    group_input_002_2.outputs[4].hide = True

    # node Group Input.003
    group_input_003 = spinner_sim_group.nodes.new("NodeGroupInput")
    group_input_003.name = "Group Input.003"
    group_input_003.outputs[0].hide = True
    group_input_003.outputs[2].hide = True
    group_input_003.outputs[3].hide = True
    group_input_003.outputs[4].hide = True

    # Set locations
    group_output_2.location = (510.50048828125, 94.5011215209961)
    group_input_2.location = (-600.0, 100.0)
    realize_instances_2.location = (-440.0, 100.0)
    delete_geometry_2.location = (-280.0, 100.0)
    named_attribute_2.location = (-280.0, -100.0)
    boolean_math_2.location = (-280.0, -60.0)
    delete_geometry_001_2.location = (-120.0, 100.0)
    named_attribute_001_2.location = (-120.0, -60.0)
    set_material_2.location = (360.0, 100.0)
    instance_on_points_2.location = (40.0, 100.0)
    mesh_circle_1.location = (40.0, -20.0)
    set_position_1.location = (200.0, 100.0)
    combine_xyz_2.location = (200.0, 0.0)
    group_input_001_2.location = (200.0, -80.0)
    group_input_002_2.location = (360.0, 0.0)
    group_input_003.location = (40.0, -160.0)

    # Set dimensions
    group_output_2.width, group_output_2.height = 140.0, 100.0
    group_input_2.width, group_input_2.height = 140.0, 100.0
    realize_instances_2.width, realize_instances_2.height = 140.0, 100.0
    delete_geometry_2.width, delete_geometry_2.height = 140.0, 100.0
    named_attribute_2.width, named_attribute_2.height = 140.0, 100.0
    boolean_math_2.width, boolean_math_2.height = 140.0, 100.0
    delete_geometry_001_2.width, delete_geometry_001_2.height = 140.0, 100.0
    named_attribute_001_2.width, named_attribute_001_2.height = 140.0, 100.0
    set_material_2.width, set_material_2.height = 140.0, 100.0
    instance_on_points_2.width, instance_on_points_2.height = 140.0, 100.0
    mesh_circle_1.width, mesh_circle_1.height = 140.0, 100.0
    set_position_1.width, set_position_1.height = 140.0, 100.0
    combine_xyz_2.width, combine_xyz_2.height = 140.0, 100.0
    group_input_001_2.width, group_input_001_2.height = 140.0, 100.0
    group_input_002_2.width, group_input_002_2.height = 140.0, 100.0
    group_input_003.width, group_input_003.height = 140.0, 100.0

    # initialize spinner_sim_group links
    # boolean_math_2.Boolean -> delete_geometry_2.Selection
    spinner_sim_group.links.new(boolean_math_2.outputs[0], delete_geometry_2.inputs[1])
    # named_attribute_2.Attribute -> boolean_math_2.Boolean
    spinner_sim_group.links.new(named_attribute_2.outputs[0], boolean_math_2.inputs[0])
    # group_input_2.Geometry -> realize_instances_2.Geometry
    spinner_sim_group.links.new(group_input_2.outputs[0], realize_instances_2.inputs[0])
    # realize_instances_2.Geometry -> delete_geometry_2.Geometry
    spinner_sim_group.links.new(realize_instances_2.outputs[0], delete_geometry_2.inputs[0])
    # set_material_2.Geometry -> group_output_2.Geometry
    spinner_sim_group.links.new(set_material_2.outputs[0], group_output_2.inputs[0])
    # delete_geometry_2.Geometry -> delete_geometry_001_2.Geometry
    spinner_sim_group.links.new(delete_geometry_2.outputs[0], delete_geometry_001_2.inputs[0])
    # named_attribute_001_2.Attribute -> delete_geometry_001_2.Selection
    spinner_sim_group.links.new(named_attribute_001_2.outputs[0], delete_geometry_001_2.inputs[1])
    # set_position_1.Geometry -> set_material_2.Geometry
    spinner_sim_group.links.new(set_position_1.outputs[0], set_material_2.inputs[0])
    # delete_geometry_001_2.Geometry -> instance_on_points_2.Points
    spinner_sim_group.links.new(delete_geometry_001_2.outputs[0], instance_on_points_2.inputs[0])
    # mesh_circle_1.Mesh -> instance_on_points_2.Instance
    spinner_sim_group.links.new(mesh_circle_1.outputs[0], instance_on_points_2.inputs[2])
    # instance_on_points_2.Instances -> set_position_1.Geometry
    spinner_sim_group.links.new(instance_on_points_2.outputs[0], set_position_1.inputs[0])
    # combine_xyz_2.Vector -> set_position_1.Offset
    spinner_sim_group.links.new(combine_xyz_2.outputs[0], set_position_1.inputs[3])
    # group_input_001_2.Y Offset -> combine_xyz_2.Y
    spinner_sim_group.links.new(group_input_001_2.outputs[3], combine_xyz_2.inputs[1])
    # group_input_002_2.Spinner Material -> set_material_2.Material
    spinner_sim_group.links.new(group_input_002_2.outputs[2], set_material_2.inputs[2])
    # group_input_003.Scale -> mesh_circle_1.Radius
    spinner_sim_group.links.new(group_input_003.outputs[1], mesh_circle_1.inputs[1])
    return spinner_sim_group




# initialize cursor_group node group
def cursor_group_node_group():
    cursor_group = bpy.data.node_groups.new(type='GeometryNodeTree', name="Cursor Group")

    cursor_group.color_tag = 'NONE'
    cursor_group.description = ""

    # cursor_group interface
    # Socket Geometry
    geometry_socket_5 = cursor_group.interface.new_socket(name="Geometry", in_out='OUTPUT',
                                                          socket_type='NodeSocketGeometry')
    geometry_socket_5.attribute_domain = 'POINT'

    # Socket Points
    points_socket = cursor_group.interface.new_socket(name="Points", in_out='INPUT', socket_type='NodeSocketGeometry')
    points_socket.attribute_domain = 'POINT'

    # Socket Radius
    radius_socket = cursor_group.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    radius_socket.default_value = 0.40000003576278687
    radius_socket.min_value = 0.0
    radius_socket.max_value = 3.4028234663852886e+38
    radius_socket.subtype = 'DISTANCE'
    radius_socket.attribute_domain = 'POINT'

    # Socket Cursor Material
    cursor_material_socket = cursor_group.interface.new_socket(name="Cursor Material", in_out='INPUT',
                                                               socket_type='NodeSocketMaterial')
    cursor_material_socket.attribute_domain = 'POINT'

    # Socket Y Offset
    y_offset_socket_2 = cursor_group.interface.new_socket(name="Y Offset", in_out='INPUT',
                                                          socket_type='NodeSocketFloat')
    y_offset_socket_2.default_value = 0.0
    y_offset_socket_2.min_value = -10000.0
    y_offset_socket_2.max_value = 10000.0
    y_offset_socket_2.subtype = 'NONE'
    y_offset_socket_2.attribute_domain = 'POINT'

    # initialize cursor_group nodes
    # node Group Output
    group_output_3 = cursor_group.nodes.new("NodeGroupOutput")
    group_output_3.name = "Group Output"
    group_output_3.is_active_output = True

    # node Group Input
    group_input_3 = cursor_group.nodes.new("NodeGroupInput")
    group_input_3.name = "Group Input"

    # node Instance on Points
    instance_on_points_3 = cursor_group.nodes.new("GeometryNodeInstanceOnPoints")
    instance_on_points_3.name = "Instance on Points"
    instance_on_points_3.inputs[1].hide = True
    instance_on_points_3.inputs[3].hide = True
    instance_on_points_3.inputs[4].hide = True
    instance_on_points_3.inputs[5].hide = True
    instance_on_points_3.inputs[6].hide = True
    # Selection
    instance_on_points_3.inputs[1].default_value = True
    # Pick Instance
    instance_on_points_3.inputs[3].default_value = False
    # Instance Index
    instance_on_points_3.inputs[4].default_value = 0
    # Rotation
    instance_on_points_3.inputs[5].default_value = (1.5707963705062866, 0.0, 0.0)
    # Scale
    instance_on_points_3.inputs[6].default_value = (1.0, 1.0, 1.0)

    # node Mesh Circle
    mesh_circle_2 = cursor_group.nodes.new("GeometryNodeMeshCircle")
    mesh_circle_2.name = "Mesh Circle"
    mesh_circle_2.fill_type = 'NGON'
    # Vertices
    mesh_circle_2.inputs[0].default_value = 32

    # node Set Material
    set_material_3 = cursor_group.nodes.new("GeometryNodeSetMaterial")
    set_material_3.name = "Set Material"
    set_material_3.inputs[1].hide = True
    # Selection
    set_material_3.inputs[1].default_value = True

    # node Set Position
    set_position_2 = cursor_group.nodes.new("GeometryNodeSetPosition")
    set_position_2.name = "Set Position"
    set_position_2.inputs[1].hide = True
    set_position_2.inputs[2].hide = True
    # Selection
    set_position_2.inputs[1].default_value = True
    # Position
    set_position_2.inputs[2].default_value = (0.0, 0.0, 0.0)

    # node Combine XYZ
    combine_xyz_3 = cursor_group.nodes.new("ShaderNodeCombineXYZ")
    combine_xyz_3.name = "Combine XYZ"
    combine_xyz_3.inputs[0].hide = True
    combine_xyz_3.inputs[2].hide = True
    # X
    combine_xyz_3.inputs[0].default_value = 0.0
    # Z
    combine_xyz_3.inputs[2].default_value = 0.0

    # node Group Input.001
    group_input_001_3 = cursor_group.nodes.new("NodeGroupInput")
    group_input_001_3.name = "Group Input.001"
    group_input_001_3.outputs[0].hide = True
    group_input_001_3.outputs[1].hide = True
    group_input_001_3.outputs[2].hide = True
    group_input_001_3.outputs[4].hide = True

    # node Group Input.002
    group_input_002_3 = cursor_group.nodes.new("NodeGroupInput")
    group_input_002_3.name = "Group Input.002"
    group_input_002_3.outputs[0].hide = True
    group_input_002_3.outputs[1].hide = True
    group_input_002_3.outputs[3].hide = True
    group_input_002_3.outputs[4].hide = True

    # node Group Input.003
    group_input_003_1 = cursor_group.nodes.new("NodeGroupInput")
    group_input_003_1.name = "Group Input.003"
    group_input_003_1.outputs[0].hide = True
    group_input_003_1.outputs[2].hide = True
    group_input_003_1.outputs[3].hide = True
    group_input_003_1.outputs[4].hide = True

    # Set locations
    group_output_3.location = (480.0, -60.0)
    group_input_3.location = (-160.0, -60.0)
    instance_on_points_3.location = (0.0, -60.0)
    mesh_circle_2.location = (0.0, -160.0)
    set_material_3.location = (320.0, -60.0)
    set_position_2.location = (160.0, -60.0)
    combine_xyz_3.location = (160.0, -160.0)
    group_input_001_3.location = (160.0, -240.0)
    group_input_002_3.location = (320.0, -160.0)
    group_input_003_1.location = (0.0, -300.0)

    # Set dimensions
    group_output_3.width, group_output_3.height = 140.0, 100.0
    group_input_3.width, group_input_3.height = 140.0, 100.0
    instance_on_points_3.width, instance_on_points_3.height = 140.0, 100.0
    mesh_circle_2.width, mesh_circle_2.height = 140.0, 100.0
    set_material_3.width, set_material_3.height = 140.0, 100.0
    set_position_2.width, set_position_2.height = 140.0, 100.0
    combine_xyz_3.width, combine_xyz_3.height = 140.0, 100.0
    group_input_001_3.width, group_input_001_3.height = 140.0, 100.0
    group_input_002_3.width, group_input_002_3.height = 140.0, 100.0
    group_input_003_1.width, group_input_003_1.height = 140.0, 100.0

    # initialize cursor_group links
    # mesh_circle_2.Mesh -> instance_on_points_3.Instance
    cursor_group.links.new(mesh_circle_2.outputs[0], instance_on_points_3.inputs[2])
    # set_position_2.Geometry -> set_material_3.Geometry
    cursor_group.links.new(set_position_2.outputs[0], set_material_3.inputs[0])
    # group_input_3.Points -> instance_on_points_3.Points
    cursor_group.links.new(group_input_3.outputs[0], instance_on_points_3.inputs[0])
    # set_material_3.Geometry -> group_output_3.Geometry
    cursor_group.links.new(set_material_3.outputs[0], group_output_3.inputs[0])
    # instance_on_points_3.Instances -> set_position_2.Geometry
    cursor_group.links.new(instance_on_points_3.outputs[0], set_position_2.inputs[0])
    # combine_xyz_3.Vector -> set_position_2.Offset
    cursor_group.links.new(combine_xyz_3.outputs[0], set_position_2.inputs[3])
    # group_input_001_3.Y Offset -> combine_xyz_3.Y
    cursor_group.links.new(group_input_001_3.outputs[3], combine_xyz_3.inputs[1])
    # group_input_002_3.Cursor Material -> set_material_3.Material
    cursor_group.links.new(group_input_002_3.outputs[2], set_material_3.inputs[2])
    # group_input_003_1.Radius -> mesh_circle_2.Radius
    cursor_group.links.new(group_input_003_1.outputs[1], mesh_circle_2.inputs[1])
    return cursor_group




# initialize gn_osu node group
def gn_osu_node_group():
    gn_osu = bpy.data.node_groups.new(type='GeometryNodeTree', name="GN_Osu")

    gn_osu.color_tag = 'NONE'
    gn_osu.description = ""

    gn_osu.is_modifier = True

    # gn_osu interface
    # Socket Geometry
    geometry_socket_6 = gn_osu.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    geometry_socket_6.attribute_domain = 'POINT'

    # Socket Geometry
    geometry_socket_7 = gn_osu.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    geometry_socket_7.attribute_domain = 'POINT'

    # Socket Cursor Collection
    cursor_collection_socket = gn_osu.interface.new_socket(name="Cursor Collection", in_out='INPUT',
                                                           socket_type='NodeSocketCollection')
    cursor_collection_socket.attribute_domain = 'POINT'

    # Socket Circles Collection
    circles_collection_socket = gn_osu.interface.new_socket(name="Circles Collection", in_out='INPUT',
                                                            socket_type='NodeSocketCollection')
    circles_collection_socket.attribute_domain = 'POINT'

    # Socket Sliders Collection
    sliders_collection_socket = gn_osu.interface.new_socket(name="Sliders Collection", in_out='INPUT',
                                                            socket_type='NodeSocketCollection')
    sliders_collection_socket.attribute_domain = 'POINT'

    # Socket Slider Balls Collection
    slider_balls_collection_socket = gn_osu.interface.new_socket(name="Slider Balls Collection", in_out='INPUT',
                                                                 socket_type='NodeSocketCollection')
    slider_balls_collection_socket.attribute_domain = 'POINT'

    # Socket SpinnersCollection
    spinnerscollection_socket = gn_osu.interface.new_socket(name="SpinnersCollection", in_out='INPUT',
                                                            socket_type='NodeSocketCollection')
    spinnerscollection_socket.attribute_domain = 'POINT'

    # Socket Cursor Material
    cursor_material_socket_1 = gn_osu.interface.new_socket(name="Cursor Material", in_out='INPUT',
                                                           socket_type='NodeSocketMaterial')
    cursor_material_socket_1.attribute_domain = 'POINT'

    # Socket Circle Material
    circle_material_socket_1 = gn_osu.interface.new_socket(name="Circle Material", in_out='INPUT',
                                                           socket_type='NodeSocketMaterial')
    circle_material_socket_1.attribute_domain = 'POINT'

    # Socket Slider Material
    slider_material_socket_1 = gn_osu.interface.new_socket(name="Slider Material", in_out='INPUT',
                                                           socket_type='NodeSocketMaterial')
    slider_material_socket_1.attribute_domain = 'POINT'

    # Socket Slider Balls Material
    slider_balls_material_socket_1 = gn_osu.interface.new_socket(name="Slider Balls Material", in_out='INPUT',
                                                                 socket_type='NodeSocketMaterial')
    slider_balls_material_socket_1.attribute_domain = 'POINT'

    # Socket Slider Headt/Tail Material
    slider_headt_tail_material_socket_1 = gn_osu.interface.new_socket(name="Slider Headt/Tail Material", in_out='INPUT',
                                                                      socket_type='NodeSocketMaterial')
    slider_headt_tail_material_socket_1.attribute_domain = 'POINT'

    # Socket Spinner Material
    spinner_material_socket_1 = gn_osu.interface.new_socket(name="Spinner Material", in_out='INPUT',
                                                            socket_type='NodeSocketMaterial')
    spinner_material_socket_1.attribute_domain = 'POINT'

    # initialize gn_osu nodes
    # node Group Input
    group_input_4 = gn_osu.nodes.new("NodeGroupInput")
    group_input_4.name = "Group Input"
    group_input_4.outputs[0].hide = True
    group_input_4.outputs[2].hide = True
    group_input_4.outputs[3].hide = True
    group_input_4.outputs[4].hide = True
    group_input_4.outputs[5].hide = True
    group_input_4.outputs[6].hide = True
    group_input_4.outputs[7].hide = True
    group_input_4.outputs[8].hide = True
    group_input_4.outputs[9].hide = True
    group_input_4.outputs[10].hide = True
    group_input_4.outputs[11].hide = True
    group_input_4.outputs[12].hide = True

    # node Group Output
    group_output_4 = gn_osu.nodes.new("NodeGroupOutput")
    group_output_4.name = "Group Output"
    group_output_4.is_active_output = True

    # node Collection Info
    collection_info_1 = gn_osu.nodes.new("GeometryNodeCollectionInfo")
    collection_info_1.name = "Collection Info"
    collection_info_1.transform_space = 'ORIGINAL'
    # Separate Children
    collection_info_1.inputs[1].default_value = False
    # Reset Children
    collection_info_1.inputs[2].default_value = False

    # node Group
    group = gn_osu.nodes.new("GeometryNodeGroup")
    group.name = "Group"
    group.node_tree = circle_sim_group_node_group()
    # Socket_4
    group.inputs[2].default_value = 0.009999999776482582

    # node Collection Info.001
    collection_info_001 = gn_osu.nodes.new("GeometryNodeCollectionInfo")
    collection_info_001.name = "Collection Info.001"
    collection_info_001.transform_space = 'ORIGINAL'
    # Separate Children
    collection_info_001.inputs[1].default_value = False
    # Reset Children
    collection_info_001.inputs[2].default_value = False

    # node Group.001
    group_001 = gn_osu.nodes.new("GeometryNodeGroup")
    group_001.name = "Group.001"
    group_001.node_tree = slider_sim_group_node_group()
    # Socket_4
    group_001.inputs[3].default_value = 0.029999999329447746
    # Socket_5
    group_001.inputs[4].default_value = 0.03999999910593033
    # Socket_6
    group_001.inputs[5].default_value = True
    # Socket_9
    group_001.inputs[8].default_value = 0.019999999552965164

    # node Join Geometry
    join_geometry = gn_osu.nodes.new("GeometryNodeJoinGeometry")
    join_geometry.name = "Join Geometry"

    # node Collection Info.002
    collection_info_002 = gn_osu.nodes.new("GeometryNodeCollectionInfo")
    collection_info_002.name = "Collection Info.002"
    collection_info_002.transform_space = 'ORIGINAL'
    # Separate Children
    collection_info_002.inputs[1].default_value = False
    # Reset Children
    collection_info_002.inputs[2].default_value = False

    # node Collection Info.003
    collection_info_003 = gn_osu.nodes.new("GeometryNodeCollectionInfo")
    collection_info_003.name = "Collection Info.003"
    collection_info_003.transform_space = 'ORIGINAL'
    # Separate Children
    collection_info_003.inputs[1].default_value = False
    # Reset Children
    collection_info_003.inputs[2].default_value = False

    # node Group.002
    group_002 = gn_osu.nodes.new("GeometryNodeGroup")
    group_002.name = "Group.002"
    group_002.node_tree = spinner_sim_group_node_group()
    # Socket_2
    group_002.inputs[1].default_value = 5.0
    # Socket_4
    group_002.inputs[3].default_value = 0.0

    # node Group.003
    group_003 = gn_osu.nodes.new("GeometryNodeGroup")
    group_003.name = "Group.003"
    group_003.node_tree = cursor_group_node_group()
    # Socket_2
    group_003.inputs[1].default_value = 0.30000001192092896
    # Socket_4
    group_003.inputs[3].default_value = -0.009999999776482582

    # node Group Input.001
    group_input_001_4 = gn_osu.nodes.new("NodeGroupInput")
    group_input_001_4.name = "Group Input.001"
    group_input_001_4.outputs[0].hide = True
    group_input_001_4.outputs[1].hide = True
    group_input_001_4.outputs[2].hide = True
    group_input_001_4.outputs[3].hide = True
    group_input_001_4.outputs[4].hide = True
    group_input_001_4.outputs[6].hide = True
    group_input_001_4.outputs[7].hide = True
    group_input_001_4.outputs[8].hide = True
    group_input_001_4.outputs[9].hide = True
    group_input_001_4.outputs[10].hide = True
    group_input_001_4.outputs[11].hide = True
    group_input_001_4.outputs[12].hide = True

    # node Group Input.002
    group_input_002_4 = gn_osu.nodes.new("NodeGroupInput")
    group_input_002_4.name = "Group Input.002"
    group_input_002_4.outputs[0].hide = True
    group_input_002_4.outputs[1].hide = True
    group_input_002_4.outputs[2].hide = True
    group_input_002_4.outputs[3].hide = True
    group_input_002_4.outputs[5].hide = True
    group_input_002_4.outputs[6].hide = True
    group_input_002_4.outputs[7].hide = True
    group_input_002_4.outputs[8].hide = True
    group_input_002_4.outputs[9].hide = True
    group_input_002_4.outputs[10].hide = True
    group_input_002_4.outputs[11].hide = True
    group_input_002_4.outputs[12].hide = True

    # node Group Input.003
    group_input_003_2 = gn_osu.nodes.new("NodeGroupInput")
    group_input_003_2.name = "Group Input.003"
    group_input_003_2.outputs[0].hide = True
    group_input_003_2.outputs[1].hide = True
    group_input_003_2.outputs[2].hide = True
    group_input_003_2.outputs[4].hide = True
    group_input_003_2.outputs[5].hide = True
    group_input_003_2.outputs[6].hide = True
    group_input_003_2.outputs[7].hide = True
    group_input_003_2.outputs[8].hide = True
    group_input_003_2.outputs[9].hide = True
    group_input_003_2.outputs[10].hide = True
    group_input_003_2.outputs[11].hide = True
    group_input_003_2.outputs[12].hide = True

    # node Group Input.004
    group_input_004_1 = gn_osu.nodes.new("NodeGroupInput")
    group_input_004_1.name = "Group Input.004"
    group_input_004_1.outputs[0].hide = True
    group_input_004_1.outputs[1].hide = True
    group_input_004_1.outputs[3].hide = True
    group_input_004_1.outputs[4].hide = True
    group_input_004_1.outputs[5].hide = True
    group_input_004_1.outputs[6].hide = True
    group_input_004_1.outputs[7].hide = True
    group_input_004_1.outputs[8].hide = True
    group_input_004_1.outputs[9].hide = True
    group_input_004_1.outputs[10].hide = True
    group_input_004_1.outputs[11].hide = True
    group_input_004_1.outputs[12].hide = True

    # node Join Geometry.001
    join_geometry_001 = gn_osu.nodes.new("GeometryNodeJoinGeometry")
    join_geometry_001.name = "Join Geometry.001"

    # node Join Geometry.002
    join_geometry_002_1 = gn_osu.nodes.new("GeometryNodeJoinGeometry")
    join_geometry_002_1.name = "Join Geometry.002"

    # node Reroute
    reroute_2 = gn_osu.nodes.new("NodeReroute")
    reroute_2.name = "Reroute"
    # node Reroute.001
    reroute_001_2 = gn_osu.nodes.new("NodeReroute")
    reroute_001_2.name = "Reroute.001"
    # node Reroute.002
    reroute_002_2 = gn_osu.nodes.new("NodeReroute")
    reroute_002_2.name = "Reroute.002"
    # node Reroute.003
    reroute_003_2 = gn_osu.nodes.new("NodeReroute")
    reroute_003_2.name = "Reroute.003"
    # node Group Input.005
    group_input_005_1 = gn_osu.nodes.new("NodeGroupInput")
    group_input_005_1.name = "Group Input.005"
    group_input_005_1.outputs[0].hide = True
    group_input_005_1.outputs[1].hide = True
    group_input_005_1.outputs[2].hide = True
    group_input_005_1.outputs[3].hide = True
    group_input_005_1.outputs[4].hide = True
    group_input_005_1.outputs[5].hide = True
    group_input_005_1.outputs[6].hide = True
    group_input_005_1.outputs[8].hide = True
    group_input_005_1.outputs[9].hide = True
    group_input_005_1.outputs[10].hide = True
    group_input_005_1.outputs[11].hide = True
    group_input_005_1.outputs[12].hide = True

    # node Group Input.006
    group_input_006_1 = gn_osu.nodes.new("NodeGroupInput")
    group_input_006_1.name = "Group Input.006"
    group_input_006_1.outputs[0].hide = True
    group_input_006_1.outputs[1].hide = True
    group_input_006_1.outputs[2].hide = True
    group_input_006_1.outputs[3].hide = True
    group_input_006_1.outputs[4].hide = True
    group_input_006_1.outputs[5].hide = True
    group_input_006_1.outputs[7].hide = True
    group_input_006_1.outputs[8].hide = True
    group_input_006_1.outputs[9].hide = True
    group_input_006_1.outputs[10].hide = True
    group_input_006_1.outputs[11].hide = True
    group_input_006_1.outputs[12].hide = True

    # node Group Input.007
    group_input_007_1 = gn_osu.nodes.new("NodeGroupInput")
    group_input_007_1.name = "Group Input.007"
    group_input_007_1.outputs[0].hide = True
    group_input_007_1.outputs[1].hide = True
    group_input_007_1.outputs[2].hide = True
    group_input_007_1.outputs[3].hide = True
    group_input_007_1.outputs[4].hide = True
    group_input_007_1.outputs[5].hide = True
    group_input_007_1.outputs[6].hide = True
    group_input_007_1.outputs[7].hide = True
    group_input_007_1.outputs[8].hide = True
    group_input_007_1.outputs[9].hide = True
    group_input_007_1.outputs[10].hide = True
    group_input_007_1.outputs[12].hide = True

    # node Group Input.008
    group_input_008_1 = gn_osu.nodes.new("NodeGroupInput")
    group_input_008_1.name = "Group Input.008"
    group_input_008_1.outputs[0].hide = True
    group_input_008_1.outputs[1].hide = True
    group_input_008_1.outputs[2].hide = True
    group_input_008_1.outputs[3].hide = True
    group_input_008_1.outputs[4].hide = True
    group_input_008_1.outputs[5].hide = True
    group_input_008_1.outputs[6].hide = True
    group_input_008_1.outputs[7].hide = True
    group_input_008_1.outputs[8].hide = True
    group_input_008_1.outputs[9].hide = True
    group_input_008_1.outputs[11].hide = True
    group_input_008_1.outputs[12].hide = True

    # node Group Input.009
    group_input_009_1 = gn_osu.nodes.new("NodeGroupInput")
    group_input_009_1.name = "Group Input.009"
    group_input_009_1.outputs[0].hide = True
    group_input_009_1.outputs[1].hide = True
    group_input_009_1.outputs[2].hide = True
    group_input_009_1.outputs[3].hide = True
    group_input_009_1.outputs[4].hide = True
    group_input_009_1.outputs[5].hide = True
    group_input_009_1.outputs[6].hide = True
    group_input_009_1.outputs[7].hide = True
    group_input_009_1.outputs[8].hide = True
    group_input_009_1.outputs[10].hide = True
    group_input_009_1.outputs[11].hide = True
    group_input_009_1.outputs[12].hide = True

    # node Group Input.010
    group_input_010_1 = gn_osu.nodes.new("NodeGroupInput")
    group_input_010_1.name = "Group Input.010"
    group_input_010_1.outputs[0].hide = True
    group_input_010_1.outputs[1].hide = True
    group_input_010_1.outputs[2].hide = True
    group_input_010_1.outputs[3].hide = True
    group_input_010_1.outputs[4].hide = True
    group_input_010_1.outputs[5].hide = True
    group_input_010_1.outputs[6].hide = True
    group_input_010_1.outputs[7].hide = True
    group_input_010_1.outputs[9].hide = True
    group_input_010_1.outputs[10].hide = True
    group_input_010_1.outputs[11].hide = True
    group_input_010_1.outputs[12].hide = True

    # Set locations
    group_input_4.location = (1480.0, 0.0)
    group_output_4.location = (2180.0, 120.0)
    collection_info_1.location = (40.0, 60.0)
    group.location = (200.0, 60.0)
    collection_info_001.location = (200.0, 240.0)
    group_001.location = (440.0, 0.0)
    join_geometry.location = (680.0, 80.0)
    collection_info_002.location = (1640.0, 0.0)
    collection_info_003.location = (1000.0, 0.0)
    group_002.location = (1160.0, 0.0)
    group_003.location = (1800.0, 0.0)
    group_input_001_4.location = (840.0, 0.0)
    group_input_002_4.location = (280.0, -180.0)
    group_input_003_2.location = (40.0, 240.0)
    group_input_004_1.location = (-120.0, 60.0)
    join_geometry_001.location = (1320.0, 80.0)
    join_geometry_002_1.location = (2000.0, 80.0)
    reroute_2.location = (360.0, -100.0)
    reroute_001_2.location = (420.0, 200.0)
    reroute_002_2.location = (420.0, -80.0)
    reroute_003_2.location = (360.0, 0.0)
    group_input_005_1.location = (200.0, -120.0)
    group_input_006_1.location = (1804.6112060546875, -173.00930786132812)
    group_input_007_1.location = (1152.1962890625, -170.53025817871094)
    group_input_008_1.location = (440.0, -420.0)
    group_input_009_1.location = (440.0, -360.0)
    group_input_010_1.location = (440.0, -300.0)

    # Set dimensions
    group_input_4.width, group_input_4.height = 140.0, 100.0
    group_output_4.width, group_output_4.height = 140.0, 100.0
    collection_info_1.width, collection_info_1.height = 140.0, 100.0
    group.width, group.height = 140.0, 100.0
    collection_info_001.width, collection_info_001.height = 140.0, 100.0
    group_001.width, group_001.height = 213.9149169921875, 100.0
    join_geometry.width, join_geometry.height = 140.0, 100.0
    collection_info_002.width, collection_info_002.height = 140.0, 100.0
    collection_info_003.width, collection_info_003.height = 140.0, 100.0
    group_002.width, group_002.height = 140.0, 100.0
    group_003.width, group_003.height = 181.4385986328125, 100.0
    group_input_001_4.width, group_input_001_4.height = 140.0, 100.0
    group_input_002_4.width, group_input_002_4.height = 140.0, 100.0
    group_input_003_2.width, group_input_003_2.height = 140.0, 100.0
    group_input_004_1.width, group_input_004_1.height = 140.0, 100.0
    join_geometry_001.width, join_geometry_001.height = 140.0, 100.0
    join_geometry_002_1.width, join_geometry_002_1.height = 140.0, 100.0
    reroute_2.width, reroute_2.height = 16.0, 100.0
    reroute_001_2.width, reroute_001_2.height = 16.0, 100.0
    reroute_002_2.width, reroute_002_2.height = 16.0, 100.0
    reroute_003_2.width, reroute_003_2.height = 16.0, 100.0
    group_input_005_1.width, group_input_005_1.height = 140.0, 100.0
    group_input_006_1.width, group_input_006_1.height = 140.0, 100.0
    group_input_007_1.width, group_input_007_1.height = 140.0, 100.0
    group_input_008_1.width, group_input_008_1.height = 140.0, 100.0
    group_input_009_1.width, group_input_009_1.height = 140.0, 100.0
    group_input_010_1.width, group_input_010_1.height = 140.0, 100.0

    # initialize gn_osu links
    # collection_info_1.Instances -> group.Geometry
    gn_osu.links.new(collection_info_1.outputs[0], group.inputs[0])
    # reroute_002_2.Output -> group_001.Geometry
    gn_osu.links.new(reroute_002_2.outputs[0], group_001.inputs[0])
    # join_geometry_002_1.Geometry -> group_output_4.Geometry
    gn_osu.links.new(join_geometry_002_1.outputs[0], group_output_4.inputs[0])
    # group_001.Geometry -> join_geometry.Geometry
    gn_osu.links.new(group_001.outputs[0], join_geometry.inputs[0])
    # collection_info_003.Instances -> group_002.Geometry
    gn_osu.links.new(collection_info_003.outputs[0], group_002.inputs[0])
    # reroute_2.Output -> group_001.Circle Mesh
    gn_osu.links.new(reroute_2.outputs[0], group_001.inputs[1])
    # collection_info_002.Instances -> group_003.Points
    gn_osu.links.new(collection_info_002.outputs[0], group_003.inputs[0])
    # group_input_4.Cursor Collection -> collection_info_002.Collection
    gn_osu.links.new(group_input_4.outputs[1], collection_info_002.inputs[0])
    # group_input_001_4.SpinnersCollection -> collection_info_003.Collection
    gn_osu.links.new(group_input_001_4.outputs[5], collection_info_003.inputs[0])
    # group_input_002_4.Slider Balls Collection -> group_001.Slider Balls
    gn_osu.links.new(group_input_002_4.outputs[4], group_001.inputs[6])
    # group_input_003_2.Sliders Collection -> collection_info_001.Collection
    gn_osu.links.new(group_input_003_2.outputs[3], collection_info_001.inputs[0])
    # group_input_004_1.Circles Collection -> collection_info_1.Collection
    gn_osu.links.new(group_input_004_1.outputs[2], collection_info_1.inputs[0])
    # group_002.Geometry -> join_geometry_001.Geometry
    gn_osu.links.new(group_002.outputs[0], join_geometry_001.inputs[0])
    # group_003.Geometry -> join_geometry_002_1.Geometry
    gn_osu.links.new(group_003.outputs[0], join_geometry_002_1.inputs[0])
    # reroute_003_2.Output -> reroute_2.Input
    gn_osu.links.new(reroute_003_2.outputs[0], reroute_2.inputs[0])
    # collection_info_001.Instances -> reroute_001_2.Input
    gn_osu.links.new(collection_info_001.outputs[0], reroute_001_2.inputs[0])
    # reroute_001_2.Output -> reroute_002_2.Input
    gn_osu.links.new(reroute_001_2.outputs[0], reroute_002_2.inputs[0])
    # group.Circle Mesh -> reroute_003_2.Input
    gn_osu.links.new(group.outputs[1], reroute_003_2.inputs[0])
    # group_input_005_1.Circle Material -> group.Circle Material
    gn_osu.links.new(group_input_005_1.outputs[7], group.inputs[1])
    # group_input_006_1.Cursor Material -> group_003.Cursor Material
    gn_osu.links.new(group_input_006_1.outputs[6], group_003.inputs[2])
    # group_input_007_1.Spinner Material -> group_002.Spinner Material
    gn_osu.links.new(group_input_007_1.outputs[11], group_002.inputs[2])
    # group_input_008_1.Slider Headt/Tail Material -> group_001.Slider Headt/Tail Material
    gn_osu.links.new(group_input_008_1.outputs[10], group_001.inputs[9])
    # group_input_009_1.Slider Balls Material -> group_001.Slider Balls Material
    gn_osu.links.new(group_input_009_1.outputs[9], group_001.inputs[7])
    # group_input_010_1.Slider Material -> group_001.Slider Material
    gn_osu.links.new(group_input_010_1.outputs[8], group_001.inputs[2])
    # group.Circles -> join_geometry.Geometry
    gn_osu.links.new(group.outputs[0], join_geometry.inputs[0])
    # join_geometry.Geometry -> join_geometry_001.Geometry
    gn_osu.links.new(join_geometry.outputs[0], join_geometry_001.inputs[0])
    # join_geometry_001.Geometry -> join_geometry_002_1.Geometry
    gn_osu.links.new(join_geometry_001.outputs[0], join_geometry_002_1.inputs[0])
    return gn_osu



