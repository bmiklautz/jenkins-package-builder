#!/usr/bin/env python

import jpb.utils.rpm as rpm
import shutil
import os
import subprocess
import glob
import logging


def generate_src_package(specfile, files, searchdir=""):
    logger = logging.getLogger("%s" % __name__)
    topdir = rpm.TOPDIR
    logger.debug(rpm.TOPDIR)
    sourcedir = os.path.join(topdir, "SOURCES")
    srpmdir = os.path.join(topdir, "SRPMS")
    rpm.prepare_rootdir(topdir)
    for i in files:
        cppath = ""
        if os.path.isfile(i):
            cppath = i
        elif searchdir and os.path.isfile(os.path.join(searchdir, i)):
            cppath = os.path.join(searchdir, i)
        else:
            logger.error("Couldn't find source file: %s", i)
            return False
        shutil.copy(cppath, sourcedir)
    subprocess.call( ["rpmbuild", "--define", "_topdir " + topdir, "--nodeps",
      "-bs", specfile])
    for filename in glob.glob(os.path.join(srpmdir, "*.src.rpm")):
        shutil.copy(filename, ".")
    rpm.clean_rootdir(topdir)
    return True


# vim:foldmethod=marker ts=2 ft=python ai sw=2
