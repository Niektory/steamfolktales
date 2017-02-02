# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from __future__ import print_function

import PyCEGUI
#from traceback import print_exc

from error import LogExceptionDecorator
from dialogue import DialogueState, DialogueResponse
# DialogueNode, DialogueCheck, DialogueResponse, loadDialogue


class GUIDialogue:
	def __init__(self, gui):
		self.gui = gui
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("Dialogue.layout")
		self.npc_text = self.window.getChild("TopFrame/NPCText")
		self.npc_name = self.window.getChild("TopFrame/NPCName")
		self.npc_portrait = self.window.getChild("TopFrame/NPCPortrait")
		self.response_list_container = self.window.getChild("BottomFrame/ResponseList")
		self.current_response_windows = []

	def hide(self):
		self.window.hide()
		self.gui.hud.show()
	"""
	def start(self, npc, pc):
		self.current_npc = npc
		self.current_pc = pc
		self.current_world = pc.world
		if isinstance(npc.dialogue, str):
			self.current_dialogue = loadDialogue(npc.dialogue)
		else:
			self.current_dialogue = npc.dialogue
		self.startCommon()
		
	def startDialogue(self, dialogue, world, pc = None):
		self.current_npc = None
		self.current_pc = pc
		self.current_world = world
		if isinstance(dialogue, str):
			self.current_dialogue = loadDialogue(dialogue)
		else:
			self.current_dialogue = dialogue
		self.startCommon()

	def startCommon(self):
		self.gui.hideAll()
		self.window.show()
		self.window.moveToFront()
		self.displayPortrait(self.current_npc)
		self.current_node = self.current_dialogue.nodes[self.current_dialogue.start_node]
		self.npc_text.setText("")
		self.history = []
		self.enterNode()
	"""

	@property
	def current_node(self):
		return self.dialogue_state.current_node

	def start(self, dialogue_state):
		self.dialogue_state = dialogue_state
		self.gui.hideAll()
		self.window.show()
		self.window.moveToFront()
		self.displayPortrait(self.dialogue_state.npc)
		self.npc_text.setText("")
		self.history = []
		self.enterNode()
		
	def end(self):
		self.dialogue_state = None
		self.hide()
	
	def displayPortrait(self, speaker):
		if speaker is None:
			self.clearPortrait()
			return
		self.npc_name.setText(speaker.name)
		self.npc_portrait.setProperty("Image", speaker.portrait)

	def clearPortrait(self):
		self.npc_name.setText("")
		self.npc_portrait.setProperty("Image", "")

	def printLine(self, speaker, text):
		self.history.append((speaker, text))
		history_text = ""
		for line_number in xrange(len(self.history)):
			if len(history_text) > 0:
				# all lines except the first
				history_text += "\n\n"
			if (line_number + 1) == len(self.history):
				# last line
				text_color = "[colour='FFFFFFFF']"
				# determine the text size before printing the last line so we can scroll here later
				# workaround: force the scrollbar to appear by adding empty space,
				# then subtract its size
				self.npc_text.setText("\n\n\n\n\n\n\n\n\n\n")
				# render the text to update the properties
				self.npc_text.render()
				scroll_pos = float(self.npc_text.getProperty("VertScrollDocumentSize"))
				self.npc_text.setText(history_text+"\n\n\n\n\n\n\n\n\n\n")
				self.npc_text.render()
				scroll_pos = float(self.npc_text.getProperty("VertScrollDocumentSize")) \
							- scroll_pos
				#self.npc_text.setText(history_text)
				#scroll_pos = self.npc_text.getProperty("VertScrollDocumentSize")
			else:
				# all lines except the last
				text_color = "[colour='FFFAE2BB']"
			if self.history[line_number][0]:
				# print the speaker's name and his line
				history_text += (text_color + self.history[line_number][0] + ": "
							+ self.history[line_number][1])
			else:
				# no speaker (narration)
				history_text += text_color + self.history[line_number][1]
			#print line.encode('ascii','ignore')
		# make some empty space so we can scroll freely
		self.npc_text.setText(history_text + "\n\n\n\n\n\n\n\n\n")
		self.npc_text.render()
		# scroll the log to only show the last line
		self.npc_text.setProperty("VertScrollPosition", str(scroll_pos))
		#print "scroll_pos:", scroll_pos
		#print "VertScrollPosition:", self.npc_text.getProperty("VertScrollPosition")
		#print "VertScrollPageSize:", self.npc_text.getProperty("VertScrollPageSize")
		#print "VertScrollDocumentSize:", self.npc_text.getProperty("VertScrollDocumentSize")
		# override the text size to prevent the user from scrolling any further down
		self.npc_text.setProperty("VertScrollDocumentSize", str(scroll_pos
					+ float(self.npc_text.getProperty("VertScrollPageSize"))))
		#print "VertScrollDocumentSize:", self.npc_text.getProperty("VertScrollDocumentSize")
		#print "---"
		#self.npc_text.setProperty(
		#		"VertScrollPosition", self.npc_text.getProperty("VertScrollDocumentSize"))

	def enterNode(self):
		self.dialogue_state.enterNode()
		if self.current_node is None:
			self.end()
			return
		#if type(self.current_node) == DialogueNode:
		#if self.current_node.speaker:
		#self.current_speaker = self.current_node.speaker
		if self.current_node.speaker == "narration":
			self.clearPortrait()
			self.printLine("", self.current_node.npc_text)
		elif self.current_node.speaker:
			speaker = self.dialogue_state.world.getCharacter(self.current_node.speaker)
			self.displayPortrait(speaker)
			self.printLine(speaker.name, self.current_node.npc_text)
		elif self.dialogue_state.npc:
			self.displayPortrait(self.dialogue_state.npc)
			self.printLine(self.dialogue_state.npc.name, self.current_node.npc_text)
		else:
			self.clearPortrait()
			self.printLine("", self.current_node.npc_text)
		#self.npc_text.setText(self.current_node.npc_text)
		#print self.current_response_windows
		while self.response_list_container.getChildCount():
			#print self.response_list_container.getChildAtIdx(0)
			self.response_list_container.removeChild(
						self.response_list_container.getChildAtIdx(0).getID())
		#for response in self.current_response_windows:
		#	print self.response_list_container.isChild(response.getID())
		#	self.response_list_container.removeChild(response)
		self.current_response_windows = []
		#self.current_responses = self.current_node.responses[:]
		self.current_responses = self.dialogue_state.valid_responses[:]
		while True:
			i, j = 0, 0 # TODO: simplify, get rid of j
			for response in self.current_responses:
				i += 1
				#if response.condition and not getattr(Campaign, response.condition)(
				#				self.current_npc, self.current_pc, self.current_world):
				#if response.condition and not Campaign.check(response.condition,
				#				self.current_npc, self.current_pc, self.current_world):
				#	continue
				#j += 1
				j = i
				new_response = PyCEGUI.WindowManager.getSingleton().createWindow(
								"TaharezLook/StaticText", "Response-" + str(i))
				if response.text:
					new_response.setText(str(j) + ". " + response.text)
				else:
					new_response.setText(str(j) + ". Continue.")
				new_response.setProperty("HorzFormatting", "WordWrapLeftAligned")
				new_response.setProperty("VertFormatting", "TopAligned")
				#for k in xrange(3):
				#print (self.window.getWidth().d_scale,
				#		self.window.getWidth().d_offset)
				new_response.setWidth(self.window.getWidth() - PyCEGUI.UDim(0, 36))
				#new_response.render()
				new_response.setHeight(PyCEGUI.UDim(0,
							int(float(new_response.getProperty("VertExtent")))+5))
				#new_response.setProperty("Size", "{{1,-28},{0,"
				#			+ str(int(float(new_response.getProperty("VertExtent")))+17) + "}}")
				#str(min(int(float(new_response.getProperty("HorzExtent"))),490))
				#new_response.setProperty("FrameEnabled", "False")
				new_response.setProperty("BackgroundEnabled", "False")
				new_response.setProperty("TextColours", "FFFAE2BB")
				self.response_list_container.addChild(new_response)
				new_response.subscribeEvent(PyCEGUI.Window.EventMouseClick, self.pickResponse)
				new_response.subscribeEvent(PyCEGUI.Window.EventMouseEntersArea,
											self.mouseEntersResponse)
				new_response.subscribeEvent(PyCEGUI.Window.EventMouseLeavesArea,
											self.mouseLeavesResponse)
				self.current_response_windows.append(new_response)
			# if there's at least one response window created we can end here
			if self.current_response_windows:
				break
			# if there are no responses we add a default one
			# and repeat the loop to create a window
			self.current_responses.append(DialogueResponse())
		"""
		elif type(self.current_node) == DialogueCheck:
			#if getattr(Campaign, self.current_node.check)(
			#					self.current_npc, self.current_pc, self.current_world):
			if Campaign.check(self.current_node.check,
								self.current_npc, self.current_pc, self.current_world):
				if self.current_node.goto_if_true:
					self.current_node = self.current_dialogue.nodes[
													self.current_node.goto_if_true]
					self.enterNode()
				else:
					self.hide()
			elif self.current_node.goto_if_false:
				self.current_node = self.current_dialogue.nodes[self.current_node.goto_if_false]
				self.enterNode()
			else:
				self.hide()
		"""

	# simplify?
	@LogExceptionDecorator
	def pickResponse(self, args):
		picked_response = self.current_responses[int(
				args.window.getName()[args.window.getName().find("-")+1:])-1]
		if picked_response.text:
			if self.dialogue_state.pc:
				self.printLine(self.dialogue_state.pc.name, picked_response.text)
			else:
				self.printLine("", picked_response.text)
		self.dialogue_state.pickResponse(picked_response)
		self.enterNode()
		#if picked_response.goto is not None:
		#	self.current_node = self.current_dialogue.nodes[picked_response.goto]
		#	self.enterNode()
		#else:
		#	self.hide()

	# simplify?
	def pickResponseNumber(self, number):
		if not self.window.isVisible():
			return
		if number > len(self.current_response_windows):
			return
		response_window = self.current_response_windows[number-1]
		picked_response = self.current_responses[int(
						response_window.getName()[response_window.getName().find("-")+1:])-1]
		if picked_response.text:
			if self.dialogue_state.pc:
				self.printLine(self.dialogue_state.pc.name, picked_response.text)
			else:
				self.printLine("", picked_response.text)
		self.dialogue_state.pickResponse(picked_response)
		self.enterNode()
		#if picked_response.goto is not None:
		#	self.current_node = self.current_dialogue.nodes[picked_response.goto]
		#	self.enterNode()
		#else:
		#	self.hide()

	@LogExceptionDecorator
	def mouseEntersResponse(self, args):
		if not args.window.isPropertyPresent("TextColours"):
			print("WARNING: mouseEntersResponse: No property TextColours in", \
				args.window.getName())
			return
		args.window.setProperty("TextColours", "FFFFFFFF")

	@LogExceptionDecorator
	def mouseLeavesResponse(self, args):
		if not args.window.isPropertyPresent("TextColours"):
			print("WARNING: mouseLeavesResponse: No property TextColours in", \
				args.window.getName())
			return
		args.window.setProperty("TextColours", "FFFAE2BB")
