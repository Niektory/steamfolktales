#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from os import listdir
from os.path import isfile, splitext

files = [ f for f in listdir('.') if isfile(f) ]
for file in files:
	if splitext(file)[1].lower() in ('.png', '.jpg', '.jpeg'):
		if not isfile(splitext(file)[0] + '.xml'):
			print 'generating xml for image:', file
			with open(splitext(file)[0] + '.xml', 'w') as output:
				output.write('<?fife type="object"?>\n<object id="' + splitext(file)[0] + '" namespace="steamfolktales" blocking="0" static="1">\n	<image source="' + file + '" direction="0" x_offset="0" y_offset="0" />\n</object>')
				