# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

import PyCEGUI
#from traceback import print_exc

class GUIInitiative:
	def __init__(self):
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("Initiative.layout")
		self.portrait_container = self.window.getChild("PortraitContainer")
		self.current_portraits = []
		self.combat = None

	def show(self, combat):
		self.window.show()
		self.window.moveToFront()
		self.combat = combat
		self.update()

	def update(self):
		# clear all portraits
		#for portrait in self.current_portraits:
		#	self.portrait_container.removeChild(portrait)
		while self.portrait_container.getChildCount():
			self.portrait_container.removeChild(
						self.portrait_container.getChildAtIdx(0).getID())
		self.current_portraits = []
		# and make new ones
		for combatant in self.combat.combatants:
			new_portrait = PyCEGUI.WindowManager.getSingleton().createWindow(
						"TaharezLook/StaticImage", "Portrait-" + combatant.ID)
			new_portrait.setSize(PyCEGUI.USize(PyCEGUI.UDim(0, 100), PyCEGUI.UDim(0, 100)))
			new_portrait.setProperty("HorzFormatting", "CentreAligned")
			new_portrait.setProperty("VertFormatting", "CentreAligned")
			new_portrait.setProperty("BackgroundEnabled", "False")
			new_portrait.setProperty("FrameEnabled", "False")
			new_portrait.setProperty("MousePassThroughEnabled", "False")
			if combatant != self.combat.combatants[self.combat.current_combatant]:
				new_portrait.setProperty("ImageColours", "FF808080")
			else:
				new_portrait.setProperty("ImageColours", "FFFFFFFF")
			if combatant.portrait:
				# portrait present
				new_portrait.setProperty("Image", combatant.portrait)
			else:
				# no portrait, using default
				new_portrait.setProperty("Image", "TaharezLook/CloseButtonHover")
			self.portrait_container.addChild(new_portrait)
			self.current_portraits.append(new_portrait)
			