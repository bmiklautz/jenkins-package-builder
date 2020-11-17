#!/usr/bin/env python
import platform
import os
import subprocess
import glob
import sys
import shutil
from jpb.utils import get_env
import tempfile

from jpb.build_provider.base import BuildProviderBase as BuildProviderBase
from jpb.build_provider.base import DistNotAvailable as DistNotAvailable

MOCK_BASE_PATH = "mockbuild"


class mock(BuildProviderBase):
    @classmethod
    def type(self):
        return "mock"

    def _cleanBuildDir(self):
        if os.path.exists(self.mockpath):
            try:
                shutil.rmtree(self.mockpath)
            except OSError:
                return False
        return True

    def _copyRPMs(self):
        if not os.path.exists(self.mockpath):
            return False
        for filename in glob.glob(os.path.join(self.mockpath, "*.rpm")):
            shutil.copy(filename, self.workspace)
        return True

    def _checkConfig(self):
        return os.path.exists(self.mock_cfg)

    def _createRepoConfig(self, cfg, repo, name):
        cfg.write("[%s]\n" % name)
        cfg.write("name=%s\n" % name)
        cfg.write("baseurl=%s\n" % repo)
        cfg.write("enabled=1\n")
        cfg.write("gpgcheck=0\n")

    def _createCustomConfig(self):
        f = open(self.mock_cfg, "r")
        (nff, ncf) = tempfile.mkstemp(suffix=".cfg", text=True)
        nf = os.fdopen(nff, "w")
        for line in f.readlines():
            if line == '"""\n':
                rid = 0
                for r in self.repos.split(","):
                    nf.write("\n")
                    self._createRepoConfig(nf, r, "jbp_tmp_%i" % rid)
                    rid = rid + 1
            nf.write(line)
        f.close()
        nf.close()
        return ncf

    def __init__(self, workspace, distribution="", architecture=""):
        if not architecture:
            architecture = platform.machine()

        BuildProviderBase.__init__(self, workspace, distribution, architecture)
        self.repos = get_env("MOCK_REPOSITORY_EXTRA")

        self.mock_cfg = get_env("MOCK_CFG")

        if not self.mock_cfg:
            if self.distribution:
                self.mock_cfg = "%s-%s" % (self.distribution, self.architecture)
            else:
                self.mock_cfg = "default"

        if not self.mock_cfg.endswith(".cfg"):
            self.mock_cfg = "/etc/mock/%s.cfg" % self.mock_cfg

        if not self._checkConfig():
            raise DistNotAvailable

        self.mockpath = os.path.join(self.workspace, MOCK_BASE_PATH)
        self.basecmd = [
            "/usr/bin/mock",
            "--isolation=simple",
            "--resultdir",
            self.mockpath,
        ]

        self._cleanBuildDir()

    def build(self, srpm):

        if not os.path.exists(srpm):
            return False

        custom_cfg = 0

        if self.repos:
            cfg = self._createCustomConfig()
            custom_cfg = 1
        else:
            cfg = self.mock_cfg

        self.buildcmd = self.basecmd + ["-r", "%s" % cfg]

        if self.macros:
            self.buildcmd = self.basecmd + ["--macro-file=%s" % self.macros]

        cmd = list(self.buildcmd)
        cmd = cmd + [srpm]

        if subprocess.call(cmd):
            if custom_cfg:
                os.unlink(cfg)
            # dump the build log to stdout
            with open(os.path.join(self.mockpath, 'build.log'), 'rb') as f:
                while os.sendfile(sys.stdout.buffer.fileno(), f.fileno(), None, 1 << 30) != 0:
                    pass
            return False
        # mock rebuilds the srpm. so the "old" one isn't required anymore.
        os.unlink(srpm)
        if custom_cfg:
            os.unlink(cfg)
        return self._copyRPMs()


# vim:foldmethod=marker ts=2 ft=python ai sw=2
