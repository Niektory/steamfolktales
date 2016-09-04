# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from fife import fife
from inspect import isclass

import gridhelper
import npcbehaviors
from cutscene import Cutscene
from dialogue import loadDialogue
from campaign.campaign import Campaign

class Exploration(object):
	def __init__(self, application):
		self.application = application
		self.pc_action = None
		
	def move(self, location):
		pc = self.application.current_character	# shortcut
		pc.visual.run(location, walk_mode=self.application.gui.hud.walk_mode)
		self.pc_action = None
	
	def act(self, action):
		pc = self.application.current_character	# shortcut
		pc.idle_script = None
		if not action.target.visual:
			return
		if gridhelper.distance(action.target.coords, pc.coords) <= action.max_distance:
			# if we're close we'll interact right away
			pc.visual.idle()
			if action.name == "Interact":
				if isinstance(action.target.interact_script, str):
					from campaign.campaign import Campaign	# FIXME: import in a method
					getattr(Campaign, action.target.interact_script)(action.target, pc)
				else:
					action.target.interact_script(action.target, pc)
			elif action.name == "Talk":
				#self.application.gui.dialogue.start(action.target, pc)
				self.application.startDialogue(action.target.dialogue, npc=action.target, pc=pc)
			elif action.name == "Loot":
				self.application.gui.looting.show(pc, action.target)
			elif action.name == "Enter":
				if action.target.portal.script is not None:
					if isinstance(action.target.portal.script, str):
						from campaign.campaign import Campaign	# FIXME: import in a method
						allow = getattr(Campaign, action.target.portal.script)(action.target, pc)
					else:
						allow = action.target.portal.script(action.target, pc)
					if not allow:
						return
				pc.teleport(action.target.portal.coords, action.target.portal.map_name)
				if action.target.portal.rotation is not None:
					pc.rotation = action.target.portal.rotation
			elif action.name == "Pick lock":
				if not pc.inventory.hasItem("Lockpicks"):
					pc.visual.say("I can't do it without lockpicks.")
				elif action.target.lock.pick(pc):
					action.target.visual.say("Lock picked!")
				else:
					action.target.visual.say("Lockpicking failed!")
			elif action.name == "Open":
				action.target.door.open(action.target, pc)
			elif action.name == "Close":
				action.target.door.close(action.target, pc)
			else:
				pc.visual.say("I don't know how to " + action.name + " " + action.target.name + "!")
		else:
			# if we're far we'll run up and interact later
			#pc.visual.run(self.visual.instance.getLocation(), cut_dist = -1)
			pc.visual.follow(action.target.visual.instance,
							walk_mode=self.application.gui.hud.walk_mode)
			self.pc_action = action
			
	def pump(self, frame_time):
		pc = self.application.current_character	# shortcut
		# triggers
		if self.application.current_character:
			trigger = self.application.world.findMapTriggerAt(
												self.application.current_character.coords)
			transition = self.application.world.findMapTransitionAt(
												self.application.current_character.coords)
			if transition:
				self.application.current_character.teleport(fife.ModelCoordinate(
						transition.dest_x, transition.dest_y, 0), transition.dest_map)
			# game over on PC death
			if self.application.current_character.dead:
				self.application.gameOver()
				return
			# map change on PC teleport
			if self.application.current_character.map_name \
												!= self.application.world.current_map_name:
				self.application.prepareChangeMap(self.application.current_character.map_name)
		else:
			trigger = self.application.world.findMapTriggerAt(None)
		if trigger:
			if callable(trigger.action):
				trigger.action(self.application.current_character)
			elif hasattr(Campaign, trigger.action):
				action = getattr(Campaign, trigger.action)
				if isclass(action) and issubclass(action, Cutscene):
					self.application.startCutscene(action)
				elif callable(action):
					action(self.application.current_character, self.application.current_character,
							self.application.world)
			else:
				dialogue = loadDialogue(trigger.action)
				if dialogue:
					Campaign.startDialogue(self.application.world, dialogue)
				else:
					print("error in trigger:", trigger, trigger.action)
			if trigger.remove_after_firing:
				self.application.world.removeMapTrigger(trigger)
		# return if no controllable pc
		if not pc or not pc.visual:
			return
		# NPC behaviors
		for character in self.application.world.characters:
			if character.dead:
				continue
			if character.map_name != self.application.world.current_map_name:
				continue
			for behavior in character.behavior:
				if behavior == "detect":
					if npcbehaviors.detect(character, frame_time):
						break
					else:
						continue
				elif behavior == "wander":
					if npcbehaviors.wander(character, frame_time):
						break
					else:
						continue
		# interaction
		if self.pc_action and gridhelper.distance(
						self.pc_action.target.coords, pc.coords) < self.pc_action.max_distance:
			self.act(self.pc_action)
			self.pc_action = None
			
