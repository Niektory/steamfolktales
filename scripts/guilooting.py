# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from __future__ import print_function

import PyCEGUI
#from traceback import print_exc

from error import LogException
from rpginventory import RPGInventory
#from weapon import Weapon
#from ammo import Ammo
from guiinventorygrid import InventoryGrid, InventoryGridFactory


class GUILooting:
	def __init__(self, application, gui):
		self.application = application
		self.gui = gui
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("Looting.layout")
		self.cancel_button = self.window.getChild("CancelButton")
		self.cancel_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.hide)
		self.take_all_button = self.window.getChild("TakeAllButton")
		self.take_all_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.takeAll)
		
		# prepare the InventoryGrid -- self.backpack_grid -- "Grid" -- x,y
		self.backpack_grid = self.window.getChild("Grid")
		self.backpack_grid.setUserString("Image", "Item_Empty/full_image")
		self.backpack_grid.setGridSize(
					RPGInventory.horz_grid_size, RPGInventory.vert_grid_size)
		self.backpack_grid.subscribeEvent(
							PyCEGUI.Window.EventDragDropItemDropped, self.dropItem)

		# prepare the InventoryGrid -- self.loot_grid -- "LootGrid" -- x,y
		self.loot_grid = self.window.getChild("LootGrid")
		self.loot_grid.setUserString("Image", "Item_Empty/full_image")
		self.loot_grid.setGridSize(
					RPGInventory.horz_grid_size, RPGInventory.vert_grid_size)
		self.loot_grid.subscribeEvent(
							PyCEGUI.Window.EventDragDropItemDropped, self.dropItem)

	def moveItems(self, src_stack, dest_stack, amount):
		for i in xrange(amount):
			dest_stack.append(src_stack.pop())
		self.refresh()
		
	def findStack(self, item):
		if item.getParent() == self.backpack_grid:
			item_coords = map(int, item.getName().split("-")[-2:])
			return self.current_character.inventory.backpack[item_coords[0]][item_coords[1]]
		elif item.getParent() == self.loot_grid:
			item_coords = map(int, item.getName().split("-")[-2:])
			return self.current_loot.inventory.backpack[item_coords[0]][item_coords[1]]
		else:
			print("Item parent unknown!")
			return

	def dropItem(self, args):
		"""
		Handle drag&dropping items on an empty cell.
		args.window -- the grid or frame (if not empty) the item is dropped on
		args.dragDropItem -- the drag container that is being dropped
		"""
		with LogException():
			# shortcuts
			backpack = self.current_character.inventory.backpack
			loot = self.current_loot.inventory.backpack
			# move the RPG item in the character object
			# determine the source stack
			src_stack = self.findStack(args.dragDropItem)
			# determine the destination stack
			if args.window == self.backpack_grid:
				item_area = args.dragDropItem.getUnclippedOuterRect().get()
				drop_x = args.window.gridXFromPixel(item_area.left())
				drop_y = args.window.gridYFromPixel(item_area.top())
				dest_stack = backpack[drop_y][drop_x]
				if not self.current_character.inventory.checkBackpackSpace(drop_x, drop_y,
								src_stack[0].size_x, src_stack[0].size_y, ignore=src_stack):
					# not enough space to move the item
					return
			elif args.window == self.loot_grid:
				item_area = args.dragDropItem.getUnclippedOuterRect().get()
				drop_x = args.window.gridXFromPixel(item_area.left())
				drop_y = args.window.gridYFromPixel(item_area.top())
				dest_stack = loot[drop_y][drop_x]
				if not self.current_loot.inventory.checkBackpackSpace(drop_x, drop_y,
								src_stack[0].size_x, src_stack[0].size_y, ignore=src_stack):
					# not enough space to move the item
					return
			else:
				print("Drag destination unknown!")
				return
			if src_stack is dest_stack:
				# destination is source! nothing to do
				return
			if dest_stack:
				# destination not empty! modify the args and call self.swapItems() instead
				args.window = args.window.getChildElementAtIdx(0)
				self.swapItems(args)
				return
			if len(src_stack) > 1:
				# moving a stack, ask how many items to move
				self.gui.popup_spinner.askForValue(len(src_stack),
							lambda amount: self.moveItems(src_stack, dest_stack, amount))
				return
			self.moveItems(src_stack, dest_stack, 1)
			# refresh the GUI
			self.refresh()

	def swapItems(self, args):
		"""
		Handle drag&dropping items on another item.
		args.window -- the drag container the item is dropped on
		args.dragDropItem -- the drag container that is being dropped
		"""
		with LogException():
			# shortcuts
			backpack = self.current_character.inventory.backpack
			loot = self.current_loot.inventory.backpack
			# swap the RPG items in the character object
			# determine the source stack
			if args.dragDropItem.getParent() == self.backpack_grid:
				src_coords = map(int, args.dragDropItem.getName().split("-")[-2:])
				src_stack = backpack[src_coords[0]][src_coords[1]]
			elif args.dragDropItem.getParent() == self.loot_grid:
				src_coords = map(int, args.dragDropItem.getName().split("-")[-2:])
				src_stack = loot[src_coords[0]][src_coords[1]]
			else:
				print("Drag source unknown!")
				return
			# determine the destination stack
			if args.window.getParent() == self.backpack_grid:
				dest_coords = map(int, args.window.getName().split("-")[-2:])
				dest_stack = backpack[dest_coords[0]][dest_coords[1]]
				if not self.current_character.inventory.checkBackpackSpace(
								dest_coords[1], dest_coords[0],
								src_stack[0].size_x, src_stack[0].size_y, ignore=dest_stack):
					# not enough space to move the item
					return
			elif args.window.getParent() == self.loot_grid:
				dest_coords = map(int, args.window.getName().split("-")[-2:])
				dest_stack = loot[dest_coords[0]][dest_coords[1]]
				if not self.current_loot.inventory.checkBackpackSpace(
								dest_coords[1], dest_coords[0],
								src_stack[0].size_x, src_stack[0].size_y, ignore=dest_stack):
					# not enough space to move the item
					return
			else:
				print("Drag destination unknown!")
				return
			# check if the dest item can be swapped back
			if args.dragDropItem.getParent() == self.backpack_grid:
				if not self.current_character.inventory.checkBackpackSpace(
								src_coords[1], src_coords[0],
								dest_stack[0].size_x, dest_stack[0].size_y, ignore=src_stack):
					return
			elif args.dragDropItem.getParent() == self.loot_grid:
				if not self.current_loot.inventory.checkBackpackSpace(src_coords[1], src_coords[0],
								dest_stack[0].size_x, dest_stack[0].size_y, ignore=src_stack):
					return
			#if isinstance(src_stack[0], Ammo) and isinstance(dest_stack[0], Weapon):
			if src_stack[0].ammo_data and dest_stack[0].weapon_data:
				if (src_stack[0].weapon_data.ammo_calibre == dest_stack[0].weapon_data.calibre
							) and (
							len(dest_stack[0].weapon_data.magazine)
							< dest_stack[0].weapon_data.magazine_size):
					# don't swap, load ammo in the gun instead
					if (len(src_stack) == 1) or (
								(dest_stack[0].weapon_data.magazine_size
								- len(dest_stack[0].weapon_data.magazine)) == 1):
						# only one bullet can be loaded
						self.loadAmmo(dest_stack[0], src_stack)
					else:
						# multiple bullets can be loaded, ask how many
						self.gui.popup_spinner.askForValue(
								min(len(src_stack),
									dest_stack[0].weapon_data.magazine_size
									- len(dest_stack[0].weapon_data.magazine)),
								lambda amount: self.loadAmmo(dest_stack[0], src_stack, amount))
					return
			if (src_stack[0].name == dest_stack[0].name) and (
								dest_stack[0].max_stack > len(dest_stack)):
				# moving on top of the same item type and there's free space,
				# stack instead of swapping
				if (len(src_stack) == 1) or ((dest_stack[0].max_stack - len(dest_stack)) == 1):
					# only one item can be moved
					self.moveItems(src_stack, dest_stack, 1)
				else:
					# multiple items can be moved, ask how many
					self.gui.popup_spinner.askForValue(
							min(len(src_stack), dest_stack[0].max_stack - len(dest_stack)),
							lambda amount: self.moveItems(src_stack, dest_stack, amount))
				return
			# all checks passed, let's swap
			src_stack[:], dest_stack[:] = dest_stack[:], src_stack[:]
			# refresh the GUI
			self.refresh()
			
	def takeAll(self, args=None):
		with LogException():
			for i in xrange(self.current_loot.inventory.vert_grid_size):
				for j in xrange(self.current_loot.inventory.horz_grid_size):
					while self.current_loot.inventory.backpack[i][j]:
						if self.current_character.inventory.addItem(
												self.current_loot.inventory.backpack[i][j][0]):
							self.current_loot.inventory.backpack[i][j].pop(0)
						else:
							break
			#self.show(self.current_character, self.current_loot)
			self.refresh()

	def unloadAmmo(self, weapon):
		with LogException():
			while len(weapon.weapon_data.magazine) > 0:
				self.current_character.inventory.addItem(weapon.weapon_data.magazine.pop())
			self.refresh()

	def loadAmmo(self, weapon, ammo_stack, amount=1):
		with LogException():
			for i in xrange(amount):
				if len(weapon.weapon_data.magazine) < weapon.weapon_data.magazine_size:
					weapon.weapon_data.magazine.append(ammo_stack.pop(0))
			self.refresh()
			if self.application.combat:
				self.application.combat.playerEndTurn()

	def clickedItem(self, args):
		with LogException():
			if args.button == PyCEGUI.RightButton:
				#coords = map(int, args.window.getName().split("-")[-2:])
				#item = self.working_inventory.backpack[coords[0]][coords[1]][0]
				stack = self.findStack(args.window)
				#if isinstance(stack[0], Weapon):
				if stack[0].weapon_data is not None:
					#self.gui.weapon_info.show(item)
					self.gui.popup_menu.show(args.position.d_x, args.position.d_y)
					self.gui.popup_menu.addMenuItem(
								"Examine", lambda args: self.gui.weapon_info.show(stack[0]))
					ammo_in_menu = []
					if len(stack[0].weapon_data.magazine) < stack[0].weapon_data.magazine_size:
						for ammo_stack in self.working_inventory.findAmmoCalibre(
												stack[0].weapon_data.calibre):
							if ammo_stack[0].name not in ammo_in_menu:
								self.gui.popup_menu.addMenuItem(
										"Load " + ammo_stack[0].name,
										lambda args, ammo_stack=ammo_stack: self.loadAmmo(
																			stack[0], ammo_stack))
							ammo_in_menu.append(ammo_stack[0].name)
					if len(stack[0].weapon_data.magazine) > 0:
						self.gui.popup_menu.addMenuItem(
										"Unload", lambda args: self.unloadAmmo(item))

	def show(self, character, loot):
		self.window.show()
		self.window.moveToFront()
		self.current_character = character
		self.current_loot = loot
		self.refresh()

	def refresh(self):
		# refresh the HUD as well
		self.gui.hud.refresh()
		if not self.window.isVisible():
			# looting screen not shown, no need to refresh
			return
		# clear the grids
		self.backpack_grid.clearGrid()
		self.loot_grid.clearGrid()
		# populate the backpack grid
		for i in xrange(self.current_character.inventory.vert_grid_size):
			for j in xrange(self.current_character.inventory.horz_grid_size):
				stack = self.current_character.inventory.backpack[i][j]
				if stack:
					# item(s) present
					self.addItemsToGrid(stack, self.backpack_grid, j, i)
		# populate the loot grid
		for i in xrange(self.current_loot.inventory.vert_grid_size):
			for j in xrange(self.current_loot.inventory.horz_grid_size):
				stack = self.current_loot.inventory.backpack[i][j]
				if stack:
					# item(s) present
					self.addItemsToGrid(stack, self.loot_grid, j, i)

	def addItemsToGrid(self, stack, grid, x, y):
		# add a drag container to the grid -- new_drag_container -- "DragContainer-y-x"
		# add an item image to the drag container -- new_item -- "Item-y-x"
		new_drag_container = PyCEGUI.WindowManager.getSingleton().createWindow(
					"DragContainer", "DragContainer-" + str(y) + "-" + str(x))
		new_drag_container.setSize(PyCEGUI.USize(
					PyCEGUI.UDim(0, 104 * stack[0].size_x), PyCEGUI.UDim(0, 104 * stack[0].size_y)))
		new_drag_container.setTooltipText(stack[0].name)
		new_drag_container.subscribeEvent(
					PyCEGUI.PushButton.EventMouseClick, self.clickedItem)
		new_item = PyCEGUI.WindowManager.getSingleton().createWindow(
					"TaharezLook/StaticImage", "Item-" + str(y) + "-" + str(x))
		new_item.setSize(PyCEGUI.USize(
					PyCEGUI.UDim(0, 104 * stack[0].size_x), PyCEGUI.UDim(0, 104 * stack[0].size_y)))
		new_item.setProperty("HorzFormatting", "CentreAligned")
		new_item.setProperty("VertFormatting", "CentreAligned")
		new_item.setProperty("BackgroundEnabled", "False")
		new_item.setProperty("FrameEnabled", "False")
		new_item.setProperty("MousePassThroughEnabled", "True")
		grid.addItem(new_drag_container, x, y, stack[0].size_x, stack[0].size_y)
		new_drag_container.addChild(new_item)
		new_drag_container.subscribeEvent(
				PyCEGUI.Window.EventDragDropItemDropped, self.swapItems)
		new_drag_container.setDragAlpha(1.0)
		if len(stack) > 1:
			# display stack size
			new_ammo_label = PyCEGUI.WindowManager.getSingleton().createWindow(
					"TaharezLook/Label", "AmmoLabel-" + str(y) + "-" + str(x))
			new_ammo_label.setPosition(
					PyCEGUI.UVector2(PyCEGUI.UDim(0, 10), PyCEGUI.UDim(0, 10)))
			new_ammo_label.setSize(
					PyCEGUI.USize(PyCEGUI.UDim(1, -20), PyCEGUI.UDim(1, -20)))
			new_ammo_label.setProperty("HorzFormatting", "RightAligned")
			new_ammo_label.setProperty("VertFormatting", "BottomAligned")
			new_ammo_label.setProperty("MousePassThroughEnabled", "True")
			new_ammo_label.setText(u"×" + str(len(stack)))
			new_drag_container.addChild(new_ammo_label)
			new_drag_container.setTooltipText(stack[0].name + u" × " + str(len(stack)))
		#elif isinstance(stack[0], Weapon):
		elif stack[0].weapon_data:
			if stack[0].weapon_data.magazine_size > 0:
				# display the ammo in the gun
				new_ammo_label = PyCEGUI.WindowManager.getSingleton().createWindow(
						"TaharezLook/Label", "AmmoLabel-" + str(y) + "-" + str(x))
				new_ammo_label.setPosition(
						PyCEGUI.UVector2(PyCEGUI.UDim(0, 10), PyCEGUI.UDim(0, 10)))
				new_ammo_label.setSize(
						PyCEGUI.USize(PyCEGUI.UDim(1, -20), PyCEGUI.UDim(1, -20)))
				new_ammo_label.setProperty("HorzFormatting", "RightAligned")
				new_ammo_label.setProperty("VertFormatting", "BottomAligned")
				new_ammo_label.setProperty("MousePassThroughEnabled", "True")
				new_ammo_label.setText(
						str(len(stack[0].magazine)) + "/" + str(stack[0].magazine_size))
				new_drag_container.addChild(new_ammo_label)
		if stack[0].image:
			# item image present
			new_item.setProperty("Image", stack[0].image)
		else:
			# no image, using default
			new_item.setProperty("Image", "TaharezLook/CloseButtonHover")

	def hide(self, args=None):
		with LogException():
			self.window.hide()
			