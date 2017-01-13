# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from __future__ import division

from fife import fife
from random import randrange, choice

from animal import Animal


class MouseListener(fife.IMouseListener):
	def __init__(self, application):
		self.application = application
		fife.IMouseListener.__init__(self)
		self.middle_click_point = None
		self.last_click_time = 0
		
	def mousePressed(self, event):
		clickpoint = fife.ScreenPoint(event.getX(), event.getY())
		
		if (event.getButton() == fife.MouseEvent.MIDDLE):
			self.middle_click_point = clickpoint
			self.application.camera.detach()
			
		elif (event.getButton() == fife.MouseEvent.RIGHT):
			if self.application.paused:
				return
			instances = self.application.view.getInstancesAt(clickpoint)
			if self.application.combat:
				# in combat
				for instance in instances:
					clicked_character = self.application.world.visual.findCharacter(instance)
					if clicked_character:
						self.application.combat.playerAttack(clicked_character,
								self.application.gui.hud.selected_attack)
						break
					if self.application.view.findTile(instance):
						self.application.combat.playerAttack(
								self.application.world.findCharacterAt(
								instance.getLocation().getLayerCoordinates()),
								self.application.gui.hud.selected_attack)
						break
			elif self.application.current_character and not self.application.cutscene:
				# out of combat
				for instance in instances:
					clicked_object = self.application.world.visual.findObject(instance)
					if clicked_object:
						if len(clicked_object.possible_actions) > 1:
							self.application.gui.popup_menu.show(event.getX(), event.getY())
							for action in clicked_object.possible_actions:
								self.application.gui.popup_menu.addMenuItem(action.name,
										lambda args:
										self.application.exploration.act(action))
						elif clicked_object.possible_actions:
							self.application.exploration.act(clicked_object.possible_actions[0])
						break

		elif (event.getButton() == fife.MouseEvent.LEFT):
			if self.application.paused:
				return
			location = self.application.view.getLocationAt(clickpoint)
			location.setLayerCoordinates(location.getLayerCoordinates())
			if self.application.combat:
				# in combat
				self.application.combat.playerRun(location)
				# add gear effect and play sound
				location_ground = fife.Location(location)
				location_ground.setLayer(self.application.map.getLayer("top_layer"))
				self.application.view.addSimpleEffect("Greengear", location_ground)
				self.application.playSound("SFT-FOOTSTEP1")
			elif not self.application.cutscene:
				# out of combat
				time = self.application.engine.getTimeManager().getTime()
				if False:#(time - self.last_click_time) < 300:
					# double click disabled for now
					if self.application.current_character:
						# run current character to clicked location
						self.application.current_character.visual.run(location)
						# cancel any scripted actions
						self.application.current_character.idle_script = None
						# add gear effect and play sound
						location_ground = fife.Location(location)
						location_ground.setLayer(self.application.map.getLayer("top_layer"))
						self.application.view.addSimpleEffect("Greengear", location_ground)
						self.application.playSound("SFT-FOOTSTEP1")
				else:
					# single click
					self.last_click_time = time
					if self.application.current_character:
						# walk current character to clicked location
						#self.application.current_character.visual.run(location,
						#						walk_mode=self.application.gui.hud.walk_mode)
						self.application.exploration.move(location)
						# cancel any scripted actions
						#self.application.current_character.idle_script = None
						# add gear effect and play sound
						location_ground = fife.Location(location)
						location_ground.setLayer(self.application.map.getLayer("top_layer"))
						self.application.view.addSimpleEffect("Greengear", location_ground)
						self.application.playSound("SFT-FOOTSTEP1")
					#else:
						# create a new character
						#character = self.application.world.addCharacterAt(
						#					location.getLayerCoordinates())
						#self.application.world.enablePlayerCharacter(character)
							
	def mouseReleased(self, event):
		if (event.getButton() == fife.MouseEvent.MIDDLE):
			self.middle_click_point = None

	def mouseMoved(self, event):
		pass
		
	def mouseEntered(self, event):
		pass
		
	def mouseExited(self, event):
		pass
		
	def mouseClicked(self, event):
		pass
		
	def mouseWheelMovedUp(self, event):
		self.application.view.zoomIn()
		
	def mouseWheelMovedDown(self, event):
		self.application.view.zoomOut()
		
	def mouseDragged(self, event):
		if self.middle_click_point:
			self.application.view.moveCamera((self.middle_click_point.x - event.getX()) / 40,
											(self.middle_click_point.y - event.getY()) / 40)
			self.middle_click_point = fife.ScreenPoint(event.getX(), event.getY())


