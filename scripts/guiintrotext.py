# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from __future__ import division

import PyCEGUI
import timeit

class GUIIntroText:
	def __init__(self):
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("IntroText.layout")
		self.visible = False
		self.fade_duration = 5
		self.fade_start = 0

	def show(self):
		self.window.show()
		self.window.moveToFront()
		self.window.setAlpha(1)
		self.visible = True

	def showFade(self, text):
		self.show()
		self.window.setAlpha(0)
		self.fade_start = timeit.default_timer()
		self.window.setText(text)
		
	def hideFade(self):
		self.visible = False
		self.fade_start = timeit.default_timer()

	def update(self):
		if not self.window.isVisible():
			return
		if self.visible:
			self.window.setAlpha((timeit.default_timer() - self.fade_start) / self.fade_duration)
		else:
			self.window.setAlpha(
				1 - (timeit.default_timer() - self.fade_start) / self.fade_duration)
			if self.window.getAlpha() <= 0:
				self.window.hide()
