#!/usr/bin/env python

class SourceProviderBase():
	@classmethod
	def type(self):
		raise NotImplementedError

	def commit_short(self):
		raise NotImplementedError
	
	def commit_version_string(self):
		raise NotImplementedError

	def generate_tarball(self, name, version, outdir):
		raise NotImplementedError

# vim:foldmethod=marker ts=2 ft=python ai sw=2
