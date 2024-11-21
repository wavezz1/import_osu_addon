import bpy, mathutils

mat = bpy.data.materials.new(name="Circles")
mat.use_nodes = True


# initialize Circles node group
def circles_node_group():
    circles = mat.node_tree
    # start with a clean node tree
    for node in circles.nodes:
        circles.nodes.remove(node)
    circles.color_tag = 'NONE'
    circles.description = ""

    # circles interface

    # initialize circles nodes
    # node Material Output
    material_output = circles.nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"
    material_output.is_active_output = True
    material_output.target = 'ALL'
    # Displacement
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Thickness
    material_output.inputs[3].default_value = 0.0

    # node Mapping
    mapping = circles.nodes.new("ShaderNodeMapping")
    mapping.name = "Mapping"
    mapping.vector_type = 'POINT'
    # Location
    mapping.inputs[1].default_value = (0.0, 0.0, 0.0)
    # Rotation
    mapping.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Scale
    mapping.inputs[3].default_value = (1.0, 1.0, 1.0)

    # node Texture Coordinate
    texture_coordinate = circles.nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.from_instancer = False

    # node Vector Math
    vector_math = circles.nodes.new("ShaderNodeVectorMath")
    vector_math.name = "Vector Math"
    vector_math.operation = 'DISTANCE'
    # Vector_001
    vector_math.inputs[1].default_value = (0.0, 0.0, 0.0)

    # node Math
    math = circles.nodes.new("ShaderNodeMath")
    math.name = "Math"
    math.operation = 'COMPARE'
    math.use_clamp = False
    # Value_001
    math.inputs[1].default_value = 5.960464477539063e-08
    # Value_002
    math.inputs[2].default_value = 0.5

    # node Emission
    emission = circles.nodes.new("ShaderNodeEmission")
    emission.name = "Emission"
    # Strength
    emission.inputs[1].default_value = 1.0

    # node Mix
    mix = circles.nodes.new("ShaderNodeMix")
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
    math_001 = circles.nodes.new("ShaderNodeMath")
    math_001.name = "Math.001"
    math_001.operation = 'COMPARE'
    math_001.use_clamp = False
    # Value_001
    math_001.inputs[1].default_value = 0.0
    # Value_002
    math_001.inputs[2].default_value = 0.5

    # node Math.002
    math_002 = circles.nodes.new("ShaderNodeMath")
    math_002.name = "Math.002"
    math_002.operation = 'SUBTRACT'
    math_002.use_clamp = False

    # node Color Ramp
    color_ramp = circles.nodes.new("ShaderNodeValToRGB")
    color_ramp.name = "Color Ramp"
    color_ramp.color_ramp.color_mode = 'RGB'
    color_ramp.color_ramp.hue_interpolation = 'NEAR'
    color_ramp.color_ramp.interpolation = 'LINEAR'

    # initialize color ramp elements
    color_ramp.color_ramp.elements.remove(color_ramp.color_ramp.elements[0])
    color_ramp_cre_0 = color_ramp.color_ramp.elements[0]
    color_ramp_cre_0.position = 0.4999999701976776
    color_ramp_cre_0.alpha = 1.0
    color_ramp_cre_0.color = (0.0, 0.0, 0.0, 1.0)

    color_ramp_cre_1 = color_ramp.color_ramp.elements.new(1.0)
    color_ramp_cre_1.alpha = 1.0
    color_ramp_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    # node Math.003
    math_003 = circles.nodes.new("ShaderNodeMath")
    math_003.name = "Math.003"
    math_003.operation = 'MULTIPLY'
    math_003.use_clamp = False

    # node Reroute
    reroute = circles.nodes.new("NodeReroute")
    reroute.name = "Reroute"

    # Set locations
    material_output.location = (1020.0, 300.0)
    mapping.location = (-360.0, 300.0)
    texture_coordinate.location = (-520.0, 300.0)
    vector_math.location = (-200.0, 300.0)
    math.location = (-40.0, 300.0)
    emission.location = (860.0, 300.0)
    mix.location = (700.0, 300.0)
    math_001.location = (140.0, 80.0)
    math_002.location = (380.0, 300.0)
    color_ramp.location = (120.0, 300.0)
    math_003.location = (540.0, 300.0)
    reroute.location = (20.0, 200.0)

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
    color_ramp.width, color_ramp.height = 240.0, 100.0
    math_003.width, math_003.height = 140.0, 100.0
    reroute.width, reroute.height = 16.0, 100.0

    # initialize circles links
    # mapping.Vector -> vector_math.Vector
    circles.links.new(mapping.outputs[0], vector_math.inputs[0])
    # texture_coordinate.Object -> mapping.Vector
    circles.links.new(texture_coordinate.outputs[3], mapping.inputs[0])
    # vector_math.Value -> math.Value
    circles.links.new(vector_math.outputs[1], math.inputs[0])
    # mix.Result -> emission.Color
    circles.links.new(mix.outputs[2], emission.inputs[0])
    # reroute.Output -> math_001.Value
    circles.links.new(reroute.outputs[0], math_001.inputs[0])
    # math_001.Value -> math_002.Value
    circles.links.new(math_001.outputs[0], math_002.inputs[1])
    # reroute.Output -> color_ramp.Fac
    circles.links.new(reroute.outputs[0], color_ramp.inputs[0])
    # color_ramp.Color -> math_002.Value
    circles.links.new(color_ramp.outputs[0], math_002.inputs[0])
    # reroute.Output -> math_003.Value
    circles.links.new(reroute.outputs[0], math_003.inputs[0])
    # math_002.Value -> math_003.Value
    circles.links.new(math_002.outputs[0], math_003.inputs[1])
    # vector_math.Value -> reroute.Input
    circles.links.new(vector_math.outputs[1], reroute.inputs[0])
    # math_003.Value -> mix.Factor
    circles.links.new(math_003.outputs[0], mix.inputs[0])
    # emission.Emission -> material_output.Surface
    circles.links.new(emission.outputs[0], material_output.inputs[0])
    return circles