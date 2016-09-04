# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

#from rpginventory import RPGItem


class Lock(object):
	def __init__(self, matching_key=None, difficulty=0, locked=True):
		self.matching_key = matching_key
		self.difficulty = difficulty
		self.locked = locked

	def pick(self, pc):
		if pc.rpg_stats.skillCheck("Sleight of Hand", -self.difficulty).success:
			self.locked = False
			return True
		return False


#class Lockpicks(RPGItem):
#	def __init__(self):
#		super(Lockpicks, self).__init__(name="Lockpicks")
