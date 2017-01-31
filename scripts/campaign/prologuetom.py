# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

@classmethod
def startPrologueTom(cls, npc, pc, world):
	world.knowledge["last_prologue"] = "Tom"
	world.knowledge["tom_prologue"] = 1
	cls.continuePrologue(npc, pc, world)
