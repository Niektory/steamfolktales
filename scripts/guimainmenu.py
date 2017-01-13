# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

import PyCEGUI
#from traceback import print_exc

from error import LogException


def closeWindow(args):
	args.window.hide()


class GUIMainMenu:
	def __init__(self, application, gui):
		self.application = application
		self.gui = gui
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("MainMenu.layout")

		self.new_game_button = self.window.getChild("MainMenu/NewGameButton")
		self.new_game_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.newGame)
		self.preferences_button = self.window.getChild("MainMenu/PreferencesButton")
		self.preferences_button.subscribeEvent(
					PyCEGUI.PushButton.EventClicked, self.gui.preferences.show)
		self.load_button = self.window.getChild("MainMenu/LoadButton")
		self.load_button.subscribeEvent(
					PyCEGUI.PushButton.EventClicked, self.gui.save_load.showLoad)
		self.map_test_button = self.window.getChild("MainMenu/MapTestButton")
		self.map_test_button.subscribeEvent(
					PyCEGUI.PushButton.EventClicked, self.gui.map_test.show)
		self.quit_game_button = self.window.getChild("MainMenu/QuitGameButton")
		self.quit_game_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.quitGame)
		self.help_button = self.window.getChild("MainMenu/HelpButton")
		self.help_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.help)

		if int(self.application.settings.get(
					"FIFE", "ScreenResolution", "1024x768").split("x")[0]) > 1024:
			self.window.setProperty("Image", "Mainscreen_Background02/full_image")

	def show(self):
		self.window.show()
		self.window.moveToFront()

	def newGame(self, args):
		with LogException():
			self.application.prepareNewGame()

	def quitGame(self, args):
		with LogException():
			self.application.quit()

	def help(self, args):
		with LogException():
			self.gui.help.home()


class GUIGameMenu:
	def __init__(self, application, gui):
		self.application = application
		self.gui = gui
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("GameMenu.layout")
		self.window.subscribeEvent(PyCEGUI.FrameWindow.EventCloseClicked, closeWindow)

		self.continue_button = self.window.getChild("ContinueButton")
		self.continue_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.hide)
		self.help_button = self.window.getChild("HelpButton")
		self.help_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.help)
		self.preferences_button = self.window.getChild("PreferencesButton")
		self.preferences_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.preferences)
		self.save_button = self.window.getChild("SaveButton")
		self.save_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.save)
		self.load_button = self.window.getChild("LoadButton")
		self.load_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.load)
		self.main_menu_button = self.window.getChild("MainMenuButton")
		self.main_menu_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.mainMenu)

	def show(self, args=None):
		with LogException():
			self.window.show()
			self.window.moveToFront()
			#self.application.pause()
		
	def hide(self, args=None):
		with LogException():
			self.window.hide()
			
	def toggle(self, args=None):
		with LogException():
			if self.window.isVisible():
				self.hide()
			else:
				self.show()

	def help(self, args):
		with LogException():
			self.gui.help.home()
			self.window.hide()

	#def saveLoad(self, args):
	#	try:
	#		self.gui.save_load.show()
	#		self.window.hide()
	#	except:
	#		print_exc()
	#		raise

	def save(self, args):
		with LogException():
			self.gui.save_load.showSave()
			self.window.hide()

	def load(self, args):
		with LogException():
			self.gui.save_load.showLoad()
			self.window.hide()

	def preferences(self, args):
		with LogException():
			self.gui.preferences.show()
			self.window.hide()

	def mainMenu(self, args):
		with LogException():
			self.application.unloadMap()
			self.gui.showMainMenu()
