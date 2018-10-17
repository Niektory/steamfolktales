# -*- coding: utf-8 -*-

import_list = ("objects/Effects/Greengear.xml",
	"objects/Effects/Tile.xml",
	"objects/Effects/Blood_Hit01.xml",
	"objects/Effects/Blood_Hit02.xml",
	# TODO: detect which characters are neededs
	"objects/Sprites - Characters/Young_Jason/Young_Jason.xml")

"""	"objects/Sprites - Characters/Thief_Spritesheets/Thief.xml",
	"objects/Sprites - Characters/Fat_Thug1/Fat_Thug1.xml",
	"objects/Sprites - Characters/Agent/Agent.xml",
	"objects/Sprites - Characters/Dusty/Dusty.xml",
	"objects/Sprites - Characters/Uncle_Garth/Uncle_Garth.xml",
	"objects/Sprites - Characters/Young_Jason/Young_Jason.xml",
	"objects/Sprites - Characters/Mark_Mapple/Mark_Mapple.xml",
	"objects/Sprites - Characters/Mr_Radcliffe/Mr_Radcliffe.xml",
	"objects/Sprites - Characters/Sebastian_Rex/Sebastian_Rex.xml",
	"objects/Sprites - Characters/Thug01_Spritesheets/Thug01.xml",
	"objects/Sprites - Characters/Thug02_Spritesheets/Thug02.xml",
	"objects/Sprites - Characters/Thug03_Spritesheets/Thug03.xml",
	"objects/Rendered Environments/Kingsworth Wilds - Watermill/Watermill_Exit.xml",
	"objects/Rendered Environments/Kingsworth Wilds - Watermill/Bookshelf.xml",
	"objects/Rendered Environments/Kingsworth Wilds - Watermill/Diary.xml",
	"objects/Watermill_exterior/Watermill_Door.xml",
	"objects/Rendered Environments/Sebastians_Mansion_1stfloor/Door_Mansion.xml",
	"objects/Rendered Environments/Sebastians_Mansion_1stfloor/Sebastian_1st_to_2ndfloor.xml",
	"objects/Rendered Environments/Sebastians_Mansion_2ndfloor/Sebastian_2nd_to_1stfloor.xml",
	"objects/Rendered Environments/Sebastians_Mansion_2ndfloor/Bedroom_Door_East.xml",
	"objects/Rendered Environments/Sebastians_Mansion_2ndfloor/Bedroom_Door_South.xml",
	"objects/Rendered Environments/Sebastians_Mansion_2ndfloor/Bedroom_Door_West.xml",
	"objects/Rendered Environments/Sebastians_Mansion_Exterior/Sebastians_Mansion_Main_Door.xml",
	"objects/Rendered Environments/Sebastians_Mansion_Exterior/Sebastians_Mansion_Vine.xml",
	"objects/Rendered Environments/Ashgrove_Sawmill/Sawmill_Hideout_Door_Outside.xml")"""

# TODO: change this to automatically detect what objects are needed on a map
# so all is needed is a sprite_name:path/file.xml mapping

import_by_map = {
"Amelia_Engineroom":(
	"objects/Sprites - Characters/Terrorist_Gil/Gil.xml",
	"objects/Sprites - Characters/Sebastian_Dustys/Sebastian_Rex_Dustys.xml"),
#"TwoMapples_Inn":(
#	"objects/Sprites - Characters/Agent/Agent.xml",
#	"objects/Sprites - Characters/Dusty/Dusty.xml",
#	"objects/Sprites - Characters/Mark_Mapple/Mark_Mapple.xml",
#	"objects/Sprites - Characters/Mr_Radcliffe/Mr_Radcliffe.xml"),
#"Sawmill_Hideout":(
	#"objects/Sprites - Characters/Young_Jason/Young_Jason.xml",
	#"objects/Sprites - Characters/Uncle_Garth/Uncle_Garth.xml",
#	"objects/Rendered Environments/Ashgrove_Sawmill/Sawmill_Hideout_Door.xml",),
#"Ashgrove_Sawmill":(
#	"objects/Sprites - Characters/Young_Jason/Young_Jason.xml",),
	#"objects/Sprites - Characters/Thug01_Spritesheets/Thug01.xml",
	#"objects/Sprites - Characters/Thug02_Spritesheets/Thug02.xml",
	#"objects/Sprites - Characters/Thug03_Spritesheets/Thug03.xml",
	#"objects/Rendered Environments/Ashgrove_Sawmill/Sawmill_Hideout_Door_Outside.xml"),
#"Sebastians_exterior":(
#	"objects/Sprites - Characters/Young_Jason/Young_Jason.xml",),
	#"objects/Rendered Environments/Sebastians_Mansion_Exterior/Sebastians_Mansion_Main_Door.xml",
	#"objects/Rendered Environments/Sebastians_Mansion_Exterior/Sebastians_Mansion_Vine.xml"),
#"Mansion01_1stfloor":(
#	"objects/Sprites - Characters/Young_Jason/Young_Jason.xml",),
	#"objects/Rendered Environments/Sebastians_Mansion_1stfloor/Door_Mansion.xml",
	#"objects/Rendered Environments/Sebastians_Mansion_1stfloor/Sebastian_1st_to_2ndfloor.xml"),
"Mansion01_2ndfloor":(
#	"objects/Sprites - Characters/Young_Jason/Young_Jason.xml",)}
	"objects/Sprites - Characters/Sebastian_Rex/Sebastian_Rex.xml",)
	#"objects/Rendered Environments/Sebastians_Mansion_2ndfloor/Sebastian_2nd_to_1stfloor.xml",
	#"objects/Rendered Environments/Sebastians_Mansion_2ndfloor/Bedroom_Door_East.xml",
	#"objects/Rendered Environments/Sebastians_Mansion_2ndfloor/Bedroom_Door_South.xml",
	#"objects/Rendered Environments/Sebastians_Mansion_2ndfloor/Bedroom_Door_West.xml")}
}