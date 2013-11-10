#!/usr/bin/env python

import os
import shutil
import re

TOPDIR="rpmbuild"

def prepare_rootdir(topdir):
	try:
		os.mkdir(topdir)
		for d in ('SOURCES', 'SPECS', 'BUILD', 'RPMS', 'SRPMS'):
			os.mkdir(os.path.join(topdir,d))
	except OSError:
		pass

def clean_rootdir(topdir):
	shutil.rmtree(topdir, True)

class SpecFile:
	def __init__(self, specfile):
		self.specfile=specfile
		f = open(specfile, "r")
		self.content = f.readlines()
		f.close()
		self.source=[]
		self.source_line=[]
		name = re.compile("Name:\s+(.*)$")
		version = re.compile("Version:\s+(.*)$")
		release = re.compile("Release:\s+(.*)$")
		source = re.compile("Source(\d+):\s+(\S+)$")
		line = 0
		for i in self.content:
			match = version.match(i)
			if match:
				self.version = match.group(1)
				self.version_line = line

			match = release.match(i)
			if match:
				self.release = match.group(1)
				self.release_line = line

			match = source.match(i)
			if match:
				self.source.append(match.group(2))
				self.source_line.append(line)

			match = name.match(i)
			if match:
				self.name=match.group(1)

			line = line + 1

	def write(self, outfile, tarball, release):
#		self.content[self.version_line] = "Version: " + version
		self.content[self.release_line] = "Release:  %s\n" % (release)
		if (len(self.source) > 1):
			for i in self.source_line[0:]:
				del self.content[i]
		self.content[self.source_line[0]] = "Source:  %s\n" % tarball
		f = open(outfile, "w")
		for i in self.content:
			f.write(i)
		f.close()

# vim:foldmethod=marker ts=2 ft=python ai sw=2
