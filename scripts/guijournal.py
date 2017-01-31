# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI
#from traceback import print_exc

from error import LogExceptionDecorator
from campaign.journal import questLog


class GUIJournal:
	def __init__(self, application):
		self.application = application
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("Journal.layout")
		self.quest_log = self.window.getChild("QuestLog")
		self.close_button = self.window.getChild("CloseButton")
		self.close_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.hide)

	@LogExceptionDecorator
	def show(self, args=None):
		self.window.show()
		self.window.moveToFront()
		self.quest_log.setText(questLog(self.application.world))
		self.application.playSound("SFT-QUESTLOG-OPEN")

	@LogExceptionDecorator
	def hide(self, args=None):
		self.window.hide()
		self.application.playSound("SFT-QUESTLOG-CLOSE")
				
	@LogExceptionDecorator
	def toggle(self, args=None):
		if self.window.isVisible():
			self.hide()
		else:
			self.show()
