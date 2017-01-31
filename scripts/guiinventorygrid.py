# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from __future__ import division

import PyCEGUI
#from traceback import print_exc

from error import LogExceptionDecorator


class InventoryGrid(PyCEGUI.Window):
	def __init__(self, type, name):
		super(InventoryGrid, self).__init__(type, name)
		self.setGridSize(1, 1)
		self.setCellSize(104, 104)
		self.item_list = []

	@LogExceptionDecorator
	def populateGeometryBuffer(self):
		if not self.isUserStringDefined("Image"):
			return
		img = PyCEGUI.PropertyHelper.stringToImage(self.getUserString("Image"))
		if not img:
			return
		for i in xrange(self.height):
			for j in xrange(self.width):
				if self.checkSpace(j, i):
					color = 0xFFFFFFFF
				else:
					color = 0xFF808080
				img.render(self.getGeometryBuffer(),
						PyCEGUI.Rectf(PyCEGUI.Vector2f(j*self.cell_width, i*self.cell_height),
										PyCEGUI.Sizef(self.cell_width, self.cell_height)),
						PyCEGUI.Rectf(PyCEGUI.Vector2f(j*self.cell_width, i*self.cell_height),
										PyCEGUI.Sizef(self.cell_width, self.cell_height)),
						PyCEGUI.ColourRect(color))
			
	def setGridSize(self, width, height):
		self.width = width
		self.height = height
		self.invalidate()
		
	def setCellSize(self, width, height):
		self.cell_width = width
		self.cell_height = height
		self.invalidate()
		
	def clearGrid(self):
		for item_data in self.item_list:
			self.removeChild(item_data[0])
		self.item_list = []
		self.invalidate()
		
	def addItem(self, item, x, y, width = 1, height = 1):
		#if not self.checkSpace(x, y, width, height):
		#	return False
		self.item_list.append((item, x, y, width, height,))
		self.addChild(item)
		item.setPosition(PyCEGUI.UVector2(
				PyCEGUI.UDim(0, x*self.cell_width), PyCEGUI.UDim(0, y*self.cell_height)))
		self.invalidate()
		return True
		
	def removeItem(self, item):
		for item_data in self.item_list:
			if item_data[0] == item:
				self.item_list.remove(item_data)
				self.removeChild(item)
				self.invalidate()
				return
	
	def gridXFromPixel(self, loc):
		grid_x = int((loc - self.getChildContentArea().get().left()) / self.cell_width + 0.5)
		if grid_x >= self.width:
			return self.width - 1
		if grid_x < 0:
			return 0
		return grid_x
	
	def gridYFromPixel(self, loc):
		grid_y = int((loc - self.getChildContentArea().get().top()) / self.cell_height + 0.5)
		if grid_y >= self.height:
			return self.height - 1
		if grid_y < 0:
			return 0
		return grid_y

	def checkSpace(self, x, y, width = 1, height = 1):
		#print self.item_list
		if (x + width) > self.width:
			return False
		if (y + height) > self.height:
			return False
		for item_data in self.item_list:
			if (x + width) <= item_data[1]:
				continue
			if (y + height) <= item_data[2]:
				continue
			if x >= (item_data[1] + item_data[3]):
				continue
			if y >= (item_data[2] + item_data[4]):
				continue
			return False
		return True

class InventoryGridFactory(PyCEGUI.WindowFactory):
	def __init__(self):
		super(InventoryGridFactory, self).__init__("InventoryGrid")
		self.windows = []

	def createWindow(self, name):
		new_window = InventoryGrid(super(InventoryGridFactory, self).getTypeName(), name)
		self.windows.append(new_window)
		return new_window

	def destroyWindow(self, window):
		self.windows.remove(window)
