# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from __future__ import print_function

from traceback import print_exception
from datetime import datetime

ERROR_FILE = "error.log"

#def printException():
#	with open(ERROR_FILE, "a") as f:
#		f.write(str(datetime.now()))
#		f.write("\n\n")
#		print_exc(file=f)
#		f.write("\n-----\n\n")
#	print("FATAL ERROR! Exception logged in", ERROR_FILE)

# TODO: change the code to use the decorator instead of this
class LogException:
	def __enter__(self):
		pass

	def __exit__(self, exc_type, exc_value, exc_traceback):
		if exc_type is None:
			return
		with open(ERROR_FILE, "a") as f:
			f.write(str(datetime.now()))
			f.write("\n\n")
			print_exception(exc_type, exc_value, exc_traceback, file=f)
			f.write("\n-----\n\n")
		print("FATAL ERROR! Exception logged in", ERROR_FILE)

def LogExceptionDecorator(function):
	def innerFunction(*args, **kwargs):
		with LogException():
			function(*args, **kwargs)
	return innerFunction
