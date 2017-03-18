# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from __future__ import division

import PyCEGUI
import timeit

from config.loadingscreens import loading_screens_by_map

class GUILoading:
	def __init__(self, application):
		self.application = application
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("Loading.layout")
		if int(self.application.settings.get(
								"FIFE", "ScreenResolution", "1024x768").split("x")[0]) > 1024:
			self.window.setProperty("Image", "Loadscreen01/full_image")
		self.default_image = self.window.getProperty("Image")
		self.action = None
		self.visible = False
		self.fade_duration = 1
		self.fade_start = 0

	def show(self):
		self.window.show()
		self.window.moveToFront()
		self.window.setAlpha(1)
		self.visible = True

	def showFade(self, action, map=None):
		self.show()
		self.window.setAlpha(0)
		self.fade_start = timeit.default_timer()
		self.action = action
		image = loading_screens_by_map.get(map)
		if image is not None:
			self.window.setProperty("Image", image + "/full_image")
		else:
			self.window.setProperty("Image", self.default_image)
		
	def hideFade(self):
		self.visible = False
		self.fade_start = 0

	def update(self):
		if not self.window.isVisible():
			return
		if self.visible:
			self.window.setAlpha((timeit.default_timer() - self.fade_start) / self.fade_duration)
			if (self.window.getAlpha() >= 1) and self.action:
				self.action()
				self.action = None
		else:
			if self.fade_start == 0:
				self.fade_start = timeit.default_timer()
			self.window.setAlpha(
				1 - (timeit.default_timer() - self.fade_start) / self.fade_duration)
			if self.window.getAlpha() <= 0:
				self.window.hide()
