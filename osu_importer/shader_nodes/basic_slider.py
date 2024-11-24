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

    # node Mix
    mix = slider.nodes.new("ShaderNodeMix")
    mix.name = "Mix"
    mix.blend_type = 'LINEAR_LIGHT'
    mix.clamp_factor = False
    mix.clamp_result = False
    mix.data_type = 'RGBA'
    mix.factor_mode = 'UNIFORM'
    # B_Color
    mix.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)

    # node Attribute.001
    attribute_001 = slider.nodes.new("ShaderNodeAttribute")
    attribute_001.name = "Attribute.001"
    attribute_001.attribute_name = "Distance"
    attribute_001.attribute_type = 'GEOMETRY'

    # node Color Ramp
    color_ramp = slider.nodes.new("ShaderNodeValToRGB")
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

    # node Attribute
    attribute = slider.nodes.new("ShaderNodeAttribute")
    attribute.name = "Attribute"
    attribute.attribute_name = "combo_color"
    attribute.attribute_type = 'GEOMETRY'

    # node Hue/Saturation/Value
    hue_saturation_value = slider.nodes.new("ShaderNodeHueSaturation")
    hue_saturation_value.name = "Hue/Saturation/Value"
    # Hue
    hue_saturation_value.inputs[0].default_value = 0.5
    # Saturation
    hue_saturation_value.inputs[1].default_value = 1.0
    # Value
    hue_saturation_value.inputs[2].default_value = 0.10000000149011612
    # Fac
    hue_saturation_value.inputs[3].default_value = 1.0

    # node Color Ramp.001
    color_ramp_001 = slider.nodes.new("ShaderNodeValToRGB")
    color_ramp_001.name = "Color Ramp.001"
    color_ramp_001.color_ramp.color_mode = 'RGB'
    color_ramp_001.color_ramp.hue_interpolation = 'NEAR'
    color_ramp_001.color_ramp.interpolation = 'EASE'

    # initialize color ramp elements
    color_ramp_001.color_ramp.elements.remove(color_ramp_001.color_ramp.elements[0])
    color_ramp_001_cre_0 = color_ramp_001.color_ramp.elements[0]
    color_ramp_001_cre_0.position = 0.5860000252723694
    color_ramp_001_cre_0.alpha = 1.0
    color_ramp_001_cre_0.color = (1.0, 1.0, 1.0, 1.0)

    color_ramp_001_cre_1 = color_ramp_001.color_ramp.elements.new(0.6000000238418579)
    color_ramp_001_cre_1.alpha = 1.0
    color_ramp_001_cre_1.color = (0.0, 0.0, 0.0, 1.0)

    # node Math.003
    math_003 = slider.nodes.new("ShaderNodeMath")
    math_003.name = "Math.003"
    math_003.operation = 'MULTIPLY'
    math_003.use_clamp = False

    # node Mix Shader
    mix_shader = slider.nodes.new("ShaderNodeMixShader")
    mix_shader.name = "Mix Shader"
    # Fac
    mix_shader.inputs[0].default_value = 0.8999999761581421

    # node Transparent BSDF
    transparent_bsdf = slider.nodes.new("ShaderNodeBsdfTransparent")
    transparent_bsdf.name = "Transparent BSDF"
    # Color
    transparent_bsdf.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)

    # node Color Ramp.002
    color_ramp_002 = slider.nodes.new("ShaderNodeValToRGB")
    color_ramp_002.name = "Color Ramp.002"
    color_ramp_002.color_ramp.color_mode = 'RGB'
    color_ramp_002.color_ramp.hue_interpolation = 'NEAR'
    color_ramp_002.color_ramp.interpolation = 'EASE'

    # initialize color ramp elements
    color_ramp_002.color_ramp.elements.remove(color_ramp_002.color_ramp.elements[0])
    color_ramp_002_cre_0 = color_ramp_002.color_ramp.elements[0]
    color_ramp_002_cre_0.position = 0.0
    color_ramp_002_cre_0.alpha = 1.0
    color_ramp_002_cre_0.color = (0.012976991012692451, 0.012976991012692451, 0.012976991012692451, 1.0)

    color_ramp_002_cre_1 = color_ramp_002.color_ramp.elements.new(0.5)
    color_ramp_002_cre_1.alpha = 1.0
    color_ramp_002_cre_1.color = (0.0, 0.0, 0.0, 1.0)

    # node Math.004
    math_004 = slider.nodes.new("ShaderNodeMath")
    math_004.name = "Math.004"
    math_004.operation = 'ADD'
    math_004.use_clamp = False

    # Set locations
    material_output.location = (1320.0, 540.0)
    emission.location = (600.0, 340.0)
    mix.location = (420.0, 420.0)
    attribute_001.location = (-380.0, 420.0)
    color_ramp.location = (-160.0, 420.0)
    attribute.location = (260.0, 180.0)
    hue_saturation_value.location = (420.0, 180.0)
    color_ramp_001.location = (-160.0, 640.0)
    math_003.location = (100.0, 640.0)
    mix_shader.location = (600.0, 480.0)
    transparent_bsdf.location = (600.0, 580.0)
    color_ramp_002.location = (-160.0, 860.0)
    math_004.location = (260.0, 640.0)

    # Set dimensions
    material_output.width, material_output.height = 140.0, 100.0
    emission.width, emission.height = 140.0, 100.0
    mix.width, mix.height = 140.0, 100.0
    attribute_001.width, attribute_001.height = 140.0, 100.0
    color_ramp.width, color_ramp.height = 240.0, 100.0
    attribute.width, attribute.height = 140.0, 100.0
    hue_saturation_value.width, hue_saturation_value.height = 150.0, 100.0
    color_ramp_001.width, color_ramp_001.height = 240.0, 100.0
    math_003.width, math_003.height = 140.0, 100.0
    mix_shader.width, mix_shader.height = 140.0, 100.0
    transparent_bsdf.width, transparent_bsdf.height = 140.0, 100.0
    color_ramp_002.width, color_ramp_002.height = 240.0, 100.0
    math_004.width, math_004.height = 140.0, 100.0

    # initialize slider links
    # attribute_001.Fac -> color_ramp.Fac
    slider.links.new(attribute_001.outputs[2], color_ramp.inputs[0])
    # attribute.Color -> hue_saturation_value.Color
    slider.links.new(attribute.outputs[0], hue_saturation_value.inputs[4])
    # mix.Result -> emission.Color
    slider.links.new(mix.outputs[2], emission.inputs[0])
    # attribute_001.Fac -> color_ramp_001.Fac
    slider.links.new(attribute_001.outputs[2], color_ramp_001.inputs[0])
    # color_ramp.Color -> math_003.Value
    slider.links.new(color_ramp.outputs[0], math_003.inputs[0])
    # color_ramp_001.Color -> math_003.Value
    slider.links.new(color_ramp_001.outputs[0], math_003.inputs[1])
    # emission.Emission -> mix_shader.Shader
    slider.links.new(emission.outputs[0], mix_shader.inputs[2])
    # transparent_bsdf.BSDF -> mix_shader.Shader
    slider.links.new(transparent_bsdf.outputs[0], mix_shader.inputs[1])
    # attribute_001.Fac -> color_ramp_002.Fac
    slider.links.new(attribute_001.outputs[2], color_ramp_002.inputs[0])
    # math_003.Value -> math_004.Value
    slider.links.new(math_003.outputs[0], math_004.inputs[0])
    # color_ramp_002.Color -> math_004.Value
    slider.links.new(color_ramp_002.outputs[0], math_004.inputs[1])
    # math_004.Value -> mix.Factor
    slider.links.new(math_004.outputs[0], mix.inputs[0])
    # hue_saturation_value.Color -> mix.A
    slider.links.new(hue_saturation_value.outputs[0], mix.inputs[6])
    # mix_shader.Shader -> material_output.Surface
    slider.links.new(mix_shader.outputs[0], material_output.inputs[0])
    return slider