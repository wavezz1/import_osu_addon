import bpy, mathutils

# initialize Slider node group
def slider_node_group():
    mat = bpy.data.materials.new(name="Slider")
    mat.use_nodes = True
    mat["osu_imported"] = True
    slider = mat.node_tree
    # start with a clean node tree
    for node in slider.nodes:
        slider.nodes.remove(node)
    slider.color_tag = 'NONE'
    slider.description = ""

    # slider interface

    # initialize slider nodes
    # node Material Output
    material_output = slider.nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"
    material_output.is_active_output = True
    material_output.target = 'ALL'
    # Displacement
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Thickness
    material_output.inputs[3].default_value = 0.0

    # node Emission
    emission = slider.nodes.new("ShaderNodeEmission")
    emission.name = "Emission"
    # Strength
    emission.inputs[1].default_value = 1.0

    # node Attribute.001
    attribute_001 = slider.nodes.new("ShaderNodeAttribute")
    attribute_001.name = "Attribute.001"
    attribute_001.attribute_name = "Distance"
    attribute_001.attribute_type = 'GEOMETRY'

    # node Mix.001
    mix_001 = slider.nodes.new("ShaderNodeMix")
    mix_001.name = "Mix.001"
    mix_001.blend_type = 'MIX'
    mix_001.clamp_factor = False
    mix_001.clamp_result = False
    mix_001.data_type = 'RGBA'
    mix_001.factor_mode = 'UNIFORM'

    # node Attribute.002
    attribute_002 = slider.nodes.new("ShaderNodeAttribute")
    attribute_002.name = "Attribute.002"
    attribute_002.attribute_name = "combo_color"
    attribute_002.attribute_type = 'GEOMETRY'

    # node Hue/Saturation/Value.001
    hue_saturation_value_001 = slider.nodes.new("ShaderNodeHueSaturation")
    hue_saturation_value_001.name = "Hue/Saturation/Value.001"
    # Hue
    hue_saturation_value_001.inputs[0].default_value = 0.5
    # Saturation
    hue_saturation_value_001.inputs[1].default_value = 1.0
    # Value
    hue_saturation_value_001.inputs[2].default_value = 0.0500001460313797
    # Fac
    hue_saturation_value_001.inputs[3].default_value = 1.0

    # node Math
    math = slider.nodes.new("ShaderNodeMath")
    math.name = "Math"
    math.operation = 'COMPARE'
    math.use_clamp = False
    # Value_001
    math.inputs[1].default_value = 0.0
    # Value_002
    math.inputs[2].default_value = 0.5

    # node Math.001
    math_001 = slider.nodes.new("ShaderNodeMath")
    math_001.name = "Math.001"
    math_001.operation = 'SUBTRACT'
    math_001.use_clamp = False

    # node Color Ramp.003
    color_ramp_003 = slider.nodes.new("ShaderNodeValToRGB")
    color_ramp_003.name = "Color Ramp.003"
    color_ramp_003.color_ramp.color_mode = 'RGB'
    color_ramp_003.color_ramp.hue_interpolation = 'NEAR'
    color_ramp_003.color_ramp.interpolation = 'EASE'

    # initialize color ramp elements
    color_ramp_003.color_ramp.elements.remove(color_ramp_003.color_ramp.elements[0])
    color_ramp_003_cre_0 = color_ramp_003.color_ramp.elements[0]
    color_ramp_003_cre_0.position = 0.5
    color_ramp_003_cre_0.alpha = 1.0
    color_ramp_003_cre_0.color = (0.0, 0.0, 0.0, 1.0)

    color_ramp_003_cre_1 = color_ramp_003.color_ramp.elements.new(0.5136368274688721)
    color_ramp_003_cre_1.alpha = 1.0
    color_ramp_003_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    # node Color Ramp.004
    color_ramp_004 = slider.nodes.new("ShaderNodeValToRGB")
    color_ramp_004.name = "Color Ramp.004"
    color_ramp_004.color_ramp.color_mode = 'RGB'
    color_ramp_004.color_ramp.hue_interpolation = 'NEAR'
    color_ramp_004.color_ramp.interpolation = 'EASE'

    # initialize color ramp elements
    color_ramp_004.color_ramp.elements.remove(color_ramp_004.color_ramp.elements[0])
    color_ramp_004_cre_0 = color_ramp_004.color_ramp.elements[0]
    color_ramp_004_cre_0.position = 0.18636363744735718
    color_ramp_004_cre_0.alpha = 1.0
    color_ramp_004_cre_0.color = (1.0, 1.0, 1.0, 1.0)

    color_ramp_004_cre_1 = color_ramp_004.color_ramp.elements.new(1.0)
    color_ramp_004_cre_1.alpha = 1.0
    color_ramp_004_cre_1.color = (0.0, 0.0, 0.0, 1.0)

    # node Color Ramp.005
    color_ramp_005 = slider.nodes.new("ShaderNodeValToRGB")
    color_ramp_005.name = "Color Ramp.005"
    color_ramp_005.color_ramp.color_mode = 'RGB'
    color_ramp_005.color_ramp.hue_interpolation = 'NEAR'
    color_ramp_005.color_ramp.interpolation = 'LINEAR'

    # initialize color ramp elements
    color_ramp_005.color_ramp.elements.remove(color_ramp_005.color_ramp.elements[0])
    color_ramp_005_cre_0 = color_ramp_005.color_ramp.elements[0]
    color_ramp_005_cre_0.position = 0.0
    color_ramp_005_cre_0.alpha = 1.0
    color_ramp_005_cre_0.color = (0.010686015710234642, 0.010686015710234642, 0.010686015710234642, 1.0)

    color_ramp_005_cre_1 = color_ramp_005.color_ramp.elements.new(1.0)
    color_ramp_005_cre_1.alpha = 1.0
    color_ramp_005_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    # node Hue/Saturation/Value.002
    hue_saturation_value_002 = slider.nodes.new("ShaderNodeHueSaturation")
    hue_saturation_value_002.name = "Hue/Saturation/Value.002"
    # Hue
    hue_saturation_value_002.inputs[0].default_value = 0.5
    # Saturation
    hue_saturation_value_002.inputs[1].default_value = 1.0
    # Value
    hue_saturation_value_002.inputs[2].default_value = 0.10000002384185791
    # Fac
    hue_saturation_value_002.inputs[3].default_value = 1.0

    # node Math.002
    math_002 = slider.nodes.new("ShaderNodeMath")
    math_002.name = "Math.002"
    math_002.operation = 'MULTIPLY_ADD'
    math_002.use_clamp = False
    # Value_001
    math_002.inputs[1].default_value = 0.5

    # Set locations
    material_output.location = (740.0, 420.0)
    emission.location = (580.0, 420.0)
    attribute_001.location = (-600.0, 420.0)
    mix_001.location = (420.0, 420.0)
    attribute_002.location = (80.0, 200.0)
    hue_saturation_value_001.location = (240.0, 200.0)
    math.location = (-440.0, -20.0)
    math_001.location = (-180.0, 420.0)
    color_ramp_003.location = (-440.0, 200.0)
    color_ramp_004.location = (-440.0, 420.0)
    color_ramp_005.location = (140.0, 420.0)
    hue_saturation_value_002.location = (240.0, 20.0)
    math_002.location = (-20.0, 420.0)

    # Set dimensions
    material_output.width, material_output.height = 140.0, 100.0
    emission.width, emission.height = 140.0, 100.0
    attribute_001.width, attribute_001.height = 140.0, 100.0
    mix_001.width, mix_001.height = 140.0, 100.0
    attribute_002.width, attribute_002.height = 140.0, 100.0
    hue_saturation_value_001.width, hue_saturation_value_001.height = 150.0, 100.0
    math.width, math.height = 140.0, 100.0
    math_001.width, math_001.height = 140.0, 100.0
    color_ramp_003.width, color_ramp_003.height = 240.0, 100.0
    color_ramp_004.width, color_ramp_004.height = 240.0, 100.0
    color_ramp_005.width, color_ramp_005.height = 240.0, 100.0
    hue_saturation_value_002.width, hue_saturation_value_002.height = 150.0, 100.0
    math_002.width, math_002.height = 140.0, 100.0

    # initialize slider links
    # emission.Emission -> material_output.Surface
    slider.links.new(emission.outputs[0], material_output.inputs[0])
    # attribute_002.Color -> hue_saturation_value_001.Color
    slider.links.new(attribute_002.outputs[0], hue_saturation_value_001.inputs[4])
    # math.Value -> math_001.Value
    slider.links.new(math.outputs[0], math_001.inputs[1])
    # color_ramp_003.Color -> math_001.Value
    slider.links.new(color_ramp_003.outputs[0], math_001.inputs[0])
    # hue_saturation_value_001.Color -> mix_001.A
    slider.links.new(hue_saturation_value_001.outputs[0], mix_001.inputs[6])
    # attribute_002.Color -> hue_saturation_value_002.Color
    slider.links.new(attribute_002.outputs[0], hue_saturation_value_002.inputs[4])
    # hue_saturation_value_002.Color -> mix_001.B
    slider.links.new(hue_saturation_value_002.outputs[0], mix_001.inputs[7])
    # math_001.Value -> math_002.Value
    slider.links.new(math_001.outputs[0], math_002.inputs[0])
    # color_ramp_004.Color -> math_002.Value
    slider.links.new(color_ramp_004.outputs[0], math_002.inputs[2])
    # math_002.Value -> color_ramp_005.Fac
    slider.links.new(math_002.outputs[0], color_ramp_005.inputs[0])
    # color_ramp_005.Color -> mix_001.Factor
    slider.links.new(color_ramp_005.outputs[0], mix_001.inputs[0])
    # attribute_001.Fac -> color_ramp_004.Fac
    slider.links.new(attribute_001.outputs[2], color_ramp_004.inputs[0])
    # attribute_001.Fac -> color_ramp_003.Fac
    slider.links.new(attribute_001.outputs[2], color_ramp_003.inputs[0])
    # attribute_001.Fac -> math.Value
    slider.links.new(attribute_001.outputs[2], math.inputs[0])
    # mix_001.Result -> emission.Color
    slider.links.new(mix_001.outputs[2], emission.inputs[0])
    return slider