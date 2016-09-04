# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from __future__ import division

from fife import fife

from ..cutscene import Cutscene


class InnIntroCutscene(Cutscene):
	def cutsceneScript(self):
		self.application.gui.intro_text.showFade("Two Maples Inn, Ashgrove")
		while self.elapsed_time < 6000:
			yield
		self.application.gui.intro_text.hideFade()
		while self.elapsed_time < 13000:
			yield
		radcliffe = self.application.world.getCharacter("Radcliffe")
		loc = radcliffe.visual.instance.getLocation()
		loc.setLayerCoordinates(fife.ModelCoordinate(-3,-2,0))
		radcliffe.visual.walk(loc)
		while self.elapsed_time < 18000:
			yield
		radcliffe.visual.say(u"“Good evening, young sirs and young lady.\n\
			Master Rex informed me that he will be somewhat delayed\n\
			by what he referred to as “a delicate process in his laboratory”.\n\
			He asked me to relay his sincerest expression of apologies to you\n\
			and that he will join you as soon as he is able.”", 9000)
		while self.elapsed_time < 27000:
			yield
		loc.setLayerCoordinates(fife.ModelCoordinate(-3,3,0))
		radcliffe.visual.walk(loc)
		while self.elapsed_time < 30500:
			yield
		radcliffe.rotation = 0
		while self.elapsed_time < 31000:
			yield

	def cameraScript(self):
		while self.elapsed_time < 14000:
			self.application.view.camera.getLocationRef().setExactLayerCoordinates(
					fife.ExactModelCoordinate(40 - self.elapsed_time*40/14000, 0, 0))
			yield

	script_list = [cutsceneScript, cameraScript]
	
#	def pump(self):
#		self.application.view.camera.getLocationRef().setExactLayerCoordinates(
#					fife.ExactModelCoordinate(max(0, 40 - self.elapsed_time*40/14000), 0, 0))
#		#self.generator.next()
#		super(InnIntroCutscene, self).pump()

"""
class InnIntroCutscene2(Cutscene):
	def cutsceneScript(self):
		radcliffe = self.application.world.getCharacter("Radcliffe")
		loc = radcliffe.visual.instance.getLocation()
		loc.setLayerCoordinates(fife.ModelCoordinate(-3,3,0))
		radcliffe.visual.walk(loc)
		while self.elapsed_time < 3500:
			yield
		radcliffe.rotation = 0
		while self.elapsed_time < 4000:
			yield
"""

class GarthIntroCutscene(Cutscene):
	def cutsceneScript(self):
		garth = self.application.world.getCharacter("Garth")
		young_jason = self.application.world.getCharacter("Young_Jason")
		garth.visual.attack(young_jason.visual.instance.getLocation())
		while self.elapsed_time < 1500:
			yield
		garth.visual.attack(young_jason.visual.instance.getLocation())
		while self.elapsed_time < 3000:
			yield


class SebastianJasonCutscene(Cutscene):
	def cutsceneScript(self):
		door_obj = self.application.world.getInteractObject("mansion2f_door1")
		door_obj.door.open(door_obj)
		sebastian = self.application.world.getCharacter("Sebastian")
		sebastian.teleport(fife.ModelCoordinate(-10,-12,0), "Mansion01_2ndfloor")
		yield
		loc = sebastian.visual.instance.getLocation()
		loc.setLayerCoordinates(fife.ModelCoordinate(-8,-14,0))
		sebastian.visual.walk(loc)
		while self.elapsed_time < 2500:
			yield
		sebastian.rotation = 45


class GarthWakeUpCutscene(Cutscene):
	def cutsceneScript(self):
		garth = self.application.world.getCharacter("Garth")
		garth.visual.say(u"“Ahaa, you bastard!\n\
			Thought you’d catch Uncle Garth unawares, did you?\n\
			I’ve been too patient with you, lad, for your father’s sake.\n\
			But he’s long gone, and it’s about time for you to be gone too.”", 6000)
		while self.elapsed_time < 6000:
			yield
		garth.sprite_override = None


class GilIntroCutscene(Cutscene):
	def cutsceneScript(self):
		gil = self.application.world.getCharacter("Gil")
		gil.teleport(fife.ModelCoordinate(-2,4,0), "Amelia_Engineroom")
		gil.use_combat_sprite = True
		yield
		loc = gil.visual.instance.getLocation()
		loc.setLayerCoordinates(fife.ModelCoordinate(-3,16,0))
		gil.visual.walk(loc)
		while self.elapsed_time < 4000:
			yield


class GilSmashPipesCutscene(Cutscene):
	def cutsceneScript(self):
		gil = self.application.world.getCharacter("Gil")
		loc = gil.visual.instance.getLocation()
		loc.setLayerCoordinates(fife.ModelCoordinate(0,19,0))
		gil.visual.walk(loc)
		while self.elapsed_time < 1500:
			yield
		loc.setLayerCoordinates(fife.ModelCoordinate(1,19,0))
		gil.visual.attack(loc)
		while self.elapsed_time < 2500:
			yield
		gil.inventory.hands = []


class DustySebastianIntroCutscene(Cutscene):
	def cutsceneScript(self):
		sebastian = self.application.world.getCharacter("Sebastian_Dustys")
		sebastian.teleport(fife.ModelCoordinate(-2,4,0), "Amelia_Engineroom")
		yield
		loc = sebastian.visual.instance.getLocation()
		loc.setLayerCoordinates(fife.ModelCoordinate(-3,16,0))
		sebastian.visual.walk(loc)
		while self.elapsed_time < 8000:
			yield
