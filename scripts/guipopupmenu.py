# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI
#from traceback import print_exc

from error import LogExceptionDecorator  # LogException


class GUIPopupMenu:
	def __init__(self, gui):
		self.gui = gui
		self.window = PyCEGUI.WindowManager.getSingleton().createWindow(
			"TaharezLook/PopupMenu",
			"PopupMenu")
		self.window.setAlwaysOnTop(True)
		self.menu_items = []
		#new_popup.setProperty("AutoResizeEnabled", "True")
		#new_popup.setProperty("Area", "{{0,0}{0,0}{1,0}{1,0}}")
		PyCEGUI.GlobalEventSet.getSingleton().subscribeEvent(
			"Window/" + PyCEGUI.Window.EventMouseButtonDown,
			self.hideIfOutside)

	def addMenuItem(self, text, callback):
		new_menu_item = PyCEGUI.WindowManager.getSingleton().createWindow(
			"TaharezLook/MenuItem",
			"MenuItem-{}".format(len(self.menu_items)))
		new_menu_item.setText(text)
		#new_menu_item.setProperty("Area", "{{0,0}{0,0}{1,0}{1,0}}")
		self.window.addChild(new_menu_item)
		self.menu_items.append(new_menu_item)
		new_menu_item.subscribeEvent(
			PyCEGUI.MenuItem.EventClicked,
			LogExceptionDecorator(callback))

	def show(self, pos_x, pos_y):
		for menu_item in self.menu_items:
			self.window.removeChild(menu_item)
		self.menu_items = []
		self.window.show()
		self.window.moveToFront()
		#print pos_x, pos_y
		#print PyCEGUI.UVector2(PyCEGUI.UDim(0, pos_x), PyCEGUI.UDim(0, pos_y))
		self.window.setPosition(PyCEGUI.UVector2(PyCEGUI.UDim(0, pos_x), PyCEGUI.UDim(0, pos_y)))

	@LogExceptionDecorator
	def hide(self, args):
		#with LogException():
		self.window.hide()

	@LogExceptionDecorator
	def hideIfOutside(self, args):
		#with LogException():
		if (args.window.getName() != "PopupMenu"
				and "MenuItem-" not in args.window.getName()):
			self.window.hide()
