# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from __future__ import print_function

import PyCEGUI
from fife import fife
#from traceback import print_exc

from error import LogException
from config.version import version
from bubble import SayBubble
from detectionbar import DetectionBar
from guipreferences import GUIPreferences
#from guinewcharacter import GUINewCharacter
from guihelp import GUIHelp
from guisaveload import GUISaveLoad
#from guiactionmenu import GUIActionMenu
from guimainmenu import GUIMainMenu, GUIGameMenu
from guitooltip import GUITooltip
from guicombatlog import GUICombatLog
from guidialogue import GUIDialogue
#from guitimeline import GUITimeline
#from guiaistatus import GUIAIStatus
from guibook import GUIBook
from guijournal import GUIJournal
from guicharactersheet import GUICharacterSheet
from guiinventory import GUIInventory
from guihud import GUIHUD
from guiloading import GUILoading
from guilooting import GUILooting
from guiinitiative import GUIInitiative
from guiweaponinfo import GUIWeaponInfo
from guipopupmenu import GUIPopupMenu
from guipopupspinner import GUIPopupSpinner
from guiintrotext import GUIIntroText
from guimaptest import GUIMapTest


class GUI:
	def __init__(self, application):
		print("* Loading GUI...")
		self.application = application
		self.bubbles = []
		self.detection_bars = []

		# create the root window
		PyCEGUI.SchemeManager.getSingleton().createFromFile("TaharezLook.scheme")
		self.root = PyCEGUI.WindowManager.getSingleton().createWindow(
					"DefaultWindow", "_MasterRoot")
		self.root.setProperty("MousePassThroughEnabled", "True")
		self.context = PyCEGUI.System.getSingleton().getDefaultGUIContext()
		self.context.setRootWindow(self.root)

		# load windows from layout files and attach them to the root
		self.loading = GUILoading(self.application)
		self.root.addChild(self.loading.window)
		self.save_load = GUISaveLoad(self.application)
		self.root.addChild(self.save_load.window)
		self.map_test = GUIMapTest(self.application)
		self.root.addChild(self.map_test.window)
		self.help = GUIHelp()
		self.root.addChild(self.help.window)
		self.book = GUIBook()
		self.root.addChild(self.book.window)
		self.combat_log = GUICombatLog(self.help)
		self.root.addChild(self.combat_log.window)
		self.dialogue = GUIDialogue(self)
		self.root.addChild(self.dialogue.window)
		self.journal = GUIJournal(self.application)
		self.root.addChild(self.journal.window)
		self.character_sheet = GUICharacterSheet(self.application)
		self.root.addChild(self.character_sheet.window)
		self.inventory = GUIInventory(self.application, self)
		self.root.addChild(self.inventory.window)
		self.looting = GUILooting(self.application, self)
		self.root.addChild(self.looting.window)
		#self.action_menu = GUIActionMenu(self.application)
		#self.root.addChild(self.action_menu.window)
		#self.timeline = GUITimeline(self.application)
		#self.root.addChild(self.timeline.window)
		#self.new_character = GUINewCharacter(self.application)
		#self.root.addChild(self.new_character.window)
		self.preferences = GUIPreferences(self.application)
		self.root.addChild(self.preferences.window)
		self.game_menu = GUIGameMenu(self.application, self)
		self.root.addChild(self.game_menu.window)
		self.main_menu = GUIMainMenu(self.application, self)
		self.root.addChild(self.main_menu.window)
		self.hud = GUIHUD(self.application, self)
		self.root.addChild(self.hud.window)
		self.root.addChild(self.hud.window_combat)
		self.initiative = GUIInitiative()
		self.root.addChild(self.initiative.window)
		self.weapon_info = GUIWeaponInfo()
		self.root.addChild(self.weapon_info.window)
		self.popup_menu = GUIPopupMenu(self)
		self.root.addChild(self.popup_menu.window)
		self.popup_spinner = GUIPopupSpinner()
		self.root.addChild(self.popup_spinner.window)
		self.intro_text = GUIIntroText()
		self.root.addChild(self.intro_text.window)
		self.global_tooltip = GUITooltip()
		self.global_tooltip.shadow.setName("GlobalTooltipShadow1")
		self.global_tooltip.shadow2.setName("GlobalTooltipShadow2")
		self.global_tooltip.shadow3.setName("GlobalTooltipShadow3")
		self.global_tooltip.shadow4.setName("GlobalTooltipShadow4")
		self.global_tooltip.window.setName("GlobalTooltip")
		self.root.addChild(self.global_tooltip.shadow)
		self.root.addChild(self.global_tooltip.shadow2)
		self.root.addChild(self.global_tooltip.shadow3)
		self.root.addChild(self.global_tooltip.shadow4)
		self.root.addChild(self.global_tooltip.window)
		self.tooltip = GUITooltip()
		self.root.addChild(self.tooltip.shadow)
		self.root.addChild(self.tooltip.shadow2)
		self.root.addChild(self.tooltip.shadow3)
		self.root.addChild(self.tooltip.shadow4)
		self.root.addChild(self.tooltip.window)
		#self.ai_status = GUIAIStatus()
		#self.root.addChild(self.ai_status.window)
		
		# register global sounds
		PyCEGUI.GlobalEventSet.getSingleton().subscribeEvent(
					"Window/" + PyCEGUI.PushButton.EventMouseButtonDown,
					self.buttonSound)

		print("* GUI loaded!")

	def buttonSound(self, args):
		with LogException():
			#print args.window.getType(), args.window.getName()
			if args.button != PyCEGUI.LeftButton:
				return
			if ((args.window.getType()
						in ("TaharezLook/Button", "TaharezLook/ImageButton", "DragContainer",
						"TaharezLook/Checkbox", "TaharezLook/TabButton"))
						or args.window.getName().startswith("Response")):
				self.application.playSound("SFT-INVENTORY-CLICK")

	def pump(self):
		#self.timeline.update()
		self.global_tooltip.clear()
		self.global_tooltip.move(0, 0)
		self.global_tooltip.printMessage("Steamfolk Tales " + version + "\n")
		self.tooltip.clear()
		# get the mouse cursor position
		ptx, pty = self.application.engine.getCursor().getPosition()
		pt = fife.ScreenPoint(ptx, pty)
		# move the tooltip near the mouse cursor
		self.tooltip.move(ptx, pty, 27, 40)
		if (self.application.gui.context.getWindowContainingMouse().getName()
					!= "_MasterRoot"):
			# cursor over the GUI, display tooltip text if any
			self.tooltip.printMessage(
					self.context.getWindowContainingMouse().getTooltipText())
		#self.action_menu.updateTextBox()
		#self.action_menu.updateButtons()
		#for bubble in self.bubbles:
		#	bubble.adjustPosition()
		self.loading.update()
		self.intro_text.update()
		self.hud.updateVisibility()
		for bar in self.detection_bars:
			bar.fill = 0.0

	def sayBubble(self, instance, text, time=2000, color=""):
		for bubble in self.bubbles:
			if instance.getFifeId() == bubble.instance.getFifeId():
				#bubble.destroy()
				bubble.edit(text, time, color)
				return
		self.bubbles.append(SayBubble(self.application, instance, text, time, color))
		#instance.say(text, time)

	def sayBubbleAdd(self, instance, text):
		for bubble in self.bubbles:
			if instance.getFifeId() == bubble.instance.getFifeId():
				#bubble.destroy()
				bubble.add(text)
				return
		#self.bubbles.append(SayBubble(self.application, instance, text, time, color))

	def detectionBar(self, instance, fill, vis_fill, color=""):
		for bar in self.detection_bars:
			if instance.getFifeId() == bar.instance.getFifeId():
				#bar.destroy()
				bar.edit(fill, vis_fill, color)
				return
		self.detection_bars.append(DetectionBar(self.application, instance, fill, vis_fill, color))

	def hideAll(self):
		self.main_menu.window.hide()
		self.combat_log.window.hide()
		self.dialogue.window.hide()
		self.book.window.hide()
		self.save_load.window.hide()
		self.preferences.window.hide()
		self.game_menu.window.hide()
		self.help.window.hide()
		self.journal.window.hide()
		self.character_sheet.window.hide()
		self.inventory.window.hide()
		self.looting.window.hide()
		self.loading.hideFade()
		self.initiative.window.hide()
		self.weapon_info.window.hide()
		self.popup_menu.window.hide()
		self.popup_spinner.window.hide()
		self.intro_text.window.hide()
		self.hud.hide()
		self.map_test.hide()

	def showHUD(self):
		self.hideAll()
		self.hud.show()
		#self.combat_log.clear()
		#self.combat_log.printMessage("Game loaded. Press F1 of click "
		#			+ self.combat_log.createLink("<here>", "home") + " for help.")

	def showMainMenu(self):
		self.hideAll()
		self.main_menu.show()
		#self.tooltip.window.hide()
		#self.tooltip.shadow.hide()
		#self.tooltip.shadow2.hide()
		#self.tooltip.shadow3.hide()
		#self.tooltip.shadow4.hide()

	def escapePressed(self):
		if self.weapon_info.window.isVisible():
			self.weapon_info.window.hide()
		elif self.game_menu.window.isVisible():
			self.game_menu.window.hide()
		elif self.help.window.isVisible():
			self.help.window.hide()
		elif self.preferences.window.isVisible():
			self.preferences.window.hide()
		elif self.save_load.window.isVisible():
			self.save_load.window.hide()
		elif self.journal.window.isVisible():
			self.journal.hide()
		elif self.character_sheet.window.isVisible():
			self.character_sheet.window.hide()
		elif self.inventory.window.isVisible():
			self.inventory.hide()
		elif self.looting.window.isVisible():
			self.looting.window.hide()
		else:
			self.game_menu.show()
