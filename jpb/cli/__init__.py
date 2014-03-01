#!/usr/bin/env python
from jpb.utils import *
from jpb.source_provider import get_source_provider
import jpb.source_provider.rpmbuild as rpmbuild
import jpb.utils.rpm as rpm
from jpb.utils.log import init_logging
import os
import sys
import glob
import logging
from jpb.build_provider.mock import mock as pbmock 
#from jpb.build_provider.build import build as pbbuild


SRC_DIR="source"
config = {}

def _common_init():
	init_logging()
	logger = logging.getLogger("%s:init" % __name__)

	for i in ('WORKSPACE', 'BUILD_ID'):
		config[i] = get_env(i)

	if not config['WORKSPACE']:
		logger.error("WORKSPACE not set")
		sys.exit(1)

	if not config['BUILD_ID']:
		logger.error("BUILD_ID not set")
		sys.exit(1)

	os.chdir(config["WORKSPACE"])

def generate_source_package():
	_common_init()
	cleanup_workspace([".rpm", ".tar.gz"])
	rpm.clean_rootdir(rpm.TOPDIR)
	logger = logging.getLogger("%s:generate_source_package" % __name__)

	sourcedir = get_env("JPB_SOURCE_DIR")
	if not sourcedir:
		sourcedir = SRC_DIR

	source = os.path.join(config['WORKSPACE'], sourcedir)

	spec=get_env("JPB_RPM_SPECFILE")
	if not spec:
		files =	os.listdir(source)
		for i in files:
			if i.endswith(".spec"):
				spec = os.path.join(source, i)
				break
		if not spec:
			logger.error("No spec file found")
			sys.exit(1)
	else:
		if not os.path.isfile(spec):
			logger.error("Spec file specified with JPB_RPM_SPECFILE not found")
			sys.exit(1)

	logger.info("Using specfile %s" % spec)
	logger.info("Gathering source informations")
	sf = rpm.SpecFile(spec)
	sp = get_source_provider(source)

	commit_string = sp.commit_version_string()
	release = generate_build_version(sf.release, 1, commit_string)
	tarball=sp.generate_tarball(sf.name, sf.version)
	specfile = sf.name+".spec"
	logger.info("Generating updated spec file")
	sf.write(specfile, tarball, release)
	logger.info("Generating source package")
	rpmbuild.generate_src_package(specfile, tarball)

	os.unlink(specfile)
	os.unlink(tarball)

def generate_binary_package():
	_common_init()
	cleanup_workspace(['.rpm'],['src.rpm'])
	logger = logging.getLogger("%s:generate_binary_package" % __name__)
	srpm = ""
	# find srpm
	files = os.listdir(".")
	for i in files:
		if i.endswith(".src.rpm"):
			srpm = i
			break
	if not srpm:
		logger.error("No src.rpm found")
		sys.exit(1)
	logger.info("Using %s" % srpm)

# Todo choose builder depending on host/user setting
	builder = pbmock(config['WORKSPACE'])
	if not builder.build(srpm):
		logger.error("Build failed see log for details")
		sys.exit(1)

# vim:foldmethod=marker ts=2 ft=python ai sw=2
