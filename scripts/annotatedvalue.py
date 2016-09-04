# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski


# TODO: make this less insane, then adapt the codebase to use it

class AnnotatedValue(object):
	def __init__(self, value, annotation=None):
		self.value = value
		self.annotation = annotation

	def __int__(self):
		return self.value

	def __str__(self):
		return "{}{}".format(
			self.value,
			" ({})".format(self.annotation) if self.annotation else "")

	def __add__(self, other):
		return AnnotatedExpression(self) + other

	def __radd__(self, other):
		return other + AnnotatedExpression(self)

	def __sub__(self, other):
		return AnnotatedExpression(self) - other

	def __rsub__(self, other):
		return other - AnnotatedExpression(self)


class AnnotatedExpression(object):
	def __init__(self, initial_value, operations=[]):
		self.initial_value = initial_value
		self.operations = operations[:]

	def __int__(self):
		value = int(self.initial_value)
		for operation in self.operations:
			if operation[0] == "+":
				value += int(operation[1])
			if operation[0] == "-":
				value -= int(operation[1])
		return value

	total = property(__int__)

	def __str__(self):
		value = str(self.initial_value)
		for operation in self.operations:
			value += "\n{} {}".format(operation[0], operation[1])
		# value += "\n---\n= {}".format(int(self))
		return value

	@property
	def result(self):
		return str(self) + "\n---\n= {}".format(int(self))

	def __add__(self, other):
		result = AnnotatedExpression(self.initial_value, self.operations)
		result.operations.append(("+", other))
		return result

	def __radd__(self, other):
		result = AnnotatedExpression(other)
		result.operations.append(("+", AnnotatedExpression(self.initial_value, self.operations)))
		return result

	def __sub__(self, other):
		result = AnnotatedExpression(self.initial_value, self.operations)
		result.operations.append(("-", other))
		return result

	def __rsub__(self, other):
		result = AnnotatedExpression(other)
		result.operations.append(("-", AnnotatedExpression(self.initial_value, self.operations)))
		return result
