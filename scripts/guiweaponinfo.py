# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

import PyCEGUI
#from traceback import print_exc

from error import LogException


class GUIWeaponInfo:
	def __init__(self):
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("WeaponInfo.layout")
		self.cancel_button = self.window.getChild("CancelButton")
		self.cancel_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.hide)

		self.name_label = self.window.getChild("NameLabel")
		self.description_label = self.window.getChild("DescriptionLabel")
		self.weapon_image = self.window.getChild("ImageFrame/WeaponImage")
		self.accuracy_edit = self.window.getChild("AccuracyEdit")
		self.damage_edit = self.window.getChild("DamageEdit")
		self.speed_edit = self.window.getChild("SpeedEdit")
		self.range_edit = self.window.getChild("RangeEdit")

	def show(self, weapon):
		with LogException():
			self.current_weapon = weapon
			self.window.show()
			self.window.moveToFront()
			self.name_label.setText(self.current_weapon.name)
			self.description_label.setText(self.current_weapon.description)
			self.weapon_image.setProperty("Image", self.current_weapon.image)
			self.accuracy_edit.setText(str(self.current_weapon.weapon_data.accuracy))
			self.damage_edit.setText(self.current_weapon.weapon_data.damage_str)
			self.speed_edit.setText(str(self.current_weapon.weapon_data.speed))
			self.range_edit.setText(self.current_weapon.weapon_data.range_str)

	def hide(self, args=None):
		with LogException():
			self.window.hide()
