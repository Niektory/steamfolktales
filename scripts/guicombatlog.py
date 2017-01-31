# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI

from error import LogExceptionDecorator


@LogExceptionDecorator
def propagateMouseWheel(args):
	args.window.getParent().fireEvent(PyCEGUI.Window.EventMouseWheel, args)


class GUICombatLog:
	def __init__(self, help):
		self.links = []
		self.help = help
		self.messages = ""
		self.last_message = ""
		self.duplicate_count = 1
		self.length_before_last = 0
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("CombatLog.layout")
		self.output = self.window.getChild("TextBox")

	def clear(self):
		# scroll the log to the beginning
		#print "VertScrollPosition: {}".format(self.output.getProperty("VertScrollPosition"))
		#print "VertScrollDocumentSize: {}".format(
		#									self.output.getProperty("VertScrollDocumentSize"))
		#print "VertScrollPageSize: {}".format(self.output.getProperty("VertScrollPageSize"))
		self.output.setProperty("VertScrollPosition", "0")
		#self.output.setProperty("VertScrollPosition", foo)
		
		#args = PyCEGUI.MouseEventArgs(self.output)
		#args.wheelChange = 1000
		#self.output.fireEvent(PyCEGUI.GUISheet.EventMouseWheel, args)
		#self.output.fireEvent(PyCEGUI.Window.EventMouseWheel, args)

		self.messages = ""
		self.last_message = ""
		self.duplicate_count = 1
		self.length_before_last = 0
		self.output.setText("")
		for link in self.links:
			if self.output.isChild(link.getID()):
				self.output.removeChild(link)
		#while self.output.getChildCount():
		#	self.output.removeChild(
		#				self.output.getChildAtIdx(0).getID())

	def printMessage(self, message):
		if message == self.last_message:
			self.duplicate_count += 1
			#self.messages = (self.messages[:self.length_before_last]
			#				+ "- " + message + " (x" + str(self.duplicate_count) + ")\n")
			self.messages = ("{}- {} (x{})\n".format(
						self.messages[:self.length_before_last], message, self.duplicate_count))
		else:
			self.length_before_last = len(self.messages)
			self.messages += ("- {}\n".format(message))
			self.duplicate_count = 1
		self.output.setText(self.messages)
		self.last_message = message
		# scroll the log to the end
		#print "VertScrollPosition: {}".format(self.output.getProperty("VertScrollPosition"))
		#print "VertScrollDocumentSize: {}".format(
		#									self.output.getProperty("VertScrollDocumentSize"))
		#print "VertScrollPageSize: {}".format(self.output.getProperty("VertScrollPageSize"))
		self.output.setProperty("VertScrollPosition",
								self.output.getProperty("VertScrollDocumentSize"))
		#args = PyCEGUI.MouseEventArgs(self.output)
		#args.wheelChange = -1000
		#self.output.fireEvent(PyCEGUI.GUISheet.EventMouseWheel, args)
		#self.output.fireEvent(PyCEGUI.Window.EventMouseWheel, args)

	def createLink(self, message, address):
		new_link = PyCEGUI.WindowManager.getSingleton().createWindow(
					"TaharezLook/StaticText", "Link-{}={}".format(len(self.links) + 1, address))
		new_link.setProperty("Text", "[colour='FF00A0FF']{}".format(message))
		new_link.setProperty("FrameEnabled", "False")
		#new_link.setProperty("Size", "{{0," + new_link.getProperty("HorzExtent") + "},{0,"
		#			+ new_link.getProperty("VertExtent") + "}}")
		new_link.setProperty("Size", "{{{{0,{}}},{{0,{}}}}}".format(
						new_link.getProperty("HorzExtent"), new_link.getProperty("VertExtent")))
		self.output.addChild(new_link)
		#self.output.setText(self.messages)
		new_link.subscribeEvent(PyCEGUI.Window.EventMouseClick, self.help.linkClicked)
		#new_link.subscribeEvent(PyCEGUI.Window.EventMouseWheel, propagateMouseWheel, "")
		new_link.subscribeEvent(PyCEGUI.Window.EventMouseWheel, propagateMouseWheel)
		self.links.append(new_link)
		return "[window='Link-{}={}']".format(len(self.links), address)
