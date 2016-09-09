# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from random import randrange, choice

from timeline import Timer
import gridhelper
from rpgdice import roll, Roll
from annotatedvalue import formatted, AnnotatedValue


class Combat(object):
	def __init__(self, application, combatants):
		self.application = application
		self.combatants = combatants
		self.current_combatant = 0
		self.animations = []
		self.multi_attack = []
		# determine initiative
		self.initiative = {}
		combat_log = self.application.gui.combat_log  # shortcut
		for combatant in self.combatants:
			self.initiative[combatant] = combatant.rpg_stats.initiative_roll
			self.application.gui.sayBubble(
				combatant.visual.instance,
				"initiative roll: {}".format(int(self.initiative[combatant])),
				3000)
			link = self.application.gui.help.createPage(
				formatted(self.initiative[combatant], multiline=True, result=True))
			combat_log.printMessage("{} rolled initiative: {}".format(
				combatant.name,
				combat_log.createLink(int(self.initiative[combatant]), link)))
		self.combatants.sort(key=lambda combatant: self.initiative[combatant])
		#self.application.gui.initiative.show(self)
		# switching to combat animations
		for combatant in self.combatants:
			combatant.visual.enterCombat(self)
			#self.application.real_timeline.addTimer(
			#				Timer("combat start idle: "+combatant.name, 0, 1, combatant.idle))
		# call beginTurn() manually after creating the Combat object!
		#self.beginTurn()
			
	def beginTurn(self):
		self.current_AP = self.combatants[self.current_combatant].rpg_stats.movement
		self.moved = False
		self.application.gui.initiative.show(self)
		self.application.gui.combat_log.window.show()
		#self.application.gui.hud.refresh()
		if self.getEnemiesOf(self.combatants[self.current_combatant]):
			if self.combatants[self.current_combatant].player_controlled:
				self.createGrid()
				self.application.gui.hud.showCombat()
			else:
				# AI in 3 lines
				# probably not very smart
				# just like this comment
				self.ai_target = choice(self.getEnemiesOf(self.combatants[self.current_combatant]))
				if not self.attack(self.ai_target, choice(self.available_attacks)):
					self.run(self.ai_target.visual.instance.getLocation())
		else:
			self.endCombat()
		#if type(self.combatants[self.current_combatant]) == NonPlayerCharacter:
		#	self.endTurn()
		#else:
		#	self.createGrid()
		
	def playerEndTurn(self, character=None):
		if not self.combatants[self.current_combatant].player_controlled:
			return
		if len(self.animations):
			return
		return self.endTurn(character)

	def endTurn(self, character=None):
		self.application.view.clearTiles()
		self.application.gui.inventory.window.hide()
		self.combatants[self.current_combatant].rpg_stats.onEndTurn()
		for combatant in self.combatants:
			if not combatant.player_controlled:
				# if there's still at least one hostile give the turn to the next combatant
				if (self.current_combatant + 1) >= len(self.combatants):
					self.current_combatant = 0
				else:
					self.current_combatant += 1
				self.beginTurn()
				return
		# no hostiles, end combat
		self.endCombat()
	
	def killAllEnemies(self):
		if not self.combatants[self.current_combatant].player_controlled:
			return
		if len(self.animations):
			return
		for enemy in self.combatants[:]:
			if not enemy.player_controlled:
				self.kill(enemy)
	
	def kill(self, target):
		if self.current_combatant > self.combatants.index(target):
			self.current_combatant -= 1
		self.combatants.remove(target)
		target.die()
	
	def endCombat(self):
		self.application.gui.initiative.window.hide()
		self.application.gui.combat_log.window.hide()
		self.application.gui.combat_log.clear()
		self.application.gui.hud.show()
		self.application.combat = None
		# switching to non-combat animations
		for combatant in self.combatants:
			combatant.visual.leaveCombat()
		#for combatant in self.combatants:
		#	combatant.idle()
	
	def playerRun(self, dest):
		if not self.combatants[self.current_combatant].player_controlled:
			return
		if len(self.animations):
			return
		return self.run(dest)
	
	def run(self, dest):
		if self.moved:
			return False
		dist = self.combatants[self.current_combatant].visual.run(dest, cut_dist = self.current_AP)
		if dist:
			#print "dist =", dist
			self.current_AP -= dist
			self.moved = True
			self.application.view.clearTiles()
			return True
		else:
			return False
		#self.combatants[self.current_combatant].idle_script = self.endTurn

	@property
	def available_attacks(self):
		attacks = []
		weapon = self.combatants[self.current_combatant].inventory.hands
		if weapon:
			if weapon[0].weapon_data.ranged:
				attacks.append("Single attack")
				if not self.moved:
					attacks.append("Full attack")
			else:
				attacks.append("High attack")
				attacks.append("Low attack")
		else:
			attacks.append("High attack")
			attacks.append("Low attack")
		return attacks
		
	def playerAttack(self, target, attack_type):
		if not self.combatants[self.current_combatant].player_controlled:
			return
		if len(self.animations):
			return
		return self.attack(target, attack_type)

	def attack(self, target, attack_type, attack_count=0):
		attacker = self.combatants[self.current_combatant]
		if attacker == target:
			# trying to attack self, aborting
			return False
		if target not in self.combatants:
			# target not in combat, aborting
			return False
		if not self.can_attack and attack_count == 0:
			# not enough AP, aborting
			return False
		if attack_type not in self.available_attacks:
			# selected attack cannot be performed, aborting
			return False
		weapon = attacker.inventory.hands
		dist = AnnotatedValue(
			gridhelper.distance(attacker.coords, target.coords),
			"distance")
		# calculate effective PDM
		if dist >= 5:
			# too far, no PDM for you!
			pdm = AnnotatedValue(0, "PDM ignored")
		else:
			# using PDM if closer than 5m
			pdm = target.rpg_stats.passive_defense_modifier
			# martial artists can in some circumstances add 2 to target's PDM
			if (attacker.martial_art_used
					and not target.martial_art_used
					and target.rpg_stats.skillTotal("Dodge") < 12
					and target.rpg_stats.skillTotal(
						weapon[0].weapon_data.skill if weapon else "Brawl") < 14):
				pdm += AnnotatedValue(2, "martial arts PDM modifier")
		# attack roll
		# TODO: golden success/tumble effects
		if weapon:
			# weapon attack
			if dist > (weapon[0].weapon_data.total_range):
				# not in range, aborting
				return False
			if (weapon[0].weapon_data.magazine_size > 0) and (
						len(weapon[0].weapon_data.magazine) == 0):
				# no ammo, aborting
				return False
			if len(weapon[0].weapon_data.magazine) > 0:
				# remove the bullet
				weapon[0].weapon_data.magazine.pop(0)
			# weapon skill check, or Rapid Fire skill check if ranged Full Attack
			skill_used = ("Rapid Shooting"
				if attack_type == "Full Attack"
				and attacker.skills["Rapid Shooting"]<attacker.skills[weapon[0].weapon_data.skill]
				else weapon[0].weapon_data.skill)
			# modifier = target's PDM + weapon accuracy - range penalty - multi attack penalty
			attack_mods = (pdm
				+ weapon[0].weapon_data.accuracy
				- dist // weapon[0].weapon_data.range
				- AnnotatedValue(attack_count, "penalty for multiple attacks"))
			hit = attacker.rpg_stats.skillCheck(skill_used, attack_mods)
			# damage roll
			damage = weapon[0].weapon_data.damage_roll
			# STR bonus for balanced and heavy weapons; can't be higher than weapon's max damage
			if weapon[0].weapon_data.skill in ("Melee, Balanced", "Melee, Heavy"):
				damage += min(attacker.rpg_stats.attributeModifier("STR"),
					weapon[0].weapon_data.max_damage)
			if attacker.martial_art_used:
				# martial art skill check; additional damage on success
				# reuses the attack roll but checks against a different skill
				martial_art_hit = attacker.rpg_stats.skillCheck(
					attacker.martial_art_used,
					attack_mods)
				martial_art_hit.results = hit.results
				if martial_art_hit.golden:
					damage += AnnotatedValue(3, annotation="martial arts golden success bonus")
				elif martial_art_hit.success:
					damage += Roll(3, annotation="martial arts damage bonus")
			# determine hit location
			if weapon[0].weapon_data.ranged:
				location_roll = roll(20)
				if location_roll >= 19:
					hit_location = "head"
				elif location_roll >= 13:
					hit_location = "torso"
				#elif location_roll >= 10:
				#	hit_location = "right arm"
				elif location_roll >= 7:
					hit_location = "arm"
				#elif location_roll >= 4:
				#	hit_location = "right leg"
				else:
					hit_location = "leg"
			else:
				if attack_type == "High attack":
					location_roll = roll(7)
					if location_roll >= 7:
						hit_location = "head"
					elif location_roll >= 5:
						hit_location = "torso"
					#elif location_roll >= 3:
					#	hit_location = "right arm"
					else:
						hit_location = "arm"
				else:
					location_roll = roll(8)
					if location_roll >= 7:
						hit_location = "torso"
					#elif location_roll >= 4:
					#	hit_location = "right leg"
					else:
						hit_location = "leg"
		else:
			# unarmed attack
			if dist > 1.5:
				# not in range, aborting
				return False
			# Brawl skill check; modifier = target's PDM
			hit = attacker.rpg_stats.skillCheck("Brawl", pdm)
			# damage roll + unarmed STR bonus
			damage = (Roll(3, annotation="unarmed damage")
				+ attacker.rpg_stats.attributeModifier("STR"))
			if attacker.martial_art_used:
				# martial art skill check; additional damage on success
				# reuses the attack roll but checks against a different skill
				martial_art_hit = attacker.rpg_stats.skillCheck(
					attacker.martial_art_used,
					pdm)
				martial_art_hit.results = hit.results
				if martial_art_hit.golden:
					damage += AnnotatedValue(4, annotation="martial arts golden success bonus")
				elif martial_art_hit.success:
					damage += Roll(4, annotation="martial arts damage bonus")
			# determine hit location
			if attack_type == "High attack":
				location_roll = roll(7)
				if location_roll >= 7:
					hit_location = "head"
				elif location_roll >= 5:
					hit_location = "torso"
				#elif location_roll >= 3:
				#	hit_location = "right arm"
				else:
					hit_location = "arm"
			else:
				location_roll = roll(8)
				if location_roll >= 7:
					hit_location = "torso"
				#elif location_roll >= 4:
				#	hit_location = "right leg"
				else:
					hit_location = "leg"
		# damage bonus from hit roll margin
		damage += AnnotatedValue(hit.margin, "hit roll's margin of success") // 2
		# save hit results to be used later by onTargetHit
		self.target = target
		self.hit = hit
		self.damage = damage
		self.hit_location = hit_location
		# play the attack animation
		attacker.visual.attack(target.visual.instance.getLocation())
		# after attacking immediately end turn
		#self.endTurn()
		self.current_AP = 0
		self.application.view.clearTiles()
		# additional attacks
		if weapon:
			# ranged Full Attack
			if (attack_type == "Full attack" and not self.moved
					and weapon[0].weapon_data.speed > attack_count + 1):
				self.multi_attack.append(
					lambda: self.attack(target, attack_type, attack_count + 1))
			# Finesse weapon with skill >= 3
			elif (weapon[0].weapon_data.skill == "Melee, Finesse" and attack_count == 0
					and attacker.rpg_stats.skills["Melee, Finesse"] >= 3
					and (attacker.rpg_stats.skills["Melee, Finesse"] >= 6 or not self.moved)):
				self.multi_attack.append(
					lambda: self.attack(target, attack_type, attack_count + 1))
		return True

	def onTargetHit(self):
		#shortcuts
		combat_log = self.application.gui.combat_log
		help = self.application.gui.help
		hit_link = help.createPage(formatted(self.hit, multiline=True, result=True))
		if self.hit:
			# attack hit, deal damage
			damage, wound = self.target.rpg_stats.takeDamage(self.damage, self.hit_location)
			# display damage and wound inflicted
			dmg_str = "{} damage".format(int(damage))
			if wound:
				dmg_str += "\n" + wound.name
			self.application.gui.sayBubble(
				self.target.visual.instance, dmg_str, 1000, "[colour='FFFF8080']")
			location_link = help.createPage("TODO: show hit location roll details")
			damage_link = help.createPage(formatted(damage, multiline=True, result=True))
			wound_link = help.createPage("TODO: show wound roll details")
			combat_log.printMessage(
				"{atk} {hit} {tgt} on the {loc}, inflicting {dmg} damage and {wnd}.".format(
					atk=self.combatants[self.current_combatant],
					hit=combat_log.createLink("hit", hit_link),
					tgt=self.target,
					loc=combat_log.createLink(self.hit_location, location_link),
					dmg=combat_log.createLink(int(damage), damage_link),
					wnd=combat_log.createLink(wound.name if wound else "no wound", wound_link)))
			if self.target.rpg_stats.cur_stamina <= 0:
				# stamina reached 0, kill and remove the target from combat
				self.kill(self.target)
				combat_log.printMessage("{} collapsed.".format(self.target.name))
			# add blood effect
			if wound:
				self.application.view.addSimpleEffect(
					"Blood_Hit01",
					self.target.visual.instance.getLocation())
			else:
				self.application.view.addSimpleEffect(
					"Blood_Hit02",
					self.target.visual.instance.getLocation())
		else:
			# attack missed
			self.application.gui.sayBubble(self.target.visual.instance, "miss", 1000)
			combat_log.printMessage(
				"{attacker} {missed} {target}.".format(
					attacker=self.combatants[self.current_combatant],
					missed=combat_log.createLink("missed", hit_link),
					target=self.target))
		self.application.playSound("SFT-KNIFE-SWING")

	def createGrid(self):
		for combatant in self.combatants:
			self.application.view.addTile(combatant.coords, 127)
		for i in xrange(-self.current_AP, self.current_AP+1):
			for j in xrange(-self.current_AP, self.current_AP+1):
				loc = self.combatants[self.current_combatant].visual.instance.getLocation()
				coords = self.combatants[self.current_combatant].coords
				coords.x += i
				coords.y += j
				loc.setLayerCoordinates(coords)
				if self.combatants[self.current_combatant].visual.testRoute(loc, self.current_AP
							-(self.combatants[self.current_combatant].rpg_stats.movement+1) // 2):
					self.application.view.addTile(coords)
					#print coords.x, coords.y
				elif self.combatants[self.current_combatant].visual.testRoute(loc,self.current_AP):
					self.application.view.addTile(coords, 127)
		
	def getEnemiesOf(self, combatant):
		enemies = []
		for potential_enemy in self.combatants:
			if combatant == potential_enemy:
				# can't be his own enemy
				continue
			if potential_enemy.dead:
				# let the dead rest in peace
				continue
			if combatant.player_controlled != potential_enemy.player_controlled:
				enemies.append(potential_enemy)
		return enemies
		
	def animationFinished(self, animation):
		#print "finished:", animation, animation
		if self.animations.count(animation):
			self.animations.remove(animation)
	
	@property
	def can_attack(self):
		return (self.current_AP * 2) >= self.combatants[self.current_combatant].rpg_stats.movement
		
	def pump(self):
		if len(self.animations):
			# wait for animations to end
			#print self.animations
			return
		if self.multi_attack:
			self.multi_attack[0]()
			self.multi_attack.pop(0)
			return
		if not self.can_attack or not self.getEnemiesOf(self.combatants[self.current_combatant]):
			# no more actions possible or no enemies left
			self.endTurn()
			return
		if not self.combatants[self.current_combatant].player_controlled:
			self.attack(self.ai_target, choice(self.available_attacks))
			return
		self.application.gui.hud.refresh()
		