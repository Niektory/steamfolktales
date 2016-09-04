# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

import PyCEGUI
from os import listdir
#from traceback import print_exc
from fife import fife

from error import LogException


#def closeWindow(args):
#	args.window.hide()

class GUIMapTest:
	def __init__(self, application):
		self.application = application
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("MapTest.layout")
		#self.window.subscribeEvent(PyCEGUI.FrameWindow.EventCloseClicked, closeWindow)
		self.file_list = self.window.getChild("Files")
		self.file_list.subscribeEvent(PyCEGUI.Listbox.EventSelectionChanged, self.fillEditBox)
		self.load_button = self.window.getChild("LoadButton")
		self.load_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.load)
		self.cancel_button = self.window.getChild("CancelButton")
		self.cancel_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.hide)
		self.name_edit = self.window.getChild("NameEdit")
		self.name_edit.subscribeEvent(PyCEGUI.Editbox.EventTextChanged, self.selectItem)
		self.sprite_edit = self.window.getChild("SpriteEdit")
		self.x_edit = self.window.getChild("XEdit")
		self.y_edit = self.window.getChild("YEdit")
		self.ignore_selecting = False

	def hide(self, args=None):
		with LogException():
			self.window.hide()

	def show(self, args=None):
		with LogException():
			self.file_list.resetList()
			self.file_items = []
			for file_name in listdir("maps"):
				if file_name.endswith(".xml"):
					self.addMapToList(file_name[:-4])
			self.window.show()
			self.window.moveToFront()

	def load(self, args):
		with LogException():
			item = self.file_list.getFirstSelectedItem()
			if item:
				self.application.prepareLoadMapTest(item.getText(), fife.ModelCoordinate(
							int(self.x_edit.getText()), int(self.y_edit.getText()), 0),
							self.sprite_edit.getText())

	def selectItem(self, args):
		with LogException():
			self.ignore_selecting = True
			item = self.file_list.findItemWithText(self.name_edit.getText(), None)
			if item:
				self.file_list.setItemSelectState(item, True)
			elif self.file_list.getFirstSelectedItem():
				self.file_list.clearAllSelections()
			self.ignore_selecting = False

	def fillEditBox(self, args):
		with LogException():
			if not self.ignore_selecting:
				item = self.file_list.getFirstSelectedItem()
				if item:
					self.name_edit.setText(item.getText())
				else:
					self.name_edit.setText("")

	def addMapToList(self, save_name):
		self.file_items.append(PyCEGUI.ListboxTextItem(save_name))
		self.file_items[-1].setAutoDeleted(False)
		#self.file_items[-1].setSelectionBrushImage("TaharezLook", "MultiListSelectionBrush")
		self.file_items[-1].setSelectionBrushImage("TaharezLook/MultiListSelectionBrush")
		self.file_items[-1].setSelectionColours(PyCEGUI.Colour(0.33, 0.295, 0.244))
		self.file_items[-1].setTextColours(PyCEGUI.Colour(0.98, 0.886, 0.733))
		self.file_list.addItem(self.file_items[-1])

