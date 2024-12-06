import bpy, mathutils

# initialize Approach Circles node group
def approach_circles_node_group():
    mat = bpy.data.materials.new(name="Approach Circles")
    mat.use_nodes = True
    mat["osu_imported"] = True
    approach_circles = mat.node_tree
    # start with a clean node tree
    for node in approach_circles.nodes:
        approach_circles.nodes.remove(node)
    approach_circles.color_tag = 'NONE'
    approach_circles.description = ""

    # approach_circles interface

    # initialize approach_circles nodes
    # node Material Output
    material_output = approach_circles.nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"
    material_output.is_active_output = True
    material_output.target = 'ALL'
    # Displacement
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Thickness
    material_output.inputs[3].default_value = 0.0

    # node Mapping
    mapping = approach_circles.nodes.new("ShaderNodeMapping")
    mapping.name = "Mapping"
    mapping.vector_type = 'POINT'
    # Location
    mapping.inputs[1].default_value = (0.0, 0.0, 0.0)
    # Rotation
    mapping.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Scale
    mapping.inputs[3].default_value = (1.0, 1.0, 1.0)

    # node Texture Coordinate
    texture_coordinate = approach_circles.nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.from_instancer = False

    # node Vector Math
    vector_math = approach_circles.nodes.new("ShaderNodeVectorMath")
    vector_math.name = "Vector Math"
    vector_math.operation = 'DISTANCE'
    # Vector_001
    vector_math.inputs[1].default_value = (0.0, 0.0, 0.0)

    # node Emission
    emission = approach_circles.nodes.new("ShaderNodeEmission")
    emission.name = "Emission"
    # Strength
    emission.inputs[1].default_value = 1.0

    # node Mix
    mix = approach_circles.nodes.new("ShaderNodeMix")
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

    # node Mix Shader
    mix_shader = approach_circles.nodes.new("ShaderNodeMixShader")
    mix_shader.name = "Mix Shader"

    # node Transparent BSDF
    transparent_bsdf = approach_circles.nodes.new("ShaderNodeBsdfTransparent")
    transparent_bsdf.name = "Transparent BSDF"
    # Color
    transparent_bsdf.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)

    # node Math
    math = approach_circles.nodes.new("ShaderNodeMath")
    math.name = "Math"
    math.operation = 'COMPARE'
    math.use_clamp = False
    # Value_001
    math.inputs[1].default_value = 0.5
    # Value_002
    math.inputs[2].default_value = 0.5

    # Set locations
    material_output.location = (1480.0, 300.0)
    mapping.location = (520.0, 300.0)
    texture_coordinate.location = (360.0, 300.0)
    vector_math.location = (680.0, 300.0)
    emission.location = (1160.0, 300.0)
    mix.location = (1000.0, 300.0)
    mix_shader.location = (1320.0, 300.0)
    transparent_bsdf.location = (1320.0, 400.0)
    math.location = (840.0, 300.0)

    # Set dimensions
    material_output.width, material_output.height = 140.0, 100.0
    mapping.width, mapping.height = 140.0, 100.0
    texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
    vector_math.width, vector_math.height = 140.0, 100.0
    emission.width, emission.height = 140.0, 100.0
    mix.width, mix.height = 140.0, 100.0
    mix_shader.width, mix_shader.height = 140.0, 100.0
    transparent_bsdf.width, transparent_bsdf.height = 140.0, 100.0
    math.width, math.height = 140.0, 100.0

    # initialize approach_circles links
    # mapping.Vector -> vector_math.Vector
    approach_circles.links.new(mapping.outputs[0], vector_math.inputs[0])
    # texture_coordinate.Object -> mapping.Vector
    approach_circles.links.new(texture_coordinate.outputs[3], mapping.inputs[0])
    # mix.Result -> emission.Color
    approach_circles.links.new(mix.outputs[2], emission.inputs[0])
    # emission.Emission -> mix_shader.Shader
    approach_circles.links.new(emission.outputs[0], mix_shader.inputs[2])
    # transparent_bsdf.BSDF -> mix_shader.Shader
    approach_circles.links.new(transparent_bsdf.outputs[0], mix_shader.inputs[1])
    # math.Value -> mix.Factor
    approach_circles.links.new(math.outputs[0], mix.inputs[0])
    # math.Value -> mix_shader.Fac
    approach_circles.links.new(math.outputs[0], mix_shader.inputs[0])
    # vector_math.Value -> math.Value
    approach_circles.links.new(vector_math.outputs[1], math.inputs[0])
    # mix_shader.Shader -> material_output.Surface
    approach_circles.links.new(mix_shader.outputs[0], material_output.inputs[0])
    return approach_circles
