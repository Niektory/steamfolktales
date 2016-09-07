# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from fife import fife
#from random import randint
#from collections import defaultdict
import xml.etree.ElementTree as ET

#from timeline import Timer
#from damage import DamagePacket
import gridhelper
from charactervisual import CharacterVisual
from rpgstats import RPGStats
from rpginventory import RPGInventory
from rpgitem import loadItem
from interaction import Interaction


class Character(object):
	def __init__(self, ID, name, coords, map_name, world, sprite):
		self.world = world
		self.ID = ID
		if name == "":
			self.name = "Nameless"
		else:
			self.name = name
		if sprite == "":
			self.sprite = "Thief"
		else:
			self.sprite = sprite
		self._coords = coords
		self.map_name = map_name
		self._rotation = 0
		self.visual = None
		
		self.rpg_stats = RPGStats()
		self.inventory = RPGInventory()
		self.knowledge = {}
		self.dialogue = None
		self.interact_script = None
		self.portrait = ""
		self.dead = False
		self.killable = False
		self.behavior = []
		self.sprite_override = None
		self.use_combat_sprite = False

		# obsolete?
		self.idle_script = None
		self.tick_script = None

	def __str__(self):
		return self.name

	@property
	def player_controlled(self):
		return (self.world.player_character == self)

	@property
	def coords(self):
		self.refresh()
		return self._coords

	@coords.setter
	def coords(self, value):
		self._coords = value
		if self.visual:
			location = self.visual.instance.getLocation()
			location.setLayerCoordinates(self._coords)
			self.visual.instance.setLocation(location)

	@property
	def rotation(self):
		self.refresh()
		return self._rotation

	@rotation.setter
	def rotation(self, value):
		self._rotation = value
		if self.visual:
			self.visual.instance.setRotation(self._rotation)
			
	def refresh(self):
		if self.visual:
			self._coords = self.visual.instance.getLocation().getLayerCoordinates()
			self._rotation = self.visual.instance.getRotation()

	#def testRoute(self, dest, max_dist = 1000):
	#	if self.visual:
	#		return self.visual.testRoute(dest, max_dist)

	#def walk(self, dest, max_dist = 1000, cut_dist = 1000):
	#	if self.visual:
	#		if self.visual.instance.getCurrentAction():
	#			if self.visual.instance.getCurrentAction().getId() == "run":
	#				self.visual.run(dest, max_dist, cut_dist)
	#				return
	#		self.visual.walk(dest, max_dist, cut_dist)

	#def run(self, dest, max_dist = 1000, cut_dist = 1000, walk_mode = "run"):
	#	if self.visual:
	#		return self.visual.run(dest, max_dist, cut_dist, walk_mode)
			
	def teleport(self, coords, map_name=None):
		if map_name in (self.map_name, None):
			self.coords = coords
			if self.visual:
				self.visual.idle()
		else:
			if self.visual:
				self.visual.destroy()
				self.visual = None
			self.coords = coords
			self.map_name = map_name
			if self.map_name == self.world.current_map_name:
				self.createVisual()

	def createVisual(self):
		self.visual = CharacterVisual(self.world.application, self)
	"""
	def interact(self, pc):
		pc.idle_script = None
		if self.visual:
			if gridhelper.distance(self.coords, pc.coords) < 5:
				# if we're close we'll interact right away
				if self == pc:
					self.visual.say("I just don't know what to do with myself.", 2000)
				elif self.interact_script:
					if isinstance(self.interact_script, str):
						from campaign.campaign import Campaign
						getattr(Campaign, self.interact_script)(self, pc)
					else:
						self.interact_script(self, pc)
				else:
					self.visual.say("I have no script, and I must interact.", 2000)
			else:
				# if we're far we'll run up and interact later
				#pc.visual.run(self.visual.instance.getLocation(), cut_dist = -1)
				pc.visual.follow(self.visual.instance)
				pc.idle_script = interactAfterRun
				pc.knowledge["interact_after_run"] = self

	def talk(self, pc):
		pc.idle_script = None
		if self.visual:
			if not self.dead:
				if gridhelper.distance(self.coords, pc.coords) < 5:
					# if we're close we'll interact right away
					if self == pc:
						self.visual.say("I just don't know what to do with myself.", 2000)
					elif self.dialogue:
						self.world.application.gui.dialogue.start(self, pc)
					else:
						self.visual.say("I have no script, and I must interact.", 2000)
				else:
					# if we're far we'll run up and interact later
					#pc.visual.run(self.visual.instance.getLocation(), cut_dist = -1)
					pc.visual.follow(self.visual.instance)
					pc.idle_script = talkAfterRun
					pc.knowledge["interact_after_run"] = self
	"""
	#def attack(self, target):
	#	if self.visual:
	#		self.visual.attack(target)

	#def idle(self):
	#	if self.visual:
	#		self.visual.idle()

	#def idle_caller(self):
	#	self.idle_script(self)

	def die(self):
		self.dead = True
		#self.inventory.unequipAll()	# no weapon looting for now
		if self.visual:
			self.visual.die()
	
	#def loot(self, pc):
	#	self.world.application.gui.looting.show(pc, self)

	@property
	def possible_actions(self):
		actions = []
		if self.dead:
			actions.append(Interaction(self, "Loot", 1.5))
		else:
			if self.interact_script:
				actions.append(Interaction(self, "Interact", 1.5))
			if self.dialogue:
				actions.append(Interaction(self, "Talk", 5))
			if self.killable:
				actions.append(Interaction(self, "Kill", 1.5))
		return actions

	#def act(self, action, pc):
	#	if action == "Interact":
	#		self.interact(pc)
	#	elif action == "Talk":
	#		self.talk(pc)
	#	elif action == "Loot":
	#		self.loot(pc)

	@property
	def martial_art_used(self):
		# return the martial art associated with the currently held weapon
		# but only if we have ranks if the proper skill
		if self.inventory.hands:
			martial_art = self.inventory.hands[0].weapon_data.martial_art
		else:
			martial_art = "Victorian Pugilism"
		return martial_art if self.rpg_stats.skills.get(martial_art) else None

	#def isUsingMartialArt(self, martial_art):
	#	if not self.rpg_stats.skills.get(martial_art):
	#		# no ranks in the skill
	#		return False
	#	if self.inventory.hands:
	#		# holding a weapon, check if proper type for this martial art
	#		return martial_art == self.inventory.hands[0].weapon_data.martial_art
	#	else:
	#		# no weapon, check if this martial art can be used unarmed
	#		return martial_art == "Victorian Pugilism"

	@classmethod
	def loadXML(cls, ID, filename, world):
		tree = ET.parse(filename)
		root = tree.getroot()
		if root.tag != "Character":
			return
		name = root.attrib["name"]
		sprite = root.attrib.get("sprite", "")
		map_name = root.attrib.get("map", "")
		x = root.attrib.get("x")
		y = root.attrib.get("y")
		if x is not None and y is not None:
			coords = fife.ModelCoordinate(int(x),int(y),0)
		else:
			coords = None
		character = cls(ID=ID, name=name, coords=coords, map_name=map_name, world=world,
						sprite=sprite)
		character.portrait = root.attrib.get("portrait", "")
		character.behavior = root.attrib.get("behavior", "").split(",")
		character.dialogue = root.attrib.get("dialogue")
		character.killable = root.attrib.get("killable") == "1"
		rotation = root.attrib.get("rotation")
		if rotation is not None:
			character.rotation = rotation
		character.interact_script = root.attrib.get("interact_script")
		for element in root:
			if element.tag == "Inventory":
				for slot_element in element:
					if slot_element.tag == "Hands":
						for item_element in slot_element:
							if item_element.tag == "Item":
								character.inventory.hands.append(
													loadItem(item_element.attrib["ID"]))
					elif slot_element.tag == "Head":
						for item_element in slot_element:
							if item_element.tag == "Item":
								character.inventory.head.append(
													loadItem(item_element.attrib["ID"]))
					elif slot_element.tag == "Body":
						for item_element in slot_element:
							if item_element.tag == "Item":
								character.inventory.body.append(
													loadItem(item_element.attrib["ID"]))
					elif slot_element.tag == "Backpack":
						for item_element in slot_element:
							if item_element.tag == "Item":
								character.inventory.addItem(item_element.attrib["ID"])
			elif element.tag == "Knowledge":
				character.knowledge[element.attrib["key"]] = element.attrib["value"]
			elif element.tag == "Stats":
				for stat_element in element:
					if stat_element.tag == "Attributes":
						for attr in character.rpg_stats.attribute_names:
							character.rpg_stats.attributes[attr] = int(stat_element.attrib[attr])
					elif stat_element.tag == "Skills":
						for skill_element in stat_element:
							if skill_element.tag == "Skill":
								character.rpg_stats.skills[skill_element.attrib["name"]] = \
														int(skill_element.attrib["rank"])
		return character


def loadCharacter(ID, world):
	return Character.loadXML(ID, "campaign_data/characters/" + ID + ".xml", world)
	
