# -*- coding: utf-8 -*-

pingpong_names = ["Bush01_animated", "Bush02_animated", "Tree01_Anim", "Tree02_Anim",
	"Tree03_Anim", "Tree04_Anim", "Water_animation", "Grass01_Animated",
	"Grass02_Animated", "Grass03_Animated", "Acer01", "Acer02", "Arbutus01", "Arbutus02",
	"Flower01", "Flower02", "Flower03", "Flower04", "Flower05"]

randomize_names = ("Bush01_animated", "Bush02_animated", "Tree01_Anim", "Tree02_Anim",
	"Tree03_Anim", "Tree04_Anim", "Grass01_Animated", "Grass02_Animated",
	"Grass03_Animated", "Acer01", "Acer02", "Arbutus01", "Arbutus02",
	"Flower01", "Flower02", "Flower03", "Flower04", "Flower05")

animal_names = ("Butterfly01", "Butterfly02", "Butterfly03", "Butterfly04")

bird_names = ("Falcon01", )

# hour format:
#	03:00 = 03.0
#	03:30 = 03.5
# line format:
#	hour : (global light R,G,B,	local light R,G,B),

light_cycle = {
	00.0 : (0.24, 0.3, 0.4,		0.75, 0.63, 0.5),
	04.0 : (0.24, 0.3, 0.4,		0.75, 0.63, 0.5),
	07.0 : (1.0, 1.01, 1.0,		0.0, 0.0, 0.0),
	17.0 : (1.0, 1.0, 1.0,		0.0, 0.0, 0.0),
	19.0 : (1.0, 0.58, 0.67,	0.2, 0.25, 0.3),
	20.0 : (0.24, 0.3, 0.4,		0.75, 0.63, 0.5),
	24.0 : (0.24, 0.3, 0.4,		0.75, 0.63, 0.5)}

# hours when image lights are turned on/off
# line format:
#   instance name : (light on hour, light off hour),

light_instances = {
	"Mansion01_lights" : (20.05, 04.0),
	"Lamppost01_light" : (20.05, 04.0),
	"Lamppost02_light" : (20.05, 04.0),
	"Lightnode_White"  : (20.05, 04.0),
	"House_Nightlights": (20.05, 04.0),
        "Church_Nightlight": (20.05, 04.0),
        "Ashgrove_Houselights1": (20.05, 04.0),
        "Ashgrove_Houselights2": (20.05, 04.0),
        "Bighouse_Nightlight": (20.05, 04.0),
        "Mr_Radcliffe_Sleep": (20.05, 04.0),
        "Sawmill_hideout_Lights": (20.05, 04.0),
        "Inn_Nightlights2": (20.05, 04.0)}
	
# hours when circle lights are turned on/off
# line format:
#   instance name : (light on hour, light off hour, X scale, Y scale, R, G, B, X offset, Y offset),

light_circles = {
	"Barrel_Fire" 		: (20.05, 04.0, 3.5, 3,   1.0, 0.72, 0.36, 0, -60),
	"Lamppost01" 		: (20.05, 04.0, 3.5, 3.5, 1.0, 0.82, 0.46, 0, -100),
	"Lamppost02" 		: (20.05, 04.0, 3.5, 3.5, 1.0, 0.82, 0.56, 0, -100),
	"Lightnode_White" 	: (20.05, 04.0, 1.5, 1.5, 0.8, 0.65, 0.38, 0, 0),
	"Sebastian_Rex" 	: (20.05, 04.0, 3,   3,   1.0, 0.82, 0.56, 0, -50)}

#hide_obstructions = ("Porch_Roof", )
