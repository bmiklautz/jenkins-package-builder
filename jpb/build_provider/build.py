#!/usr/bin/env python
from jpb.build_provider.base import BuildProviderBase as BuildProviderBase
from jpb.build_provider.base import DistNotAvailable as DistNotAvailable
import os
import subprocess
import platform
import shutil
import glob

BUILD_BASE_PATH = "/usr/lib/build/"
BUILD_CONFIG_PATH = BUILD_BASE_PATH + "configs"
BUILD_CONF_EXTENSION = "conf"
BUILD_RPM_HOME="home/abuild/rpmbuild/RPMS"
BUILD_ROOT_PREFIX="build-"

class CanNotClean(Exception):
	pass

class build(BuildProviderBase):
	
	#--uid uid:gid
	@classmethod
	def type(self):
		return "build"

	def __init__(self, workspace, distribution = "" , architecture = ""):
		if not architecture:
			architecture = platform.machine()
		BuildProviderBase.__init__(self, workspace, distribution, architecture)

		if self.distribution and not self._checkConfig(self.distribution):
			raise DistNotAvailable

		builddir = "buildroots/" + BUILD_ROOT_PREFIX
		if not self.distribution:
			builddir = builddir + "default"
		else:
			builddir = builddir + self.distribution
		builddir = builddir + "/" + self.architecture
		self.buildroot = os.path.join(self.workspace, builddir)
		self.rpmdir = os.path.join(self.buildroot, BUILD_RPM_HOME)
		uid = os.getuid()
		gid = os.getgid()
		if self.architecture != "x86_64":
			self.basecmd = ["sudo", "-n", "/usr/bin/linux32", "/usr/bin/build", "--root=%s" % self.buildroot, "--uid", "%d:%d" % (uid,gid)]
		else:
			self.basecmd = ["sudo", "-n", "/usr/bin/build", "--root=%s" % self.buildroot, "--uid", "%d:%d" % (uid,gid)]
		self.buildcmd =  self.basecmd + ["--arch", self.architecture, "--clean"]
		if (self.distribution):
			self.buildcmd =  self.basecmd + ["--arch", self.architecture, "--clean", "--dist", self.distribution]
		else:
			self.buildcmd =  self.basecmd + ["--arch", self.architecture, "--clean"]
		self.killcmd =  self.basecmd + ["--kill"]

	def _checkConfig(self, distribution):
		return os.path.exists(os.path.join(BUILD_CONFIG_PATH, "%s.%s" % (distribution, BUILD_CONF_EXTENSION)))
	
	def _cleanRPMDir(self):
		if (os.path.exists(self.rpmdir)):
			try:
				shutil.rmtree(self.rpmdir)
			except OSError:
				return False
		return True

	def _copyRPMs(self):
		if not os.path.exists(self.rpmdir):
			return False
		for i in os.listdir(self.rpmdir):
			cdir = os.path.join(self.rpmdir, i)
			for filename in glob.glob(os.path.join(cdir, '*.rpm')):
			    shutil.copy(filename, self.workspace)
		return True
		
	def build(self, srpm):
		if not os.path.exists(srpm):
			return False
	
		cmd = list(self.buildcmd)
		cmd = cmd + [srpm] 
		cmd = cmd + ["--stage=-bb"]
		print cmd

		if subprocess.call(cmd):
			return False

		return self._copyRPMs()
	
# vim:foldmethod=marker ts=2 ft=python ai sw=2
