# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

import xml.etree.ElementTree as ET

from xmlhelper import indent
from campaign.campaign import Campaign


class DialogueCheck(object):
	def __init__(self, check, goto_if_true = None, goto_if_false = None):
		self.check = check
		self.goto_if_true = goto_if_true
		self.goto_if_false = goto_if_false
		
class DialogueNode(object):
	def __init__(self, text, speaker = None):
		self.npc_text = text
		self.speaker = speaker
		self.responses = []

class DialogueResponse(object):
	def __init__(self, text = None, goto = None, condition = None):
		self.condition = condition
		self.text = text
		self.goto = goto


class Dialogue(object):
	def __init__(self):
		self.nodes = {None:None}
		self.start_node = 0

	def saveXML(self, filename):
		root = ET.Element("Dialogue")
		tree = ET.ElementTree(root)
		root.set("start_node", str(self.start_node))
		for key, node in sorted(self.nodes.iteritems()):
			if isinstance(node, DialogueNode):
				element = ET.SubElement(root, "DialogueNode")
				element.set("key", str(key))
				if node.speaker:
					element.set("speaker", node.speaker)
				element.set("npc_text", node.npc_text)
				#element.text = node.npc_text
				for response in node.responses:
					response_element = ET.SubElement(element, "DialogueResponse")
					if response.text:
						response_element.set("text", response.text)
					if response.condition:
						response_element.set("condition", response.condition)
					if response.goto:
						response_element.set("goto", str(response.goto))
			elif isinstance(node, DialogueCheck):
				element = ET.SubElement(root, "DialogueCheck")
				element.set("key", str(key))
				element.set("check", node.check)
				if node.goto_if_true:
					element.set("goto_if_true", str(node.goto_if_true))
				if node.goto_if_false:
					element.set("goto_if_false", str(node.goto_if_false))
		indent(root)
		tree.write(filename, encoding="UTF-8", xml_declaration=True)
		
	def loadXML(self, filename):
		try:
			tree = ET.parse(filename)
		except IOError:
			return False
		root = tree.getroot()
		if root.tag != "Dialogue":
			return False
		self.start_node = int(root.attrib["start_node"])
		self.nodes = {None:None}
		for element in root:
			if element.tag == "DialogueNode":
				key = int(element.attrib["key"])
				text = element.attrib["npc_text"]
				speaker = element.attrib.get("speaker")
				node = DialogueNode(text, speaker)
				self.nodes[key] = node
				for response_element in element:
					if response_element.tag == "DialogueResponse":
						text = response_element.attrib.get("text")
						goto = response_element.attrib.get("goto")
						if goto is not None:
							goto = int(goto)
						condition = response_element.attrib.get("condition")
						response = DialogueResponse(text, goto, condition)
						node.responses.append(response)
			elif element.tag == "DialogueCheck":
				key = int(element.attrib["key"])
				check = element.attrib["check"]
				goto_if_true = element.attrib.get("goto_if_true")
				if goto_if_true is not None:
					goto_if_true = int(goto_if_true)
				goto_if_false = element.attrib.get("goto_if_false")
				if goto_if_false is not None:
					goto_if_false = int(goto_if_false)
				node = DialogueCheck(check, goto_if_true, goto_if_false)
				self.nodes[key] = node
		return True


def loadDialogue(name):
	dialogue = Dialogue()
	if dialogue.loadXML("campaign_data/dialogues/" + name + ".xml"):
		return dialogue
	else:
		return None
	
def saveDialogue(dialogue, name):
	dialogue.saveXML("campaign_data/dialogues/" + name + ".xml")


class DialogueState(object):
	def __init__(self, dialogue, world, npc=None, pc=None):
		self.dialogue = dialogue
		self.world = world
		self.npc = npc
		self.pc = pc
		self.current_node = self.dialogue.nodes[self.dialogue.start_node]

	@property
	def valid_responses(self):
		#valid = []
		#for response in self.current_node.responses:
		#	if response.condition and not Campaign.check(response.condition,
		#											npc=self.npc, pc=self.pc, world=self.world):
		#		continue
		#	valid.append(response)
		return [response for response in self.current_node.responses
				if not response.condition or
				Campaign.check(response.condition, npc=self.npc, pc=self.pc, world=self.world)]

	def pickResponse(self, picked_response):
		if isinstance(picked_response, int):
			picked_response = self.valid_responses[picked_response]
		#if picked_response.goto is not None:
		self.current_node = self.dialogue.nodes[picked_response.goto]
		#return self.enterNode()

	def enterNode(self):
		#if type(self.current_node) == DialogueNode:
		#	return self.current_node
		while isinstance(self.current_node, DialogueCheck):
			#if getattr(Campaign, self.current_node.check)(
			#					self.current_npc, self.current_pc, self.current_world):
			if Campaign.check(self.current_node.check, npc=self.npc, pc=self.pc, world=self.world):
			#	if self.current_node.goto_if_true:
				self.current_node = self.dialogue.nodes[self.current_node.goto_if_true]
			#		self.enterNode()
			#	else:
			#		self.current_node = None
			#		return None
			#elif self.current_node.goto_if_false:
			else:
				self.current_node = self.dialogue.nodes[self.current_node.goto_if_false]
			#	self.enterNode()
			#else:
			#	self.current_node = None
			#	return None
		return # self.current_node
