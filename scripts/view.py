# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from __future__ import division, print_function

import math
import PyCEGUI
from random import randrange
from fife import fife
from fife.extensions.pychan.internal import get_manager

from character import Character
#from obstacle import Obstacle
from timeline import Timer
from animal import Animal, Bird
from plant import Plant
from effects import SimpleEffect
from config import customanimations
from error import LogExceptionDecorator


class ViewLayerChangeListener(fife.LayerChangeListener):
	def onLayerChanged(self, layer, changedInstances): pass
	def onInstanceDelete(self, layer, instance): pass

	def __init__(self, view):
		super(ViewLayerChangeListener, self).__init__()
		self.view = view

	@LogExceptionDecorator
	def onInstanceCreate(self, layer, instance):
		# force lighting update whenever an instance is added
		self.view.last_hour = None


class View:
	def __init__(self, application):
		print("* Initializing view...")
		self.application = application
		self.camera = self.application.camera
		self.target_zoom = 1.0
		self.camera.setZoom(1.0)

		self.camera_move_key_up = False
		self.camera_move_key_down = False
		self.camera_move_key_left = False
		self.camera_move_key_right = False
		self.camera_move_mouse_up = False
		self.camera_move_mouse_down = False
		self.camera_move_mouse_left = False
		self.camera_move_mouse_right = False
		self.effects = []
		#self.tiles = {}
		self.tiles = []
		self.hidden_obstructions = []
		self.last_hour = None
		self.cursor = self.application.cursor

		self.camera.setViewPort(fife.Rect(
				0,0,self.application.engine.getRenderBackend().getScreenWidth(),
				self.application.engine.getRenderBackend().getScreenHeight()))

		print("  * Enabling renderers...")
		self.instance_renderer = fife.InstanceRenderer.getInstance(self.camera)
		self.instance_renderer.addIgnoreLight(["effects"])
		#self.foo = True

		self.floating_text_renderer = fife.FloatingTextRenderer.getInstance(self.camera)
		textfont = get_manager().createFont("fonts/rpgfont.png", 0,
					str(application.settings.get("FIFE", "FontGlyphs")));
		self.floating_text_renderer.setFont(textfont)
		self.floating_text_renderer.activateAllLayers(self.application.map)
		#self.floating_text_renderer.setBackground(210, 210, 100, 63)
		#self.floating_text_renderer.setBorder(210, 210, 100)
		self.floating_text_renderer.setEnabled(True)

		self.grid_renderer = self.camera.getRenderer("GridRenderer")
		self.grid_renderer.setEnabled(False)
		self.grid_renderer.activateAllLayers(self.application.map)
		
		self.coordinate_renderer = fife.CoordinateRenderer.getInstance(self.camera)
		self.coordinate_renderer.setFont(textfont)
		self.coordinate_renderer.setEnabled(False)
		self.coordinate_renderer.activateAllLayers(self.application.map)
		
		self.cell_renderer = fife.CellRenderer.getInstance(self.camera)
		self.cell_renderer.clearActiveLayers()
		self.cell_renderer.addActiveLayer(self.application.maplayer)
		self.cell_renderer.setEnabled(True)
		self.cell_renderer.setEnabledBlocking(False)
		self.cell_renderer.setEnabledFogOfWar(False)
		
		self.concimg = self.application.engine.getImageManager().load(
						"objects/Effects/black_cell.png")
		self.maskimg = self.application.engine.getImageManager().load(
						"objects/Effects/mask_cell.png")
		self.cell_renderer.setConcealImage(self.concimg)
		self.cell_renderer.setMaskImage(self.maskimg)
		self.cell_renderer.setFogOfWarLayer(self.application.maplayer)
			
		#self.cell_renderer.setEnabledPathVisual(True)
		#self.cell_renderer.setPathColor(255, 210, 0)
		
		self.light_renderer = fife.LightRenderer.getInstance(self.camera)
		self.light_renderer.setEnabled(True)
		self.light_renderer.clearActiveLayers()
		self.light_renderer.addActiveLayer(self.application.maplayer)
	
		print("  * Customizing looping animations...")
		self.pingPongAnimations()
		print("  * Activating plants and animals...")
		self.randomizeAnimations()
		self.activateAnimals()

		if self.application.current_character:
			if self.application.current_character.visual:
				self.camera.attach(self.application.current_character.visual.instance)
				self.application.current_character.visual.instance.setVisitor(True)
				self.application.current_character.visual.instance.setVisitorRadius(9)

		self.layer_change_listener = ViewLayerChangeListener(self)
		self.application.maplayer.addChangeListener(self.layer_change_listener)
		print("* View initialized!")


	def toggleCoordinates(self):
		self.coordinate_renderer.setEnabled(not self.coordinate_renderer.isEnabled())

	def toggleGrid(self):
		self.grid_renderer.setEnabled(not self.grid_renderer.isEnabled())

	def toggleCells(self):
		self.cell_renderer.setEnabledBlocking(not self.cell_renderer.isEnabledBlocking())

	def toggleFogOfWar(self):
		self.cell_renderer.setEnabledFogOfWar(not self.cell_renderer.isEnabledFogOfWar())
		self.camera.refresh()

	def zoomIn(self):
		if self.target_zoom < 1:
			self.target_zoom *= 2.0
		else:
			self.target_zoom = min(self.target_zoom + 1, 3)

	def zoomOut(self):
		if self.target_zoom <= 1:
			self.target_zoom = max(self.target_zoom / 2, 0.25)
		else:
			self.target_zoom = max(self.target_zoom - 1, 1)

	def moveCamera(self, camera_move_x, camera_move_y):
		scr_coord = self.camera.getOrigin() + fife.ScreenPoint(camera_move_x, camera_move_y)
		coord = self.camera.toMapCoordinates(scr_coord, False)
		coord.z = 0

		#cur_rot = self.camera.getRotation()
		#cell_dimensions = self.camera.getCellImageDimensions()
		#new_coord2 = self.camera.getLocation().getMapCoordinates()
		#new_coord2.x += ((math.cos(cur_rot / 180 * math.pi) * camera_move_x / cell_dimensions.x
		#		- math.sin(cur_rot / 180 * math.pi) * camera_move_y / cell_dimensions.y)
		#		/ self.target_zoom * math.sqrt(2))
		#new_coord2.y += ((math.cos(cur_rot / 180 * math.pi) * camera_move_y / cell_dimensions.y
		#		+ math.sin(cur_rot / 180 * math.pi) * camera_move_x / cell_dimensions.x)
		#		/ self.target_zoom * math.sqrt(2))

		#x_error = abs(new_coord2.x - new_coord.x)
		#y_error = abs(new_coord2.y - new_coord.y)
		#if  x_error > self.x_error:
		#	print(self.x_error, self.y_error)
		#	self.x_error = x_error
		#if  y_error > self.y_error:
		#	print(self.x_error, self.y_error)
		#	self.y_error = y_error

		# limit the camera to the current map's borders
		map_size = self.application.maplayer.getCellCache().getSize()
		if coord.x < map_size.x:
			coord.x = map_size.x
		if coord.y < map_size.y:
			coord.y = map_size.y
		if coord.x > map_size.w:
			coord.x = map_size.w
		if coord.y > map_size.h:
			coord.y = map_size.h

		loc = self.camera.getLocation()
		loc.setMapCoordinates(coord)
		self.camera.setLocation(loc)

	def animateCamera(self):
		# detach the camera if there's no PC or no PC visual; might crash otherwise
		if not self.application.current_character:
			self.camera.detach()
		elif not self.application.current_character.visual:
			self.camera.detach()
		# animate zooming
		cur_zoom = self.camera.getZoom()
		if self.target_zoom > cur_zoom:
			if self.target_zoom < cur_zoom + 0.1:
				self.camera.setZoom(self.target_zoom)
			else:
				self.camera.setZoom(cur_zoom + 0.1)
		elif self.target_zoom < cur_zoom:
			if self.target_zoom > cur_zoom - 0.1:
				self.camera.setZoom(self.target_zoom)
			else:
				self.camera.setZoom(cur_zoom - 0.1)
		# animate panning
		if self.camera_move_key_up or self.camera_move_mouse_up:
			camera_move_y = -25
		elif self.camera_move_key_down or self.camera_move_mouse_down:
			camera_move_y = 25
		else:
			camera_move_y = 0
		if self.camera_move_key_left or self.camera_move_mouse_left:
			camera_move_x = -25
		elif self.camera_move_key_right or self.camera_move_mouse_right:
			camera_move_x = 25
		else:
			camera_move_x = 0
		self.moveCamera(camera_move_x, camera_move_y)

	def getInstancesAt(self, screenpoint):
		return (self.camera.getMatchingInstances(screenpoint, self.application.maplayer) +
				self.camera.getMatchingInstances(screenpoint,
				self.application.map.getLayer("ground_layer")))

	def getLocationAt(self, screenpoint):
		target_mapcoord = self.camera.toMapCoordinates(screenpoint, False)
		target_mapcoord.z = 0
		location = fife.Location(self.application.maplayer)
		location.setMapCoordinates(target_mapcoord)
		return location

	def highlightTile(self, instance):
		self.instance_renderer.addColored(instance, 210, 210, 100)
	
	def highlightObject(self, target_object):
		instance = target_object.visual.instance
		# display instance info in the tooltip
		if len(target_object.possible_actions) == 1 and not self.application.combat:
			self.application.gui.tooltip.printMessage(target_object.possible_actions[0].name + ": "
													+ target_object.name + "\n")
		else:
			self.application.gui.tooltip.printMessage(target_object.name + "\n")
		if self.application.world.visual.findCharacter(instance):
			# display character info in the tooltip
			self.application.gui.tooltip.printMessage("Stamina: "
											+ str(target_object.rpg_stats.cur_stamina)
											+ "/" + str(target_object.rpg_stats.max_stamina) + "\n")
			if len(target_object.rpg_stats.wounds):
				wounds_str = "Wounds: "
				for wound in target_object.rpg_stats.wounds:
					wounds_str += wound.name + ", "
				wounds_str = wounds_str[:-2]
			else:
				wounds_str = "No wounds"
			self.application.gui.tooltip.printMessage(wounds_str + "\n")
			#print str(target_object.rpg_stats.wounds)
			#print "Wounds: " + str(target_object.rpg_stats.wounds)
		# highlight the instance
		self.instance_renderer.addColored(instance, 210, 210, 100, 192)
		#self.instance_renderer.addOutlined(instance, 210, 210, 100, 1)

	def highlightInstances(self):
		# reset cursor
		self.cursor = self.application.cursor
		for map_object in (
					self.application.world.characters + self.application.world.interact_objects):
			if map_object.visual:
				# clear colorings and outlines from map objects
				self.instance_renderer.removeOutlined(map_object.visual.instance)
				self.instance_renderer.removeColored(map_object.visual.instance)
		for tile in self.tiles:
			# clear colorings from tiles
			self.instance_renderer.removeColored(tile)
		if self.application.combat:
			if len(self.application.combat.animations):
				# no highlighting when combat animations are playing -> abort
				return
		#if (PyCEGUI.System.getSingleton().getWindowContainingMouse().getName() == "_MasterRoot"):
		# CEGUI wiki says: The chain call of methods
		# CEGUI::System::getSingleton().getDefaultGUIContext()
		# should be called as rarely as possible, instead one should keep it's result
		# in appropriate variable. 
		ptx, pty = self.application.engine.getCursor().getPosition()
		pt = fife.ScreenPoint(ptx, pty)
		# move the tooltip near the mouse cursor
		#self.application.gui.tooltip.move(ptx, pty)
		if (self.application.gui.context.getWindowContainingMouse().getName()
					!= "_MasterRoot"):
			# cursor over the GUI, abort
			#self.application.gui.tooltip.printMessage(
			#		self.application.gui.context.getWindowContainingMouse().getTooltipText())
			return
		#if self.application.combat:
			# display combat info in the tooltip
			#self.application.gui.tooltip.printMessage("Movement left: " + 
			#		str(self.application.combat.current_AP))
		for instance in self.hidden_obstructions:
			instance.get2dGfxVisual().setTransparency(0)
		self.hidden_obstructions = []
		if self.application.current_character:
			if self.application.current_character.visual:
				self.instance_renderer.addTransparentArea(
						self.application.current_character.visual.instance,
						["obstruction"], 1, 1, 254, True)
		instances = self.getInstancesAt(pt)
		for instance in instances:
			# skip distractions under the cursor
			#if instance.getObject().getId() in []:
			#	continue
			# display object name in the tooltip
			#self.application.gui.tooltip.printMessage("Object ID: " + instance.getObject().getId())
			# display coordinates in the tooltip
			#self.application.gui.tooltip.printMessage("Coordinates: "
			#			+ str(instance.getLocation().getLayerCoordinates()))
			# hide obstructing objects under the cursor
			#if instance.getObject().getId() in customanimations.hide_obstructions:
			if instance.getObject().getNamespace() == "obstruction":
				instance.get2dGfxVisual().setTransparency(254)
				self.hidden_obstructions.append(instance)
			target_object = self.application.world.visual.findObject(instance)
			if target_object:
				# highlight the instance
				self.highlightObject(target_object)
				# highlight the tile under the character
				tile = self.findTileAt(target_object.coords)
				if tile:
					self.highlightTile(tile)
				#break
				return
			target_tile = self.findTile(instance)
			if target_tile:
			#if instance in self.tiles:
				# highlight the instance
				self.highlightTile(instance)
				# highlight the character standing on the tile
				character = self.application.world.findCharacterAt(
								instance.getLocation().getLayerCoordinates())
				if character:
					if character.visual:
						self.highlightObject(character)
				#break
				return
		# display map transition info
		location = self.getLocationAt(pt)
		transition = self.application.world.findMapTransitionAt(location.getLayerCoordinates())
		if transition:
			self.application.gui.tooltip.printMessage(transition.name)
			self.cursor = self.application.map_cursor

		# outline the selected character
		#if self.application.current_character:
		#	if self.application.current_character.visual.instance:
		#		self.instance_renderer.addOutlined(
		#						self.application.current_character.visual.instance,
		#						255, 255, 255, 2)

	def pingPongAnimations(self):
		for object_name in reversed(customanimations.pingpong_names):
			if not self.application.model.getObject(object_name, "steamfolktales"):
				continue
			print("Customizing animation:", object_name)
			action = self.application.model.getObject(
										object_name, "steamfolktales").getAction("idle")
			visual = action.get2dGfxVisual()
			anim = visual.getAnimationByAngle(visual.getActionImageAngles()[0])
			for i in xrange(anim.getFrameCount()-2, 0, -1):
				anim.addFrame(anim.getFrame(i), anim.getFrameDuration(i))
			action.setDuration(anim.getDuration())
			customanimations.pingpong_names.remove(object_name)

	def randomizeAnimations(self):
		self.plants = []
		for instance in self.application.maplayer.getInstances():
			if instance.getObject().getId() in customanimations.randomize_names:
				self.plants.append(Plant(instance))
				#instance.actRepeat("idle")
				#instance.setActionRuntime(randrange(
				#				instance.getObject().getAction("idle").getDuration()))

	def activateAnimals(self):
		self.animals = []
		for instance in self.application.maplayer.getInstances():
			if instance.getObject().getId() in customanimations.animal_names:
				self.animals.append(Animal(instance, self.application))
		for instance in self.application.map.getLayer("top_layer").getInstances():
			if instance.getObject().getId() in customanimations.bird_names:
				self.animals.append(Bird(instance, self.application))

	def updateLighting(self):
		hour = self.application.world.getHour()
		# optimization: this method is expensive, so only run it:
		# - after loading a new map (self.last_hour is None)
		# - if the hour has changed since the last run
		# - if new instances were added since the last run (a listener sets self.last_hour to None)
		# TODO: in the last case: only update the new instances, not all of them
		if hour == self.last_hour:
			return
		self.last_hour = hour
		day = self.application.world.getDay()
		# tooltip clock
		#self.application.gui.tooltip.printMessage("Day " + str(day)
		#			+ "; Time: " + str(int(hour)) + ":" + str(int((hour%1.0)*60)))
		# day-night cycle
		self.light_renderer.removeAll("pc")
		cycle = customanimations.light_cycle
		for next_hour in cycle:
			if hour < next_hour:
				factor = (hour - prev_hour) / (next_hour - prev_hour)
				# global light
				self.camera.setLightingColor(
							cycle[prev_hour][0]+factor*(cycle[next_hour][0]-cycle[prev_hour][0]),
							cycle[prev_hour][1]+factor*(cycle[next_hour][1]-cycle[prev_hour][1]),
							cycle[prev_hour][2]+factor*(cycle[next_hour][2]-cycle[prev_hour][2]))
				# local lights
				#if self.application.current_character:
				#	if self.application.current_character.visual:
				#		for i in xrange(2):
				#			self.light_renderer.addSimpleLight("pc",
				#				fife.RendererNode(
				#				self.application.current_character.visual.instance),
				#				255, 64, 32, 3.0, 1.875,
				#				int((cycle[prev_hour][3]+factor*
				#				(cycle[next_hour][3]-cycle[prev_hour][3]))*255),
				#				int((cycle[prev_hour][4]+factor*
				#				(cycle[next_hour][4]-cycle[prev_hour][4]))*255),
				#				int((cycle[prev_hour][5]+factor*
				#				(cycle[next_hour][5]-cycle[prev_hour][5]))*255))
				for instance in self.application.maplayer.getInstances():
					if not instance:
						print("getInstances() error!", instance)
						#self.application.maplayer.getInstances()
						continue
					if instance.getObject().getId() not in customanimations.light_circles:
						continue
					circle = customanimations.light_circles[instance.getObject().getId()]
					if not ((circle[0] < hour < circle[1]) or (hour < circle[1] < circle[0])
							or (circle[1] < circle[0] < hour)):
						continue
					for i in xrange(2): # double light power!
						self.light_renderer.addSimpleLight(group="pc",
							n=fife.RendererNode(instance, fife.Point(
								int(circle[7]),
								#int(circle[7] * self.camera.getZoom()),
								int(circle[8]))),
								#int(circle[8] * self.camera.getZoom()))),
							intensity=255, radius=64, subdivisions=32,
							xstretch=circle[2], ystretch=circle[3],
							r=int(circle[4]*255), g=int(circle[5]*255), b=int(circle[6]*255))
				break
			prev_hour = next_hour
		# set transparency for light overlay instances
		for instance in self.application.maplayer.getInstances():
			if not instance:
				print("getInstances() error!", instance) #self.application.maplayer.getInstances()
				continue
			if instance.getObject().getId() in customanimations.light_instances:
				hours = customanimations.light_instances[instance.getObject().getId()]
				if ((hours[0] < hour < hours[1]) or (hour < hours[1] < hours[0])
												or (hours[1] < hours[0] < hour)):
					instance.get2dGfxVisual().setTransparency(0)
				else:
					instance.get2dGfxVisual().setTransparency(255)

	def addSimpleEffect(self, object_name, location):
		self.effects.append(SimpleEffect(self.application, object_name, location))

	def addTile(self, coords, transparency=0):
		instance = self.application.map.getLayer("ground_layer").createInstance(
					self.application.model.getObject("Tile", "steamfolktales"), coords)
		fife.InstanceVisual.create(instance)
		instance.get2dGfxVisual().setTransparency(transparency)
		#self.instance_renderer.addColored(instance, r, g, b, a)
		#self.tiles[coords] = instance
		self.tiles.append(instance)
		
	def findTile(self, instance):
		for tile in self.tiles:
			if tile.getFifeId() == instance.getFifeId():
				return True
		return False
		
	def findTileAt(self, coords):
		for tile in self.tiles:
			if tile.getLocation().getLayerCoordinates() == coords:
				return tile
		
	def clearTiles(self):
		#print self.tiles
		#for instance in self.tiles.values():
		for instance in self.tiles:
			#print instance
			self.application.map.getLayer("ground_layer").deleteInstance(instance)
		#self.tiles = {}
		self.tiles = []

	def pump(self):
		self.updateLighting()
		if not self.application.cutscene:
			self.animateCamera()
		else:
			self.camera.refresh()
		self.highlightInstances()
		self.application.engine.getCursor().set(self.cursor)
