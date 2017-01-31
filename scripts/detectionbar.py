# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife
import PyCEGUI

from timeline import Timer

class DetectionBar(fife.InstanceDeleteListener):
	def __init__(self, application, instance, fill, vis_fill, color=""):
		fife.InstanceDeleteListener.__init__(self)
		self.application = application
		self.instance = instance
		self.timer = Timer("DetectionBar" + str(fill), time=200, action=self.destroy,
						tick_action=self.adjustPosition)
		self.application.real_timeline.addTimer(self.timer)
		self.instance.addDeleteListener(self)
		self.bar = PyCEGUI.WindowManager.getSingleton().createWindow(
						"TaharezLook/ProgressBar",
						"DetectionBar-" + str(self.instance.getFifeId()))
		self.bar.setProperty("MousePassThroughEnabled", "True")
		self.bar.setProperty("Size", "{{0,60},{0,10}}")
		self.application.gui.root.addChild(self.bar)
		self.fill = 0.0
		self.edit(fill, vis_fill, color)

	def edit(self, fill, vis_fill, color=""):
		if fill > self.fill:
			self.bar.setProgress(float(vis_fill))
			self.fill = fill
			self.bar.setProperty("LightsColour", color)
		self.timer.time = 200
		self.adjustPosition()

	def adjustPosition(self):
		coords = self.application.camera.toScreenCoordinates(
					self.instance.getLocation().getMapCoordinates())
		#self.bar.setProperty("Position", "{{0,"
		#			+ str(coords.x - int(float(self.horz_extent)) / 2)
		#			+ "},{0," + str(coords.y - int(float(self.vert_extent)) - 90) + "}}")
		self.bar.setProperty("Position", "{{0,"
					+ str(coords.x - 30)
					+ "},{0," + str(coords.y - 90) + "}}")

	def destroy(self):
		PyCEGUI.WindowManager.getSingleton().destroyWindow(self.bar)
		if self.application.gui.detection_bars.count(self):
			self.application.gui.detection_bars.remove(self)
		if self.application.real_timeline.timers.count(self.timer):
			self.application.real_timeline.timers.remove(self.timer)

	def onInstanceDeleted(self, instance):
		self.destroy()

