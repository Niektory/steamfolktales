# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

import PyCEGUI
#from traceback import print_exc

from error import LogException
from campaign.journal import questLog


class GUIJournal:
	def __init__(self, application):
		self.application = application
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("Journal.layout")
		self.quest_log = self.window.getChild("QuestLog")
		self.close_button = self.window.getChild("CloseButton")
		self.close_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.hide)

	def show(self, args=None):
		with LogException():
			self.window.show()
			self.window.moveToFront()
			self.quest_log.setText(questLog(self.application.world))
			self.application.playSound("SFT-QUESTLOG-OPEN")

	def hide(self, args=None):
		with LogException():
			self.window.hide()
			self.application.playSound("SFT-QUESTLOG-CLOSE")
				
	def toggle(self, args=None):
		with LogException():
			if self.window.isVisible():
				self.hide()
			else:
				self.show()
