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

SRC_DIR="source"
config = {}

def generate_source_package():
	init_logging()
	logger = logging.getLogger("%s:generate_source_package" % __name__)
	for i in ('WORKSPACE', 'BUILD_ID'):
		config[i] = get_env(i)

	if not config['WORKSPACE']:
		logger.error("WORKSPACE not set")
		sys.exit(1)

	os.chdir(config["WORKSPACE"])
	cleanup_workspace()

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
# vim:foldmethod=marker ts=2 ft=python ai sw=2
