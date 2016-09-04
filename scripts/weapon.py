# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

#from collections import OrderedDict

#from rpginventory import RPGItem
from rpgstats import Roll  #roll


#class WeaponDamage(object):
#	def __init__(self, dice):
#		self.dice = dice

class WeaponData(object):
	def __init__(self, damage, accuracy=0, speed=1, range=1.5, range_increments=1,
				magazine_size=0, calibre=None, skill="Brawl", sprite="unarmed",
				ranged=False, martial_art=None):
		# valid damage formats: "XdY+Z" (some parts can be omitted) or (X,Y,Z)
		# it used to accept more complex expressions but seriously let's not do this
		if isinstance(damage, str):
		#	damage_list = []
		#	for i in damage.split("+"):
		#		if "d" in i:
		#			if i.split("d")[0]:
		#				damage_list.append(tuple(map(int, i.split("d"))))
		#			else:
		#				damage_list.append((1,int(i.split("d")[1])))
		#		else:
		#			damage_list.append((int(i),1))
		#	self.damage = tuple(damage_list)
			x, y, z = 0, 0, 0
			for i in damage.split("+"):
				if "d" in i:
					if i.split("d")[0]:
						x, y = map(int, i.split("d"))
					else:
						x, y = 1, int(i.split("d")[1])
				else:
					z = int(i)
			self.damage = x, y, z
		else:
			self.damage = damage
		print self.damage
		self.accuracy = accuracy
		self.speed = speed
		self.range = range
		self.range_increments = range_increments
		self.magazine_size = magazine_size
		self.calibre = calibre
		self.skill = skill
		self.sprite = sprite
		self.magazine = []
		self.ranged = ranged
		self.martial_art = martial_art

	@property
	def damage_roll(self):
		#damage_sum = 0
		#for die in self.damage:
		#	damage_sum += roll(die[1], die[0])
		#return damage_sum
		return Roll(self.damage[1], self.damage[0], self.damage[2])
	
	@property
	def damage_str(self):
		damage_string = ""
		x, y, z = self.damage
		if x:
			damage_string += str(x)
		if y:
			damage_string += "d{}".format(str(y))
		if y and z:
			damage_string += "+"
		if z:
			damage_string += str(z)
		#for die in self.damage:
		#	if len(damage_string):
		#		damage_string += "+"
		#	if die[0] > 1:
		#		damage_string += str(die[0])
		#	if die[1] > 1:
		#		damage_string += "d" + str(die[1])
		#	if (die[0] == 1) and (die[1] == 1):
		#		damage_string += "1"
		return damage_string

	@property
	def total_range(self):
		return self.range * self.range_increments

	@property
	def range_str(self):
		range_string = str(self.range) + "m"
		if self.range_increments > 1:
			range_string += "*" + str(self.range_increments)
		return range_string
"""
class Dagger(Weapon):
	def __init__(self):
		super(Dagger, self).__init__("Dagger", "Dagger", ((1,4),), speed=2, skill="Melee, Finesse",
				sprite="dagger", image="Basic_Dagger/full_image")

class Axe(Weapon):
	def __init__(self):
		super(Axe, self).__init__("Axe", "Axe", ((1,8),), skill="Melee, Heavy", sprite="axe",
				image="Basic_Axe/full_image")

class GoodRevolver(Weapon):
	def __init__(self):
		super(GoodRevolver, self).__init__("GoodRevolver",
				"R. Bailey 8mm Peacemaker Revolver", ((1,6),(3,1)),
				accuracy=1, speed=3, range=8, range_increments=7, magazine_size=6, calibre="8mm-S",
				skill="Handguns", sprite="revolver", image="Good_Revolver/full_image", ranged=True,
				description="The most common type of revolver in the known world. Almost every \
				adventurer, noble, pirate and guardsman has one of these. Based on an old and \
				reliable single action revolver mechanism and the common 8mm cartridge, this is \
				the type of weapon you can get ammunition, repair and replacement for almost \
				everywhere in the world. Generally every weapon manufacturer is able to produce \
				these.")

class Revolver(Weapon):
	def __init__(self):
		super(Revolver, self).__init__("Revolver",
				"Revolver", ((1,6),), range=5, range_increments=7,
				magazine_size=4, calibre="6mm-S", ranged=True,
				skill="Handguns", sprite="revolver", image="Basic_Revolver/full_image")

class HeavyRevolver(Weapon):
	def __init__(self):
		super(HeavyRevolver, self).__init__("HeavyRevolver",
				"Heavy Revolver", ((1,6),(6,1)), range=10,
				range_increments=7, magazine_size=5, calibre="12mm-S", ranged=True,
				skill="Handguns", sprite="revolver", image="Heavy_Revolver/full_image")
										
class Sword(Weapon):
	def __init__(self):
		super(Sword, self).__init__("Sword",
				"Common Sword", ((1,6),), skill="Melee, Balanced", size_x=2,
				sprite="sword", image="Common_Sword/full_image")
"""