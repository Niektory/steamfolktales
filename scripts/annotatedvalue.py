# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski


class AnnotatedValue(object):
	def __init__(self, value, annotation=None):
		self.value = value
		self.annotation = annotation

	def __int__(self):
		return int(self.value)

	def __str__(self):
		return "{}{}".format(
			self.value,
			" ({})".format(self.annotation) if self.annotation else "")

	def __add__(self, other):
		return AnnotatedExpression(self, "+", other)

	def __radd__(self, other):
		return AnnotatedExpression(other, "+", self)

	def __sub__(self, other):
		return AnnotatedExpression(self, "-", other)

	def __rsub__(self, other):
		return AnnotatedExpression(other, "-", self)


class AnnotatedExpression(object):
	def __init__(self, lvalue, operation, rvalue):
		self.lvalue = lvalue
		self.operation = operation
		self.rvalue = rvalue

	@property
	def value(self):
		lvalue = getattr(self.lvalue, "value", self.lvalue)
		rvalue = getattr(self.rvalue, "value", self.rvalue)
		if self.operation == "+":
			return int(lvalue) + int(rvalue)
		if self.operation == "-":
			return int(lvalue) - int(rvalue)

	def __int__(self):
		return int(self.value)

	def formatted(self, multiline=False, result=False):
		need_parentheses = self.operation == "-" and getattr(self.rvalue, "operation", None) == "-"
		lvalue = formatted(self.lvalue, multiline=multiline, result=False)
		rvalue = formatted(self.rvalue, multiline=multiline, result=False)
		return "{lvalue}{separator}{operator} {rvalue}{result}".format(
			lvalue=lvalue,
			separator="\n" if multiline else " ",
			operator=self.operation,
			rvalue="({})".format(rvalue) if need_parentheses else rvalue,
			result="{}= {}".format("\n---\n" if multiline else " ", self.value) if result else "")

	def __str__(self):
		return self.formatted()

	def __add__(self, other):
		return AnnotatedExpression(self, "+", other)

	def __radd__(self, other):
		return AnnotatedExpression(other, "+", self)

	def __sub__(self, other):
		return AnnotatedExpression(self, "-", other)

	def __rsub__(self, other):
		return AnnotatedExpression(other, "-", self)


def formatted(value, multiline=False, result=False):
	try:
		format = value.formatted
	except AttributeError:
		return str(value)
	else:
		return format(multiline=multiline, result=result)
