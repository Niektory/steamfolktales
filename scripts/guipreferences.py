# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from __future__ import division

import PyCEGUI
from fife import fife
#from traceback import print_exc

from error import LogException


#def closeWindow(args):
#	args.window.hide()

#def doNothing(args):
#	return


class GUIPreferences:
	def __init__(self, application):
		self.application = application
		#self.resolution_items = []
		self.initKeyMap()

		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("Preferences.layout")
		#self.window.subscribeEvent(PyCEGUI.FrameWindow.EventCloseClicked, closeWindow)

		# add tabs for video, audio and controls
		self.tab_control = self.window.getChild("TabControl")
		self.page_gameplay = self.window.getChild("TabPaneGameplay")
		self.page_video = self.window.getChild("TabPaneVideo")
		self.page_audio = self.window.getChild("TabPaneAudio")
		self.page_controls = self.window.getChild("TabPaneControls")
		self.page_controls_scrollable = self.page_controls.getChild("ScrollablePane")
		self.tab_control.addTab(self.page_gameplay)
		self.tab_control.addTab(self.page_video)
		self.tab_control.addTab(self.page_audio)
		self.tab_control.addTab(self.page_controls)

		# gameplay controls
		self.time_acceleration_edit = self.page_gameplay.getChild("TimeAccelerationEdit")
		self.walk_speed_edit = self.page_gameplay.getChild("WalkSpeedEdit")
		self.run_speed_edit = self.page_gameplay.getChild("RunSpeedEdit")
		self.preload_sprites_checkbox = self.page_gameplay.getChild("PreloadSpritesCheckbox")

		# video and audio controls
		self.resolution_list = self.page_video.getChild("Resolutions")
		self.fullscreen_checkbox = self.page_video.getChild("Fullscreen")
		self.enable_sound_checkbox = self.page_audio.getChild("Enable")
		self.volume_slider = self.page_audio.getChild("VolumeSlider")

		# hotkey controls
		self.hotkey_labels = []
		self.hotkey_edits = []
		#for action in self.application.combat_actions.actions:
		#	self.hotkey_actions.append(action.name)
		self.hotkey_actions = [
			"-- Debug --", "Grid Coordinates", "Grid Instances", "Grid Blockers", "Character Info",
			"Tooltip", "Fog of War", "Advance Time", "Turbo", "Kill Enemies",
			"-- Camera Control --",
			"Attach to PC", "Pan Up", "Pan Down", "Pan Left", "Pan Right", "Zoom In", "Zoom Out",
			"-- Game Control --", "Quick Save", "Quick Load", "Pause",
			"-- Open Windows --", "Character Sheet", "Inventory", "Journal",
			"-- Combat Control --", "End Turn",
			"-- Movement Mode --", "Cycle", "Walk", "Run", "Sneak"]
		vert_pos = 10
		for action in self.hotkey_actions:
			new_hotkey_label = PyCEGUI.WindowManager.getSingleton().createWindow(
					"TaharezLook/Label", "HotkeyLabel-" + action)
			new_hotkey_label.setProperty("Text", action)
			new_hotkey_label.setProperty("Position", "{{0,10},{0," + str(vert_pos) + "}}")
			#new_hotkey_label.setProperty("FrameEnabled", "False")
			#new_hotkey_label.setProperty("BackgroundEnabled", "False")
			new_hotkey_label.setProperty("VertFormatting", "TopAligned")
			new_hotkey_label.setProperty("Disabled", "True")

			if action[1] == "-":
				# just a separator label
				new_hotkey_label.setProperty("Size", "{{1,-20},{0,20}}")
				#new_hotkey_label.setProperty("HorzFormatting", "HorzCentred")
				new_hotkey_label.setProperty("HorzFormatting", "CentreAligned")
			else:
				new_hotkey_label.setProperty("Size", "{{0,140},{0,20}}")
				new_hotkey_label.setProperty("HorzFormatting", "RightAligned")

				new_hotkey_edit = PyCEGUI.WindowManager.getSingleton().createWindow(
						"TaharezLook/Editbox", "HotkeyEdit-" + action)
				#if self.application.settings.get("hotkeys", action):
				#	new_hotkey_edit.setProperty("Text", str(self.toCeguiKey(
				#			self.application.settings.get("hotkeys", action))))
				#	new_hotkey_edit.setProperty("HiddenData", str(
				#			self.application.settings.get("hotkeys", action)))
				new_hotkey_edit.setProperty("Size", "{{1,-170},{0,28}}")
				new_hotkey_edit.setProperty("Position", "{{0,160},{0," + str(vert_pos - 7) + "}}")
				new_hotkey_edit.setProperty("TextParsingEnabled", "False")
				new_hotkey_edit.setProperty("MouseInputPropagationEnabled", "True")

				new_hotkey_edit.subscribeEvent(PyCEGUI.Editbox.EventKeyDown, self.hotkeyPressed)
				new_hotkey_edit.subscribeEvent(PyCEGUI.Editbox.EventKeyUp, lambda args: True)
				new_hotkey_edit.subscribeEvent(
								PyCEGUI.Editbox.EventCharacterKey, lambda args: True)

				self.page_controls_scrollable.addChild(new_hotkey_edit)
				self.hotkey_edits.append(new_hotkey_edit)
				self.hotkey_labels.append(new_hotkey_label)

			self.page_controls_scrollable.addChild(new_hotkey_label)
			vert_pos += 30

		self.OK_button = self.window.getChild("OKButton")
		self.OK_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.savePreferences)
		self.cancel_button = self.window.getChild("CancelButton")
		self.cancel_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.hide)

	def savePreferences(self, args):
		with LogException():
			if self.enable_sound_checkbox.isSelected():
				self.application.fifesoundmanager.setVolume(
							self.volume_slider.getScrollPosition() / 10)
			else:
				self.application.fifesoundmanager.setVolume(0.0)
			self.application.settings.set("gameplay", "TimeAcceleration",
						int(self.time_acceleration_edit.getText()))
			self.application.settings.set("gameplay", "WalkSpeed",
						float(self.walk_speed_edit.getText()))
			self.application.settings.set("gameplay", "RunSpeed",
						float(self.run_speed_edit.getText()))
			self.application.settings.set("gameplay", "PreloadSprites",
						self.preload_sprites_checkbox.isSelected())

			if self.resolution_list.getFirstSelectedItem():
				self.application.settings.set("FIFE", "ScreenResolution",
						self.resolution_list.getFirstSelectedItem().getText())
			self.application.settings.set("FIFE", "FullScreen",
						self.fullscreen_checkbox.isSelected())
			self.application.settings.set("FIFE", "PlaySounds",
						self.enable_sound_checkbox.isSelected())
			self.application.settings.set("FIFE", "InitialVolume",
						self.volume_slider.getScrollPosition())
			for i in xrange(len(self.hotkey_edits)):
				self.application.settings.set("hotkeys", self.hotkey_labels[i].getText(),
						self.hotkey_edits[i].getProperty("HiddenData"))
			self.application.settings.saveSettings()
			self.application.gui.hud.updateTooltips()
			self.window.hide()

	def show(self, args=None):
		with LogException():
			settings = self.application.settings	# shortcut

			# load gameplay settings
			self.time_acceleration_edit.setText(
						str(settings.get("gameplay", "TimeAcceleration", 1)))
			self.walk_speed_edit.setText(
						str(settings.get("gameplay", "WalkSpeed", 1.8)))
			self.run_speed_edit.setText(str(settings.get("gameplay", "RunSpeed", 4.0)))
			self.preload_sprites_checkbox.setSelected(
						settings.get("gameplay", "PreloadSprites", True))
			
			# load video and audio settings
			self.resolution_list.resetList()
			self.resolution_items = []
			for resolution in self.application.settings._resolutions:
				self.resolution_items.append(PyCEGUI.ListboxTextItem(resolution))
				self.resolution_items[-1].setAutoDeleted(False)
				self.resolution_items[-1].setSelectionBrushImage(
														"TaharezLook/MultiListSelectionBrush")
				self.resolution_items[-1].setSelectionColours(PyCEGUI.Colour(0.33, 0.295, 0.244))
				self.resolution_items[-1].setTextColours(PyCEGUI.Colour(0.98, 0.886, 0.733))
				self.resolution_list.addItem(self.resolution_items[-1])
				if resolution == settings.get("FIFE", "ScreenResolution", "1024x768"):
					self.resolution_list.setItemSelectState(self.resolution_items[-1], True)
			self.fullscreen_checkbox.setSelected(settings.get("FIFE", "FullScreen", False))
			self.enable_sound_checkbox.setSelected(settings.get("FIFE", "PlaySounds", True))
			self.volume_slider.setScrollPosition(settings.get("FIFE", "InitialVolume", 10.0))

			# load hotkeys
			for action in self.hotkey_actions:
				if action[1] == "-":
					# skip separator labels
					continue
				hotkey_edit = self.page_controls_scrollable.getChild("HotkeyEdit-" + action)
				if settings.get("hotkeys", action):
					hotkey_edit.setProperty("Text", str(self.toCeguiKey(
															settings.get("hotkeys", action))))
					hotkey_edit.setProperty("HiddenData", str(settings.get("hotkeys", action)))
				else:
					hotkey_edit.setProperty("Text", "")
					hotkey_edit.setProperty("HiddenData", "")

			self.window.show()
			self.window.moveToFront()

	def hide(self, args=None):
		with LogException():
			self.window.hide()

	def hotkeyPressed(self, args):
		with LogException():
			for edit in self.hotkey_edits:
				if str(args.scancode) == edit.getText():
					return True
			if args.scancode in [PyCEGUI.Key.Escape, PyCEGUI.Key.F1]:
				args.window.setText("")
				args.window.setProperty("HiddenData", "")
			else:
				args.window.setText(str(args.scancode))
				args.window.setProperty("HiddenData", str(self.toFifeKey(args.scancode)))
			args.window.deactivate()
			return True

	def toFifeKey(self, key):
		return self.r_keymap[key]

	def toCeguiKey(self, key):
		return self.keymap[int(key)]

	def initKeyMap(self):
		self.keymap = dict()
		self.keymap[fife.Key.NUM_1] = PyCEGUI.Key.One
		self.keymap[fife.Key.NUM_2] = PyCEGUI.Key.Two
		self.keymap[fife.Key.NUM_3] = PyCEGUI.Key.Three
		self.keymap[fife.Key.NUM_4] = PyCEGUI.Key.Four
		self.keymap[fife.Key.NUM_5] = PyCEGUI.Key.Five
		self.keymap[fife.Key.NUM_6] = PyCEGUI.Key.Six
		self.keymap[fife.Key.NUM_7] = PyCEGUI.Key.Seven
		self.keymap[fife.Key.NUM_8] = PyCEGUI.Key.Eight
		self.keymap[fife.Key.NUM_9] = PyCEGUI.Key.Nine
		self.keymap[fife.Key.NUM_0] = PyCEGUI.Key.Zero

		self.keymap[fife.Key.Q] = PyCEGUI.Key.Q
		self.keymap[fife.Key.W] = PyCEGUI.Key.W
		self.keymap[fife.Key.E] = PyCEGUI.Key.E
		self.keymap[fife.Key.R] = PyCEGUI.Key.R
		self.keymap[fife.Key.T] = PyCEGUI.Key.T
		self.keymap[fife.Key.Y] = PyCEGUI.Key.Y
		self.keymap[fife.Key.U] = PyCEGUI.Key.U
		self.keymap[fife.Key.I] = PyCEGUI.Key.I
		self.keymap[fife.Key.O] = PyCEGUI.Key.O
		self.keymap[fife.Key.P] = PyCEGUI.Key.P
		self.keymap[fife.Key.A] = PyCEGUI.Key.A
		self.keymap[fife.Key.S] = PyCEGUI.Key.S
		self.keymap[fife.Key.D] = PyCEGUI.Key.D
		self.keymap[fife.Key.F] = PyCEGUI.Key.F
		self.keymap[fife.Key.G] = PyCEGUI.Key.G
		self.keymap[fife.Key.H] = PyCEGUI.Key.H
		self.keymap[fife.Key.J] = PyCEGUI.Key.J
		self.keymap[fife.Key.K] = PyCEGUI.Key.K
		self.keymap[fife.Key.L] = PyCEGUI.Key.L
		self.keymap[fife.Key.Z] = PyCEGUI.Key.Z
		self.keymap[fife.Key.X] = PyCEGUI.Key.X
		self.keymap[fife.Key.C] = PyCEGUI.Key.C
		self.keymap[fife.Key.V] = PyCEGUI.Key.V
		self.keymap[fife.Key.B] = PyCEGUI.Key.B
		self.keymap[fife.Key.N] = PyCEGUI.Key.N
		self.keymap[fife.Key.M] = PyCEGUI.Key.M

		self.keymap[fife.Key.COMMA] = PyCEGUI.Key.Comma
		self.keymap[fife.Key.PERIOD] = PyCEGUI.Key.Period
		self.keymap[fife.Key.SLASH] = PyCEGUI.Key.Slash
		self.keymap[fife.Key.BACKSLASH] = PyCEGUI.Key.Backslash
		self.keymap[fife.Key.MINUS] = PyCEGUI.Key.Minus
		self.keymap[fife.Key.EQUALS] = PyCEGUI.Key.Equals

		self.keymap[fife.Key.SEMICOLON] = PyCEGUI.Key.Semicolon
		self.keymap[fife.Key.LEFTBRACKET] = PyCEGUI.Key.LeftBracket
		self.keymap[fife.Key.RIGHTBRACKET] = PyCEGUI.Key.RightBracket
		self.keymap[fife.Key.QUOTE] = PyCEGUI.Key.Apostrophe
		self.keymap[fife.Key.BACKQUOTE] = PyCEGUI.Key.Grave

		self.keymap[fife.Key.ENTER] = PyCEGUI.Key.Return
		self.keymap[fife.Key.SPACE] = PyCEGUI.Key.Space
		self.keymap[fife.Key.BACKSPACE] = PyCEGUI.Key.Backspace
		self.keymap[fife.Key.TAB] = PyCEGUI.Key.Tab

		self.keymap[fife.Key.ESCAPE] = PyCEGUI.Key.Escape
		self.keymap[fife.Key.PAUSE] = PyCEGUI.Key.Pause
		self.keymap[fife.Key.SYSREQ] = PyCEGUI.Key.SysRq
		self.keymap[fife.Key.POWER] = PyCEGUI.Key.Power

		self.keymap[fife.Key.NUM_LOCK] = PyCEGUI.Key.NumLock
		self.keymap[fife.Key.SCROLL_LOCK] = PyCEGUI.Key.ScrollLock

		self.keymap[fife.Key.F1] = PyCEGUI.Key.F1
		self.keymap[fife.Key.F2] = PyCEGUI.Key.F2
		self.keymap[fife.Key.F3] = PyCEGUI.Key.F3
		self.keymap[fife.Key.F4] = PyCEGUI.Key.F4
		self.keymap[fife.Key.F5] = PyCEGUI.Key.F5
		self.keymap[fife.Key.F6] = PyCEGUI.Key.F6
		self.keymap[fife.Key.F7] = PyCEGUI.Key.F7
		self.keymap[fife.Key.F8] = PyCEGUI.Key.F8
		self.keymap[fife.Key.F9] = PyCEGUI.Key.F9
		self.keymap[fife.Key.F10] = PyCEGUI.Key.F10
		self.keymap[fife.Key.F11] = PyCEGUI.Key.F11
		self.keymap[fife.Key.F12] = PyCEGUI.Key.F12
		self.keymap[fife.Key.F13] = PyCEGUI.Key.F13
		self.keymap[fife.Key.F14] = PyCEGUI.Key.F14
		self.keymap[fife.Key.F15] = PyCEGUI.Key.F15

		self.keymap[fife.Key.LEFT_CONTROL] = PyCEGUI.Key.LeftControl
		self.keymap[fife.Key.LEFT_ALT] = PyCEGUI.Key.LeftAlt
		self.keymap[fife.Key.LEFT_SHIFT] = PyCEGUI.Key.LeftShift
		self.keymap[fife.Key.LEFT_SUPER] = PyCEGUI.Key.LeftWindows
		self.keymap[fife.Key.RIGHT_CONTROL] = PyCEGUI.Key.RightControl
		self.keymap[fife.Key.RIGHT_ALT] = PyCEGUI.Key.RightAlt
		self.keymap[fife.Key.RIGHT_SHIFT] = PyCEGUI.Key.RightShift
		self.keymap[fife.Key.RIGHT_SUPER] = PyCEGUI.Key.RightWindows
		self.keymap[fife.Key.MENU] = PyCEGUI.Key.AppMenu

		self.keymap[fife.Key.KP0] = PyCEGUI.Key.Numpad0
		self.keymap[fife.Key.KP1] = PyCEGUI.Key.Numpad1
		self.keymap[fife.Key.KP2] = PyCEGUI.Key.Numpad2
		self.keymap[fife.Key.KP3] = PyCEGUI.Key.Numpad3
		self.keymap[fife.Key.KP4] = PyCEGUI.Key.Numpad4
		self.keymap[fife.Key.KP5] = PyCEGUI.Key.Numpad5
		self.keymap[fife.Key.KP6] = PyCEGUI.Key.Numpad6
		self.keymap[fife.Key.KP7] = PyCEGUI.Key.Numpad7
		self.keymap[fife.Key.KP8] = PyCEGUI.Key.Numpad8
		self.keymap[fife.Key.KP9] = PyCEGUI.Key.Numpad9
		self.keymap[fife.Key.KP_PERIOD] = PyCEGUI.Key.Decimal
		self.keymap[fife.Key.KP_PLUS] = PyCEGUI.Key.Add
		self.keymap[fife.Key.KP_MINUS] = PyCEGUI.Key.Subtract
		self.keymap[fife.Key.KP_MULTIPLY] = PyCEGUI.Key.Multiply
		self.keymap[fife.Key.KP_DIVIDE] = PyCEGUI.Key.Divide
		self.keymap[fife.Key.KP_ENTER] = PyCEGUI.Key.NumpadEnter

		self.keymap[fife.Key.UP] = PyCEGUI.Key.ArrowUp
		self.keymap[fife.Key.LEFT] = PyCEGUI.Key.ArrowLeft
		self.keymap[fife.Key.RIGHT] = PyCEGUI.Key.ArrowRight
		self.keymap[fife.Key.DOWN] = PyCEGUI.Key.ArrowDown

		self.keymap[fife.Key.HOME] = PyCEGUI.Key.Home
		self.keymap[fife.Key.END] = PyCEGUI.Key.End
		self.keymap[fife.Key.PAGE_UP] = PyCEGUI.Key.PageUp
		self.keymap[fife.Key.PAGE_DOWN] = PyCEGUI.Key.PageDown
		self.keymap[fife.Key.INSERT] = PyCEGUI.Key.Insert
		self.keymap[fife.Key.DELETE] = PyCEGUI.Key.Delete

		self.r_keymap = {v:k for k, v in self.keymap.items()}

