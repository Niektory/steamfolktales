# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

class Cutscene(object):
	def __init__(self, application):
		self.application = application
		#self.start_time = self.application.engine.getTimeManager().getTime()
		self.start_time = self.application.real_timeline.clock
		if hasattr(self, "script_list"):
			self.generators = [script(self) for script in self.script_list]
		else:
			self.generators = [self.cutsceneScript()]

	@property
	def elapsed_time(self):
		#return self.application.engine.getTimeManager().getTime() - self.start_time
		return self.application.real_timeline.clock - self.start_time
	
	def pump(self):
		#self.application.gui.global_tooltip.printMessage("cutscene time: " +
		#				str(self.elapsed_time))
		#self.generator.next()
		for generator in self.generators[:]:
			try:
				generator.next()
			except StopIteration:
				self.generators.remove(generator)
		return bool(self.generators)
