# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from collections import OrderedDict

from wound import Wound
from rpgdice import roll, Roll, Check
from annotatedvalue import AnnotatedValue


class RPGStats(object):
	attribute_names = ("STR", "CON", "DEX", "REF", "INT", "WIT", "CHA", "EMP")
	combat_skills = ("Handguns", "Long Guns", "Rapid Shooting", "Dodge", "Brawl",
			"Melee, Balanced", "Melee, Finesse", "Melee, Heavy", "Throwing")
	martial_arts = ("Victoran Pugilism", "Northern Bladesmastery",
			"Wolfbite", "Shadowplay", "Fencing",)
	agility_skills = ("Stealth", "Sleight of Hand")
	mental_skills = ("Mechanics", "Gunsmith", "Blacksmith", "Clockwork",
			"Locksmith", "Medicine")
	social_skills = ("Bargain", "Diplomacy")
	empathic_skills = ()
	awareness_skills = ()
	non_combat_skills = (agility_skills + mental_skills + social_skills
			+ empathic_skills + awareness_skills)

	def __init__(self):
		self.character_points = 100
		# attributes
		self.attributes = OrderedDict()
		for attribute in self.attribute_names:
			self.attributes[attribute] = 10
		# skills
		self.skills = OrderedDict()
		for skill in (self.combat_skills + self.martial_arts + self.agility_skills
				+ self.mental_skills + self.social_skills + self.empathic_skills
				+ self.awareness_skills):
			self.skills[skill] = 0
		# health
		self.cur_stamina = self.max_stamina
		self.wounds = []
		
	# skill checks and attribute modifiers
	
	def assignedAttribute(self, skill):
		if skill in (self.combat_skills + self.martial_arts + self.agility_skills):
			return "DEX"
		elif skill in self.mental_skills:
			return "INT"
		elif skill in self.social_skills:
			return "CHA"
		elif skill in self.empathic_skills:
			return "EMP"
		elif skill in self.awareness_skills:
			return "WIT"
		
	def skillBase(self, skill):
		return 8
	
	def attributeModifier(self, attribute):
		return AnnotatedValue(self.attributes[attribute] // 2 - 5, "{} modifier".format(attribute))
		
	def skillModifier(self, skill):
		return self.attributeModifier(self.assignedAttribute(skill))
		
	def skillTotal(self, skill):
		return AnnotatedValue(
			self.skillBase(skill) + self.skills[skill] + self.skillModifier(skill),
			"{} total".format(skill))
		
	def skillCheck(self, skill, modifier=0):
		return Check(6, 3, self.skillTotal(skill) + modifier - self.wounds_skill_penalty)
		
	# derived stats and checks
	
	@property
	def movement(self):
		return (self.attributes["DEX"] + self.attributes["STR"] // 2) // 2
	
	@property
	def max_stamina(self):
		return self.attributes["CON"] * 2

	@property
	def critical_wound_threshold(self):
		return self.attributes["CON"]

	@property
	def severe_wound_threshold(self):
		return self.attributes["CON"] * 2 // 3

	@property
	def minor_wound_threshold(self):
		return self.attributes["CON"] // 3
		
	@property
	def pain_threshold(self):
		return (self.attributes["CON"] + self.attributes["WIT"]) // 2

	def painCheck(self, modifier=0):
		return Check(6, 3, self.pain_threshold - modifier)

	@property
	def initiative(self):
		return (AnnotatedValue(40, "initiative base")
			- AnnotatedValue(self.attributes["WIT"], "WIT")
			- AnnotatedValue(self.attributes["REF"], "REF"))
		
	@property
	def initiative_roll(self):
		return self.initiative + Roll(6, 1)
		
	@property
	def passive_defense_modifier(self):
		return (AnnotatedValue(2, "PDM base")
			- AnnotatedValue(self.skills["Dodge"], "Dodge ranks")
			- AnnotatedValue(self.attributeModifier("REF"), "REF modifier")
			+ self.wounds_pdm_penalty)

	# damage, wounds
	
	@property
	def wounds_pdm_penalty(self):
		modifier = 0
		for wound in self.wounds:
			modifier += getattr(wound, "pdm_penalty", 0)
		return AnnotatedValue(modifier, "wounds PDM penalty")

	@property
	def wounds_skill_penalty(self):
		modifier = 0
		for wound in self.wounds:
			modifier += getattr(wound, "skill_penalty", 0)
		return AnnotatedValue(modifier, "wounds skill penalty")
	
	#@property
	#def knocked_down(self):
	#	for wound in self.wounds:
	#		if getattr(wound, "knockdown", False):
	#			return True
	#	return False

	def takeDamage(self, damage, hit_location):
		#stamina_damage = min(damage, self.critical_wound_threshold)
		# TODO: proper annotations when threshold reached
		if damage > self.critical_wound_threshold:
			damage = self.critical_wound_threshold
		self.cur_stamina -= int(damage)
		#if damage >= self.critical_wound_threshold:
		#	wound = "critical wound"
		if damage >= self.severe_wound_threshold:
			if hit_location == "head":
				wound_roll = roll(6)
				if wound_roll == 1:
					wound = Wound("loss of hearing", hit_location, 50)
				elif wound_roll == 2:
					wound = Wound("temporary loss of sight", hit_location, 50, 1)
					self.wounds.append(Wound("blindness", hit_location, 2, 0, ["blindness"]))
				elif wound_roll == 3:
					wound = Wound("stumble", hit_location, 1, 2, ["stumble"])
				elif wound_roll == 4:
					wound = Wound("dizziness", hit_location, 50)
					wound.pdm_penalty = 3
				elif wound_roll == 5:
					wound = Wound("striking pain", hit_location, 50, 2)
				else:
					wound = Wound("bleeding wound", hit_location, 50, 0, ["bleeding"])
				if self.painCheck().failure:
					wound.effects.append("unconsciousness")
			elif hit_location == "torso":
				wound_roll = roll(6)
				if wound_roll == 1:
					wound = Wound("hurt in the privates", hit_location, 50, 2, ["stunned"])
					if self.painCheck(2).failure:
						wound.effects.append("unconsciousness")
				else:
					if wound_roll == 2:
						wound = Wound("fractured rib", hit_location, 5000, 1)
					elif wound_roll == 3:
						wound = Wound("knocked back", hit_location, 50, 1, ["knockback"])
					elif wound_roll == 4:
						wound = Wound(
							"blood poisoning", hit_location, 5000, 0, ["blood poisoning"])
					elif wound_roll == 5:
						wound = Wound("striking pain", hit_location, 50, 2)
					else:
						wound = Wound("bleeding wound", hit_location, 50, 0, ["bleeding"])
					if self.painCheck().failure:
						wound.effects.append("unconsciousness")
			elif hit_location == "arm":
				wound_roll = roll(6)
				if wound_roll == 1:
					wound = Wound("limb numb", hit_location, 4)
					wound.skill_penalty = 10
				elif wound_roll == 2:
					wound = Wound("minor fracture", hit_location, 5000)
					wound.skill_penalty = 1
				elif wound_roll == 3:
					wound = Wound("muscle tear", hit_location, 1000, 0, ["arm muscle tear"])
					wound.skill_penalty = 1
				elif wound_roll == 4:
					wound = Wound("dislocation", hit_location, 5000)
					wound.skill_penalty = 10
				elif wound_roll == 5:
					wound = Wound("bruised badly", hit_location, 50)
					wound.skill_penalty = 2
				else:
					wound = Wound("bleeding wound", hit_location, 50, 0, ["bleeding"])
				if self.painCheck().failure:
					wound.effects.append("disarm")
			elif hit_location == "leg":
				wound_roll = roll(6)
				if wound_roll == 1:
					wound = Wound("limb numb", hit_location, 4, 0, ["leg numb"])
				elif wound_roll == 2:
					wound = Wound("minor fracture", hit_location, 5000)
					wound.pdm_penalty = 1
				elif wound_roll == 3:
					wound = Wound("muscle tear", hit_location, 1000, 0, ["leg muscle tear"])
					wound.pdm_penalty = 1
				elif wound_roll == 4:
					wound = Wound("dislocation", hit_location, 5000, 0,
										["knockdown", "leg dislocation"])
				elif wound_roll == 5:
					wound = Wound("bruised badly", hit_location, 50)
					wound.pdm_penalty = 2
				else:
					wound = Wound("bleeding wound", hit_location, 50, 0, ["bleeding"])
				if self.painCheck().failure:
					wound.effects.append("knockdown")
			#wound = Wound("severe " + hit_location + " wound", hit_location)
		elif damage >= self.minor_wound_threshold:
			if hit_location == "head":
				if self.painCheck().success:
					wound = Wound("minor head wound", hit_location, 1, 1)
				else:
					wound = Wound("minor head wound", hit_location, 1, 2)
			elif hit_location == "torso":
				wound = Wound("minor torso wound", hit_location, 1, 1)
			elif hit_location == "arm":
				wound = Wound("minor arm wound", hit_location, 1)
				wound.skill_penalty = 1
			elif hit_location == "leg":
				wound = Wound("knockdown", hit_location, 0, 0, ["knockdown"])
				#wound.effects.append("knockdown")
		else:
			wound = None
		if wound:
			if wound.duration:
				self.wounds.append(wound)
		return damage, wound
	
	def onEndTurn(self):
		for wound in reversed(self.wounds[:]):
			if not wound.onEndTurn():
				self.wounds.remove(wound)
