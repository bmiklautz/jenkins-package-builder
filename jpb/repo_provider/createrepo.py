#!/usr/bin/env python

from jpb.repo_provider.base import RepoProviderBase, RepoPathNotFound, NoFilesToAdd
import jpb.utils.rpm as rpm
from jpb.utils import get_env
import os
import shutil
import subprocess
import logging


REPOSITORY_DEFAULT = "/srv/repository/"
REPOMANAGE = "/usr/bin/repomanage"


class createrepo(RepoProviderBase):
    class Error(Exception):
        pass

    @classmethod
    def type(self):
        return "createrepo"

    def __init__(
        self, config, distribution="", architecture="", repopath="", reponame=""
    ):
        self.config = config
        self.distribution = distribution
        if repopath:
            self.repopath = repopath
        else:
            self.repopath = REPOSITORY_DEFAULT
        try:
            os.stat(self.repopath)
        except:
            print("Used repo path ", self.repopath)
            raise RepoPathNotFound
        self.architecture = architecture
        if reponame:
            self.reponame = reponame
        else:
            rname = config["JOB_NAME"]
            rname = rname.replace("-repos", "")
            self.reponame = rname.replace("-binaries", "")

    def _get_rpm_arch(self, filename):
        if self.architecture:
            return self.architecture
        return rpm.get_rpm_information(filename)["arch"]

    def cleanup_repo(self, keep):
        repo_base_path = os.path.join(self.repopath, self.reponame)
        cmd = [REPOMANAGE, "--old", "--keep", str(keep), repo_base_path]
        try:
            files = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            return False
        for f in files.split("\n"):
            if not f:
                continue
            try:
                os.stat(f)
                os.remove(f)
            except:
                return False

        return True

    def add_to_repo(self, filelist):
        if not filelist:
            raise NoFilesToAdd
        logger = logging.getLogger("%s" % __name__)
        # repo_path is the location where the repo should go
        # might be /srv/repos/rpm/fedora/21
        # appended will be the reponame and arch
        repo_base_path = os.path.join(self.repopath, self.reponame)
        for i in filelist:
            if i.endswith(".src.rpm"):
                arch = "source"
            else:
                arch = self._get_rpm_arch(i)
            repopath = os.path.join(repo_base_path, arch)
            try:
                os.stat(repopath)
            except:
                os.makedirs(repopath)
            shutil.copy(i, repopath)

        if not get_env("JPB_REPO_KEEP"):
            binaries_to_keep = 1
        else:
            binaries_to_keep = int(get_env("JPB_REPO_KEEP"))

        if binaries_to_keep != 0:
            if not self.cleanup_repo(binaries_to_keep):
                logger.error("Problem cleaning up the repository")
                return False

        logger.info("Updating repo %s" % repo_base_path)
        cmd = ["createrepo", "--update", repo_base_path]
        if subprocess.call(cmd):
            return False
        return True


# vim:foldmethod=marker ts=2 ft=python ai sw=2
