#!/usr/bin/env python
import subprocess
from jpb.source_provider.base import SourceProviderBase
import re
import os

class GitSourceProvider(SourceProviderBase):
	def __init__(self, repo, commit = ""):
		self.repo = repo+"/.git"
		self.basecmd = ["git", "--git-dir=%s" % (self.repo)]
		if not commit:
			self.commit = "HEAD"
		else:
			self.commit = commit
		try:
			gv=re.compile("git version (.*)").match(subprocess.check_output(["git", "--version"]))
		except OSError:
			 print >> sys.stderr, "Git not found or could not execute"
			 sys.exit(1)

	@classmethod
	def type(self):
		return "git"

	def commit_short(self):
		cmd = list(self.basecmd)
		cmd.append("rev-parse")
		cmd.append("--short")
		cmd.append(self.commit)
		return subprocess.check_output(cmd).rstrip()
	
	def commit_version_string(self):
		return "~1.git" + self.commit_short()

	def generate_tarball(self, name, version):
		ptype="tar.gz"
		cmd = list(self.basecmd)
		cmd = cmd + [ "archive", "--format=%s" % (ptype), "--prefix="+name+"/", "-o"]
		outfile="%s-%s+git%s.%s" % (name, version, self.commit_short(), ptype)
		cmd.append(outfile)
		cmd.append(self.commit)
		subprocess.call(cmd)
		return outfile

# vim:foldmethod=marker ts=2 ft=python ai sw=2
