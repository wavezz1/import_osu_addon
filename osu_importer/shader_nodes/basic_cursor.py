import bpy, mathutils

# initialize Cursor node group
def cursor_node_group():
    mat = bpy.data.materials.new(name="Cursor")
    mat.use_nodes = True
    mat["osu_imported"] = True
    cursor = mat.node_tree
    # start with a clean node tree
    for node in cursor.nodes:
        cursor.nodes.remove(node)
    cursor.color_tag = 'NONE'
    cursor.description = ""

    # cursor interface

    # initialize cursor nodes
    # node Material Output
    material_output = cursor.nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"
    material_output.is_active_output = True
    material_output.target = 'ALL'
    # Displacement
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Thickness
    material_output.inputs[3].default_value = 0.0

    # node Mapping
    mapping = cursor.nodes.new("ShaderNodeMapping")
    mapping.name = "Mapping"
    mapping.vector_type = 'POINT'
    # Location
    mapping.inputs[1].default_value = (0.0, 0.0, 0.0)
    # Rotation
    mapping.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Scale
    mapping.inputs[3].default_value = (1.0, 1.0, 1.0)

    # node Texture Coordinate
    texture_coordinate = cursor.nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.from_instancer = False

    # node Vector Math
    vector_math = cursor.nodes.new("ShaderNodeVectorMath")
    vector_math.name = "Vector Math"
    vector_math.operation = 'DISTANCE'
    # Vector_001
    vector_math.inputs[1].default_value = (0.0, 0.0, 0.0)

    # node Emission
    emission = cursor.nodes.new("ShaderNodeEmission")
    emission.name = "Emission"
    # Strength
    emission.inputs[1].default_value = 1.0

    # node Mix
    mix = cursor.nodes.new("ShaderNodeMix")
    mix.name = "Mix"
    mix.blend_type = 'MIX'
    mix.clamp_factor = True
    mix.clamp_result = False
    mix.data_type = 'RGBA'
    mix.factor_mode = 'UNIFORM'
    # A_Color
    mix.inputs[6].default_value = (1.0, 0.0, 0.001448678900487721, 1.0)
    # B_Color
    mix.inputs[7].default_value = (0.008570834994316101, 0.0, 0.0001307307102251798, 1.0)

    # node Map Range
    map_range = cursor.nodes.new("ShaderNodeMapRange")
    map_range.name = "Map Range"
    map_range.clamp = True
    map_range.data_type = 'FLOAT'
    map_range.interpolation_type = 'LINEAR'
    # From Min
    map_range.inputs[1].default_value = 0.0
    # From Max
    map_range.inputs[2].default_value = 1.0
    # To Min
    map_range.inputs[3].default_value = -0.19999998807907104
    # To Max
    map_range.inputs[4].default_value = 2.9499998092651367

    # Set locations
    material_output.location = (1020.0, 300.0)
    mapping.location = (220.0, 300.0)
    texture_coordinate.location = (60.0, 300.0)
    vector_math.location = (380.0, 300.0)
    emission.location = (860.0, 300.0)
    mix.location = (700.0, 300.0)
    map_range.location = (540.0, 300.0)

    # Set dimensions
    material_output.width, material_output.height = 140.0, 100.0
    mapping.width, mapping.height = 140.0, 100.0
    texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
    vector_math.width, vector_math.height = 140.0, 100.0
    emission.width, emission.height = 140.0, 100.0
    mix.width, mix.height = 140.0, 100.0
    map_range.width, map_range.height = 140.0, 100.0

    # initialize cursor links
    # mapping.Vector -> vector_math.Vector
    cursor.links.new(mapping.outputs[0], vector_math.inputs[0])
    # texture_coordinate.Object -> mapping.Vector
    cursor.links.new(texture_coordinate.outputs[3], mapping.inputs[0])
    # mix.Result -> emission.Color
    cursor.links.new(mix.outputs[2], emission.inputs[0])
    # map_range.Result -> mix.Factor
    cursor.links.new(map_range.outputs[0], mix.inputs[0])
    # vector_math.Value -> map_range.Value
    cursor.links.new(vector_math.outputs[1], map_range.inputs[0])
    # emission.Emission -> material_output.Surface
    cursor.links.new(emission.outputs[0], material_output.inputs[0])
    return cursor