# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from random import randrange

from annotatedvalue import formatted, AnnotatedValueBase


def roll(sides=6, dice=1):
	return sum([randrange(1, sides + 1) for i in xrange(dice)])


#def totalDecorator(function):
#	return lambda self, other: function(self.total, other)

class Roll(AnnotatedValueBase):
	def __init__(self, sides=6, dice=1, modifier=0, annotation=None):
		self.sides = sides
		self.dice = dice
		self.modifier = modifier
		self.annotation = annotation
		self.results = [randrange(1, sides+1) for i in xrange(dice)]

	@property
	def value(self):
		return sum(self.results) + self.modifier

	def __getitem__(self, key):
		return self.results[key]

	@property
	def d_notation(self):
		return "{dice}d{sides}{modifier}".format(
			dice=self.dice if self.dice > 1 else "",
			sides=self.sides,
			modifier="+{}".format(self.modifier) if self.modifier else "")

	def __str__(self):
		return "{total} ({annotation}rolled {d_notation}, got {results})".format(
			total=self.value,
			annotation="{}: ".format(self.annotation) if self.annotation else "",
			d_notation=self.d_notation,
			results=str(self.results).replace("[", "\\["))  # need to escape "[" because of CEGUI

	# adding Rolls to ints, how cool is that? (I'm going to regret this)
	#__add__, __sub__, __radd__, __rsub__ = map(
	#	totalDecorator,
	#	(int.__add__, int.__sub__, int.__radd__, int.__rsub__))


class Check(object):
	def __init__(self, sides=6, dice=1, target=0):
		self.sides = sides
		self.dice = dice
		self.target = target
		self.results = Roll(sides=sides, dice=dice)

	def __int__(self):
		return int(self.results)

	@property
	def margin(self):
		return self.target - self.results

	def __nonzero__(self):
		return self.results <= self.target

	success = property(__nonzero__)

	@property
	def failure(self):
		return not self.success

	@property
	def golden(self):
		return self.success and self.results[0] == 1

	@property
	def fumble(self):
		return not self.success and self.results[0] == self.sides

	def __getitem__(self, key):
		return self.results[key]

	def __str__(self):
		if self.golden:
			return "golden success"
		elif self.success:
			return "success"
		elif self.fumble:
			return "fumble"
		elif self.failure:
			return "failure"
		else:
			return "cat state"

	def formatted(self, multiline=False, result=False):
		return "{target} (need to roll this or lower){separator}roll {roll}{result}".format(
			target=formatted(self.target, multiline=multiline, result=result),
			separator="\n" if multiline else " vs. ",
			roll=self.results,
			result="{}{}".format("\n" if multiline else " ", str(self) if result else ""))
