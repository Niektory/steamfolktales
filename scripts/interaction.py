# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

class Interaction(object):
	def __init__(self, target, name, max_distance):
		self.target = target
		self.name = name
		#self.script = script
		self.max_distance = max_distance
