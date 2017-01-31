# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from __future__ import print_function

import PyCEGUI
#from traceback import print_exc
from copy import deepcopy

from error import LogExceptionDecorator
from rpginventory import RPGInventory
#from weapon import Weapon
#from nonplayercharacter import NonPlayerCharacter
#from ammo import Ammo
from guiinventorygrid import InventoryGrid, InventoryGridFactory
#from guiinventoryitem import InventoryItem, InventoryItemFactory


#def myPrint(printable):
#	try:
#		print printable
#	except:
#		print_exc()
#		raise

class GUIInventory:
	def __init__(self, application, gui):
		# let's try this factory stuff once again...
		self.grid_factory = InventoryGridFactory()
		# register new window factory with the system
		PyCEGUI.WindowFactoryManager.getSingleton().addFactory(self.grid_factory)
		# create an instance of the new window type, named "BackpackGrid"
		#self.backpack_grid = PyCEGUI.WindowManager.getSingleton().createWindow(
		#			"InventoryGrid", "BackpackGrid")
		#self.backpack_grid.setUserString("Image", "Item_Empty/full_image")
		#self.window.addChild(self.backpack_grid)
		#self.backpack_grid.setSize(PyCEGUI.USize(PyCEGUI.UDim(0, 416), PyCEGUI.UDim(0, 416)))
		#self.backpack_grid.setGridSize(3, 2)
		#self.backpack_grid.setCellSize(104, 104)
		#self.backpack_grid.addItem(0, 1, 1, 2, 1)

		self.application = application
		self.gui = gui
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("Inventory.layout")
		self.ok_button = self.window.getChild("OKButton")
		self.ok_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.modifyInventory)
		self.cancel_button = self.window.getChild("CancelButton")
		self.cancel_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.hide)
		self.reset_button = self.window.getChild("ResetButton")
		self.reset_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.show)

		# prepare the InventoryGrid -- self.backpack_grid -- "Grid" -- x,y
		self.backpack_grid = self.window.getChild("Grid")
		self.backpack_grid.setUserString("Image", "Item_Empty/full_image")
		self.backpack_grid.setGridSize(
					RPGInventory.horz_grid_size, RPGInventory.vert_grid_size)
		self.hands_grid = self.window.getChild("HandsGrid")
		self.hands_grid.setUserString("Image", "Hands_Background/full_image")
		self.hands_grid.setCellSize(208, 104)
		self.head_grid = self.window.getChild("HeadGrid")
		self.head_grid.setUserString("Image", "Head_Background/full_image")
		self.body_grid = self.window.getChild("BodyGrid")
		self.body_grid.setUserString("Image", "Body_Background/full_image")
		self.backpack_grid.subscribeEvent(
							PyCEGUI.Window.EventDragDropItemDropped, self.dropItem)
		self.hands_grid.subscribeEvent(
							PyCEGUI.Window.EventDragDropItemDropped, self.dropItem)
		self.head_grid.subscribeEvent(
							PyCEGUI.Window.EventDragDropItemDropped, self.dropItem)
		self.body_grid.subscribeEvent(
							PyCEGUI.Window.EventDragDropItemDropped, self.dropItem)

	def moveItems(self, src_stack, dest_stack, amount):
		for i in xrange(amount):
			dest_stack.append(src_stack.pop())
		self.refresh()

	def findStack(self, item):
		if item.getParent() == self.hands_grid:
			return self.working_inventory.hands
		elif item.getParent() == self.head_grid:
			return self.working_inventory.head
		elif item.getParent() == self.body_grid:
			return self.working_inventory.body
		elif item.getParent() == self.backpack_grid:
			item_coords = map(int, item.getName().split("-")[-2:])
			return self.working_inventory.backpack[item_coords[0]][item_coords[1]]
		else:
			print("Item parent unknown!")
			return

	@LogExceptionDecorator
	def dropItem(self, args):
		"""
		Handle drag&dropping items on an empty cell.
		args.window -- the grid or frame (if not empty) the item is dropped on
		args.dragDropItem -- the drag container that is being dropped
		"""
		self.application.playSound("SFT-INVENTORY-CLICK")
		backpack = self.working_inventory.backpack	# shortcut
		# move the RPG item in the character object
		# determine the source stack
		src_stack = self.findStack(args.dragDropItem)
		# determine the destination stack
		if args.window == self.hands_grid:
			dest_stack = self.working_inventory.hands
			if src_stack[0].equipment_type != 0:
				# trying to equip a wrong item type
				return
		elif args.window == self.head_grid:
			dest_stack = self.working_inventory.head
			if src_stack[0].equipment_type != 1:
				# trying to equip a wrong item type
				return
		elif args.window == self.body_grid:
			dest_stack = self.working_inventory.body
			if src_stack[0].equipment_type != 2:
				# trying to equip a wrong item type
				return
		elif args.window == self.backpack_grid:
			item_area = args.dragDropItem.getUnclippedOuterRect().get()
			#item_area.offset(Vector2f(square_size.d_width / 2, square_size.d_height / 2))
			drop_x = args.window.gridXFromPixel(item_area.left())
			drop_y = args.window.gridYFromPixel(item_area.top())
			#dest_coords = (drop_x, drop_y)
			dest_stack = backpack[drop_y][drop_x]
			if not self.working_inventory.checkBackpackSpace(drop_x, drop_y,
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

	@LogExceptionDecorator
	def swapItems(self, args):
		"""
		Handle drag&dropping items on another item.
		args.window -- the drag container the item is dropped on
		args.dragDropItem -- the drag container that is being dropped
		"""
		self.application.playSound("SFT-INVENTORY-CLICK")
		backpack = self.working_inventory.backpack	# shortcut
		# swap the RPG items in the character object
		# determine the source stack
		if args.dragDropItem.getParent() == self.hands_grid:
			src_stack = self.working_inventory.hands
		elif args.dragDropItem.getParent() == self.head_grid:
			src_stack = self.working_inventory.head
		elif args.dragDropItem.getParent() == self.body_grid:
			src_stack = self.working_inventory.body
		elif args.dragDropItem.getParent() == self.backpack_grid:
			src_coords = map(int, args.dragDropItem.getName().split("-")[-2:])
			src_stack = backpack[src_coords[0]][src_coords[1]]
		else:
			print("Drag source unknown!")
			return
		# determine the destination stack
		if args.window.getParent() == self.hands_grid:
			dest_stack = self.working_inventory.hands
			if src_stack[0].equipment_type != 0:
				# trying to equip a wrong item type
				return
		elif args.window.getParent() == self.head_grid:
			dest_stack = self.working_inventory.head
			if src_stack[0].equipment_type != 1:
				# trying to equip a wrong item type
				return
		elif args.window.getParent() == self.body_grid:
			dest_stack = self.working_inventory.body
			if src_stack[0].equipment_type != 2:
				# trying to equip a wrong item type
				return
		elif args.window.getParent() == self.backpack_grid:
			dest_coords = map(int, args.window.getName().split("-")[-2:])
			dest_stack = backpack[dest_coords[0]][dest_coords[1]]
			if not self.working_inventory.checkBackpackSpace(dest_coords[1], dest_coords[0],
							src_stack[0].size_x, src_stack[0].size_y, ignore=dest_stack):
				# not enough space to move the item
				return
		else:
			print("Drag destination unknown!")
			return
		# check if the dest item can be swapped back
		if args.dragDropItem.getParent() == self.hands_grid:
			if dest_stack[0].equipment_type != 0:
				return
		elif args.dragDropItem.getParent() == self.head_grid:
			if dest_stack[0].equipment_type != 1:
				return
		elif args.dragDropItem.getParent() == self.body_grid:
			if dest_stack[0].equipment_type != 2:
				return
		elif args.dragDropItem.getParent() == self.backpack_grid:
			if not self.working_inventory.checkBackpackSpace(src_coords[1], src_coords[0],
							dest_stack[0].size_x, dest_stack[0].size_y, ignore=src_stack):
				return
		#if isinstance(src_stack[0], Ammo) and isinstance(dest_stack[0], Weapon):
		if src_stack[0].ammo_data and dest_stack[0].weapon_data:
			if (src_stack[0].ammo_data.calibre == dest_stack[0].weapon_data.calibre) and (
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

	@LogExceptionDecorator
	def unloadAmmo(self, weapon):
		while len(weapon.weapon_data.magazine) > 0:
			self.working_inventory.addItem(weapon.weapon_data.magazine.pop())
		self.refresh()

	@LogExceptionDecorator
	def loadAmmo(self, weapon, ammo_stack, amount=1):
		for i in xrange(amount):
			if len(weapon.weapon_data.magazine) < weapon.weapon_data.magazine_size:
				weapon.weapon_data.magazine.append(ammo_stack.pop(0))
		self.refresh()
		if self.application.combat:
			self.application.combat.playerEndTurn()

	@LogExceptionDecorator
	def clickedItem(self, args):
		if args.button == PyCEGUI.RightButton:
			#coords = map(int, args.window.getName().split("-")[-2:])
			#item = self.working_inventory.backpack[coords[0]][coords[1]][0]
			stack = self.findStack(args.window)
			#if isinstance(stack[0], Weapon):
			if stack[0].weapon_data is None:
				return
			#self.gui.weapon_info.show(item)
			self.gui.popup_menu.show(args.position.d_x, args.position.d_y)
			self.gui.popup_menu.addMenuItem(
				"Examine",
				lambda args: self.gui.weapon_info.show(stack[0]))
			ammo_in_menu = []
			if len(stack[0].weapon_data.magazine) < stack[0].weapon_data.magazine_size:
				for ammo_stack in self.working_inventory.findAmmoCalibre(
						stack[0].weapon_data.calibre):
					if ammo_stack[0].name not in ammo_in_menu:
						self.gui.popup_menu.addMenuItem(
							"Load " + ammo_stack[0].name,
							lambda args, a_stack=ammo_stack: self.loadAmmo(stack[0], a_stack))
					ammo_in_menu.append(ammo_stack[0].name)
			if len(stack[0].weapon_data.magazine) > 0:
				self.gui.popup_menu.addMenuItem(
								"Unload", lambda args: self.unloadAmmo(item))

	@LogExceptionDecorator
	def show(self, args=None):
		if self.application.combat:
			if len(self.application.combat.animations):
				return
			if not self.application.combat.combatants[
					self.application.combat.current_combatant].player_controlled:
				return
		if self.application.current_character:
			self.showCharacter(self.application.current_character)

	def showCharacter(self, character):
		self.window.show()
		self.window.moveToFront()
		self.current_character = character
		self.working_inventory = deepcopy(self.current_character.inventory)
		self.previous_weapon = self.working_inventory.backpack[0][0]
		self.refresh()

	def refresh(self):
		# refresh the HUD as well
		self.gui.hud.refresh()
		if not self.window.isVisible():
			# inventory not shown, no need to refresh
			return
		# clear the grids
		self.backpack_grid.clearGrid()
		self.hands_grid.clearGrid()
		self.head_grid.clearGrid()
		self.body_grid.clearGrid()
		# populate the backpack grid
		for i in xrange(self.working_inventory.vert_grid_size):
			for j in xrange(len(self.working_inventory.backpack[i])):
				stack = self.working_inventory.backpack[i][j]
				if stack:
					# item(s) present
					self.addItemsToGrid(stack, self.backpack_grid, j, i)
		# populate the equipment grids
		stack = self.working_inventory.hands
		if stack:
			# item(s) present
			self.addItemsToGrid(stack, self.hands_grid, 0, 0)
		stack = self.working_inventory.head
		if stack:
			# item(s) present
			self.addItemsToGrid(stack, self.head_grid, 0, 0)
		stack = self.working_inventory.body
		if stack:
			# item(s) present
			self.addItemsToGrid(stack, self.body_grid, 0, 0)

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
		elif stack[0].weapon_data is not None:
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
						str(len(stack[0].weapon_data.magazine))
						+ "/" + str(stack[0].weapon_data.magazine_size))
				new_drag_container.addChild(new_ammo_label)
		if stack[0].image:
			# item image present
			new_item.setProperty("Image", stack[0].image)
		else:
			# no image, using default
			new_item.setProperty("Image", "TaharezLook/CloseButtonHover")

	@LogExceptionDecorator
	def hide(self, args=None):
		self.window.hide()
			
	@LogExceptionDecorator
	def toggle(self, args=None):
		if self.window.isVisible():
			self.hide()
		else:
			self.show()

	@LogExceptionDecorator
	def modifyInventory(self, args):
		self.current_character.inventory = self.working_inventory
		if self.working_inventory.backpack[0][0] != self.previous_weapon:
			if self.application.combat:
				self.current_character.visual.idle()
				self.application.combat.playerEndTurn()
		self.window.hide()
