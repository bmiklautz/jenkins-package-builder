#!/usr/bin/env python

class SourceProviderBase():
	@classmethod
	def type(self):
		raise NotImplementedErrora

	def commit_short(self):
		raise NotImplementedErrora
	
	def commit_version_string(self):
		raise NotImplementedErrora

	def generate_tarball(self, name, version, outdir):
		raise NotImplementedErrora

# vim:foldmethod=marker ts=2 ft=python ai sw=2
