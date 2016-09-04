# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

import PyCEGUI

class GUIIntroText:
	def __init__(self):
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("IntroText.layout")
		self.visible = False
		self.fade_speed = 0.01

	def show(self):
		self.window.show()
		self.window.moveToFront()
		self.window.setAlpha(1.0)
		self.visible = True

	def showFade(self, text):
		self.show()
		self.window.setAlpha(self.fade_speed)
		self.window.setText(text)
		
	def hideFade(self):
		self.visible = False

	def update(self):
		if not self.window.isVisible():
			return
		alpha = self.window.getAlpha()
		if self.visible:
			self.window.setAlpha(alpha + self.fade_speed)
		else:
			self.window.setAlpha(alpha - self.fade_speed)
			if alpha <= 0.0:
				self.window.hide()
				