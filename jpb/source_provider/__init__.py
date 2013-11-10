#!/usr/bin/env python

from jpb.source_provider.git import GitSourceProvider

def get_source_provider(repo):
	return GitSourceProvider(repo)

# vim:foldmethod=marker ts=2 ft=python ai sw=2
