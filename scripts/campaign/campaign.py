# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

class Campaign(object):
	from characters import initCharacters
	from cutscenes import (
		InnIntroCutscene,
		#InnIntroCutscene2,
		GarthIntroCutscene,
		SebastianJasonCutscene,
		GarthWakeUpCutscene,
		GilIntroCutscene,
		GilSmashPipesCutscene,
		DustySebastianIntroCutscene
	)
	from prologue import (
		initPrologue,
		continuePrologue
		#checkFinished3Prologues,
		#checkFinishedPrologueLastJason,
		#checkFinishedPrologueLastTom,
		#checkFinishedPrologueLastDusty,
		#checkNotFinishedPrologueJason,
		#checkNotFinishedPrologueTom,
		#checkNotFinishedPrologueDusty
	)
	from prologuejason import (
		#initPrologueJason,
		startPrologueJason,
		startPrologueJasonSawmill,
		startPrologueJasonSawmill2,
		enteringSawmillMonologue,
		outsideMansionMonologue,
		startGarthDuel,
		finishJasonPrologue,
		#checkReturnedToGarth,
		mansionDoorExitScript,
		radcliffeDoorInteractScript,
		sebastianDoorInteractScript,
		garthInteractScript,
		hideoutDoorScript,
		sawmillDoorScript,
		triggerSebastianLootDialogue,
		turnAroundJasonSebastian
	)
	from prologuedusty import (
		#initPrologueDusty,
		startPrologueDusty,
		#gilSmashPipes,
		startGilFight,
		sebastianExitsEngineroom,
		sebastianEntersCabins1,
		sebastianEntersCabins2
	)
	from prologuetom import (
		startPrologueTom
	)

	@classmethod
	def init(cls, world):
		cls.initCharacters(world)
		cls.initPrologue(world)
		#cls.initPrologueJason(world)
		#cls.initPrologueDusty(world)
		
	@staticmethod
	def startDialogue(world, dialogue):
		#world.application.gui.dialogue.startDialogue(dialogue, world)
		world.application.startDialogue(dialogue)
	
	@classmethod
	def check(cls, condition, npc, pc, world):
		val = eval(condition)
		return val(npc=npc, pc=pc, world=world) if callable(val) else val
		