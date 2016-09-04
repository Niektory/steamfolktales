# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

def questLog(world):
	quest_log = u""
	if world.knowledge.get("jason_prologue"):
		quest_log += u"Jason's Memories"
		if world.knowledge.get("jason_prologue") == 1:
			quest_log += u"\nSteal something nice from the mansion to satisfy Uncle Garth.\n\n"
		elif world.knowledge.get("jason_prologue") == 2:
			quest_log += u"\nSneak back into Uncle Garth's hideout and get rid of him.\n\n"
		elif world.knowledge.get("jason_prologue") == 3:
			quest_log += u" - Completed\n\n"
	return quest_log
