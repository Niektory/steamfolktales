# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from __future__ import print_function

from fife import fife
import xml.etree.ElementTree as ET

import gridhelper
from rpginventory import RPGInventory
from interaction import Interaction
from lock import Lock


class InteractObject(object):
	def __init__(self, ID, name, coords, map_name, world, sprite):
		self.world = world
		self.ID = ID
		if name == "":
			self.name = "Nameless"
		else:
			self.name = name
		if sprite == "":
			self.sprite = "Watermill_Door"
		else:
			self.sprite = sprite
		self._coords = coords
		self.map_name = map_name
		self._rotation = 0
		self.visual = None
		
		self.knowledge = {}
		self.interact_script = None
		self.lock = None
		self.portal = None
		self.door = None
		self.inventory = None

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
		
	def createVisual(self):
		self.visual = InteractObjectVisual(self.world.application, self)

	@property
	def possible_actions(self):
		actions = []
		if self.interact_script:
			actions.append(Interaction(self, "Interact", 1.5))
		elif self.lock and self.lock.locked:
			actions.append(Interaction(self, "Pick lock", 1.5))
		else:
			if self.door:
				if self.door.closed:
					actions.append(Interaction(self, "Open", 1.5))
				else:
					actions.append(Interaction(self, "Close", 1.5))
			if self.inventory:
				actions.append(Interaction(self, "Loot", 1.5))
			if self.portal:
				actions.append(Interaction(self, "Enter", 1.5))
		return actions

	@classmethod
	def loadXML(cls, ID, filename, world):
		tree = ET.parse(filename)
		root = tree.getroot()
		if root.tag != "InteractObject":
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
		interact_object = cls(ID=ID, name=name, coords=coords, map_name=map_name, world=world,
								sprite=sprite)
		interact_object.interact_script = root.attrib.get("interact_script")
		for element in root:
			if element.tag == "Inventory":
				interact_object.inventory = RPGInventory()
				for item_element in element:
					if item_element.tag == "Item":
						interact_object.inventory.addItem(item_element.attrib["ID"])
			elif element.tag == "Door":
				interact_object.door = Door(closed = element.attrib.get("closed") != "0")
			elif element.tag == "Portal":
				coords = fife.ModelCoordinate(
						int(element.attrib["x"]), int(element.attrib["y"]), 0)
				map_name = element.attrib.get("map")
				rotation = element.attrib.get("rotation")
				if rotation is not None:
					rotation = int(rotation)
				script = element.attrib.get("script")
				interact_object.portal = Portal(coords=coords, map_name=map_name,
												rotation=rotation, script=script)
			elif element.tag == "Lock":
				matching_key = element.attrib.get("matching_key")
				difficulty = int(element.attrib.get("difficulty", 0))
				locked = element.attrib.get("locked") != "0"
				interact_object.lock = Lock(matching_key=matching_key, difficulty=difficulty,
											locked=locked)
			else:
				print("Unknown tag:", element.tag)
		return interact_object


def loadInteractObject(ID, world):
	return InteractObject.loadXML(ID, "campaign_data/interact_objects/" + ID + ".xml", world)
	

class InteractObjectVisual(object):
	def __init__(self, application, interact_object):
		self.application = application
		self.interact_object = interact_object
		self.instance = self.application.maplayer.getInstance("o:" + self.interact_object.ID)
		if self.instance:
			if self.interact_object.coords is None:
				self.interact_object.coords = self.instance.getLocation().getLayerCoordinates()
			else:
				location = self.instance.getLocation()
				location.setLayerCoordinates(self.interact_object.coords)
				self.instance.setLocation(location)
				self.instance.setRotation(self.interact_object.rotation)
		else:
			if self.interact_object.coords is None:
				print("Error creating instance for", self.interact_object.ID)
			else:
				self.instance = self.application.maplayer.createInstance(
						self.application.model.getObject(
						self.interact_object.sprite, "steamfolktales"),
						self.interact_object.coords)
				fife.InstanceVisual.create(self.instance)
				self.instance.setRotation(self.interact_object.rotation)

	def displayStats(self):
		char_msg = ""
		char_msg += "I'm " + str(self.interact_object.name) + "."
		self.application.gui.sayBubble(self.instance, char_msg)

	def destroy(self):
		self.instance.getLocation().getLayer().deleteInstance(self.instance)

	def say(self, text, time=2000, color=""):
		self.application.gui.sayBubble(self.instance, text, time, color)
	
		
class Door(object):
	def __init__(self, closed=True):
		self.closed = closed
		
	def close(self, interact_obj, pc=None):
		if pc is not None and interact_obj.coords == pc.coords:
			# standing in the doorway, can't close
			return
		self.closed = True
		if not interact_obj.visual:
			return
		interact_obj.visual.instance.actRepeat("closed")
		interact_obj.visual.instance.setOverrideBlocking(True)
		interact_obj.visual.instance.setBlocking(True)
		interact_obj.visual.application.playSound("SFT-DOOR-CLOSE")

	def open(self, interact_obj, pc=None):
		self.closed = False
		if not interact_obj.visual:
			return
		interact_obj.visual.instance.actRepeat("open")
		interact_obj.visual.instance.setOverrideBlocking(True)
		interact_obj.visual.instance.setBlocking(False)
		interact_obj.visual.application.playSound("SFT-DOOR-OPEN")


class Portal(object):
	def __init__(self, coords, map_name=None, rotation=None, script=None):
		self.coords = coords
		self.map_name = map_name
		self.rotation = rotation
		self.script = script
		