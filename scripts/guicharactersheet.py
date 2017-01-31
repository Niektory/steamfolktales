# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI
#from traceback import print_exc
from copy import deepcopy

from error import LogExceptionDecorator


def calcSkillValue(value):
	return value * (value + 1) // 2

def calcAttributeValue(value):
	total_value = 0
	for i in xrange(1, value-9):
		total_value += i*i
	return total_value
	
def calcMaxSkillValue(available_cp, cur_value):
	cp_left = available_cp
	value = cur_value
	while cp_left > value:
		value += 1
		cp_left -= value
	return value

def calcMaxAttributeValue(available_cp, cur_value):
	cp_left = available_cp
	value = cur_value
	while cp_left >= ((value-9)*(value-9)):
		value += 1
		cp_left -= ((value-10)*(value-10))
	return value


class GUICharacterSheet:
	def __init__(self, application):
		self.application = application
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile(
						"CharacterSheet.layout")
		#self.window.subscribeEvent(PyCEGUI.FrameWindow.EventCloseClicked, closeWindow)
		self.name_label = self.window.getChild("NameLabel")
		self.portrait = self.window.getChild("Portrait")
		self.health_label = self.window.getChild("HealthLabel")
		self.cp_edit = self.window.getChild("CPEdit")
		self.stamina_edit = self.window.getChild("DerivedStatsGroup/StaminaEdit")
		self.movement_edit = self.window.getChild("DerivedStatsGroup/MovementEdit")
		self.initiative_edit = self.window.getChild("DerivedStatsGroup/InitiativeEdit")
		self.pdm_edit = self.window.getChild("DerivedStatsGroup/PDMEdit")
		
		self.attributes_group = self.window.getChild("AttributesGroup")
		self.combat_skills_group = self.window.getChild("CombatSkillsGroup")
		self.martial_arts_group = self.window.getChild("MartialArtsGroup")
		self.non_combat_skills_group = self.window.getChild("NonCombatSkillsGroup")
		self.ok_button = self.window.getChild("OKButton")
		self.ok_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.modifyCharacter)
		self.cancel_button = self.window.getChild("CancelButton")
		self.cancel_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.hide)
		self.reset_button = self.window.getChild("ResetButton")
		self.reset_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.show)
		self.attribute_labels = []
		self.attribute_edits = []
		self.skill_labels = []
		self.skill_edits = []

	@LogExceptionDecorator
	def show(self, args=None):
		if self.application.current_character:
			self.showCharacter(self.application.current_character)

	def showCharacter(self, character):
		self.window.show()
		self.window.moveToFront()
		self.current_character = character
		self.working_stats = deepcopy(self.current_character.rpg_stats)
		# display name, portrait
		self.name_label.setText(self.current_character.name)
		self.portrait.setProperty("Image", self.current_character.portrait)
		#self.cp_edit.setText(str(self.working_stats.character_points))
		# display health info
		health_str = ("Stamina: " + str(self.working_stats.cur_stamina)
									+ "/" + str(self.working_stats.max_stamina))
		if len(self.working_stats.wounds):
			for wound in self.working_stats.wounds:
				health_str += "\n" + wound.name
		else:
			health_str += "\nNo wounds"
		self.health_label.setText(health_str)
		# remove old widgets
		#for widget in self.attribute_labels + self.attribute_edits:
		#	self.attributes_group.removeChild(widget)
		#for widget in self.skill_labels + self.skill_edits:
		#	self.combat_skills_group.removeChild(widget)
		#	self.martial_arts_group.removeChild(widget)
		#	self.non_combat_skills_group.removeChild(widget)
		while self.attributes_group.getChildCount():
			self.attributes_group.removeChild(
						self.attributes_group.getChildAtIdx(0).getID())
		while self.combat_skills_group.getChildCount():
			self.combat_skills_group.removeChild(
						self.combat_skills_group.getChildAtIdx(0).getID())
		while self.martial_arts_group.getChildCount():
			self.martial_arts_group.removeChild(
						self.martial_arts_group.getChildAtIdx(0).getID())
		while self.non_combat_skills_group.getChildCount():
			self.non_combat_skills_group.removeChild(
						self.non_combat_skills_group.getChildAtIdx(0).getID())
		# load character attributes and create widgets for them
		self.attribute_labels = []
		self.attribute_edits = []
		vert_pos = 10
		for attribute in self.working_stats.attributes:
			new_attribute_label = PyCEGUI.WindowManager.getSingleton().createWindow(
					"TaharezLook/Label", "AttributeLabel-" + attribute)
			new_attribute_label.setText(attribute)
			new_attribute_label.setProperty("Position", "{{0,0},{0," + str(vert_pos) + "}}")
			#new_attribute_label.setProperty("FrameEnabled", "False")
			#new_attribute_label.setProperty("BackgroundEnabled", "False")
			new_attribute_label.setProperty("VertFormatting", "TopAligned")
			new_attribute_label.setProperty("Disabled", "True")
			new_attribute_label.setProperty("Size", "{{0,40},{0,20}}")
			new_attribute_label.setProperty("HorzFormatting", "RightAligned")

			new_attribute_spinner = PyCEGUI.WindowManager.getSingleton().createWindow(
					"TaharezLook/Spinner", "AttributeEdit-" + attribute)
			new_attribute_spinner.setProperty("Size", "{{0,50},{0,28}}")
			new_attribute_spinner.setProperty("Position", "{{0,50},{0," + str(vert_pos - 6) + "}}")
			new_attribute_spinner.setTextInputMode(PyCEGUI.Spinner.Integer)
			new_attribute_spinner.setCurrentValue(self.working_stats.attributes[attribute])
			new_attribute_spinner.setMinimumValue(self.working_stats.attributes[attribute])
			new_attribute_spinner.setMaximumValue(18)
			new_attribute_spinner.setStepSize(1)
			new_attribute_spinner.subscribeEvent(PyCEGUI.Spinner.EventValueChanged, self.update)
			#new_attribute_edit.setText(str(self.current_character.rpg_stats.attributes[attribute]))
			
			#new_attribute_edit.setProperty("TextParsingEnabled", "False")
			#new_attribute_edit.setProperty("ValidationString", "[[:digit:]]*")
			#new_attribute_edit.setProperty("MaxTextLength", "2")
			new_attribute_edit = new_attribute_spinner.getChild("__auto_editbox__")
			new_attribute_edit.setReadOnly(True)

			self.attribute_labels.append(new_attribute_label)
			self.attribute_edits.append(new_attribute_spinner)
			self.attributes_group.addChild(new_attribute_label)
			self.attributes_group.addChild(new_attribute_spinner)
			vert_pos += 30
		# load character skills and create widgets for them
		self.skill_labels = []
		self.skill_edits = []
		self.loadSkillGroup(self.working_stats.combat_skills, self.combat_skills_group)
		self.loadSkillGroup(self.working_stats.martial_arts, self.martial_arts_group)
		self.loadSkillGroup(self.working_stats.non_combat_skills, self.non_combat_skills_group)
		# calculate total character points value of stats
		self.total_cp = self.working_stats.character_points
		for attribute in self.working_stats.attributes.values():
			self.total_cp += calcAttributeValue(attribute)
		for skill in self.working_stats.skills.values():
			self.total_cp += calcSkillValue(skill)
		self.update()

	def loadSkillGroup(self, skills, group):
		vert_pos = 10
		horz_pos = 0
		for skill in skills:
			new_skill_label = PyCEGUI.WindowManager.getSingleton().createWindow(
					"TaharezLook/Label", "SkillLabel-" + skill)
			new_skill_label.setText(skill)
			new_skill_label.setProperty("Position", "{{0," + str(horz_pos)
										+ "},{0," + str(vert_pos) + "}}")
			#new_skill_label.setProperty("FrameEnabled", "False")
			#new_skill_label.setProperty("BackgroundEnabled", "False")
			new_skill_label.setProperty("VertFormatting", "TopAligned")
			new_skill_label.setProperty("Disabled", "True")
			new_skill_label.setProperty("Size", "{{0,175},{0,20}}")
			new_skill_label.setProperty("HorzFormatting", "RightAligned")

			new_skill_spinner = PyCEGUI.WindowManager.getSingleton().createWindow(
					"TaharezLook/Spinner", "SkillEdit-" + skill)
			new_skill_spinner.setProperty("Size", "{{0,50},{0,28}}")
			new_skill_spinner.setProperty("Position", "{{0," + str(horz_pos + 185)
										+ "},{0," + str(vert_pos - 6) + "}}")
			new_skill_spinner.setTextInputMode(PyCEGUI.Spinner.Integer)
			new_skill_spinner.setCurrentValue(self.working_stats.skills[skill])
			new_skill_spinner.setMinimumValue(self.working_stats.skills[skill])
			new_skill_spinner.setMaximumValue(10)
			new_skill_spinner.setStepSize(1)
			new_skill_spinner.subscribeEvent(PyCEGUI.Spinner.EventValueChanged, self.update)

			new_skill_edit = new_skill_spinner.getChild("__auto_editbox__")
			new_skill_edit.setReadOnly(True)
			#new_skill_edit.setEnabled(False)
			#new_skill_edit.setText(str(self.current_character.rpg_stats.skills[skill]))
			#new_skill_edit.setProperty("TextParsingEnabled", "False")
			#new_skill_edit.setProperty("ValidationString", "[[:digit:]]*")
			#new_skill_edit.setProperty("MaxTextLength", "2")

			self.skill_labels.append(new_skill_label)
			self.skill_edits.append(new_skill_spinner)
			group.addChild(new_skill_label)
			group.addChild(new_skill_spinner)
			vert_pos += 30
			if vert_pos >= 490:
				vert_pos = 10
				horz_pos += 250

	@LogExceptionDecorator
	def update(self, args=None):
		# calculate available character points and update the spinners
		cur_total_value = 0
		for attribute in self.attribute_edits:
			cur_total_value += calcAttributeValue(int(attribute.getCurrentValue()))
		for skill in self.skill_edits:
			cur_total_value += calcSkillValue(int(skill.getCurrentValue()))
		cur_cp_available = self.total_cp - cur_total_value
		self.working_stats.character_points = cur_cp_available
		self.cp_edit.setText(str(cur_cp_available))
		for attribute in self.attribute_edits:
			attribute.setMaximumValue(min(18,
					calcMaxAttributeValue(cur_cp_available, int(attribute.getCurrentValue()))))
			if attribute.getMaximumValue() == attribute.getCurrentValue():
				attribute.getChild("__auto_incbtn__").setEnabled(False)
			else:
				attribute.getChild("__auto_incbtn__").setEnabled(True)
			attribute.getChild("__auto_incbtn__").setTooltipText("Cost: "
						+ str((int(attribute.getCurrentValue())-9)
						*(int(attribute.getCurrentValue())-9))
						+ " CP")
			if attribute.getMinimumValue() == attribute.getCurrentValue():
				attribute.getChild("__auto_decbtn__").setEnabled(False)
			else:
				attribute.getChild("__auto_decbtn__").setEnabled(True)
		for skill in self.skill_edits:
			skill.setMaximumValue(min(10,
					calcMaxSkillValue(cur_cp_available, int(skill.getCurrentValue()))))
			if skill.getMaximumValue() == skill.getCurrentValue():
				skill.getChild("__auto_incbtn__").setEnabled(False)
			else:
				skill.getChild("__auto_incbtn__").setEnabled(True)
			skill.getChild("__auto_incbtn__").setTooltipText("Cost: "
						+ str(int(skill.getCurrentValue())+1)
						+ " CP")
			if skill.getMinimumValue() == skill.getCurrentValue():
				skill.getChild("__auto_decbtn__").setEnabled(False)
			else:
				skill.getChild("__auto_decbtn__").setEnabled(True)

		for i in xrange(len(self.attribute_edits)):
			self.working_stats.attributes[self.attribute_labels[i].getText()] = (
					int(self.attribute_edits[i].getCurrentValue()))
		for i in xrange(len(self.skill_edits)):
			self.working_stats.skills[self.skill_labels[i].getText()] = (
					int(self.skill_edits[i].getCurrentValue()))
		# display derived stats
		if self.working_stats.max_stamina == self.current_character.rpg_stats.max_stamina:
			self.stamina_edit.setText(str(self.working_stats.max_stamina))
		else:
			self.stamina_edit.setText(
					"[colour='FF80FF00']" + str(self.working_stats.max_stamina))
		if self.working_stats.movement == self.current_character.rpg_stats.movement:
			self.movement_edit.setText(str(self.working_stats.movement))
		else:
			self.movement_edit.setText("[colour='FF80FF00']" + str(self.working_stats.movement))
		if self.working_stats.initiative == self.current_character.rpg_stats.initiative:
			self.initiative_edit.setText(str(self.working_stats.initiative))
		else:
			self.initiative_edit.setText(
					"[colour='FF80FF00']" + str(self.working_stats.initiative))
		if (self.working_stats.passive_defense_modifier
					== self.current_character.rpg_stats.passive_defense_modifier):
			self.pdm_edit.setText(str(self.working_stats.passive_defense_modifier))
		else:
			self.pdm_edit.setText(
					"[colour='FF80FF00']" + str(self.working_stats.passive_defense_modifier))

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
	def modifyCharacter(self, args):
		#self.current_character.name = self.name_edit.getText()
		self.current_character.rpg_stats = self.working_stats
		self.window.hide()
