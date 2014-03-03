#!/usr/bin/env python

class RepoProviderBase():
	@classmethod
	def type(self):
		raise NotImplementedError

class RepoPathNotFound(Exception):
	pass

class NoFilesToAdd(Exception):
	pass

# vim:foldmethod=marker ts=2 ft=python ai sw=2
