# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife

#from cutscenes import InnIntroCutscene, InnIntroCutscene2, GarthIntroCutscene


@classmethod
def initPrologue(cls, world):
	world.current_map_name = "TwoMapples_Inn"
	world.camera_coords = fife.ModelCoordinate(40, 0, 0)
	world.addMapTrigger(
		"Two Mapples Inn intro", "TwoMapples_Inn", None, None, None, None,
		"InnIntroCutscene", True)
	#world.addMapTrigger(
	#	"Two Mapples Inn prologue dialogue Radcliffe", "TwoMapples_Inn", None, None, None, None,
	#	lambda pc: cls.startDialogue(world, "prologue_dialogue0"), True)
	#world.addMapTrigger(
	#	"Two Mapples Inn Radcliffe walks to the bar", "TwoMapples_Inn", None, None, None, None,
	#	lambda pc: world.application.startCutscene(cls.InnIntroCutscene2), True)
	world.addMapTrigger(
		"Two Mapples Inn prologue dialogue", "TwoMapples_Inn", None, None, None, None,
		"prologue_dialogue", True)


@classmethod
def continuePrologue(cls, npc, pc, world):
	world.disablePlayerCharacter()
	world.application.prepareChangeMap("TwoMapples_Inn")
	world.addMapTrigger(
		"Two Mapples Inn prologue dialogue cont.", "TwoMapples_Inn", None, None, None, None,
		"prologue_dialogue", True)


"""
@staticmethod
def checkFinished3Prologues(npc, pc, world):
	return (world.knowledge.get("jason_prologue") and world.knowledge.get("dusty_prologue")
			and world.knowledge.get("tom_prologue"))

@staticmethod
def checkFinishedPrologueLastJason(npc, pc, world):
	return world.knowledge.get("last_prologue") == "Jason"

@staticmethod
def checkFinishedPrologueLastTom(npc, pc, world):
	return world.knowledge.get("last_prologue") == "Tom"

@staticmethod
def checkFinishedPrologueLastDusty(npc, pc, world):
	return world.knowledge.get("last_prologue") == "Dusty"

@staticmethod
def checkNotFinishedPrologueJason(npc, pc, world):
	return not world.knowledge.get("jason_prologue")

@staticmethod
def checkNotFinishedPrologueTom(npc, pc, world):
	return not world.knowledge.get("tom_prologue")

@staticmethod
def checkNotFinishedPrologueDusty(npc, pc, world):
	return not world.knowledge.get("dusty_prologue")
"""