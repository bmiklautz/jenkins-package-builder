#!/usr/bin/env python
import platform 
import os
import subprocess
import glob
import shutil

from jpb.build_provider.base import BuildProviderBase as BuildProviderBase
from jpb.build_provider.base import DistNotAvailable as DistNotAvailable

MOCK_BASE_PATH = "mockbuild"

class mock(BuildProviderBase):
	
	@classmethod
	def type(self):
		return "mock"

	def _cleanBuildDir(self):
		if (os.path.exists(self.mockpath)):
			try:
				shutil.rmtree(self.mockpath)
			except OSError:
				return False
		return True
		
	def _copyRPMs(self):
		if not os.path.exists(self.mockpath):
			return False
		for filename in glob.glob(os.path.join(self.mockpath, '*.rpm')):
			shutil.copy(filename, self.workspace)
		return True

	def _checkConfig(self):
		return os.path.exists(os.path.join("/etc/mock", "%s-%s.cfg" % (self.distribution, self.architecture)))

	def __init__(self, workspace, distribution = "" , architecture = ""):
		if not architecture:
			architecture = platform.machine()
		BuildProviderBase.__init__(self, workspace, distribution, architecture)

		if self.distribution and not self._checkConfig():
			raise DistNotAvailable

		self.mockpath = os.path.join(self.workspace, MOCK_BASE_PATH)
		self.basecmd = ["/usr/bin/mock"]
		if (self.distribution):
			self.buildcmd =  self.basecmd + ["--resultdir", self.mockpath, "-r", "%s-%s" % (self.distribution, self.architecture) ]
		else:
			self.buildcmd =  self.basecmd + ["--resultdir", self.mockpath]
		self._cleanBuildDir()

	def build(self, srpm):
		if not os.path.exists(srpm):
			return False
	
		cmd = list(self.buildcmd)
		cmd = cmd + [srpm] 

		if subprocess.call(cmd):
			return False
		# mock rebuilds the srpm. so the "old" one isn't required anymore.
		os.unlink(srpm)
		return self._copyRPMs()
	
# vim:foldmethod=marker ts=2 ft=python ai sw=2
