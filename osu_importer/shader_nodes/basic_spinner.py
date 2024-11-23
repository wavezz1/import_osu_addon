import bpy, mathutils


# initialize Spinner node group
def spinner_node_group():
    mat = bpy.data.materials.new(name="Spinner")
    mat.use_nodes = True
    mat["osu_imported"] = True
    spinner = mat.node_tree
    # start with a clean node tree
    for node in spinner.nodes:
        spinner.nodes.remove(node)
    spinner.color_tag = 'NONE'
    spinner.description = ""

    # spinner interface

    # initialize spinner nodes
    # node Material Output
    material_output = spinner.nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"
    material_output.is_active_output = True
    material_output.target = 'ALL'
    # Displacement
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Thickness
    material_output.inputs[3].default_value = 0.0

    # node Mapping
    mapping = spinner.nodes.new("ShaderNodeMapping")
    mapping.name = "Mapping"
    mapping.vector_type = 'POINT'
    # Location
    mapping.inputs[1].default_value = (0.0, 0.0, 0.0)
    # Rotation
    mapping.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Scale
    mapping.inputs[3].default_value = (1.0, 1.0, 1.0)

    # node Texture Coordinate
    texture_coordinate = spinner.nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.from_instancer = False

    # node Emission
    emission = spinner.nodes.new("ShaderNodeEmission")
    emission.name = "Emission"
    # Strength
    emission.inputs[1].default_value = 1.0

    # node Mix
    mix = spinner.nodes.new("ShaderNodeMix")
    mix.name = "Mix"
    mix.blend_type = 'MIX'
    mix.clamp_factor = True
    mix.clamp_result = False
    mix.data_type = 'RGBA'
    mix.factor_mode = 'UNIFORM'
    # A_Color
    mix.inputs[6].default_value = (0.0, 0.0, 0.0, 1.0)
    # B_Color
    mix.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)

    # node Vector Math
    vector_math = spinner.nodes.new("ShaderNodeVectorMath")
    vector_math.name = "Vector Math"
    vector_math.operation = 'DISTANCE'
    # Vector_001
    vector_math.inputs[1].default_value = (0.0, 0.0, 0.0)

    # node Math
    math = spinner.nodes.new("ShaderNodeMath")
    math.name = "Math"
    math.operation = 'COMPARE'
    math.use_clamp = False
    # Value_001
    math.inputs[1].default_value = 4.800000190734863
    # Value_002
    math.inputs[2].default_value = 0.20000001788139343

    # node Math.001
    math_001 = spinner.nodes.new("ShaderNodeMath")
    math_001.name = "Math.001"
    math_001.operation = 'COMPARE'
    math_001.use_clamp = False
    # Value_001
    math_001.inputs[1].default_value = 0.0
    # Value_002
    math_001.inputs[2].default_value = 0.20000000298023224

    # node Math.002
    math_002 = spinner.nodes.new("ShaderNodeMath")
    math_002.name = "Math.002"
    math_002.operation = 'ADD'
    math_002.use_clamp = False

    # Set locations
    material_output.location = (1460.0, 300.0)
    mapping.location = (500.0, 300.0)
    texture_coordinate.location = (340.0, 300.0)
    emission.location = (1300.0, 300.0)
    mix.location = (1140.0, 300.0)
    vector_math.location = (660.0, 300.0)
    math.location = (820.0, 300.0)
    math_001.location = (820.0, 100.0)
    math_002.location = (980.0, 300.0)

    # Set dimensions
    material_output.width, material_output.height = 140.0, 100.0
    mapping.width, mapping.height = 140.0, 100.0
    texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
    emission.width, emission.height = 140.0, 100.0
    mix.width, mix.height = 140.0, 100.0
    vector_math.width, vector_math.height = 140.0, 100.0
    math.width, math.height = 140.0, 100.0
    math_001.width, math_001.height = 140.0, 100.0
    math_002.width, math_002.height = 140.0, 100.0

    # initialize spinner links
    # texture_coordinate.Object -> mapping.Vector
    spinner.links.new(texture_coordinate.outputs[3], mapping.inputs[0])
    # mix.Result -> emission.Color
    spinner.links.new(mix.outputs[2], emission.inputs[0])
    # mapping.Vector -> vector_math.Vector
    spinner.links.new(mapping.outputs[0], vector_math.inputs[0])
    # vector_math.Value -> math.Value
    spinner.links.new(vector_math.outputs[1], math.inputs[0])
    # vector_math.Value -> math_001.Value
    spinner.links.new(vector_math.outputs[1], math_001.inputs[0])
    # math_001.Value -> math_002.Value
    spinner.links.new(math_001.outputs[0], math_002.inputs[1])
    # math.Value -> math_002.Value
    spinner.links.new(math.outputs[0], math_002.inputs[0])
    # math_002.Value -> mix.Factor
    spinner.links.new(math_002.outputs[0], mix.inputs[0])
    # emission.Emission -> material_output.Surface
    spinner.links.new(emission.outputs[0], material_output.inputs[0])
    return spinner