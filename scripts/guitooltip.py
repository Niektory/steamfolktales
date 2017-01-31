# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI

class GUITooltip:
	# TODO: merge the shadows with the main window; and fix the transparency
	def __init__(self):
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("Tooltip.layout")
		#self.shadow = self.window.clone("TooltipShadow")
		#self.shadow2 = self.window.clone("TooltipShadow2")
		#self.shadow3 = self.window.clone("TooltipShadow3")
		#self.shadow4 = self.window.clone("TooltipShadow4")
		self.shadow = self.window.clone()
		self.shadow.setName("TooltipShadow")
		self.shadow2 = self.window.clone()
		self.shadow2.setName("TooltipShadow2")
		self.shadow3 = self.window.clone()
		self.shadow3.setName("TooltipShadow3")
		self.shadow4 = self.window.clone()
		self.shadow4.setName("TooltipShadow4")
		self.enabled = True

	def clear(self):
		self.window.setText("")
		self.window.hide()
		self.shadow.setText("")
		self.shadow.hide()
		self.shadow2.setText("")
		self.shadow2.hide()
		self.shadow3.setText("")
		self.shadow3.hide()
		self.shadow4.setText("")
		self.shadow4.hide()
		self.messages = ""
		self.shadow_messages = ""
		
	def toggle(self):
		self.enabled = not self.enabled

	def printMessage(self, message, color = ""):
		if self.enabled:
			self.window.show()
			self.messages += (color + message)
			self.window.setText(self.messages)
			self.window.setProperty("Size",
					"{{0," + self.window.getProperty("HorzExtent") + "},{0," +
					self.window.getProperty("VertExtent") + "}}")
			self.shadow.show()
			self.shadow_messages += (message)
			self.shadow.setText("[colour='FF000000']" + self.shadow_messages)
			self.shadow.setProperty("Size",
					"{{0," + self.window.getProperty("HorzExtent") + "},{0," +
					self.window.getProperty("VertExtent") + "}}")
			self.shadow2.show()
			self.shadow2.setText("[colour='FF000000']" + self.shadow_messages)
			self.shadow2.setProperty("Size",
					"{{0," + self.window.getProperty("HorzExtent") + "},{0," +
					self.window.getProperty("VertExtent") + "}}")
			self.shadow3.show()
			self.shadow3.setText("[colour='FF000000']" + self.shadow_messages)
			self.shadow3.setProperty("Size",
					"{{0," + self.window.getProperty("HorzExtent") + "},{0," +
					self.window.getProperty("VertExtent") + "}}")
			self.shadow4.show()
			self.shadow4.setText("[colour='FF000000']" + self.shadow_messages)
			self.shadow4.setProperty("Size",
					"{{0," + self.window.getProperty("HorzExtent") + "},{0," +
					self.window.getProperty("VertExtent") + "}}")
			#self.shadow.moveToFront()
			#self.shadow2.moveToFront()
			#self.shadow3.moveToFront()
			#self.shadow4.moveToFront()
			#self.window.moveToFront()

	def move(self, x, y, x_offset=0, y_offset=0):
		self.window.setPosition(
				PyCEGUI.UVector2(PyCEGUI.UDim(0,x+x_offset), PyCEGUI.UDim(0,y+y_offset)))
		self.shadow.setPosition(
				PyCEGUI.UVector2(PyCEGUI.UDim(0,x+x_offset+1), PyCEGUI.UDim(0,y+y_offset)))
		self.shadow2.setPosition(
				PyCEGUI.UVector2(PyCEGUI.UDim(0,x+x_offset-1), PyCEGUI.UDim(0,y+y_offset)))
		self.shadow3.setPosition(
				PyCEGUI.UVector2(PyCEGUI.UDim(0,x+x_offset), PyCEGUI.UDim(0,y+y_offset+1)))
		self.shadow4.setPosition(
				PyCEGUI.UVector2(PyCEGUI.UDim(0,x+x_offset), PyCEGUI.UDim(0,y+y_offset-1)))

