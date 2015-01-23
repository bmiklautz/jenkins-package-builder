#!/usr/bin/env python

import jpb.utils.rpm as rpm
import shutil
import os
import subprocess
import glob

def generate_src_package(specfile, tarball):
	topdir = rpm.TOPDIR
	sourcedir = os.path.join(topdir, "SOURCES")
	srpmdir = os.path.join(topdir, "SRPMS")
	rpm.prepare_rootdir(topdir)		
	shutil.copy(tarball, sourcedir)
        subprocess.call(["rpmbuild","--define", "_topdir "+ topdir, "--nodeps", "-bs", specfile])
	for filename in glob.glob(os.path.join(srpmdir, '*.src.rpm')):
	    shutil.copy(filename, ".")
	rpm.clean_rootdir(topdir)

# vim:foldmethod=marker ts=2 ft=python ai sw=2
