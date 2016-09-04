# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from __future__ import division

#from fife import fife
#from math import floor, ceil, atan, sqrt, tan, cos
#from operator import attrgetter, methodcaller

#from timeline import TacticsTimeline, Timer
#from playercharacter import PlayerCharacter
#from nonplayercharacter import NonPlayerCharacter
from character import Character, loadCharacter
#from charactervisual import CharacterVisual
from interactobject import InteractObject, loadInteractObject


class Transition(object):
	def __init__(self, name, map, left, top, right, bottom, dest_map, dest_x, dest_y):
		self.name = name
		self.map = map
		self.left = left
		self.top = top
		self.right = right
		self.bottom = bottom
		self.dest_map = dest_map
		self.dest_x = dest_x
		self.dest_y = dest_y


class Trigger(object):
	def __init__(self, name, map, left, top, right, bottom, action, remove_after_firing):
		self.name = name
		self.map = map
		self.left = left
		self.top = top
		self.right = right
		self.bottom = bottom
		self.action = action
		self.remove_after_firing = remove_after_firing


class World(object):
	"""Contains all current game data. Saved and loaded to disk by the serializer."""
	def __init__(self, application, map_name=""):
		self.application = application
		#self.maplayer = maplayer
		self.visual = None
		self.current_map_name = map_name

		self.player_character = None
		self.characters = []	# list of all characters
		self.interact_objects = []	# list of all interact objects (doors etc.)
		#self.object_counter = 0	# increases when creating objects; used to assign object IDs
		self._game_time = 0	# in-game time in miliseconds
		self.knowledge = {}	# campaign variables
		self.map_transitions = []
		self.map_triggers = []

	@property
	def game_time(self):
		self.refresh()
		return self._game_time

	@game_time.setter
	def game_time(self, value):
		self._game_time = value
		if self.visual:
			self.visual.game_timeline.time = self._game_time

	def getHour(self):
		"""Returns the current hour as float. Range: <0.0, 24.0)"""
		return (self.game_time % 86400000) / 3600000

	def getDay(self):
		"""Returns the current day as int, starting from 1."""
		return self.game_time // 86400000 + 1

	def advanceTime(self, time_delta):
		"""Manually advance the time. Bypasses pause."""
		self.game_time = self.game_time + time_delta

	def refresh(self):
		"""Updates the world state from visuals. Call this before saving the game."""
		for character in self.characters:
			character.refresh()
		if self.visual:
			self._game_time = self.visual.game_timeline.time

	#def assignID(self, obj):
	#	obj.ID = self.object_counter
	#	self.object_counter += 1

	#def findObjectByID(self, ID):
	#	for character in self.characters:
	#		if character.ID == ID:
	#			return character
	#	for obstacle in self.obstacles:
	#		if obstacle.ID == ID:
	#			return obstacle
	
	def getCharacter(self, ID):
		for character in self.characters:
			if character.ID == ID:
				return character

	def getInteractObject(self, ID):
		for interact_object in self.interact_objects:
			if interact_object.ID == ID:
				return interact_object

	def addInteractObjectAt(self, coords, map_name, ID, name, sprite, obj_type=InteractObject,
							lock=None):
		interact_object = obj_type(ID, name, coords, map_name, self, sprite, lock=lock)
		#self.assignID(interact_object)
		if self.visual and self.current_map_name == map_name:
			interact_object.createVisual()
		self.interact_objects.append(interact_object)
		return interact_object

	def addInteractObject(self, interact_object):
		if self.visual and self.current_map_name == interact_object.map_name:
			interact_object.createVisual()
		self.interact_objects.append(interact_object)

	def enablePlayerCharacter(self, character):
		if self.visual and self.current_map_name == character.map_name:
			self.application.camera.attach(character.visual.instance)
		self.player_character = character

	def disablePlayerCharacter(self):
		self.player_character = None

	def addCharacterAt(self, coords, map_name, ID, name="", sprite=""):
		#if not self.application.maplayer.getCellCache().getCell(coords):
		#	return
		#if self.application.maplayer.getCellCache().getCell(coords).getCellType() > 1:
		#	return
		character = Character(ID, name, coords, map_name, self, sprite)
		#self.assignID(character)
		if self.visual and self.current_map_name == map_name:
			character.createVisual()
		self.characters.append(character)
		return character
	
	def addCharacter(self, character):
		if self.visual and self.current_map_name == character.map_name:
			character.createVisual()
		self.characters.append(character)
	
	def loadCharacter(self, ID):
		self.addCharacter(loadCharacter(ID, self))
	
	def loadInteractObject(self, ID):
		self.addInteractObject(loadInteractObject(ID, self))
	
	def findCharacterAt(self, coords):
		for character in self.characters:
			if character.coords is not None:
				if character.coords == coords:
					return character

	def addMapTransition(self, name, map, left, top, right, bottom, dest_map, dest_x, dest_y):
		self.map_transitions.append(
					Transition(name, map, left, top, right, bottom, dest_map, dest_x, dest_y))
	
	def findMapTransitionAt(self, coords):
		for transition in self.map_transitions:
			if self.current_map_name != transition.map:
				continue
			if not (transition.left <= coords.x <= transition.right):
				continue
			if not (transition.top <= coords.y <= transition.bottom):
				continue
			return transition

	def addMapTrigger(self, name, map, left, top, right, bottom, script, remove_after_firing=False):
		self.map_triggers.append(
					Trigger(name, map, left, top, right, bottom, script, remove_after_firing))
	
	def removeMapTrigger(self, trigger):
		if isinstance(trigger, str):
			for map_trigger in self.map_triggers:
				if map_trigger.name == trigger:
					self.map_triggers.remove(map_trigger)
					return
		else:
			self.map_triggers.remove(trigger)

	def findMapTriggerAt(self, coords):
		for trigger in self.map_triggers:
			if self.current_map_name != trigger.map:
				continue
			if trigger.left is None:
				return trigger
			elif coords is None:
				continue
			if not (trigger.left <= coords.x <= trigger.right):
				continue
			if not (trigger.top <= coords.y <= trigger.bottom):
				continue
			return trigger
