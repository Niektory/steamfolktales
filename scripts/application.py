# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from __future__ import print_function

from fife import fife
from fife.extensions.pychan.pychanbasicapplication import PychanApplicationBase
from fife.extensions.cegui.ceguibasicapplication import CEGUIApplicationBase, CEGUIEventListener
from fife.extensions.soundmanager import SoundManager
#import pickle
#from traceback import print_exc
#import cProfile
#from multiprocessing import Process, Pipe
#from random import randrange

from input import MouseListener, KeyListener
from view import View
from timeline import RealTimeline, Timer
from character import Character
from world import World
from worldvisual import WorldVisual
#from obstacle import Obstacle
from gui import GUI
from combat import Combat
import serializer
import memtest
from exploration import Exploration
from campaign.campaign import Campaign
from config import importobjects
from config import music
from dialogue import DialogueState, loadDialogue


class Listener(CEGUIEventListener):
	def __init__(self, application):
		super(Listener, self).__init__(application)

	def keyPressed(self, evt):
		pass


class Application(CEGUIApplicationBase, PychanApplicationBase):
	def __init__(self, settings):
		#self.ar = []
		#for i in xrange(512):
		#	self.ar.append(' ' * memtest.MEGA)
		#self.a = ' ' * memtest.MEGA * 1024
		#memtest.alloc_max_str()
		#memtest.alloc_max_array()
		
		print("* Initializing application...")
		super(Application, self).__init__(settings)
		self.settings = settings
		self.model = self.engine.getModel()
		self.mapLoader = fife.MapLoader(self.model, 
									self.engine.getVFS(), 
									self.engine.getImageManager(), 
									self.engine.getRenderBackend())
		self.objectLoader = fife.ObjectLoader(self.model, 
									self.engine.getVFS(), 
									self.engine.getImageManager())
#		self.atlasLoader = fife.AtlasLoader(self.model, 
#									self.engine.getVFS(), 
#									self.engine.getImageManager())

		self.map = None
		self.world = None
		self.view = None

		self.eventmanager = self.engine.getEventManager()
		self.mouselistener = MouseListener(self)
		self.keylistener = KeyListener(self)
		self.eventmanager.addMouseListenerFront(self.mouselistener)
		self.eventmanager.addKeyListenerFront(self.keylistener)
		self.soundmanager = SoundManager(self.engine)
		self.fifesoundmanager = self.engine.getSoundManager()
		self.imagemanager = self.engine.getImageManager()
		print("* Application initialized!")

		self.gui = GUI(self)
		self.real_timeline = RealTimeline()
		self.engine.getTimeManager().registerEvent(self.real_timeline)
		self.game_speed = 1
		
		#print self.engine.getRenderBackend().isDepthBufferEnabled()

#		self.loadAtlas("objects/nature.xml")
		print("* Loading objects...")
		for import_object in importobjects.import_list:
			self.loadObject(import_object)
		if self.settings.get("gameplay", "PreloadSprites", True):
			self.imagemanager.reloadAll()
		print("* Objects loaded!")

		self.sounds = {}
		self.music = None
		self.music_name = ""
		#self.music = self.soundmanager.createSoundEmitter("music/SFT-Two Mapple Inn.ogg")
