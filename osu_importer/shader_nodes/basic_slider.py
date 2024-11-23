import bpy, mathutils

#initialize Slider node group
def slider_node_group():
	mat = bpy.data.materials.new(name="Slider")
	mat.use_nodes = True
	mat["osu_imported"] = True
	slider = mat.node_tree
	#start with a clean node tree
	for node in slider.nodes:
		slider.nodes.remove(node)
	slider.color_tag = 'NONE'
	slider.description = ""

	#slider interface
	
	#initialize slider nodes
	#node Material Output
	material_output = slider.nodes.new("ShaderNodeOutputMaterial")
	material_output.name = "Material Output"
	material_output.is_active_output = True
	material_output.target = 'ALL'
	#Displacement
	material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
	#Thickness
	material_output.inputs[3].default_value = 0.0
	
	#node Emission
	emission = slider.nodes.new("ShaderNodeEmission")
	emission.name = "Emission"
	#Strength
	emission.inputs[1].default_value = 1.0
	
	#node Mix
	mix = slider.nodes.new("ShaderNodeMix")
	mix.name = "Mix"
	mix.blend_type = 'MIX'
	mix.clamp_factor = False
	mix.clamp_result = False
	mix.data_type = 'RGBA'
	mix.factor_mode = 'UNIFORM'
	#A_Color
	mix.inputs[6].default_value = (0.0, 0.0, 0.0, 1.0)
	#B_Color
	mix.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
	
	#node Attribute.001
	attribute_001 = slider.nodes.new("ShaderNodeAttribute")
	attribute_001.name = "Attribute.001"
	attribute_001.attribute_name = "Distance"
	attribute_001.attribute_type = 'GEOMETRY'
	
	#node Math
	math = slider.nodes.new("ShaderNodeMath")
	math.name = "Math"
	math.operation = 'COMPARE'
	math.use_clamp = False
	#Value_001
	math.inputs[1].default_value = 0.0
	#Value_002
	math.inputs[2].default_value = 0.5
	
	#node Math.001
	math_001 = slider.nodes.new("ShaderNodeMath")
	math_001.name = "Math.001"
	math_001.operation = 'SUBTRACT'
	math_001.use_clamp = False
	
	#node Color Ramp
	color_ramp = slider.nodes.new("ShaderNodeValToRGB")
	color_ramp.name = "Color Ramp"
	color_ramp.color_ramp.color_mode = 'RGB'
	color_ramp.color_ramp.hue_interpolation = 'NEAR'
	color_ramp.color_ramp.interpolation = 'LINEAR'
	
	#initialize color ramp elements
	color_ramp.color_ramp.elements.remove(color_ramp.color_ramp.elements[0])
	color_ramp_cre_0 = color_ramp.color_ramp.elements[0]
	color_ramp_cre_0.position = 0.4999999701976776
	color_ramp_cre_0.alpha = 1.0
	color_ramp_cre_0.color = (0.0, 0.0, 0.0, 1.0)

	color_ramp_cre_1 = color_ramp.color_ramp.elements.new(1.0)
	color_ramp_cre_1.alpha = 1.0
	color_ramp_cre_1.color = (1.0, 1.0, 1.0, 1.0)

	
	#node Math.002
	math_002 = slider.nodes.new("ShaderNodeMath")
	math_002.name = "Math.002"
	math_002.operation = 'MULTIPLY'
	math_002.use_clamp = False
	
	
	#Set locations
	material_output.location = (740.0, 420.0)
	emission.location = (580.0, 420.0)
	mix.location = (420.0, 420.0)
	attribute_001.location = (-320.0, 420.0)
	math.location = (-160.0, 200.0)
	math_001.location = (100.0, 420.0)
	color_ramp.location = (-160.0, 420.0)
	math_002.location = (260.0, 420.0)
	
	#Set dimensions
	material_output.width, material_output.height = 140.0, 100.0
	emission.width, emission.height = 140.0, 100.0
	mix.width, mix.height = 140.0, 100.0
	attribute_001.width, attribute_001.height = 140.0, 100.0
	math.width, math.height = 140.0, 100.0
	math_001.width, math_001.height = 140.0, 100.0
	color_ramp.width, color_ramp.height = 240.0, 100.0
	math_002.width, math_002.height = 140.0, 100.0
	
	#initialize slider links
	#mix.Result -> emission.Color
	slider.links.new(mix.outputs[2], emission.inputs[0])
	#attribute_001.Fac -> math.Value
	slider.links.new(attribute_001.outputs[2], math.inputs[0])
	#math.Value -> math_001.Value
	slider.links.new(math.outputs[0], math_001.inputs[1])
	#attribute_001.Fac -> color_ramp.Fac
	slider.links.new(attribute_001.outputs[2], color_ramp.inputs[0])
	#color_ramp.Color -> math_001.Value
	slider.links.new(color_ramp.outputs[0], math_001.inputs[0])
	#attribute_001.Fac -> math_002.Value
	slider.links.new(attribute_001.outputs[2], math_002.inputs[0])
	#math_001.Value -> math_002.Value
	slider.links.new(math_001.outputs[0], math_002.inputs[1])
	#math_002.Value -> mix.Factor
	slider.links.new(math_002.outputs[0], mix.inputs[0])
	#emission.Emission -> material_output.Surface
	slider.links.new(emission.outputs[0], material_output.inputs[0])
	return slider
