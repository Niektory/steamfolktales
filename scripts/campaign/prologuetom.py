# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

@classmethod
def startPrologueTom(cls, npc, pc, world):
	world.knowledge["last_prologue"] = "Tom"
	world.knowledge["tom_prologue"] = 1
	cls.continuePrologue(npc, pc, world)
