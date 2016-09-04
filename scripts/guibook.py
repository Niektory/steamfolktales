# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

import PyCEGUI
#from traceback import print_exc

from error import LogException


def closeWindow(args):
	with LogException():
		args.window.hide()

class GUIBook:
	def __init__(self):
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("Book.layout")
		self.left_page = self.window.getChild("LeftPage")
		self.right_page = self.window.getChild("RightPage")
		self.window.subscribeEvent(PyCEGUI.Window.EventMouseClick, closeWindow)

	def show(self, page_list):
		self.window.show()
		self.window.moveToFront()
		self.current_page_list = page_list
		self.left_page.setText(self.current_page_list[0])
		if len(self.current_page_list) > 1:
			self.right_page.setText(self.current_page_list[1])
