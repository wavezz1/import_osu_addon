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
    math.inputs[1].default_value = 1.0499999523162842
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

    # node Reroute
    reroute = slider_balls.nodes.new("NodeReroute")
    reroute.name = "Reroute"
    # node Mix Shader
    mix_shader = slider_balls.nodes.new("ShaderNodeMixShader")
    mix_shader.name = "Mix Shader"

    # node Transparent BSDF
    transparent_bsdf = slider_balls.nodes.new("ShaderNodeBsdfTransparent")
    transparent_bsdf.name = "Transparent BSDF"
    # Color
    transparent_bsdf.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)

    # Set locations
    material_output.location = (700.0, 300.0)
    mapping.location = (-260.0, 300.0)
    texture_coordinate.location = (-420.0, 300.0)
    vector_math.location = (-100.0, 300.0)
    math.location = (60.0, 300.0)
    emission.location = (380.0, 300.0)
    mix.location = (220.0, 300.0)
    reroute.location = (120.0, 200.0)
    mix_shader.location = (540.0, 300.0)
    transparent_bsdf.location = (540.0, 400.0)

    # Set dimensions
    material_output.width, material_output.height = 140.0, 100.0
    mapping.width, mapping.height = 140.0, 100.0
    texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
    vector_math.width, vector_math.height = 140.0, 100.0
    math.width, math.height = 140.0, 100.0
    emission.width, emission.height = 140.0, 100.0
    mix.width, mix.height = 140.0, 100.0
    reroute.width, reroute.height = 16.0, 100.0
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
    # vector_math.Value -> reroute.Input
    slider_balls.links.new(vector_math.outputs[1], reroute.inputs[0])
    # math.Value -> mix.Factor
    slider_balls.links.new(math.outputs[0], mix.inputs[0])
    # emission.Emission -> mix_shader.Shader
    slider_balls.links.new(emission.outputs[0], mix_shader.inputs[2])
    # transparent_bsdf.BSDF -> mix_shader.Shader
    slider_balls.links.new(transparent_bsdf.outputs[0], mix_shader.inputs[1])
    # math.Value -> mix_shader.Fac
    slider_balls.links.new(math.outputs[0], mix_shader.inputs[0])
    # mix_shader.Shader -> material_output.Surface
    slider_balls.links.new(mix_shader.outputs[0], material_output.inputs[0])
    return slider_balls