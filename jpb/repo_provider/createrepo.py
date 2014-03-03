#!/usr/bin/env python

from jpb.repo_provider.base import RepoProviderBase, RepoPathNotFound, NoFilesToAdd
import jpb.utils.rpm as rpm
import os
import shutil
import subprocess
import logging


REPOSITORY_DEFAULT = "/srv/repository/"

class createrepo(RepoProviderBase):

	class Error(Exception):
		pass

	@classmethod
	def type(self):
		return "createrepo"

	def __init__(self, config, distribution="", architecture = "", repopath = "", reponame = ""):
		self.config = config
		self.distribution = distribution
		if repopath:
			self.repopath = repopath
		else:
			self.repopath = REPOSITORY_DEFAULT	
		try:
			os.stat(self.repopath)
		except:
			print "Used repo path ", self.repopath
			raise RepoPathNotFound 
		self.architecture = architecture
		if reponame:
			self.reponame = reponame
		else:
			rname = config['JOB_NAME']
			rname = rname.replace("-repos", "")
			self.reponame = rname.replace("-binaries", "")

	def _get_rpm_arch(self, filename):
		if self.architecture:
			return self.architecture
		return rpm.get_rpm_information(filename)['arch']
		
	def add_to_repo(self, filelist):
		if not filelist:
			raise NoFilesToAdd
		repos = []	
		logger = logging.getLogger("%s" % __name__)
		#repo path format: repopath/dist/arch/package
		# dist will be obmitted if not set
		for i in filelist:
			arch = self._get_rpm_arch(i)
			repopath = ""
			if self.distribution:
				repopath = os.path.join(self.repopath, self.distribution, arch, self.reponame)	
			else:
				repopath = os.path.join(self.repopath, arch, self.reponame)	
			# copy the file to the d
			try:
				os.stat(repopath)
			except:
				os.makedirs(repopath) 
			shutil.copy(i, repopath)
			if not repopath in repos:
				repos.append(repopath)
		for repo in repos:
			logger.info("Updating repo %s" % repo)
			cmd = ["createrepo", repo]
			if subprocess.call(cmd):
				return False
		return True
			
# vim:foldmethod=marker ts=2 ft=python ai sw=2
