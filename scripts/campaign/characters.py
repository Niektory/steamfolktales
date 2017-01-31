# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife
from os import listdir


@classmethod
def initCharacters(cls, world):
	for file_name in listdir("campaign_data/characters"):
		if file_name.endswith(".xml"):
			world.loadCharacter(file_name.split("\\")[-1][:-4])
	for file_name in listdir("campaign_data/interact_objects"):
		if file_name.endswith(".xml"):
			world.loadInteractObject(file_name.split("\\")[-1][:-4])
