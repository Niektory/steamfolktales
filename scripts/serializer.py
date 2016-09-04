# -*- coding: utf-8 -*-
# Copyright 2016 Tomasz "Niektóry" Turowski

from __future__ import print_function

from fife import fife
from dill import Pickler, Unpickler	# from pickle
from sys import setrecursionlimit
import copy_reg
import types
from StringIO import StringIO
"""
def _pickle_method(method):
	func_name = method.im_func.__name__
	obj = method.im_self
	cls = method.im_class
	return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
	for cls in cls.mro():
		try:
			func = cls.__dict__[func_name]
		except KeyError:
			pass
		else:
			break
	return func.__get__(obj, cls)
"""
def persistent_id(obj):
#	print type(obj), obj
	if str(type(obj)) == "<class 'scripts.application.Application'>":
		return "None"
	elif str(type(obj)) == "<class 'scripts.character.CharacterListener'>":
		return "None"
	elif str(type(obj)) == "<class 'scripts.worldvisual.WorldVisual'>":
		return "None"
	elif str(type(obj)) == "<class 'scripts.charactervisual.CharacterVisual'>":
		return "None"
	elif str(type(obj)) == "<class 'scripts.interactobject.InteractObjectVisual'>":
		return "None"
	elif type(obj) == fife.Layer:
		return "None"
	elif type(obj) == fife.Instance:
		return "None"
	elif type(obj) in [fife.ScreenPoint, fife.ModelCoordinate]:
		return "ModelCoordinate " + str(obj.x) + " " + str(obj.y) + " " + str(obj.z)
#	elif (str(obj).find("Visual") != -1) and (str(type(obj)).find("dict") == -1):
#		return None
	else:
#		print type(obj), obj
		return None

def persistent_load(persid):
	if persid == "None":
		return None
	elif persid.startswith("ModelCoordinate "):
		return fife.ModelCoordinate(int(persid.split()[1]), int(persid.split()[2]),
									int(persid.split()[3]))
	else:
		raise pickle.UnpicklingError, "Invalid persistent id"

def save(obj, filename):
	print("* Saving...")
	setrecursionlimit(10000)
	#copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
	with open(filename, "wb") as out_file:
		pickler = Pickler(out_file, -1)
		pickler.persistent_id = persistent_id
		pickler.dump(obj)
	print("* Saved!")

def load(filename):
	print("* Loading...")
	#copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
	with open(filename, "rb") as in_file:
		unpickler = Unpickler(in_file)
		unpickler.persistent_load = persistent_load
		loaded = unpickler.load()
	print("* Loaded!")
	return loaded

def dump(obj):
	print("* Dumping...")
	setrecursionlimit(10000)
	#copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
	pickle_buffer = StringIO()
	pickler = Pickler(pickle_buffer, -1)
	pickler.persistent_id = persistent_id
	pickler.dump(obj)
	print("* Dumped!")
	return pickle_buffer

def restore(pickle_buffer):
	#print "* Restoring..."
	#copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
	pickle_buffer.seek(0)
	unpickler = Unpickler(pickle_buffer)
	unpickler.persistent_load = persistent_load
	obj = unpickler.load()
	#print "* Restored!"
	return obj

def clone(obj):
	return restore(dump(obj))

