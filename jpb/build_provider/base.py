#!/usr/bin/env python
from jpb.utils import get_env
import logging

class DistNotAvailable(Exception):
	pass

class BuildProviderBase():
	@classmethod
	def type(self):
		raise NotImplementedError

	def __init__(self, workspace, distribution, architecture):
		self.architecture = architecture
		self.distribution = distribution
		self.workspace = workspace
		self.macros = get_env("RPM_MACROS")
		self.logger = logging.getLogger("%s:build" % __name__)

	def build(self, srpm):
		raise NotImplementedError
	
		
# vim:foldmethod=marker ts=2 ft=python ai sw=2
