# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI
#from traceback import print_exc

from error import LogExceptionDecorator
#from weapon import Weapon


class GUIHUD:
	def __init__(self, application, gui):
		self.application = application
		self.gui = gui
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("HUD.layout")
		self.window_combat = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile(
					"HUDCombat.layout")

		self.selected_attack = ""
		self.walk_mode = "walk"
		self.visible = False

		self.camp_button = self.window.getChild("CampButton")
		self.camp_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.camp)
		self.character_button = self.window.getChild("CharacterButton")
		self.character_button.subscribeEvent(
					PyCEGUI.PushButton.EventClicked, self.gui.character_sheet.toggle)
		self.inventory_button = self.window.getChild("InventoryButton")
		self.inventory_button.subscribeEvent(
					PyCEGUI.PushButton.EventClicked, self.gui.inventory.toggle)
		self.journal_button = self.window.getChild("JournalButton")
		self.journal_button.subscribeEvent(
					PyCEGUI.PushButton.EventClicked, self.gui.journal.toggle)
		self.options_button = self.window.getChild("OptionsButton")
		self.options_button.subscribeEvent(
					PyCEGUI.PushButton.EventClicked, self.gui.game_menu.toggle)
		self.walk_button = self.window.getChild("WalkButton")
		self.walk_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.changeWalkMode)
		self.map_button = self.window.getChild("MapButton")
		#self.map_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.walkClicked)

		self.character_button_combat = self.window_combat.getChild("CharacterButton")
		self.character_button_combat.subscribeEvent(
					PyCEGUI.PushButton.EventClicked, self.gui.character_sheet.toggle)
		self.inventory_button_combat = self.window_combat.getChild("InventoryButton")
		self.inventory_button_combat.subscribeEvent(
					PyCEGUI.PushButton.EventClicked, self.gui.inventory.toggle)
		self.options_button_combat = self.window_combat.getChild("OptionsButton")
		self.options_button_combat.subscribeEvent(
					PyCEGUI.PushButton.EventClicked, self.gui.game_menu.toggle)
		self.defend_button_combat = self.window_combat.getChild("DefendButton")
		self.defend_button_combat.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.defend)
		self.weapon_background_combat = self.window_combat.getChild("WeaponBackground")
		self.weapon_background_combat.subscribeEvent(
					PyCEGUI.PushButton.EventMouseClick, self.clickedItem)
		self.weapon_image_combat = self.window_combat.getChild("WeaponBackground/WeaponImage")
		self.ammo_label_combat = self.window_combat.getChild("WeaponBackground/AmmoLabel")
		self.attack_label_combat = self.window_combat.getChild("WeaponBackground/AttackLabel")
		
		self.updateTooltips()

	def updateTooltips(self):
		self.camp_button.setTooltipText("Rest"
											+ self.getHotkeyTooltip("Advance Time"))
		self.character_button.setTooltipText("Character Sheet"
											+ self.getHotkeyTooltip("Character Sheet"))
		self.inventory_button.setTooltipText("Inventory"
											+ self.getHotkeyTooltip("Inventory"))
		self.journal_button.setTooltipText("Journal"
											+ self.getHotkeyTooltip("Journal"))
		self.options_button.setTooltipText("Options \\[Esc]")
		self.walk_button.setTooltipText("Movement Mode"
											+ self.getHotkeyTooltip("Cycle"))
		self.map_button.setTooltipText("Map")
		self.character_button_combat.setTooltipText("Character Sheet"
											+ self.getHotkeyTooltip("Character Sheet"))
		self.inventory_button_combat.setTooltipText("Inventory"
											+ self.getHotkeyTooltip("Inventory"))
		self.options_button_combat.setTooltipText("Options \\[Esc]")
		self.defend_button_combat.setTooltipText("End Turn"
											+ self.getHotkeyTooltip("End Turn"))

	def getHotkeyTooltip(self, hotkey_name):
		if self.application.settings.get("hotkeys", hotkey_name):
			return " \\[" + str(self.gui.preferences.toCeguiKey(self.application.settings.get(
																"hotkeys", hotkey_name))) + "]"
		else:
			return ""

	@LogExceptionDecorator
	def camp(self, args=None):
		self.application.world.advanceTime(6 * 3600000)

	def selectAttack(self, attack):
		self.selected_attack = attack
		self.refresh()
		
	@LogExceptionDecorator
	def changeWalkMode(self, args=None, mode=None):
		if not self.application.current_character:
			return
		if mode:
			self.walk_mode = mode
		elif self.walk_mode == "walk":
			self.walk_mode = "run"
		elif self.walk_mode == "run":
			self.walk_mode = "sneak"
		else:
			self.walk_mode = "walk"
		self.refresh()
		self.application.current_character.visual.idle()
	
	@LogExceptionDecorator
	def clickedItem(self, args):
		if args.button != PyCEGUI.RightButton:
			return
		if not self.application.combat:
			return
		item = self.application.current_character.inventory.hands
		self.gui.popup_menu.show(args.position.d_x, args.position.d_y)
		for attack in self.application.combat.available_attacks:
			self.gui.popup_menu.addMenuItem(attack,
								lambda args, attack=attack: self.selectAttack(attack))
		if not item:
			return
		#if not isinstance(item[0], Weapon):
		if item[0].weapon_data is None:
			return
		#self.gui.popup_menu.addMenuItem("Examine",
		#				lambda args: self.gui.weapon_info.show(item[0]))
		ammo_in_menu = []
		if len(item[0].weapon_data.magazine) < item[0].weapon_data.magazine_size:
			for ammo_stack in self.application.current_character.inventory.findAmmoCalibre(
								item[0].weapon_data.calibre):
				if ammo_stack[0].name in ammo_in_menu:
					continue
				self.gui.popup_menu.addMenuItem("Load " + ammo_stack[0].name,
							lambda args, ammo_stack=ammo_stack:
							self.gui.inventory.loadAmmo(item[0], ammo_stack))
				amount = min(item[0].weapon_data.magazine_size-len(
							item[0].weapon_data.magazine),len(ammo_stack),3)
				if len(ammo_stack) > 1 and amount > 1 and not self.application.combat.moved:
					self.gui.popup_menu.addMenuItem(
							"Load "+str(amount)+u"×"+ammo_stack[0].name,
							lambda args, ammo_stack=ammo_stack, amount=amount:
							self.gui.inventory.loadAmmo(item[0], ammo_stack, amount))
				ammo_in_menu.append(ammo_stack[0].name)
		if len(item[0].weapon_data.magazine) > 0:
			self.gui.popup_menu.addMenuItem("Unload",
							lambda args: self.gui.inventory.unloadAmmo(item[0]))

	def refresh(self):
		if not self.application.current_character:
			return
		weapon = self.application.current_character.inventory.hands
		if weapon:
			self.weapon_image_combat.setProperty("Image", weapon[0].image)
			if weapon[0].weapon_data.magazine_size > 0:
				self.ammo_label_combat.setText(
					str(len(weapon[0].weapon_data.magazine)) + "/" + str(weapon[0].magazine_size))
			else:
				self.ammo_label_combat.setText("")
		else:
			self.weapon_image_combat.setProperty("Image", "")
			self.ammo_label_combat.setText("")
		if self.application.combat:
			if self.selected_attack not in self.application.combat.available_attacks:
				self.selected_attack = self.application.combat.available_attacks[0]
		self.attack_label_combat.setText(self.selected_attack)
		#else:
		#	self.attack_label_combat.setText("")
		if not self.application.current_character.visual:
			return
		if self.walk_mode == "walk":
			self.walk_button.setProperty("NormalImage", "Button_Walk01/full_image")
			self.walk_button.setProperty("HoverImage", "Button_Walk02/full_image")
			self.walk_button.setProperty("PushedImage", "Button_Walk01/full_image")
			self.application.current_character.visual.sneaking = False
		elif self.walk_mode == "run":
			self.walk_button.setProperty("NormalImage", "Button_Run01/full_image")
			self.walk_button.setProperty("HoverImage", "Button_Run02/full_image")
			self.walk_button.setProperty("PushedImage", "Button_Run01/full_image")
			self.application.current_character.visual.sneaking = False
		else:
			self.walk_button.setProperty("NormalImage", "Button_Sneak01/full_image")
			self.walk_button.setProperty("HoverImage", "Button_Sneak02/full_image")
			self.walk_button.setProperty("PushedImage", "Button_Sneak01/full_image")
			self.application.current_character.visual.sneaking = True

	def show(self):
		self.window_combat.hide()
		self.visible = True
		#self.window.show()
		self.window.moveToFront()
		self.refresh()
		#self.application.pause()

	def updateVisibility(self):
		if self.visible and not self.window_combat.isVisible():
			self.window.show()
		
	def showCombat(self):
		self.window.hide()
		self.window_combat.show()
		self.window_combat.moveToFront()
		self.refresh()
		
	@LogExceptionDecorator
	def hide(self, args=None):
		self.window.hide()
		self.window_combat.hide()
		self.visible = False

	@LogExceptionDecorator
	def defend(self, args):
		self.gui.application.combat.playerEndTurn()
