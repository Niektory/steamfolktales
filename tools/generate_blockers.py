#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from PIL import Image

#input_image_file = "Victoran_Wilds01_block.tga"
#output_file = "blockers.xml"
#map_border_x_min = -51
#map_border_x_max = 50
#map_border_y_min = -56
#map_border_y_max = 63
#map_image_x_offset = 0
#map_image_y_offset = 25
#half_tile_size_x = 39
#half_tile_size_y = 25
#blocking_colors = (0, (0,0,0))
#probe_x = 13
#probe_y = 8

input_image_file = "Watermill_interior.tga"
output_file = "blockers.xml"
map_border_x_min = -10
map_border_x_max = 5
map_border_y_min = -6
map_border_y_max = 7
map_image_x_offset = 0
map_image_y_offset = 25
half_tile_size_x = 39
half_tile_size_y = 25
blocking_colors = (0, (0,0,0))
probe_x = 6
probe_y = 4

im = Image.open(input_image_file)
pix = im.load()
size = im.size
center_x = size[0]/2 - map_image_x_offset
center_y = size[1]/2 - map_image_y_offset

with open(output_file, 'w') as output:
	for x in xrange(map_border_x_min, map_border_x_max+1):
		for y in xrange(map_border_y_min, map_border_y_max+1):
			if (center_x + half_tile_size_x*x + half_tile_size_x*y - probe_x >= 0) and (center_x + half_tile_size_x*x + half_tile_size_x*y + probe_x < size[0]) and (center_y - half_tile_size_y*x + half_tile_size_y*y - probe_y >= 0) and (center_y - half_tile_size_y*x + half_tile_size_y*y + probe_y < size[1]):
				if (pix[center_x + half_tile_size_x*x + half_tile_size_x*y, center_y - half_tile_size_y*x + half_tile_size_y*y] not in blocking_colors) and (pix[center_x + half_tile_size_x*x + half_tile_size_x*y - probe_x, center_y - half_tile_size_y*x + half_tile_size_y*y - probe_y] not in blocking_colors) and (pix[center_x + half_tile_size_x*x + half_tile_size_x*y - probe_x, center_y - half_tile_size_y*x + half_tile_size_y*y + probe_y] not in blocking_colors) and (pix[center_x + half_tile_size_x*x + half_tile_size_x*y + probe_x, center_y - half_tile_size_y*x + half_tile_size_y*y - probe_y] not in blocking_colors) and (pix[center_x + half_tile_size_x*x + half_tile_size_x*y + probe_x, center_y - half_tile_size_y*x + half_tile_size_y*y + probe_y] not in blocking_colors):
					continue
			output.write('<cell x="'+str(x)+'" y="'+str(y)+'" blocker_type="blocker" />\n')
