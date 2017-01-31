# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife

from timeline import Timer


class SimpleEffect(fife.InstanceActionListener):
	def __init__(self, application, object_name, location):
		fife.InstanceActionListener.__init__(self)
		self.application = application
		self.instance = location.getLayer().createInstance(
				self.application.model.getObject(object_name, "effects"),
				location.getExactLayerCoordinates())
		fife.InstanceVisual.create(self.instance)
		self.instance.addActionListener(self)
		self.instance.actOnce("idle")

	def onInstanceActionFinished(self, instance, action):
		self.application.real_timeline.addTimer(Timer("destroy effect", action=self.destroy))

	def onInstanceActionCancelled(self, instance, action):
		return

	def destroy(self):
		self.instance.getLocation().getLayer().deleteInstance(self.instance)
