# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from rpgitem import RPGItem, loadItem


class RPGInventory(object):
	horz_grid_size = 4
	vert_grid_size = 4

	def __init__(self):
		# equipment slots
		self.hands = []
		self.head = []
		self.body = []
		# backpack[y][x] -- stack of items
		self.backpack = []
		for i in xrange(self.vert_grid_size):
			self.backpack.append([])
			for j in xrange(self.horz_grid_size):
				self.backpack[i].append([])

	def checkBackpackSpace(self, x, y, size_x, size_y, ignore=None):
		# check if within bounds
		if x < 0:
			return False
		if y < 0:
			return False
		if (x + size_x) > self.horz_grid_size:
			return False
		if (y + size_y) > self.vert_grid_size:
			return False
		# check if no conflicting items to the bottom/right/at the same place
		for i in xrange(size_y):
			for j in xrange(size_x):
				if not self.backpack[y+i][x+j]:
					continue
				if self.backpack[y+i][x+j] is ignore:
					continue
				return False
		# check if no conflicting items to the top/left
		for i in xrange(y+1):
			for j in xrange(x+1):
				if not self.backpack[i][j]:
					continue
				if self.backpack[i][j] is ignore:
					continue
				if (j + self.backpack[i][j][0].size_x) <= x:
					continue
				if (i + self.backpack[i][j][0].size_y) <= y:
					continue
				return False
		return True
				
	def addItem(self, item):
		if isinstance(item, str):
			return self.addItem(loadItem(item))
		elif not isinstance(item, RPGItem):
			return False
		# check if we can stack with an existing item
		for i in xrange(self.vert_grid_size):
			for j in xrange(self.horz_grid_size):
				if self.backpack[i][j]:
					if (self.backpack[i][j][0].name == item.name) and (
								len(self.backpack[i][j]) < item.max_stack):
						self.backpack[i][j].append(item)
						return True
		# look for a free slot
		for i in xrange(self.vert_grid_size - item.size_y + 1):
			for j in xrange(self.horz_grid_size - item.size_x + 1):
				if self.checkBackpackSpace(j, i, item.size_x, item.size_y):
					self.backpack[i][j] = [item]
					return True
		return False

	def findAmmoCalibre(self, calibre):
		ammo_stacks = []
		for i in xrange(self.vert_grid_size):
			for j in xrange(self.horz_grid_size):
				if (self.backpack[i][j] and hasattr(self.backpack[i][j][0], "ammo_calibre")
										and self.backpack[i][j][0].ammo_calibre == calibre):
					ammo_stacks.append(self.backpack[i][j])
		return ammo_stacks

	@property
	def weapon_sprite(self):
		if self.hands:
			#if isinstance(self.backpack[0][0], Weapon):
			return self.hands[0].weapon_data.sprite
		return "unarmed"

	def unequipAll(self):
		while self.hands:
			self.addItem(self.hands.pop())
		while self.head:
			self.addItem(self.head.pop())
		while self.body:
			self.addItem(self.body.pop())

	def hasItem(self, item_type):
		#if isinstance(item_type, str):
		#	return self.hasItem(loadItem(item_type))
		#elif not isinstance(item_type, RPGItem):
		#	return False
		for i in xrange(self.vert_grid_size):
			for j in xrange(self.horz_grid_size):
				#if self.backpack[i][j] and isinstance(self.backpack[i][j][0], item_type):
				if self.backpack[i][j] and self.backpack[i][j][0].ID == item_type:
					return True
		return False
		