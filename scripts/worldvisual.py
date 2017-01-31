# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife
#from math import floor, ceil, atan, sqrt, tan, cos
#from operator import attrgetter, methodcaller

#import gridhelper
from timeline import GameTimeline	#TacticsTimeline, Timer
#from character import Character
#from charactervisual import CharacterVisual
#from obstacle import Obstacle, ObstacleVisual

class WorldVisual(object):
	def __init__(self, application, maplayer, world):
		"""Create fife instances of all objects and the game timer. Used after loading the world."""
		self.application = application
		self.maplayer = maplayer
		self.world = world
		# create character instances and listeners
		for	character in self.world.characters:
			if character.map_name == self.world.current_map_name:
				character.createVisual()
		# create interact objects instances
		for	interact_object in self.world.interact_objects:
			#print "Creating visual:", interact_object.name
			if interact_object.map_name == self.world.current_map_name:
				#print interact_object.map_name
				interact_object.createVisual()
		# create the game timer
		self.game_timeline = GameTimeline(world.game_time, self.application)
		#self.application.engine.getTimeManager().registerEvent(self.game_timeline)

	def cleanUp(self):
		"""Call this when quitting the game."""
		self.application.engine.getTimeManager().unregisterEvent(self.game_timeline)
		for map_object in (self.world.characters + self.world.interact_objects):
			if map_object.visual:
				map_object.visual.destroy()
				map_object.visual = None

	def findCharacter(self, instance):
		"""Return the character object represented by instance."""
		for character in self.world.characters:
			if character.visual:
				if instance.getFifeId() == character.visual.instance.getFifeId():
					return character
	
	def findInteractObject(self, instance):
		"""Return the interact object represented by instance."""
		for interact_object in self.world.interact_objects:
			if interact_object.visual:
				if instance.getFifeId() == interact_object.visual.instance.getFifeId():
					return interact_object

	def findObject(self, instance):
		"""Return the object represented by instance."""
		obj = self.findCharacter(instance)
		if obj:
			return obj
		obj = self.findInteractObject(instance)
		if obj:
			return obj
