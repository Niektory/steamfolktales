# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife
from random import randrange

class Plant(fife.InstanceActionListener):
	def __init__(self, instance):
		fife.InstanceActionListener.__init__(self)
		self.instance = instance
		self.instance.addActionListener(self)
		self.idle()

	def onInstanceActionFinished(self, instance, action):
		self.idle()

	def onInstanceActionCancelled(self, instance, action):
		print("Plant.onInstanceActionCancelled()")
		return

	def idle(self):
		if randrange(6):	# larger number = bigger chance to stay still
			self.instance.actOnce("still")
		else:
			self.instance.actOnce("idle")
