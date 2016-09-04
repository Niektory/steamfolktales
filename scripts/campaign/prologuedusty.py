# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from fife import fife

@classmethod
def startPrologueDusty(cls, npc, pc, world):
	world.knowledge["last_prologue"] = "Dusty"
	world.knowledge["dusty_prologue"] = 1
	dusty = world.getCharacter("Dusty")
	world.enablePlayerCharacter(dusty)

	world.addMapTrigger(
		"Gil enters the engine room", "Amelia_Engineroom", None, None, None, None,
		"GilIntroCutscene", True)
	world.addMapTrigger(
		"Dusty and Gil dialogue", "Amelia_Engineroom", None, None, None, None,
		"prologue_dusty_gil_dialogue", True)
	gil = world.getCharacter("Gil")
	world.addMapTrigger(
		"Dusty and Gil fight", "Amelia_Engineroom", None, None, None, None,
		"startGilFight", True)
	world.addMapTrigger(
		"Sebastian enters the engine room", "Amelia_Engineroom", None, None, None, None,
		"DustySebastianIntroCutscene", True)
	world.addMapTrigger(
		"Dusty and Sebastian in engine room dialogue", "Amelia_Engineroom", None, None, None, None,
		"prologue_dusty_sebastian_dialogue", True)
	world.addMapTrigger(
		"Sebastian exits engine room", "Amelia_Engineroom", None, None, None, None,
		"sebastianExitsEngineroom", True)

	world.addMapTrigger(
		"Sebastian teleports to Cabins", "Amelia_Cabins1", None, None, None, None,
		"sebastianEntersCabins1", True)
	world.addMapTrigger(
		"Sebastian walks to his room in Cabins", "Amelia_Cabins1", None, None, None, None,
		"sebastianEntersCabins2", True)
	#world.addMapTrigger(
	#	"Sebastian gives Dusty the gun dialogue", "Amelia_Cabins1", None, None, None, None,
	#	"prologue_dusty_sebastian_gun_dialogue", True)
	#world.addMapTrigger(
	#	"Dusty and Sebastian find the bomb dialogue", "Amelia_Cabins1", None, None, None, None,
	#	"prologue_dusty_sebastian_bomb_dialogue", True)
	#world.addMapTrigger(
	#	"Dusty and Sebastian pilot dialogue", "Amelia_Cabins1", None, None, None, None,
	#	"prologue_dusty_sebastian_pilot_dialogue", True)
	#world.addMapTrigger(
	#	"end of Dusty's prologue", "Amelia_Cabins1", None, None, None, None,
	#	"continuePrologue", True)

#@classmethod
#def gilSmashPipes(cls, npc, pc, world):
#	npc.world.application.startCutscene(cls.GilSmashPipesCutscene)

@staticmethod
def startGilFight(npc, pc, world):
	gil = world.getCharacter("Gil")
	world.application.startCombat([gil, pc])

@staticmethod
def sebastianExitsEngineroom(npc, pc, world):
	sebastian = world.getCharacter("Sebastian_Dustys")
	stairs = world.getInteractObject("amelia_engineroom_stairs")
	loc = stairs.visual.instance.getLocation()
	#loc.setLayerCoordinates(fife.ModelCoordinate(-3,16,0))
	sebastian.visual.walk(loc)

@staticmethod
def sebastianEntersCabins1(npc, pc, world):
	sebastian = world.getCharacter("Sebastian_Dustys")
	sebastian.teleport(fife.ModelCoordinate(0,-20,0), "Amelia_Cabins1")
	#sebastian.rotation = 270

@staticmethod
def sebastianEntersCabins2(npc, pc, world):
	sebastian = world.getCharacter("Sebastian_Dustys")
	#sebastian.rotation = 270
	loc = sebastian.visual.instance.getLocation()
	loc.setLayerCoordinates(fife.ModelCoordinate(4,-19,0))
	sebastian.visual.walk(loc)
	sebastian.dialogue = "prologue_dusty_sebastian_gun_dialogue"
