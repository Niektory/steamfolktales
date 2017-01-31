# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from __future__ import print_function

from fife import fife
from random import randrange

from timeline import Timer
#from damage import DamagePacket
#import gridhelper
from campaign.campaign import Campaign
from error import LogExceptionDecorator

class CharacterListener(fife.InstanceActionListener):
	"""Receives fife events related to the character."""
	def __init__(self, character):
		fife.InstanceActionListener.__init__(self)
		self.character = character

	@LogExceptionDecorator
	def onInstanceActionFinished(self, instance, action):
		self.character.onInstanceActionFinished(action)

	@LogExceptionDecorator
	def onInstanceActionCancelled(self, instance, action):
		return

	@LogExceptionDecorator
	def onInstanceActionFrame(self, instance, action, frame):
		self.character.onInstanceActionFrame(action, frame)

class CharacterTimer(fife.TimeEvent):
	def __init__(self, character):
		super(CharacterTimer, self).__init__(0)
		self.character = character

	@LogExceptionDecorator
	def updateEvent(self, time):
		"""Called by FIFE. time = miliseconds since last update."""
		if self.character.visual.application.paused:
			return
		if self.character.visual.application.combat:
			return
		if self.character.dead:
			return
		if self.character.tick_script:
			getattr(Campaign, self.character.tick_script)(self.character, time)
		if self.character.idle_script and (
							self.character.visual.state == self.character.visual.STATE_IDLE):
			self.character.idle_script(self.character)

