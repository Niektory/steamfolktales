# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import xml.etree.ElementTree as ET

from weapon import WeaponData
from ammo import AmmoData


class RPGItem(object):
	def __init__(self, ID, name, image=None, description="", max_stack=1,
				size_x=1, size_y=1):
		self.ID = ID
		self.name = name
		self.description = description
		self.image = image
		#self.equipment_type = equipment_type
		self.max_stack = max_stack
		self.size_x = size_x
		self.size_y = size_y
		self.weapon_data = None
		self.ammo_data = None
	
	@property
	def equipment_type(self):
		if self.weapon_data is not None:
			return 0
		return None
		
	@classmethod
	def loadXML(cls, ID, filename):
		tree = ET.parse(filename)
		root = tree.getroot()
		if root.tag != "Item":
			return
		name = root.attrib["name"]
		image = root.attrib.get("image")
		#equipment_type = root.attrib.get("equipment_type")
		description = root.attrib.get("description", "")
		size_x = int(root.attrib.get("size_x", 1))
		size_y = int(root.attrib.get("size_y", 1))
		max_stack = int(root.attrib.get("max_stack", 1))
		item = cls(ID=ID, name=name, image=image, #equipment_type=equipment_type,
				description=description, max_stack=max_stack, size_x=size_x, size_y=size_y)
		for element in root:
			if element.tag == "WeaponData":
				damage = element.attrib["damage"]
				skill = element.attrib["skill"]
				sprite = element.attrib["sprite"]
				accuracy = int(element.attrib.get("accuracy", 0))
				speed = int(element.attrib.get("speed", 1))
				range = float(element.attrib.get("range", 1.5))
				range_increments = int(element.attrib.get("range_increments", 1))
				magazine_size = int(element.attrib.get("magazine_size", 0))
				calibre = element.attrib.get("calibre")
				ranged = True if element.attrib.get("ranged") == "1" else False
				martial_art = element.attrib.get("martial_art", None)
				item.weapon_data = WeaponData(damage=damage, skill=skill, sprite=sprite,
						accuracy=accuracy, speed=speed, range=range,
						range_increments=range_increments, magazine_size=magazine_size,
						calibre=calibre, ranged=ranged, martial_art=martial_art)
			elif element.tag == "AmmoData":
				item.ammo_data = AmmoData(element.attrib["calibre"])
		return item


def loadItem(ID):
	return RPGItem.loadXML(ID, "campaign_data/items/" + ID + ".xml")
	