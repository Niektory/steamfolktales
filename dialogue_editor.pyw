#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright 2017 Tomasz "Niektóry" Turowski

import wx
from os import listdir

from scripts.dialogue import (Dialogue, DialogueNode, DialogueCheck, DialogueResponse,
								loadDialogue, saveDialogue)

def toInt(str):
	try:
		return int(str)
	except ValueError:
		return None
		
def toStr(num):
	return str(num) if num != None else ""
	
def changeKey(dialogue, old_key, new_key):
	if old_key == new_key:
		return
	dialogue.nodes[new_key] = dialogue.nodes.pop(old_key)

class DialogueEditorFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="Dialogue Editor")
		self.panel = wx.Panel(self)

		self.dialogue = None

		self.tree = wx.TreeCtrl(self.panel) #, size=wx.Size(300,400))
		self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTree)
		self.tree.Hide()

		files = []
		for file_name in listdir("campaign_data/dialogues"):
			if file_name.endswith(".xml"):
				files.append(file_name[:-4])
		self.listbox = wx.ListBox(self.panel, choices=files)
		self.listbox.Bind(wx.EVT_LISTBOX, self.onListbox)

		self.radiobox = wx.RadioBox(self.panel, label="dialogue tree view", majorDimension=1,
					choices=("list (full)", "list (compact)", "nested (full)", "nested (compact)"))
		self.radiobox.Bind(wx.EVT_RADIOBOX, self.onRadiobox)

		self.label_node_type = wx.StaticText(self.panel)
		self.button_save_node = wx.Button(self.panel, label="save node")
		self.button_save_node.Bind(wx.EVT_BUTTON, self.onSaveNode)
		self.button_delete_node = wx.Button(self.panel, label="delete node")
		self.button_delete_node.Bind(wx.EVT_BUTTON, self.onDeleteNode)
		self.button_add_response = wx.Button(self.panel, label="add response")
		self.button_add_response.Bind(wx.EVT_BUTTON, self.onAddResponse)
		self.button_add_node = wx.Button(self.panel, label="add node")
		self.button_add_node.Bind(wx.EVT_BUTTON, self.onAddNode)
		self.button_add_check = wx.Button(self.panel, label="add check")
		self.button_add_check.Bind(wx.EVT_BUTTON, self.onAddCheck)

		self.button_save_dialogue = wx.Button(self.panel, label="save dialogue")
		self.button_save_dialogue.Bind(wx.EVT_BUTTON, self.onSaveDialogue)
		self.button_quit = wx.Button(self.panel, label="quit")
		self.button_quit.Bind(wx.EVT_BUTTON, self.onQuit)
		self.button_save_dialogue.Hide()
		self.button_quit.Hide()

		self.label_node_key = wx.StaticText(self.panel, label="key:",
							style=wx.ALIGN_RIGHT)
		self.text_node_key = wx.TextCtrl(self.panel)
		self.label_dn_speaker = wx.StaticText(self.panel, label="speaker:",
							style=wx.ALIGN_RIGHT)
		self.text_dn_speaker = wx.TextCtrl(self.panel) #, value="node.speaker")
		self.label_dn_text = wx.StaticText(self.panel, label="npc_text:",
							style=wx.ALIGN_RIGHT)
		self.text_dn_text = wx.TextCtrl(self.panel,
							#value="node.npc_text", size=wx.Size(200,200),
							style=wx.TE_MULTILINE)
		self.label_dr_condition = wx.StaticText(self.panel, label="condition:",
							style=wx.ALIGN_RIGHT)
		self.text_dr_condition = wx.TextCtrl(self.panel)
		self.label_dr_goto = wx.StaticText(self.panel, label="goto:", style=wx.ALIGN_RIGHT)
		self.text_dr_goto = wx.TextCtrl(self.panel)
		self.label_dr_text = wx.StaticText(self.panel, label="text:", style=wx.ALIGN_RIGHT)
		self.text_dr_text = wx.TextCtrl(self.panel, #size=wx.Size(200,200),
							style=wx.TE_MULTILINE)
		self.label_dc_check = wx.StaticText(self.panel, label="check:", style=wx.ALIGN_RIGHT)
		self.text_dc_check = wx.TextCtrl(self.panel)#, value=node.check)
		self.label_dc_true = wx.StaticText(self.panel, label="goto_if_true:",
							style=wx.ALIGN_RIGHT)
		self.text_dc_true = wx.TextCtrl(self.panel)
		self.label_dc_false = wx.StaticText(self.panel, label="goto_if_false:",
							style=wx.ALIGN_RIGHT)
		self.text_dc_false = wx.TextCtrl(self.panel)
		self.clearRightPanel()

		self.left_box = wx.BoxSizer(wx.VERTICAL)
		self.left_box.Add(self.listbox, 1, wx.EXPAND)
		self.left_box.Add(self.tree, 1, wx.EXPAND)
		self.right_top_box = wx.BoxSizer(wx.HORIZONTAL)
		self.right_top_box.Add(self.button_add_response)
		self.right_top_box.Add(self.button_add_node)
		self.right_top_box.Add(self.button_add_check)
		self.right_top_box.AddStretchSpacer(1)
		self.right_top_box.Add(self.button_save_node)
		self.right_top_box.Add(self.button_delete_node)
		self.right_bottom_grid = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
		self.right_bottom_grid.AddGrowableCol(1)
		self.right_bottom_grid.AddGrowableRow(2)
		self.right_bottom_grid.AddGrowableRow(5)
		self.right_bottom_grid.Add(self.label_node_key, 0, wx.EXPAND)
		self.right_bottom_grid.Add(self.text_node_key, 1, wx.EXPAND)
		self.right_bottom_grid.Add(self.label_dn_speaker, 0, wx.EXPAND)
		self.right_bottom_grid.Add(self.text_dn_speaker, 1, wx.EXPAND)
		self.right_bottom_grid.Add(self.label_dn_text, 0, wx.EXPAND)
		self.right_bottom_grid.Add(self.text_dn_text, 1, wx.EXPAND)
		self.right_bottom_grid.Add(self.label_dr_condition, 0, wx.EXPAND)
		self.right_bottom_grid.Add(self.text_dr_condition, 1, wx.EXPAND)
		self.right_bottom_grid.Add(self.label_dr_goto, 0, wx.EXPAND)
		self.right_bottom_grid.Add(self.text_dr_goto, 1, wx.EXPAND)
		self.right_bottom_grid.Add(self.label_dr_text, 0, wx.EXPAND)
		self.right_bottom_grid.Add(self.text_dr_text, 1, wx.EXPAND)
		self.right_bottom_grid.Add(self.label_dc_check, 0, wx.EXPAND)
		self.right_bottom_grid.Add(self.text_dc_check, 1, wx.EXPAND)
		self.right_bottom_grid.Add(self.label_dc_true, 0, wx.EXPAND)
		self.right_bottom_grid.Add(self.text_dc_true, 1, wx.EXPAND)
		self.right_bottom_grid.Add(self.label_dc_false, 0, wx.EXPAND)
		self.right_bottom_grid.Add(self.text_dc_false, 1, wx.EXPAND)
		self.right_bottom_box = wx.BoxSizer(wx.HORIZONTAL)
		self.right_bottom_box.AddStretchSpacer(1)
		self.right_bottom_box.Add(self.button_save_dialogue)
		self.right_bottom_box.Add(self.button_quit)
		self.right_box = wx.BoxSizer(wx.VERTICAL)
		self.right_box.Add(self.right_top_box, 0, wx.ALL | wx.EXPAND, 5)
		self.right_box.Add(self.label_node_type, 0, wx.ALL, 5)
		self.right_box.Add(self.right_bottom_grid, 10000, wx.ALL | wx.EXPAND, 5)
		self.right_box.AddStretchSpacer(1)
		self.right_box.Add(self.right_bottom_box, 0, wx.ALL | wx.EXPAND, 5)
		self.right_box.Add(self.radiobox, 0, wx.ALL | wx.EXPAND, 5)
		self.box = wx.BoxSizer(wx.HORIZONTAL)
		self.box.Add(self.left_box, 1, wx.EXPAND)
		self.box.Add(self.right_box, 1, wx.EXPAND)
		self.panel.SetSizerAndFit(self.box)
		self.SetMinSize(wx.Size(600,500))
		self.Fit()

	def onSaveDialogue(self, event):
		saveDialogue(self.dialogue, self.listbox.GetString(self.listbox.GetSelection()))
		self.button_save_dialogue.SetLabel("saved!")
		
	def onQuit(self, event):
		self.button_save_dialogue.Hide()
		self.button_quit.Hide()
		self.tree.Hide()
		self.listbox.Show()
		self.listbox.SetSelection(wx.NOT_FOUND)
		self.clearRightPanel()
		self.panel.Layout()

	def onListbox(self, event):
		if self.listbox.GetSelection() == wx.NOT_FOUND:
			return
		self.dialogue = loadDialogue(self.listbox.GetString(self.listbox.GetSelection()))
		self.populateTree()
		self.listbox.Hide()
		self.tree.Show()
		self.button_save_dialogue.Show()
		self.button_quit.Show()
		self.panel.Layout()

	def onRadiobox(self, event):
		self.populateTree()

	def clearRightPanel(self):
		#self.right_top_box.DeleteWindows()
		#self.right_top_box.Clear()
		#self.right_bottom_grid.DeleteWindows()
		#self.right_bottom_grid.Clear()
		self.button_save_node.Hide()
		self.button_delete_node.Hide()
		self.button_add_response.Hide()
		self.button_add_node.Hide()
		self.button_add_check.Hide()
		self.label_node_key.Hide()
		self.text_node_key.Hide()
		self.label_dn_speaker.Hide()
		self.text_dn_speaker.Hide()
		self.label_dn_text.Hide()
		self.text_dn_text.Hide()
		self.label_dr_condition.Hide()
		self.text_dr_condition.Hide()
		self.label_dr_goto.Hide()
		self.text_dr_goto.Hide()
		self.label_dr_text.Hide()
		self.text_dr_text.Hide()
		self.label_dc_check.Hide()
		self.text_dc_check.Hide()
		self.label_dc_true.Hide()
		self.text_dc_true.Hide()
		self.label_dc_false.Hide()
		self.text_dc_false.Hide()
		self.label_node_type.SetLabel("")
		self.text_dn_speaker.SetValue("")
		self.text_dn_text.SetValue("")
		self.text_dr_condition.SetValue("")
		self.text_dr_goto.SetValue("")
		self.text_dr_text.SetValue("")
		self.text_dc_check.SetValue("")
		self.text_dc_true.SetValue("")
		self.text_dc_false.SetValue("")

	def onSaveNode(self, event):
		key, node = self.tree.GetPyData(self.tree.GetFocusedItem())
		if isinstance(node, DialogueNode):
			changeKey(self.dialogue, key, toInt(self.text_node_key.GetValue()))
			node.speaker = self.text_dn_speaker.GetValue()
			node.npc_text = self.text_dn_text.GetValue()
		elif isinstance(node, DialogueResponse):
			node.condition = self.text_dr_condition.GetValue()
			node.goto = toInt(self.text_dr_goto.GetValue())
			node.text = self.text_dr_text.GetValue()
		elif isinstance(node, DialogueCheck):
			changeKey(self.dialogue, key, toInt(self.text_node_key.GetValue()))
			node.check = self.text_dc_check.GetValue()
			node.goto_if_true = toInt(self.text_dc_true.GetValue())
			node.goto_if_false = toInt(self.text_dc_false.GetValue())
		self.populateTree()

	def onDeleteNode(self, event):
		key, node = self.tree.GetPyData(self.tree.GetFocusedItem())
		if isinstance(node, DialogueNode) or isinstance(node, DialogueCheck):
			del self.dialogue.nodes[key]
		elif isinstance(node, DialogueResponse):
			self.dialogue.nodes[key].responses.remove(node)
		self.populateTree()

	def onAddResponse(self, event):
		key, node = self.tree.GetPyData(self.tree.GetFocusedItem())
		if not isinstance(node, DialogueNode):
			return
		node.responses.append(DialogueResponse())
		self.populateTree()

	def onAddNode(self, event):
		self.dialogue.nodes[-1] = DialogueNode("<new node>")
		self.populateTree()

	def onAddCheck(self, event):
		self.dialogue.nodes[-1] = DialogueCheck("<new check>")
		self.populateTree()

	def onTree(self, event):
		self.clearRightPanel()
		data = self.tree.GetPyData(event.GetItem())
		if data is None:
			self.label_node_type.SetLabel("")
			self.button_add_node.Show()
			self.button_add_check.Show()
		else:
			key, node = data
			if isinstance(node, DialogueNode):
				self.label_node_type.SetLabel("DialogueNode [" + str(key) + "]")
				self.text_node_key.SetValue(str(key))
				self.text_dn_speaker.SetValue(toStr(node.speaker))
				self.text_dn_text.SetValue(node.npc_text)
				self.button_add_response.Show()
				self.label_node_key.Show()
				self.text_node_key.Show()
				self.label_dn_speaker.Show()
				self.text_dn_speaker.Show()
				self.label_dn_text.Show()
				self.text_dn_text.Show()
			elif isinstance(node, DialogueResponse):
				self.label_node_type.SetLabel("DialogueResponse attached to DialogueNode ["
												+ str(key) + "]")
				self.text_dr_condition.SetValue(toStr(node.condition))
				self.text_dr_goto.SetValue(toStr(node.goto))
				self.text_dr_text.SetValue(toStr(node.text))
				self.label_dr_condition.Show()
				self.text_dr_condition.Show()
				self.label_dr_goto.Show()
				self.text_dr_goto.Show()
				self.label_dr_text.Show()
				self.text_dr_text.Show()
			elif isinstance(node, DialogueCheck):
				self.label_node_type.SetLabel("DialogueCheck [" + str(key) + "]")
				self.text_node_key.SetValue(str(key))
				self.text_dc_check.SetValue(node.check)
				self.text_dc_true.SetValue(toStr(node.goto_if_true))
				self.text_dc_false.SetValue(toStr(node.goto_if_false))
				self.label_node_key.Show()
				self.text_node_key.Show()
				self.label_dc_check.Show()
				self.text_dc_check.Show()
				self.label_dc_true.Show()
				self.text_dc_true.Show()
				self.label_dc_false.Show()
				self.text_dc_false.Show()
			self.button_save_node.Show()
			self.button_delete_node.Show()
		self.panel.Layout()

	def populateTree(self):
		self.tree.DeleteAllItems()
		self.button_save_dialogue.SetLabel("save dialogue")
		if not self.dialogue:
			return
		if self.radiobox.GetSelection() > 1:
			root = self.tree.AddRoot(self.listbox.GetString(self.listbox.GetSelection()))
			self.walkNode(self.dialogue.start_node, [], root, self.dialogue)
		else:
			root = self.tree.AddRoot(self.listbox.GetString(self.listbox.GetSelection()))
			for key, node in sorted(self.dialogue.nodes.iteritems()):
				if isinstance(node, DialogueNode):
					item = self.tree.AppendItem(root, "[" + str(key) + "] " + toStr(node.speaker)
												+ ": " + node.npc_text)
					self.tree.SetPyData(item, (key, node))
					for response in node.responses:
						if response.text:
							response_item = self.tree.AppendItem(item, response.text)
							self.tree.SetPyData(response_item, (key, response))
						elif self.radiobox.GetSelection() == 0:
							response_item = self.tree.AppendItem(item, u"…")
							self.tree.SetPyData(response_item, (key, response))
						else:
							response_item = item
						if response.condition:
							condition_item = self.tree.AppendItem(response_item,
																"condition: " + response.condition)
							self.tree.SetPyData(condition_item, (key, response))
						if response.goto:
							goto_item = self.tree.AppendItem(response_item,
																u"→ [" + str(response.goto) + "]")
							self.tree.SetPyData(goto_item, (key, response))
							if response.goto not in self.dialogue.nodes:
								self.tree.SetItemBackgroundColour(goto_item, wx.Colour(255,0,0))
				elif isinstance(node, DialogueCheck):
					item = self.tree.AppendItem(root, "[" + str(key) + "] check: "
												+ node.check)
					self.tree.SetPyData(item, (key, node))
					if node.goto_if_true:
						goto_item = self.tree.AppendItem(item,
													u"if true → [" + str(node.goto_if_true) + "]")
						self.tree.SetPyData(goto_item, (key, node))
						if node.goto_if_true not in self.dialogue.nodes:
							self.tree.SetItemBackgroundColour(goto_item, wx.Colour(255,0,0))
					if node.goto_if_false:
						goto_item = self.tree.AppendItem(item,
													u"if false → [" + str(node.goto_if_false) + "]")
						self.tree.SetPyData(goto_item, (key, node))
						if node.goto_if_false not in self.dialogue.nodes:
							self.tree.SetItemBackgroundColour(goto_item, wx.Colour(255,0,0))
		self.tree.ExpandAll()
		self.tree.EnsureVisible(root)
		self.clearRightPanel()

	def walkNode(self, key, stack, parent, dialogue, prefix=""):
		try:
			node = dialogue.nodes[key]
		except KeyError:
			self.tree.SetItemBackgroundColour(parent, wx.Colour(255,0,0))
			return
		stack.append(key)
		if isinstance(node, DialogueNode):
			item = self.tree.AppendItem(parent, prefix + "[" + str(key) + "] " + toStr(node.speaker)
										+ ": " + node.npc_text)
			self.tree.SetPyData(item, (key, node))
			for response in node.responses:
				if response.text:
					response_item = self.tree.AppendItem(item, response.text)
					self.tree.SetPyData(response_item, (key, response))
				else:
					if self.radiobox.GetSelection() == 2:
						response_item = self.tree.AppendItem(item, u"…")
						self.tree.SetPyData(response_item, (key, response))
					else:
						response_item = item
				if response.condition:
					condition_item = self.tree.AppendItem(response_item,
															"condition: " + response.condition)
					self.tree.SetPyData(condition_item, (key, response))
				if response.goto:
					if response.goto not in stack:
						self.walkNode(response.goto, stack, response_item, dialogue)
					else:
						goto_item = self.tree.AppendItem(response_item,
																u"→ [" + str(response.goto) + "]")
						self.tree.SetPyData(goto_item, (key, response))
		elif isinstance(node, DialogueCheck):
			item = self.tree.AppendItem(parent, prefix + "[" + str(key) + "] check: "
										+ node.check)
			self.tree.SetPyData(item, (key, node))
			if node.goto_if_true:
				if node.goto_if_true not in stack:
					self.walkNode(node.goto_if_true, stack, item, dialogue, u"if true → ")
				else:
					goto_item = self.tree.AppendItem(item,
													u"if true → [" + str(node.goto_if_true) + "]")
					self.tree.SetPyData(goto_item, (key, node))
			if node.goto_if_false:
				if node.goto_if_false not in stack:
					self.walkNode(node.goto_if_false, stack, item, dialogue, u"if false → ")
				else:
					goto_item = self.tree.AppendItem(item,
													u"if false → [" + str(node.goto_if_false) + "]")
					self.tree.SetPyData(goto_item, (key, node))
		stack.pop()


if __name__ == '__main__':
	app = wx.App(0)
	frame = DialogueEditorFrame()
	frame.Show()
	app.MainLoop()
