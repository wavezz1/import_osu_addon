import bpy, mathutils


# initialize Slider_Balls node group
def slider_balls_node_group():
    mat = bpy.data.materials.new(name="Slider_Balls")
    mat.use_nodes = True
    mat["osu_imported"] = True
    slider_balls = mat.node_tree
    # start with a clean node tree
    for node in slider_balls.nodes:
        slider_balls.nodes.remove(node)
    slider_balls.color_tag = 'NONE'
    slider_balls.description = ""

    # slider_balls interface

    # initialize slider_balls nodes
    # node Material Output
    material_output = slider_balls.nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"
    material_output.is_active_output = True
    material_output.target = 'ALL'
    # Displacement
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Thickness
    material_output.inputs[3].default_value = 0.0

    # node Mapping
    mapping = slider_balls.nodes.new("ShaderNodeMapping")
    mapping.name = "Mapping"
    mapping.vector_type = 'POINT'
    # Location
    mapping.inputs[1].default_value = (0.0, 0.0, 0.0)
    # Rotation
    mapping.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Scale
    mapping.inputs[3].default_value = (1.0, 1.0, 1.0)

    # node Texture Coordinate
    texture_coordinate = slider_balls.nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.from_instancer = False

    # node Vector Math
    vector_math = slider_balls.nodes.new("ShaderNodeVectorMath")
    vector_math.name = "Vector Math"
    vector_math.operation = 'DISTANCE'
    # Vector_001
    vector_math.inputs[1].default_value = (0.0, 0.0, 0.0)

    # node Math
    math = slider_balls.nodes.new("ShaderNodeMath")
    math.name = "Math"
    math.operation = 'COMPARE'
    math.use_clamp = False
    # Value_001
    math.inputs[1].default_value = 1.0
    # Value_002
    math.inputs[2].default_value = 0.5

    # node Emission
    emission = slider_balls.nodes.new("ShaderNodeEmission")
    emission.name = "Emission"
    # Strength
    emission.inputs[1].default_value = 1.0

    # node Mix
    mix = slider_balls.nodes.new("ShaderNodeMix")
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

    # node Math.001
    math_001 = slider_balls.nodes.new("ShaderNodeMath")
    math_001.name = "Math.001"
    math_001.hide = True
    math_001.operation = 'COMPARE'
    math_001.use_clamp = False
    # Value_001
    math_001.inputs[1].default_value = 0.0
    # Value_002
    math_001.inputs[2].default_value = 0.5

    # node Math.002
    math_002 = slider_balls.nodes.new("ShaderNodeMath")
    math_002.name = "Math.002"
    math_002.operation = 'SUBTRACT'
    math_002.use_clamp = False

    # node Math.003
    math_003 = slider_balls.nodes.new("ShaderNodeMath")
    math_003.name = "Math.003"
    math_003.operation = 'MULTIPLY'
    math_003.use_clamp = False

    # node Reroute
    reroute = slider_balls.nodes.new("NodeReroute")
    reroute.name = "Reroute"
    # node Map Range
    map_range = slider_balls.nodes.new("ShaderNodeMapRange")
    map_range.name = "Map Range"
    map_range.clamp = False
    map_range.data_type = 'FLOAT'
    map_range.interpolation_type = 'LINEAR'
    # From Min
    map_range.inputs[1].default_value = 0.0
    # From Max
    map_range.inputs[2].default_value = 1.0
    # To Min
    map_range.inputs[3].default_value = -1.3199998140335083
    # To Max
    map_range.inputs[4].default_value = 1.0

    # node Mix Shader
    mix_shader = slider_balls.nodes.new("ShaderNodeMixShader")
    mix_shader.name = "Mix Shader"

    # node Transparent BSDF
    transparent_bsdf = slider_balls.nodes.new("ShaderNodeBsdfTransparent")
    transparent_bsdf.name = "Transparent BSDF"
    # Color
    transparent_bsdf.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)

    # Set locations
    material_output.location = (1313.6466064453125, 319.01947021484375)
    mapping.location = (-260.0, 300.0)
    texture_coordinate.location = (-420.0, 300.0)
    vector_math.location = (-100.0, 300.0)
    math.location = (60.0, 300.0)
    emission.location = (860.0, 300.0)
    mix.location = (700.0, 300.0)
    math_001.location = (380.0, 140.0)
    math_002.location = (380.0, 300.0)
    math_003.location = (540.0, 300.0)
    reroute.location = (120.0, 200.0)
    map_range.location = (220.0, 300.0)
    mix_shader.location = (1020.0, 220.0)
    transparent_bsdf.location = (1020.0, 300.0)

    # Set dimensions
    material_output.width, material_output.height = 140.0, 100.0
    mapping.width, mapping.height = 140.0, 100.0
    texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
    vector_math.width, vector_math.height = 140.0, 100.0
    math.width, math.height = 140.0, 100.0
    emission.width, emission.height = 140.0, 100.0
    mix.width, mix.height = 140.0, 100.0
    math_001.width, math_001.height = 140.0, 100.0
    math_002.width, math_002.height = 140.0, 100.0
    math_003.width, math_003.height = 140.0, 100.0
    reroute.width, reroute.height = 16.0, 100.0
    map_range.width, map_range.height = 140.0, 100.0
    mix_shader.width, mix_shader.height = 140.0, 100.0
    transparent_bsdf.width, transparent_bsdf.height = 140.0, 100.0

    # initialize slider_balls links
    # mapping.Vector -> vector_math.Vector
    slider_balls.links.new(mapping.outputs[0], vector_math.inputs[0])
    # texture_coordinate.Object -> mapping.Vector
    slider_balls.links.new(texture_coordinate.outputs[3], mapping.inputs[0])
    # vector_math.Value -> math.Value
    slider_balls.links.new(vector_math.outputs[1], math.inputs[0])
    # mix.Result -> emission.Color
    slider_balls.links.new(mix.outputs[2], emission.inputs[0])
    # reroute.Output -> math_001.Value
    slider_balls.links.new(reroute.outputs[0], math_001.inputs[0])
    # math_001.Value -> math_002.Value
    slider_balls.links.new(math_001.outputs[0], math_002.inputs[1])
    # reroute.Output -> math_003.Value
    slider_balls.links.new(reroute.outputs[0], math_003.inputs[0])
    # math_002.Value -> math_003.Value
    slider_balls.links.new(math_002.outputs[0], math_003.inputs[1])
    # vector_math.Value -> reroute.Input
    slider_balls.links.new(vector_math.outputs[1], reroute.inputs[0])
    # math_003.Value -> mix.Factor
    slider_balls.links.new(math_003.outputs[0], mix.inputs[0])
    # vector_math.Value -> map_range.Value
    slider_balls.links.new(vector_math.outputs[1], map_range.inputs[0])
    # map_range.Result -> math_002.Value
    slider_balls.links.new(map_range.outputs[0], math_002.inputs[0])
    # emission.Emission -> mix_shader.Shader
    slider_balls.links.new(emission.outputs[0], mix_shader.inputs[2])
    # transparent_bsdf.BSDF -> mix_shader.Shader
    slider_balls.links.new(transparent_bsdf.outputs[0], mix_shader.inputs[1])
    # math.Value -> mix_shader.Fac
    slider_balls.links.new(math.outputs[0], mix_shader.inputs[0])
    # mix_shader.Shader -> material_output.Surface
    slider_balls.links.new(mix_shader.outputs[0], material_output.inputs[0])
    return slider_balls