#		self.sound_attack = self.soundmanager.createSoundEmitter("sfx/attack-1.ogg")
		#self.music.looping = True
		if not self.settings.get("FIFE", "PlaySounds"):
			self.fifesoundmanager.setVolume(0.0)
		#self.music.play()

		self.cursor = self.imagemanager.load("gui/cursors/Mousecursor01.png")
		self.cursor.setXShift(-4)
		#self.imagemanager.free("gui/cursors/Mousecursor01.png")
		#self.imagemanager.reload("gui/cursors/Mousecursor01.png")
		self.map_cursor = self.imagemanager.load("gui/cursors/Mousecursor02.png")
		self.map_cursor.setXShift(-29)
		self.map_cursor.setYShift(-29)
		#self.null_image = self.imagemanager.loadBlank(1, 1)
		#self.engine.getCursor().set(self.null_image)
		#self.engine.getCursor().setDrag(self.cursor, -4, 0)
		self.engine.getCursor().set(self.cursor)

		self.unloadMap()
		
		self.lastmem = 0

	def createListener(self):
		self._listener = Listener(self)
		return self._listener

	def playSound(self, sound):
		if sound not in self.sounds:
			self.sounds[sound] = self.soundmanager.createSoundEmitter(
					"sfx/" + sound + ".ogg")
		self.sounds[sound].play()

	def loadObject(self, filename, pingpong = False, object_name = ""):
		if self.objectLoader.isLoadable(filename):
			self.objectLoader.load(filename)
		else:
			print("WARNING: Can't load", filename)

	def loadAtlas(self, filename):
		if self.atlasLoader.isLoadable(filename):
			self.atlasLoader.load(filename)
		else:
			print("WARNING: Can't load", filename)


	def loadMap(self, map_name):
		print("* Loading objects for map", map_name)
		for import_object in importobjects.import_by_map.get(map_name, ()):
			self.loadObject(import_object)
		if self.settings.get("gameplay", "PreloadSprites", True):
			self.imagemanager.reloadAll()
		print("* Objects loaded!")
		filename = str("maps/" + map_name + ".xml")
		if self.mapLoader.isLoadable(filename):
			print("* Loading map", map_name)
			self.map = self.mapLoader.load(filename)
			self.camera = self.map.getCamera("main_camera")
			self.maplayer = self.map.getLayer("buildings_layer")
			#print "imagemanager.reloadAll()"
			#self.imagemanager.reloadAll()
			print("* Map loaded!")
		else:
			print("WARNING: Can't load map")
		if music.music_by_map.get(map_name, self.music_name) != self.music_name:
			self.music_name = music.music_by_map[map_name]
			if self.music:
				self.music.stop()
			self.music = self.soundmanager.createSoundEmitter(
					"music/" + self.music_name + ".ogg")
			self.music.looping = True
			self.music.play()

	def unloadMap(self):
		self.real_timeline.clear()
		if self.world:
			self.world.visual.cleanUp()
		if self.map:
			self.model.deleteMap(self.map)
		if self.imagemanager.getMemoryUsed() > 700000000:
			self.imagemanager.freeUnreferenced()
		print("Memory used by the image manager:", "{:,}".format(self.imagemanager.getMemoryUsed()))
		self.map = None
		self.world = None
		self.view = None
		self.change_map_name = None
		self.combat = None
		self.cutscene = None
		self.exploration = None
		
	def gameOver(self):
		self.unloadMap()
		self.gui.showMainMenu()

	def newGame(self):
		self.loadMap(self.world.current_map_name)
		self.world.visual = WorldVisual(self, self.maplayer, self.world)
		self.view = View(self)
		self.view.camera.getLocationRef().setLayerCoordinates(
					fife.ModelCoordinate(40, 0, 0))
		self.gui.showHUD()
		self.unpause(True)
		self.change_map_name = None
		self.exploration = Exploration(self)
		print("* Game started!")

	def loadMapTest(self, map_name, pc_coords, pc_sprite):
		print("* Loading map test...")
		self.unloadMap()
		self.world = World(self)
		#self.world = World(self, "Ashgrove")
		#campaign.init(self.world)
		self.world.current_map_name = map_name
		if not pc_sprite.endswith(".xml"):
			print("Incorrect sprite file name", pc_sprite)
			return
		pc_sprite_name = pc_sprite.split("\\")[-1][:-4]
		print(pc_sprite, pc_sprite_name)
		pc = self.world.addCharacterAt(pc_coords,
								map_name, "test_character", "test character", str(pc_sprite_name))
		self.world.enablePlayerCharacter(pc)
		self.loadObject("objects\\Sprites - Characters\\" + str(pc_sprite))
		self.loadMap(self.world.current_map_name)
		self.world.visual = WorldVisual(self, self.maplayer, self.world)
		self.view = View(self)
		#self.view.camera.getLocationRef().setLayerCoordinates(
		#			fife.ModelCoordinate(40, 0, 0))
		self.gui.showHUD()
		self.unpause(True)
		self.change_map_name = None
		self.exploration = Exploration(self)
		print("* Map loaded!")

	def saveGame(self, save_name):
		self.world.refresh()
		serializer.save(self.world, "saves/" + save_name + ".sav")
		print("* Game saved!")

	def loadGame(self, save_name):
		self.loadMap(self.world.current_map_name)
		self.world.application = self
		self.world.visual = WorldVisual(self, self.maplayer, self.world)
		self.view = View(self)
		self.gui.showHUD()
		self.unpause(True)
		self.change_map_name = None
		self.exploration = Exploration(self)
		print("* Game loaded!")
		
	def changeMap(self, map_name):
		self.real_timeline.clear()
		self.world.visual.cleanUp()
		self.world.visual = None
		self.world.current_map_name = map_name
		if self.map:
			self.model.deleteMap(self.map)
		if self.imagemanager.getMemoryUsed() > 700000000:
			self.imagemanager.freeUnreferenced()
		print("Memory used by the image manager:", "{:,}".format(self.imagemanager.getMemoryUsed()))
		self.loadMap(self.world.current_map_name)
		self.world.visual = WorldVisual(self, self.maplayer, self.world)
		self.view = View(self)
		self.gui.showHUD()
		self.unpause(True)
		self.exploration = Exploration(self)

	def prepareChangeMap(self, map_name):
		if map_name == self.world.current_map_name:
			return
		print("* Changing map...")
		self.pause(True)
		self.gui.loading.showFade(lambda: self.prepareChangeMap2(map_name), map=map_name)

	def prepareChangeMap2(self, map_name):
		self.change_map_name = map_name

	def prepareNewGame(self):
		print("* Starting new game...")
		self.unloadMap()
		self.world = World(self)
		#self.world = World(self, "Ashgrove")
		Campaign.init(self.world)
		#self.real_timeline.addTimer(Timer("new game", 50, 1, self.newGame))
		self.gui.loading.showFade(self.newGame, map=self.world.current_map_name)

	def prepareLoadGame(self, save_name):
		self.unloadMap()
		self.world = serializer.load("saves/" + save_name + ".sav")
		#self.real_timeline.addTimer(Timer("load game", 50, 1, self.loadGame, args=save_name))
		self.gui.loading.showFade(lambda: self.loadGame(save_name),
									map=self.world.current_map_name)

	def prepareLoadMapTest(self, map_name, pc_coords, pc_sprite):
		self.gui.loading.showFade(lambda: self.loadMapTest(map_name, pc_coords, pc_sprite),
									map=map_name)

	def setTimeMultiplier(self, multiplier):
		self.real_timeline.multiplier = multiplier
		self.model.setTimeMultiplier(multiplier)

	def unpause(self, init=False):
		if init:
			self._paused = False
			self.force_paused = False
		self.world.visual.game_timeline.paused = False
		self.setTimeMultiplier(self.game_speed)

	def pause(self, override=False):
		if override:
			self._paused = True
		self.world.visual.game_timeline.paused = True
		self.setTimeMultiplier(0)

	def togglePause(self):
		if self.force_paused:
			return
		if self._paused:
			self._paused = False
			self.unpause()
		else:
			self._paused = True
			self.pause()

	@property
	def paused(self):
		return self._paused or self.force_paused

	def forcePause(self):
		gui_pause = (self.gui.dialogue.window.isVisible() or self.gui.game_menu.window.isVisible()
				or self.gui.preferences.window.isVisible() or self.gui.help.window.isVisible()
				or self.gui.save_load.window.isVisible() or self.gui.book.window.isVisible()
				or self.gui.journal.window.isVisible()
				or self.gui.character_sheet.window.isVisible()
				or self.gui.inventory.window.isVisible() or self.gui.looting.window.isVisible()
				or self.gui.weapon_info.window.isVisible() or self.gui.loading.window.isVisible())
		#if gui_pause and not self.force_paused:
		if gui_pause or self._paused:
			self.pause()
		#if not gui_pause and self.force_paused and not self._paused:
		else:
			self.unpause()
		self.force_paused = gui_pause	# obsolete?

	@property
	def current_character(self):
		return self.world.player_character

	def startCombat(self, combatants):
		for character in self.world.characters:
			if character.visual:
				character.visual.idle()
		self.combat = Combat(self, combatants)
		self.combat.beginTurn()

	def startCutscene(self, Cutscene):
		self.cutscene = Cutscene(self)
		self.gui.hideAll()

	def startDialogue(self, dialogue, npc=None, pc=None):
		if isinstance(dialogue, str):
			dialogue = loadDialogue(dialogue)
		self.gui.dialogue.start(DialogueState(dialogue, self.world, npc=npc, pc=pc))

	def _pump(self):
		if self.imagemanager.getMemoryUsed() != self.lastmem:
			print("Memory used by the image manager:", "{:,}".format(
															self.imagemanager.getMemoryUsed()))
			#memtest.alloc_max_str()
			#memtest.alloc_max_array()
			self.lastmem = self.imagemanager.getMemoryUsed()
		#if self.imagemanager.getMemoryUsed() > 800000000:
		#	self.imagemanager.freeUnreferenced()
		self.gui.pump()
		#if self.world:
		if self.view:
			self.forcePause()
			if self.change_map_name and (self.world.current_map_name != self.change_map_name):
				self.changeMap(self.change_map_name)
				#memtest.alloc_max_str()
				#memtest.alloc_max_array()
			elif self.cutscene:
				if not self.cutscene.pump():
					self.cutscene = None
					self.gui.hud.show()
				#try:
				#	self.cutscene.pump()
				#except StopIteration:
				#	self.cutscene = None
				#	self.gui.hud.show()
			elif self.combat:
				self.combat.pump()
			elif self.exploration and not self.paused:
				self.exploration.pump(self.real_timeline.last_frame_time)
		#if self.world:
		#	if self.world.visual:
		if self.view:
			self.view.pump()
		if self._listener.quitrequested:
			self.quit()
