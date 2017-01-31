# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

import PyCEGUI
from os import listdir
#from traceback import print_exc

from error import LogExceptionDecorator


#def closeWindow(args):
#	args.window.hide()


class GUISaveLoad:
	def __init__(self, application):
		self.application = application
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("SaveLoad.layout")
		#self.window.subscribeEvent(PyCEGUI.FrameWindow.EventCloseClicked, closeWindow)
		self.file_list = self.window.getChild("Files")
		self.file_list.subscribeEvent(PyCEGUI.Listbox.EventSelectionChanged, self.fillEditBox)
		self.save_button = self.window.getChild("SaveButton")
		self.save_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.save)
		self.load_button = self.window.getChild("LoadButton")
		self.load_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.load)
		self.cancel_button = self.window.getChild("CancelButton")
		self.cancel_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.hide)
		self.name_edit = self.window.getChild("NameEdit")
		self.name_edit.subscribeEvent(PyCEGUI.Editbox.EventTextChanged, self.selectItem)
		self.ignore_selecting = False

	#def show(self, args=None):
	#	self.window.show()
	#	self.window.moveToFront()
	#	if self.application.map:
	#		self.save_button.show()
	#	else:
	#		self.save_button.hide()

	@LogExceptionDecorator
	def hide(self, args=None):
		self.window.hide()

	@LogExceptionDecorator
	def showSave(self, args=None):
		self.file_list.resetList()
		self.file_items = []
		for file_name in listdir("saves"):
			if file_name.endswith(".sav"):
				self.addSaveToList(file_name[:-4])
		self.selectItem()
		self.window.show()
		self.window.moveToFront()
		self.save_button.show()
		self.load_button.hide()

	@LogExceptionDecorator
	def showLoad(self, args=None):
		self.file_list.resetList()
		self.file_items = []
		for file_name in listdir("saves"):
			if file_name.endswith(".sav"):
				self.addSaveToList(file_name[:-4])
		self.selectItem()
		self.window.show()
		self.window.moveToFront()
		self.save_button.hide()
		self.load_button.show()

	@LogExceptionDecorator
	def save(self, args):
		item = self.file_list.getFirstSelectedItem()
		if item:
			self.application.saveGame(item.getText())
		elif (len(self.name_edit.getText()) > 0) and (self.name_edit.getText()[0] != " "):
			self.application.saveGame(self.name_edit.getText())
			#self.addSaveToList(self.name_edit.getText())
		self.window.hide()

	@LogExceptionDecorator
	def load(self, args):
		item = self.file_list.getFirstSelectedItem()
		if item:
			self.application.prepareLoadGame(item.getText())

	@LogExceptionDecorator
	def selectItem(self, args=None):
		self.ignore_selecting = True
		item = self.file_list.findItemWithText(self.name_edit.getText(), None)
		if item:
			self.file_list.setItemSelectState(item, True)
		elif self.file_list.getFirstSelectedItem():
			self.file_list.clearAllSelections()
		self.ignore_selecting = False

	@LogExceptionDecorator
	def fillEditBox(self, args):
		if not self.ignore_selecting:
			item = self.file_list.getFirstSelectedItem()
			if item:
				self.name_edit.setText(item.getText())
			else:
				self.name_edit.setText("")

	def addSaveToList(self, save_name):
		self.file_items.append(PyCEGUI.ListboxTextItem(save_name))
		self.file_items[-1].setAutoDeleted(False)
		#self.file_items[-1].setSelectionBrushImage("TaharezLook", "MultiListSelectionBrush")
		self.file_items[-1].setSelectionBrushImage("TaharezLook/MultiListSelectionBrush")
		self.file_items[-1].setSelectionColours(PyCEGUI.Colour(0.33, 0.295, 0.244))
		self.file_items[-1].setTextColours(PyCEGUI.Colour(0.98, 0.886, 0.733))
		self.file_list.addItem(self.file_items[-1])
