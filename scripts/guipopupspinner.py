# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

import PyCEGUI
#from traceback import print_exc

from error import LogException


class GUIPopupSpinner:
	def __init__(self):
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("PopupSpinner.layout")

		self.value_spinner = self.window.getChild("ValueSpinner")
		self.value_spinner.subscribeEvent(PyCEGUI.Spinner.EventValueChanged, self.update)

		self.ok_button = self.window.getChild("OKButton")
		self.ok_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.acceptValue)
		self.cancel_button = self.window.getChild("CancelButton")
		self.cancel_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.hide)

	def show(self, args=None):
		with LogException():
			self.window.show()

	def askForValue(self, max_value, callback):
		self.max_value = max_value
		self.callback = callback
		self.window.show()
		self.window.moveToFront()
		self.value_spinner.setCurrentValue(1)
		self.value_spinner.setMaximumValue(self.max_value)
		#new_attribute_spinner.setTextInputMode(PyCEGUI.Spinner.Integer)
		#new_attribute_spinner.setMinimumValue(self.working_stats.attributes[attribute])
		#new_attribute_spinner.setStepSize(1)
		#new_attribute_edit = new_attribute_spinner.getChild("__auto_editbox__")
		#new_attribute_edit.setReadOnly(True)
		self.update()

	def update(self, args=None):
		with LogException():
			if self.value_spinner.getMaximumValue() == self.value_spinner.getCurrentValue():
				self.value_spinner.getChild("__auto_incbtn__").setEnabled(False)
			else:
				self.value_spinner.getChild("__auto_incbtn__").setEnabled(True)
			if self.value_spinner.getMinimumValue() == self.value_spinner.getCurrentValue():
				self.value_spinner.getChild("__auto_decbtn__").setEnabled(False)
			else:
				self.value_spinner.getChild("__auto_decbtn__").setEnabled(True)

	def hide(self, args=None):
		with LogException():
			self.window.hide()
			
	def toggle(self, args=None):
		with LogException():
			if self.window.isVisible():
				self.hide()
			else:
				self.show()

	def acceptValue(self, args):
		with LogException():
			self.callback(int(self.value_spinner.getCurrentValue()))
			self.window.hide()
