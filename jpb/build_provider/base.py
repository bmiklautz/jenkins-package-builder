#!/usr/bin/env python

class BuildProviderBase():
	@classmethod
	def type(self):
		raise NotImplementedError

	def __init__(self, workspace, distribution, architecture):
		self.architecture = architecture
		self.distribution = distribution
		self.workspace = workspace

	def build(self, srpm):
		raise NotImplementedError
	
		
# vim:foldmethod=marker ts=2 ft=python ai sw=2
