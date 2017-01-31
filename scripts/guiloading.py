# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI
from traceback import print_exc

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
		self.fade_speed = 0.03

	def show(self):
		self.window.show()
		self.window.moveToFront()
		self.window.setAlpha(1.0)
		self.visible = True

	def showFade(self, action, map=None):
		self.show()
		self.window.setAlpha(self.fade_speed)
		self.action = action
		image = loading_screens_by_map.get(map)
		if image is not None:
			self.window.setProperty("Image", image + "/full_image")
		else:
			self.window.setProperty("Image", self.default_image)
		
	def hideFade(self):
		self.visible = False

	def update(self):
		if not self.window.isVisible():
			return
		alpha = self.window.getAlpha()
		if self.visible:
			self.window.setAlpha(alpha + self.fade_speed)
			if (alpha >= 1.0) and self.action:
				self.action()
				self.action = None
		else:
			self.window.setAlpha(alpha - self.fade_speed)
			if alpha <= 0.0:
				self.window.hide()