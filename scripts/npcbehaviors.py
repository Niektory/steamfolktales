# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from __future__ import division

from fife import fife
from random import randrange

import gridhelper


def wander(self, time):
	if randrange(400) or (self.visual.state == self.visual.STATE_RUN2):
		#self.visual.instance.actOnce("idle")
		return
	location = self.visual.instance.getLocation()
	rect = map(int, self.knowledge["wander_rect"].split(","))
	while True:
		coords = location.getLayerCoordinates()
		coords.x = randrange(rect[0], rect[2]+1)
		coords.y = randrange(rect[1], rect[3]+1)
		if location.getLayer().getCellCache().getCell(coords).getCellType() <= 1:
			location.setLayerCoordinates(coords)
			self.visual.walk(location)
			break

def detect(self, time):
	# abort if in combat or dead
	if self.visual.combat:
		return
	pc = self.visual.application.current_character
	if pc.dead:
		return
	#self.knowledge["prev.suspicion"] = self.knowledge.get("suspicion", 0)
	# measure distance and angle
	dist = gridhelper.distance(self.coords, pc.coords)
	#if dist > 16:
	#	return
	angle = gridhelper.angleDifference(self.rotation,
				fife.getAngleBetween(self.visual.instance.getLocation(),
				pc.visual.instance.getLocation()))
	# increase suspicion based on time delta, angle, distance, sneak skill, movement
	stealth_rating = (pc.rpg_stats.skillTotal("Stealth").value
		- self.rpg_stats.attributeModifier("WIT") - 6)
	if pc.visual.state == pc.visual.STATE_IDLE:
		v_increment = 2.5 - stealth_rating / 8
		a_increment = 1.0 - stealth_rating / 8
	elif pc.visual.sneaking:
		v_increment = 2.5 - stealth_rating / 8
		a_increment = 2.0 - stealth_rating / 8
		if self.visual.state != self.visual.STATE_IDLE:
			a_increment -= stealth_rating / 8
	else:
		v_increment = 2.5
		a_increment = 2.0
	v_increment -= angle / 90 + dist / 8
	a_increment -= dist / 8
	if angle > 105:
		v_increment = 0
	# check line of sight
	cells = self.visual.application.maplayer.getCellCache().getCellsInLine(self.coords, pc.coords)
	for cell in cells[1:-1]:
		if cell.getCellType() > 1:
			v_increment = 0.0
	#a_increment = 0
	# final increment
	increment = max(0, v_increment) + max(0, a_increment)
	# display and decrease suspicion based on time delta
	"""
	if self.knowledge.get("suspicion"):
		if 4000 <= self.knowledge["suspicion"] or 1.5 <= increment:
			#self.visual.say(str(int(self.knowledge["suspicion"])), 200, "[colour='FFFF0000']")
			self.visual.say(u"“Who's there?”", 2000, "[colour='FFFF0000']")
			self.visual.application.gui.global_tooltip.printMessage(self.name + " suspicion: " +
						str(int(self.knowledge["suspicion"])), "[colour='FFFF0000']")
		elif 2000 <= self.knowledge["suspicion"] < 4000 or 1 <= increment < 1.5:
			#self.visual.say(str(int(self.knowledge["suspicion"])), 200, "[colour='FFFFFF00']")
			self.visual.say(u"“What was that?”", 2000, "[colour='FFFF8000']")
			self.visual.application.gui.global_tooltip.printMessage(self.name + " suspicion: " +
						str(int(self.knowledge["suspicion"])), "[colour='FFFF8000']")
		elif 1000 <= self.knowledge["suspicion"] < 2000 or 0.6 <= increment < 1:
			self.visual.say(u"?", 200, "[colour='FFFF8000']")
			self.visual.application.gui.global_tooltip.printMessage(self.name + " suspicion: " +
						str(int(self.knowledge["suspicion"])), "[colour='FFFF8000']")
		elif 500 <= self.knowledge["suspicion"] < 1000 or 0.2 <= increment < 0.6:
			self.visual.say(u"?", 200, "[colour='FFFFFF00']")
			self.visual.application.gui.global_tooltip.printMessage(self.name + " suspicion: " +
						str(int(self.knowledge["suspicion"])), "[colour='FFFFFF00']")
		else:
			self.visual.application.gui.global_tooltip.printMessage(self.name + " suspicion: " +
						str(int(self.knowledge["suspicion"])))
		#if self.knowledge["suspicion"] <= self.knowledge["prev.suspicion"]:
		self.knowledge["suspicion"] -= time / 3.0
		if self.knowledge["suspicion"] < 0:
			self.knowledge["suspicion"] = 0
	"""
	#if increment < 0.001:
	#	return
	self.knowledge["suspicion"] = self.knowledge.get("suspicion", 0) + increment * time
	#return
	if 6000 <= self.knowledge["suspicion"] or 1.5 <= v_increment:
		# threshold reached, start combat
		combatants = [pc, self]
		for character in self.world.characters:
			if character in combatants:
				continue
			if character.dead:
				continue
			if not character.killable:
				continue
			if character.map_name != self.map_name:
				continue
			if gridhelper.distance(self.coords, character.coords) > 15:
				continue
			combatants.append(character)
		self.world.application.startCombat(combatants)
	elif 4000 <= self.knowledge["suspicion"] or 1.0 <= v_increment or 1.0 <= a_increment:
		# investigate the player's location
		self.visual.say(u"“Who's there?”", 2000, "[colour='FFFF0000']")
		pc.visual.say(u"!!", 200, "[colour='FFFF0000']")
		#self.visual.application.gui.global_tooltip.printMessage(self.name + " suspicion: " +
		#			str(int(self.knowledge["suspicion"])), "[colour='FFFF0000']")
		pc.world.application.gui.detectionBar(pc.visual.instance,
				4 + max(self.knowledge["suspicion"] / 6000, v_increment / 1.5),
				max(self.knowledge["suspicion"] / 6000, v_increment / 1.5), "FFFF0000")
		pc.world.application.gui.detectionBar(self.visual.instance,
				4 + max(self.knowledge["suspicion"] / 6000, v_increment / 1.5),
				max(self.knowledge["suspicion"] / 6000, v_increment / 1.5), "FFFF0000")
		self.knowledge["prev.investigate"] = self.knowledge.get(
													"investigate", fife.ModelCoordinate(0,0,0))
		self.knowledge["investigate"] = pc.visual.instance.getLocation().getLayerCoordinates()
		if self.knowledge["investigate"] != self.knowledge["prev.investigate"]:
			location = pc.visual.instance.getLocation()
			location.setLayerCoordinates(self.knowledge["investigate"])
			self.visual.walk(location)
	elif 2000 <= self.knowledge["suspicion"] or 1.0 <= increment:
		# turn to face the player
		self.visual.say(u"“What was that?”", 2000, "[colour='FFFF8000']")
		pc.visual.say(u"!", 200, "[colour='FFFF8000']")
		pc.world.application.gui.detectionBar(pc.visual.instance,
				2 + max(self.knowledge["suspicion"] / 4000, v_increment / 1, a_increment / 1),
				max(self.knowledge["suspicion"] / 4000, v_increment / 1, a_increment / 1),
				"FFFF8000")
		pc.world.application.gui.detectionBar(self.visual.instance,
				2 + max(self.knowledge["suspicion"] / 4000, v_increment / 1, a_increment / 1),
				max(self.knowledge["suspicion"] / 4000, v_increment / 1, a_increment / 1),
				"FFFF8000")
		#self.visual.application.gui.global_tooltip.printMessage(self.name + " suspicion: " +
		#			str(int(self.knowledge["suspicion"])), "[colour='FFFF8000']")
		self.visual.instance.setFacingLocation(pc.visual.instance.getLocation())
	elif 1000 <= self.knowledge["suspicion"] or 0.6 <= increment:
		self.visual.say(u"?", 200, "[colour='FFFF8000']")
		pc.visual.say(u"?", 200, "[colour='FFFF8000']")
		pc.world.application.gui.detectionBar(pc.visual.instance,
				max(self.knowledge["suspicion"] / 2000, increment / 1),
				max(self.knowledge["suspicion"] / 2000, increment / 1), "FFFF8000")
		pc.world.application.gui.detectionBar(self.visual.instance,
				max(self.knowledge["suspicion"] / 2000, increment / 1),
				max(self.knowledge["suspicion"] / 2000, increment / 1), "FFFF8000")
		#self.visual.application.gui.global_tooltip.printMessage(self.name + " suspicion: " +
		#			str(int(self.knowledge["suspicion"])), "[colour='FFFF8000']")
	elif 500 <= self.knowledge["suspicion"] or 0.2 <= increment:
		self.visual.say(u"?", 200, "[colour='FFFFFF00']")
		pc.visual.say(u"?", 200, "[colour='FFFFFF00']")
		pc.world.application.gui.detectionBar(pc.visual.instance,
				max(self.knowledge["suspicion"] / 2000, increment / 1),
				max(self.knowledge["suspicion"] / 2000, increment / 1), "FFFFFF00")
		pc.world.application.gui.detectionBar(self.visual.instance,
				max(self.knowledge["suspicion"] / 2000, increment / 1),
				max(self.knowledge["suspicion"] / 2000, increment / 1), "FFFFFF00")
		#self.visual.application.gui.global_tooltip.printMessage(self.name + " suspicion: " +
		#			str(int(self.knowledge["suspicion"])), "[colour='FFFFFF00']")
	#else:
	#	self.visual.application.gui.global_tooltip.printMessage(self.name + " suspicion: " +
	#				str(int(self.knowledge["suspicion"])), "[colour='FFFFFFFF']")
	#if self.knowledge["suspicion"] <= self.knowledge["prev.suspicion"]:
	self.knowledge["suspicion"] -= time / 3
	if self.knowledge["suspicion"] < 0:
		self.knowledge["suspicion"] = 0
	#self.visual.sayAdd("\n+" + str(int(increment*100)))
	#self.visual.application.gui.global_tooltip.printMessage(
	#							" (+" + str(int(increment*1000)) + ")\n")
