# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from __future__ import division


class AnnotatedValueBase(object):
	def __int__(self):
		return int(self.value)

	def __add__(self, other):
		return AnnotatedExpression(self, "+", other)

	def __radd__(self, other):
		return AnnotatedExpression(other, "+", self)

	def __sub__(self, other):
		return AnnotatedExpression(self, "-", other)

	def __rsub__(self, other):
		return AnnotatedExpression(other, "-", self)

	def __mul__(self, other):
		return AnnotatedExpression(self, "*", other)

	def __rmul__(self, other):
		return AnnotatedExpression(other, "*", self)

	def __floordiv__(self, other):
		return AnnotatedExpression(self, "//", other)

	def __rfloordiv__(self, other):
		return AnnotatedExpression(other, "//", self)

	def __truediv__(self, other):
		return AnnotatedExpression(self, "/", other)

	def __rtruediv__(self, other):
		return AnnotatedExpression(other, "/", self)


class AnnotatedValue(AnnotatedValueBase):
	def __init__(self, value, annotation=None):
		self.value = value
		self.annotation = annotation

	def __str__(self):
		return "{}{}".format(
			self.value,
			" ({})".format(self.annotation) if self.annotation else "")


class AnnotatedExpression(AnnotatedValueBase):
	def __init__(self, lvalue, operation, rvalue):
		self.lvalue = lvalue
		self.operation = operation
		self.rvalue = rvalue

	@property
	def value(self):
		lvalue = getattr(self.lvalue, "value", self.lvalue)
		rvalue = getattr(self.rvalue, "value", self.rvalue)
		if self.operation == "+":
			return lvalue + rvalue
		if self.operation == "-":
			return lvalue - rvalue
		if self.operation == "*":
			return lvalue * rvalue
		if self.operation == "/":
			return lvalue / rvalue
		if self.operation == "//":
			return lvalue // rvalue

	def formatted(self, multiline=False, result=False):
		l_need_parentheses = (
			self.operation in ("*", "/", "//")
			and getattr(self.lvalue, "operation", None) in ("+", "-"))
		r_need_parentheses = (
			(self.operation == "-" and getattr(self.rvalue, "operation", None) == "-")
			or (self.operation in ("*", "/", "//")
				and getattr(self.rvalue, "operation", None) in ("+", "-"))
			or (self.operation in ("/", "//")
				and getattr(self.rvalue, "operation", None) in ("*", "/", "//")))
		lvalue = formatted(self.lvalue, multiline=multiline, result=False)
		rvalue = formatted(self.rvalue, multiline=multiline, result=False)
		return "{lvalue}{separator}{operator} {rvalue}{result}".format(
			lvalue="({})".format(lvalue) if l_need_parentheses else lvalue,
			separator="\n" if multiline else " ",
			operator=self.operation,
			rvalue="({})".format(rvalue) if r_need_parentheses else rvalue,
			result="{}= {}".format("\n---\n" if multiline else " ", self.value) if result else "")

	def __str__(self):
		return self.formatted()


def formatted(value, multiline=False, result=False):
	try:
		format = value.formatted
	except AttributeError:
		return str(value)
	else:
		return format(multiline=multiline, result=result)