class KeyListener(fife.IKeyListener):
	def __init__(self, application):
		self.application = application
		fife.IKeyListener.__init__(self)
		self.alt_pressed = False

	def getHotkey(self, hotkey_name):
		if self.application.settings.get("hotkeys", hotkey_name):
			return int(self.application.settings.get("hotkeys", hotkey_name))
		else:
			return None
		
	def keyPressed(self, event):
		key_val = event.getKey().getValue()

		if key_val == self.getHotkey("Quick Load"):
			self.application.prepareLoadGame("quick")
		elif key_val == fife.Key.F1:
			self.application.gui.help.home()
		elif self.application.view:
			if key_val == fife.Key.ESCAPE:
				self.application.gui.escapePressed()
			elif self.application.gui.dialogue.window.isVisible() \
						and fife.Key.NUM_1 <= key_val <= fife.Key.NUM_9:
				self.application.gui.dialogue.pickResponseNumber(key_val - fife.Key.NUM_0)
			elif self.application.gui.dialogue.window.isVisible() \
						and fife.Key.KP1 <= key_val <= fife.Key.KP9:
				self.application.gui.dialogue.pickResponseNumber(key_val - fife.Key.KP0)

			elif key_val == self.getHotkey("Quick Save"):
				self.application.saveGame("quick")
			elif key_val == self.getHotkey("Pause"):
				self.application.togglePause()
			elif key_val == self.getHotkey("Turbo"):
				self.application.game_speed = 6

			elif key_val == self.getHotkey("Journal"):
				if self.application.gui.journal.window.isVisible():
					self.application.gui.journal.hide()
				else:
					self.application.gui.journal.show(self.application.world)
			elif key_val == self.getHotkey("Character Sheet"):
				if self.application.gui.character_sheet.window.isVisible():
					self.application.gui.character_sheet.window.hide()
				elif self.application.current_character:
					self.application.gui.character_sheet.showCharacter(
												self.application.current_character)
			elif key_val == self.getHotkey("Inventory"):
				if self.application.gui.inventory.window.isVisible():
					self.application.gui.inventory.hide()
				elif self.application.current_character:
					self.application.gui.inventory.show()

			elif key_val == self.getHotkey("Grid Coordinates"):
				self.application.view.toggleCoordinates()
			elif key_val == self.getHotkey("Grid Instances"):
				self.application.view.toggleGrid()
			elif key_val == self.getHotkey("Grid Blockers"):
				self.application.view.toggleCells()
			elif key_val == self.getHotkey("Fog of War"):
				self.application.view.toggleFogOfWar()
			elif key_val == self.getHotkey("Character Info"):
				for character in self.application.world.characters:
					if character.visual:
						character.visual.displayStats()
			elif key_val == self.getHotkey("Tooltip"):
				self.application.gui.tooltip.toggle()
			elif key_val == self.getHotkey("Advance Time"):
				self.application.world.advanceTime(6 * 3600000)
			elif key_val == self.getHotkey("Kill Enemies"):
				if self.application.combat:
					self.application.combat.killAllEnemies()

			elif key_val == self.getHotkey("Attach to PC"):
				if self.application.current_character:
					self.application.camera.attach(
										self.application.current_character.visual.instance)
			elif key_val == self.getHotkey("Zoom In"):
				self.application.view.zoomIn()
			elif key_val == self.getHotkey("Zoom Out"):
				self.application.view.zoomOut()
			elif key_val == self.getHotkey("Pan Up"):
				self.application.view.camera_move_key_up = True
			elif key_val == self.getHotkey("Pan Down"):
				self.application.view.camera_move_key_down = True
			elif key_val == self.getHotkey("Pan Left"):
				self.application.view.camera_move_key_left = True
			elif key_val == self.getHotkey("Pan Right"):
				self.application.view.camera_move_key_right = True

			elif key_val == self.getHotkey("End Turn"):
				if self.application.combat:
					self.application.combat.playerEndTurn()

			elif key_val == self.getHotkey("Cycle"):
				self.application.gui.hud.changeWalkMode()
			elif key_val == self.getHotkey("Walk"):
				self.application.gui.hud.changeWalkMode(mode="walk")
			elif key_val == self.getHotkey("Run"):
				self.application.gui.hud.changeWalkMode(mode="run")
			elif key_val == self.getHotkey("Sneak"):
				self.application.gui.hud.changeWalkMode(mode="sneak")

			# press 0 for magic!
			elif key_val == fife.Key.NUM_0:
				for i in xrange(1,5):
					self.application.loadObject("objects/Animals/Butterfly0" + str(i) + ".xml")
				ptx, pty = self.application.engine.getCursor().getPosition()
				pt = fife.ScreenPoint(ptx, pty)
				location = self.application.view.getLocationAt(pt)
				instance = self.application.maplayer.createInstance(
						self.application.model.getObject(
						"Butterfly0"+str(randrange(1,4)), "steamfolktales"),
						location.getLayerCoordinates())
				fife.InstanceVisual.create(instance)
				self.application.view.animals.append(Animal(instance, self.application))

	def keyReleased(self, event):
		key_val = event.getKey().getValue()
		if self.application.view:
			if key_val == self.getHotkey("Pan Up"):
				self.application.view.camera_move_key_up = False
			elif key_val == self.getHotkey("Pan Down"):
				self.application.view.camera_move_key_down = False
			elif key_val == self.getHotkey("Pan Left"):
				self.application.view.camera_move_key_left = False
			elif key_val == self.getHotkey("Pan Right"):
				self.application.view.camera_move_key_right = False

			elif key_val == self.getHotkey("Turbo"):
				self.application.game_speed = 1

