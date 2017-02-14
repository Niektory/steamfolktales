# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from __future__ import print_function

from fife import fife
from random import randrange

from timeline import Timer
from error import LogExceptionDecorator

class Animal(fife.InstanceActionListener):
	STATE_IDLE, STATE_RUN1, STATE_RUN2 = range(3)

	def __init__(self, instance, application):
		fife.InstanceActionListener.__init__(self)
		self.application = application
		self.instance = instance
		self.instance.addActionListener(self)
		self.state = self.STATE_IDLE
		self.idle()

	@LogExceptionDecorator
	def onInstanceActionFinished(self, instance, action):
		self.application.real_timeline.addTimer(Timer("idle animal", action=self.idle))

	@LogExceptionDecorator
	def onInstanceActionCancelled(self, instance, action):
		if self.state == self.STATE_RUN1:
			print("Animal out of control!")
		print("Animal.onInstanceActionCancelled() called")
		return

	def idle(self):
		if randrange(2):
			self.state = self.STATE_IDLE
			self.instance.actOnce("idle")
		else:
			location = fife.Location(self.instance.getLocation())
			coords = location.getLayerCoordinates()
			coords.x += randrange(-2, 3)
			coords.y += randrange(-2, 3)
			location.setLayerCoordinates(coords)
			self.run(location)

	def run(self, dest):
		if self.state == self.STATE_RUN1:
			print("ABORT! Animal out of control!")
			return
		self.state = self.STATE_RUN1
		#print "Animal run from:", self.instance.getLocation().getExactLayerCoordinates()
		#print "Animal run to:", dest.getExactLayerCoordinates()
		self.instance.move("idle", dest, 0.5)
		self.state = self.STATE_RUN2
		#print "Animal running..."


class Bird(fife.InstanceActionListener):
	STATE_IDLE, STATE_RUN1, STATE_RUN2 = range(3)

	def __init__(self, instance, application):
		fife.InstanceActionListener.__init__(self)
		self.application = application
		self.instance = instance
		self.instance.addActionListener(self)
		self.state = self.STATE_IDLE
		self.idle()

	@LogExceptionDecorator
	def onInstanceActionFinished(self, instance, action):
		if self.state == self.STATE_RUN1:
			print("Bird out of control!")
		self.application.real_timeline.addTimer(Timer("idle bird", action=self.idle))

	@LogExceptionDecorator
	def onInstanceActionCancelled(self, instance, action):
		print("Bird.onInstanceActionCancelled() called")
		return

	def idle(self):
		location = fife.Location(self.instance.getLocation())
		coords = location.getLayerCoordinates()
		coords.x = randrange(-49, 49)
		coords.y = randrange(-54, 62)
		location.setLayerCoordinates(coords)
		self.run(location)

	def run(self, dest):
		if self.state == self.STATE_RUN1:
			print("ABORT! Bird out of control!")
			return
		self.state = self.STATE_RUN1
		#print "Bird run from:", self.instance.getLocation().getExactLayerCoordinates()
		#print "Bird run to:", dest.getExactLayerCoordinates()
		self.instance.move("idle", dest, 5.0)
		self.state = self.STATE_RUN2
		#print "Bird running..."