class CharacterVisual(object):
	STATE_IDLE, STATE_RUN1, STATE_RUN2, STATE_SCRIPT = range(4)
	
	def __init__(self, application, character):
		self.application = application
		self.character = character
		self.listener = CharacterListener(self)
		self.instance = self.application.maplayer.getInstance("c:" + self.character.ID)
		if self.instance:
			if self.character.coords is None:
				self.character.coords = self.instance.getLocation().getLayerCoordinates()
			else:
				location = self.instance.getLocation()
				location.setLayerCoordinates(self.character.coords)
				self.instance.setLocation(location)
				self.instance.setRotation(self.character.rotation)
		else:
			if self.character.coords is None:
				print("Error creating instance for", self.character.ID, self.character.name)
			else:
				self.instance = self.application.maplayer.createInstance(
						self.application.model.getObject(
						self.character.sprite, "steamfolktales"), self.character.coords)
				fife.InstanceVisual.create(self.instance)
				self.instance.setRotation(self.character.rotation)
		self.instance.addActionListener(self.listener)
		self.state = self.STATE_IDLE
		self.combat = None
		self.sneaking = False #self.application.gui.hud.walk_mode == "sneak"
		self.application.real_timeline.addTimer(Timer("idle " + self.character.name,
														action=self.idle))
		self.timer = CharacterTimer(self.character)
		self.application.engine.getTimeManager().registerEvent(self.timer)

	#@property
	#def sneaking(self):
	#	return self.application.gui.hud.walk_mode == "sneak"

	def onInstanceActionFinished(self, action):
		if self.state == self.STATE_RUN1:
			print(self.character.name, "out of control!")
		self.idle()

	def onInstanceActionFrame(self, action, frame):
		if self.combat:
			self.combat.onTargetHit()

	def idle(self):
		if self.combat:
			self.combat.animationFinished(self.character)
		#if self.character.idle_script:
		#	self.state = self.STATE_SCRIPT
		#	self.character.idle_caller()
		#else:
		self.state = self.STATE_IDLE
		if self.character.dead:
			self.instance.actRepeat("dead")
		elif self.combat or self.character.use_combat_sprite:
			self.instance.actRepeat(self.character.inventory.weapon_sprite + "_idle")
		elif self.sneaking:
			self.instance.actRepeat("sneak_idle")
		elif self.character.sprite_override:
			self.instance.actRepeat(self.character.sprite_override)
		else:
			self.instance.actRepeat("idle")

	#def pump(self):
	#	if not self.character.idle_script:
	#		return
	#	if self.state != self.STATE_IDLE:
	#		return
	#	#self.state = self.STATE_SCRIPT
	#	self.character.idle_script(self.character)

	def attack(self, target):
		self.instance.actOnce(self.character.inventory.weapon_sprite + "_attack", target)
		if self.combat:
			self.combat.animations.append(self.character)
		
	def testRoute(self, dest, max_dist = 1000):
		if not self.application.maplayer.getCellCache().getCell(dest.getLayerCoordinates()):
			return
		if self.application.maplayer.getCellCache().getCell(
					dest.getLayerCoordinates()).getCellType() > 1:
			# destination blocked, aborting
			return
		route = self.instance.getObject().getPather().createRoute(
					self.instance.getLocation(), dest, True)
		if route.getRouteStatus() == 4:
			# route failed, aborting
			return
		elif route.getRouteStatus() == 3:
			# route solved, returning length
			if (len(route.getPath()) - 1) > max_dist:
				return
			return len(route.getPath()) - 1
		else:
			# this shouldn't happen
			print("WARNING: RouteStatus:", route.getRouteStatus())

	def walk(self, dest, max_dist = 1000, cut_dist = 1000):
		if self.instance.getCurrentAction():
			if self.instance.getCurrentAction().getId() == "run":
				self.run(dest, max_dist, cut_dist)
				return
		self.run(dest, max_dist, cut_dist, "walk")

	def run(self, dest, max_dist = 1000, cut_dist = 1000, walk_mode="run"):
		if self.state == self.STATE_RUN1:
			# this shouldn't happen
			print("ABORT!", self.character.name)
			return
		# check if the route is clear first
		route = self.instance.getObject().getPather().createRoute(
					self.instance.getLocation(), dest, True)
		if route.getRouteStatus() == 4:
			# route failed, aborting
			return
		elif route.getRouteStatus() == 3:
			# route solved, moving after checking distance
			if (len(route.getPath()) - 1) > max_dist:
				return
			if cut_dist > 0:
				if (len(route.getPath()) - 1) > cut_dist:
					route.cutPath(cut_dist + 1)
			else:
				route.cutPath(len(route.getPath()) + cut_dist)
			route.setRotation(self.instance.getRotation())
			self.state = self.STATE_RUN1
			# FIXME: using .follow instead of .move causes jerking for one frame (fixed?)
			if self.combat or self.character.use_combat_sprite:
				#self.instance.move(
				#			self.character.inventory.weapon_sprite+"_walk", route.getEndNode(),
				#			self.application.settings.get("gameplay", "RunSpeed", 4.0))
				self.instance.follow(
							self.character.inventory.weapon_sprite+"_walk", route,
							self.application.settings.get("gameplay", "RunSpeed", 4.0))
			elif walk_mode == "run":
				#self.instance.move("run", route.getEndNode(),
				#			self.application.settings.get("gameplay", "RunSpeed", 4.0))
				self.instance.follow("run", route,
							self.application.settings.get("gameplay", "RunSpeed", 4.0))
			elif walk_mode == "walk":
				#self.instance.move("walk", dest,
				#			self.application.settings.get("gameplay", "WalkSpeed", 1.8))
				self.instance.follow("walk", route,
							self.application.settings.get("gameplay", "WalkSpeed", 1.8))
			else:
				#self.instance.move(self.character.inventory.weapon_sprite+"_walk", dest,
				#			self.application.settings.get("gameplay", "WalkSpeed", 1.8))
				self.instance.follow("sneak_walk", route,
							self.application.settings.get("gameplay", "WalkSpeed", 1.8))
			self.state = self.STATE_RUN2
			if self.combat:
				self.combat.animations.append(self.character)
			return len(route.getPath()) - 1
		else:
			# this shouldn't happen
			print("WARNING: RouteStatus:", route.getRouteStatus())

	def follow(self, target, walk_mode="run"):
		if self.state == self.STATE_RUN1:
			# this shouldn't happen
			print("ABORT!", self.character.name)
			return
		self.state = self.STATE_RUN1
		if self.combat:
			self.instance.follow(
						self.character.inventory.weapon_sprite+"_walk", target,
						self.application.settings.get("gameplay", "RunSpeed", 4.0))
		elif walk_mode == "run":
			self.instance.follow("run", target,
						self.application.settings.get("gameplay", "RunSpeed", 4.0))
		elif walk_mode == "walk":
			self.instance.follow("walk", target,
						self.application.settings.get("gameplay", "WalkSpeed", 1.8))
		else:
			self.instance.follow("sneak_walk", target,
						self.application.settings.get("gameplay", "WalkSpeed", 1.8))
		#self.instance.follow("walk", target,
		#				self.application.settings.get("gameplay", "WalkSpeed", 1.8))
		self.state = self.STATE_RUN2

	def die(self):
		self.instance.actOnce("die")
		if self.combat:
			self.combat.animations.append(self.character)
		
	def enterCombat(self, combat):
		self.combat = combat
		self.idle()
		
	def leaveCombat(self):
		self.combat = None
		self.idle()
		
	def displayStats(self):
		char_msg = ""
		char_msg += "I'm " + str(self.character.name) + "."
		self.application.gui.sayBubble(self.instance, char_msg)

	def destroy(self):
		self.instance.getLocation().getLayer().deleteInstance(self.instance)
		self.application.engine.getTimeManager().unregisterEvent(self.timer)

	def say(self, text, time=2000, color=""):
		self.application.gui.sayBubble(self.instance, text, time, color)

	def sayAdd(self, text):
		self.application.gui.sayBubbleAdd(self.instance, text)
