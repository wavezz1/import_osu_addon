import bpy, mathutils

# initialize Circles node group
def circles_node_group():
    mat = bpy.data.materials.new(name="Circles")
    mat.use_nodes = True
    mat["osu_imported"] = True
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

    # node Emission
    emission = circles.nodes.new("ShaderNodeEmission")
    emission.name = "Emission"
    # Strength
    emission.inputs[1].default_value = 1.0

    # node Mix
    mix = circles.nodes.new("ShaderNodeMix")
    mix.name = "Mix"
    mix.blend_type = 'MIX'
    mix.clamp_factor = False
    mix.clamp_result = False
    mix.data_type = 'RGBA'
    mix.factor_mode = 'UNIFORM'

    # node Attribute
    attribute = circles.nodes.new("ShaderNodeAttribute")
    attribute.name = "Attribute"
    attribute.attribute_name = "combo_color"
    attribute.attribute_type = 'INSTANCER'

    # node Hue/Saturation/Value
    hue_saturation_value = circles.nodes.new("ShaderNodeHueSaturation")
    hue_saturation_value.name = "Hue/Saturation/Value"
    # Hue
    hue_saturation_value.inputs[0].default_value = 0.5
    # Saturation
    hue_saturation_value.inputs[1].default_value = 1.0
    # Value
    hue_saturation_value.inputs[2].default_value = 0.0500001460313797
    # Fac
    hue_saturation_value.inputs[3].default_value = 1.0

    # node Math
    math = circles.nodes.new("ShaderNodeMath")
    math.name = "Math"
    math.operation = 'COMPARE'
    math.use_clamp = False
    # Value_001
    math.inputs[1].default_value = 0.0
    # Value_002
    math.inputs[2].default_value = 0.5

    # node Math.001
    math_001 = circles.nodes.new("ShaderNodeMath")
    math_001.name = "Math.001"
    math_001.operation = 'SUBTRACT'
    math_001.use_clamp = False

    # node Color Ramp
    color_ramp = circles.nodes.new("ShaderNodeValToRGB")
    color_ramp.name = "Color Ramp"
    color_ramp.color_ramp.color_mode = 'RGB'
    color_ramp.color_ramp.hue_interpolation = 'NEAR'
    color_ramp.color_ramp.interpolation = 'EASE'

    # initialize color ramp elements
    color_ramp.color_ramp.elements.remove(color_ramp.color_ramp.elements[0])
    color_ramp_cre_0 = color_ramp.color_ramp.elements[0]
    color_ramp_cre_0.position = 0.5
    color_ramp_cre_0.alpha = 1.0
    color_ramp_cre_0.color = (0.0, 0.0, 0.0, 1.0)

    color_ramp_cre_1 = color_ramp.color_ramp.elements.new(0.5136368274688721)
    color_ramp_cre_1.alpha = 1.0
    color_ramp_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    # node Color Ramp.001
    color_ramp_001 = circles.nodes.new("ShaderNodeValToRGB")
    color_ramp_001.name = "Color Ramp.001"
    color_ramp_001.color_ramp.color_mode = 'RGB'
    color_ramp_001.color_ramp.hue_interpolation = 'NEAR'
    color_ramp_001.color_ramp.interpolation = 'EASE'

    # initialize color ramp elements
    color_ramp_001.color_ramp.elements.remove(color_ramp_001.color_ramp.elements[0])
    color_ramp_001_cre_0 = color_ramp_001.color_ramp.elements[0]
    color_ramp_001_cre_0.position = 0.18636363744735718
    color_ramp_001_cre_0.alpha = 1.0
    color_ramp_001_cre_0.color = (1.0, 1.0, 1.0, 1.0)

    color_ramp_001_cre_1 = color_ramp_001.color_ramp.elements.new(1.0)
    color_ramp_001_cre_1.alpha = 1.0
    color_ramp_001_cre_1.color = (0.0, 0.0, 0.0, 1.0)

    # node Color Ramp.002
    color_ramp_002 = circles.nodes.new("ShaderNodeValToRGB")
    color_ramp_002.name = "Color Ramp.002"
    color_ramp_002.color_ramp.color_mode = 'RGB'
    color_ramp_002.color_ramp.hue_interpolation = 'NEAR'
    color_ramp_002.color_ramp.interpolation = 'LINEAR'

    # initialize color ramp elements
    color_ramp_002.color_ramp.elements.remove(color_ramp_002.color_ramp.elements[0])
    color_ramp_002_cre_0 = color_ramp_002.color_ramp.elements[0]
    color_ramp_002_cre_0.position = 0.0
    color_ramp_002_cre_0.alpha = 1.0
    color_ramp_002_cre_0.color = (0.010686015710234642, 0.010686015710234642, 0.010686015710234642, 1.0)

    color_ramp_002_cre_1 = color_ramp_002.color_ramp.elements.new(1.0)
    color_ramp_002_cre_1.alpha = 1.0
    color_ramp_002_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    # node Hue/Saturation/Value.001
    hue_saturation_value_001 = circles.nodes.new("ShaderNodeHueSaturation")
    hue_saturation_value_001.name = "Hue/Saturation/Value.001"
    # Hue
    hue_saturation_value_001.inputs[0].default_value = 0.5
    # Saturation
    hue_saturation_value_001.inputs[1].default_value = 1.0
    # Value
    hue_saturation_value_001.inputs[2].default_value = 0.10000002384185791
    # Fac
    hue_saturation_value_001.inputs[3].default_value = 1.0

    # node Math.002
    math_002 = circles.nodes.new("ShaderNodeMath")
    math_002.name = "Math.002"
    math_002.operation = 'MULTIPLY_ADD'
    math_002.use_clamp = False
    # Value_001
    math_002.inputs[1].default_value = 0.5

    # Set locations
    material_output.location = (1317.999755859375, 300.0)
    mapping.location = (-180.0, 300.0)
    texture_coordinate.location = (-340.0, 300.0)
    vector_math.location = (-20.0, 300.0)
    emission.location = (1160.0, 300.0)
    mix.location = (1000.0, 300.0)
    attribute.location = (660.0, 80.0)
    hue_saturation_value.location = (820.0, 80.0)
    math.location = (140.0, -140.0)
    math_001.location = (400.0, 300.0)
    color_ramp.location = (140.0, 80.0)
    color_ramp_001.location = (140.0, 300.0)
    color_ramp_002.location = (720.0, 300.0)
    hue_saturation_value_001.location = (820.0, -100.0)
    math_002.location = (560.0, 300.0)

    # Set dimensions
    material_output.width, material_output.height = 140.0, 100.0
    mapping.width, mapping.height = 140.0, 100.0
    texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
    vector_math.width, vector_math.height = 140.0, 100.0
    emission.width, emission.height = 140.0, 100.0
    mix.width, mix.height = 140.0, 100.0
    attribute.width, attribute.height = 140.0, 100.0
    hue_saturation_value.width, hue_saturation_value.height = 150.0, 100.0
    math.width, math.height = 140.0, 100.0
    math_001.width, math_001.height = 140.0, 100.0
    color_ramp.width, color_ramp.height = 240.0, 100.0
    color_ramp_001.width, color_ramp_001.height = 240.0, 100.0
    color_ramp_002.width, color_ramp_002.height = 240.0, 100.0
    hue_saturation_value_001.width, hue_saturation_value_001.height = 150.0, 100.0
    math_002.width, math_002.height = 140.0, 100.0

    # initialize circles links
    # mapping.Vector -> vector_math.Vector
    circles.links.new(mapping.outputs[0], vector_math.inputs[0])
    # texture_coordinate.Object -> mapping.Vector
    circles.links.new(texture_coordinate.outputs[3], mapping.inputs[0])
    # attribute.Color -> hue_saturation_value.Color
    circles.links.new(attribute.outputs[0], hue_saturation_value.inputs[4])
    # mix.Result -> emission.Color
    circles.links.new(mix.outputs[2], emission.inputs[0])
    # math.Value -> math_001.Value
    circles.links.new(math.outputs[0], math_001.inputs[1])
    # color_ramp.Color -> math_001.Value
    circles.links.new(color_ramp.outputs[0], math_001.inputs[0])
    # vector_math.Value -> math.Value
    circles.links.new(vector_math.outputs[1], math.inputs[0])
    # vector_math.Value -> color_ramp.Fac
    circles.links.new(vector_math.outputs[1], color_ramp.inputs[0])
    # vector_math.Value -> color_ramp_001.Fac
    circles.links.new(vector_math.outputs[1], color_ramp_001.inputs[0])
    # hue_saturation_value.Color -> mix.A
    circles.links.new(hue_saturation_value.outputs[0], mix.inputs[6])
    # attribute.Color -> hue_saturation_value_001.Color
    circles.links.new(attribute.outputs[0], hue_saturation_value_001.inputs[4])
    # hue_saturation_value_001.Color -> mix.B
    circles.links.new(hue_saturation_value_001.outputs[0], mix.inputs[7])
    # math_001.Value -> math_002.Value
    circles.links.new(math_001.outputs[0], math_002.inputs[0])
    # color_ramp_001.Color -> math_002.Value
    circles.links.new(color_ramp_001.outputs[0], math_002.inputs[2])
    # math_002.Value -> color_ramp_002.Fac
    circles.links.new(math_002.outputs[0], color_ramp_002.inputs[0])
    # color_ramp_002.Color -> mix.Factor
    circles.links.new(color_ramp_002.outputs[0], mix.inputs[0])
    # emission.Emission -> material_output.Surface
    circles.links.new(emission.outputs[0], material_output.inputs[0])
    return circles