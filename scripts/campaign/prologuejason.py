# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife

#from cutscenes import GarthWakeUpCutscene

@classmethod
def startPrologueJason(cls, npc, pc, world):
	young_jason = world.getCharacter("Young_Jason")
	world.enablePlayerCharacter(young_jason)
	world.knowledge["jason_prologue"] = 1
	world.addMapTrigger(
		"Young Jason beaten by Uncle Garth", "Sawmill_Hideout", None, None, None, None,
		"GarthIntroCutscene", True)
	world.addMapTrigger(
		"Young Jason beaten by Uncle Garth dialogue", "Sawmill_Hideout", None, None, None, None,
		"prologue_jason_dialogue", True)
	world.addMapTransition("teleport to the mansion", "Sebastians_exterior", -59, -5, -58, -4,
							"Sebastians_exterior", 3, -1)
	#world.getCharacter("Garth").interact_script = "garthInteractScript"
	world.addMapTrigger(
		"Sebastian walks in", "Mansion01_2ndfloor", None, None, None, None,
		"triggerSebastianLootDialogue", False)
	#sebastian = world.getCharacter("Sebastian")
	#sebastian.teleport(fife.ModelCoordinate(0,-10,0), "Mansion01_2ndfloor")
	#sebastian.rotation = 225

@classmethod
def startPrologueJasonSawmill(cls, npc, pc, world):
	young_jason = world.getCharacter("Young_Jason")
	young_jason.teleport(fife.ModelCoordinate(-68,-14,0), "Ashgrove_Sawmill")
	young_jason.rotation = 0
	young_jason.sprite_override = None
	world.enablePlayerCharacter(young_jason)
	world.knowledge["jason_prologue"] = 2
	world.addMapTrigger(
		"Young Jason entering the sawmill", "Ashgrove_Sawmill", None, None, None, None,
		"prologue_jason_sawmill_dialogue", True)
	garth = world.getCharacter("Garth")
	garth.teleport(fife.ModelCoordinate(2,1,0))
	garth.sprite_override = "sleep"
	garth.interact_script = "garthInteractScript"

@staticmethod
def startPrologueJasonSawmill2(npc, pc, world):
	young_jason = world.getCharacter("Young_Jason")
	young_jason.visual.say(u"“I have no choice. I must get rid of Uncle Garth.\n\
		But he’ll just beat me up again if he sees me return empty-handed.\n\
		I better sneak in from the back.”", 6000)

@staticmethod
def enteringSawmillMonologue(npc, pc, world):
	young_jason = world.getCharacter("Young_Jason")
	young_jason.visual.say(
		u"“If he wakes up, I’m finished.\n\
		I better just slit his throat while he sleeps and then get out of the town.”", 6000)

@staticmethod
def outsideMansionMonologue(npc, pc, world):
	young_jason = world.getCharacter("Young_Jason")
	young_jason.visual.say(
		u"“*sniff* I hate this! I hate Uncle Garth, and I hate my life!\n\
			*sniff* But he’s just so strong, and I’m just too scared of him.\n\
			What could I do?”", 6000)

@classmethod
def startGarthDuel(cls, npc, pc, world):
	garth = world.getCharacter("Garth")
	if world.application.maplayer.getCellCache().getCell(
												fife.ModelCoordinate(1,0,0)).getCellType() > 1:
		garth.teleport(fife.ModelCoordinate(3,2,0))
	else:
		garth.teleport(fife.ModelCoordinate(1,0,0))
	world.application.startCombat([garth, pc])
	world.addMapTrigger("Uncle Garth defeated", "Sawmill_Hideout", None, None, None, None,
		"prologue_jason_garth_defeated_dialogue", True)
	world.knowledge["last_prologue"] = "Jason"

@classmethod
def finishJasonPrologue(cls, npc, pc, world):
	world.knowledge["jason_prologue"] = 3
	cls.continuePrologue(npc, pc, world)

#@staticmethod
#def checkReturnedToGarth(npc, pc, world):
#	return world.knowledge.get("jason_prologue") >= 2

@classmethod
def garthInteractScript(cls, npc, pc):
	#if cls.checkReturnedToGarth(npc, pc, npc.world):
	if npc.world.knowledge.get("jason_prologue") >= 2:
		npc.world.application.startCutscene(cls.GarthWakeUpCutscene)
		npc.world.addMapTrigger(
			"Uncle Garth wakes up", "Sawmill_Hideout", None, None, None, None,
			"startGarthDuel", True)
	else:
		npc.visual.say(u"“Still here? Get out and better not return empty-handed.”")

@classmethod
def mansionDoorExitScript(cls, obj, pc):
	pc.visual.say(u"“I can’t go back until I’ve found something valuable.”")
	return False

@classmethod
def radcliffeDoorInteractScript(cls, npc, pc):
	pc.visual.say(u"“This is a servant’s room.\n\
		There seems to be nothing of value, and I better not wake up the servant.”", 4000)

@classmethod
def sebastianDoorInteractScript(cls, npc, pc):
	pc.visual.say(u"“Uh-oh, the master of the house seems to be sleeping here.\n\
		I better check the other rooms first.”", 4000)

@classmethod
def hideoutDoorScript(cls, obj, pc):
	young_jason = pc.world.getCharacter("Young_Jason")
	#if cls.checkReturnedToGarth(None, pc, pc.world):
	if pc.world.knowledge.get("jason_prologue") >= 2:
		young_jason.visual.say(u"“No! I won’t run away!\n\
			I will settle this matter once and for all.”")
		return False
	else:
		young_jason.world.addMapTrigger(
			"Young Jason outside the mansion", "Sebastians_exterior", None, None, None, None,
			"prologue_jason_mansion_dialogue", True)
		young_jason.world.addMapTrigger(
			"Young Jason outside the mansion 2", "Sebastians_exterior", None, None, None, None,
			"outsideMansionMonologue", True)
		return True

@classmethod
def sawmillDoorScript(cls, obj, pc):
	pc.world.addMapTrigger(
		"Young Jason enters the sawmill hideout", "Sawmill_Hideout", None, None, None, None,
		"prologue_jason_hideout_dialogue", True)
	return True

@classmethod
def triggerSebastianLootDialogue(cls, npc, pc, world):
	if pc.inventory.hasItem("Brooch1"):
		#door_obj = pc.world.getInteractObject("mansion2f_door1")
		#door_obj.door.open(door_obj, pc)
		#sebastian = pc.world.getCharacter("Sebastian")
		#sebastian.teleport(fife.ModelCoordinate(-8,-14,0), "Mansion01_2ndfloor")
		#sebastian.teleport(fife.ModelCoordinate(-10,-12,0), "Mansion01_2ndfloor")
		#sebastian.rotation = 45
		#cls.startDialogue(pc.world, "prologue_jason_sebastian_dialogue")
		pc.world.application.startCutscene(cls.SebastianJasonCutscene)
		pc.world.removeMapTrigger("Sebastian walks in")
		pc.world.addMapTrigger(
			"Sebastian and Jason dialogue", "Mansion01_2ndfloor", None, None, None, None,
			"prologue_jason_sebastian_dialogue", True)

@classmethod
def turnAroundJasonSebastian(cls, npc, pc, world):
	young_jason = world.getCharacter("Young_Jason")
	sebastian = world.getCharacter("Sebastian")
	young_jason.rotation = 225
	young_jason.sprite_override = "dagger_idle"
	young_jason.visual.idle()
