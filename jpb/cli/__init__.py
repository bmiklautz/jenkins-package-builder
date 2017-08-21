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
import platform
from jpb.repo_provider.createrepo import createrepo
from jpb.repo_provider.createrepo import createrepo
#from jpb.build_provider.build import build as pbbuild

SRC_DIR="source"
config = {}

def _common_init():
	init_logging()
	logger = logging.getLogger("%s:init" % __name__)

	for i in ('WORKSPACE', 'BUILD_NUMBER', 'JOB_NAME'):
		config[i] = get_env(i)

	if not config['WORKSPACE']:
		logger.error("WORKSPACE not set")
		sys.exit(1)

	if not config['BUILD_NUMBER']:
		logger.error("BUILD_NUMBER not set")
		sys.exit(1)

	os.chdir(config["WORKSPACE"])

def generate_source_package():
	_common_init()
	files=[]
	cleanup_workspace([".rpm", ".tar.gz"])
	rpm.clean_rootdir(rpm.TOPDIR)
	logger = logging.getLogger("%s:generate_source_package" % __name__)
	no_scm = get_env("JPB_SOURCE_NO_SCM")

	sourcedir = get_env("JPB_SOURCE_DIR")
	if not sourcedir:
		sourcedir = SRC_DIR

	source = os.path.join(config['WORKSPACE'], sourcedir)

	spec=get_env("JPB_RPM_SPECFILE")
	if not spec:
		for i in os.listdir(source):
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

	if no_scm:
		specfile = spec
		tarball = sf.get_source_name()
	else:
		sp = get_source_provider(source)
		commit_string = sp.commit_version_string()
		if get_env("USE_ORIG_VERSION"):
			release = sf.release
		else:
			release = generate_build_version(sf.release, config['BUILD_NUMBER'], commit_string)
		tarball=sp.generate_tarball(sf.name, sf.version)
		specfile = sf.name+".spec"
		logger.info("Generating updated spec file %s" % specfile)
		sf.write(specfile, tarball, release)

	logger.info("Generating source package")
	files.append(tarball)
	files = files + sf.get_additional_sources()
	if not rpmbuild.generate_src_package(specfile, files, sourcedir):
		logger.error("Problem while generating the source package")

	if not no_scm:
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

	arch = get_env("architecture")
	distri = get_env("distribution")
	logger.info("Building for distribution %s and architecture %s" % (distri, arch))
	if (platform.dist()[0] == "fedora"):
		from jpb.build_provider.mock import mock as cbuilder
	elif (platform.dist()[0] == "SuSE"):
		from jpb.build_provider.build import build as cbuilder
	else:
		logger.error("Currently unsupported build platform")
		sys.exit(1)

	builder = cbuilder(config['WORKSPACE'], distribution = distri, architecture = arch)
	if not builder.build(srpm):
		logger.error("Build failed see log for details")
		sys.exit(1)


def provide_package():
	_common_init()
	logger = logging.getLogger("%s:provide_package" % __name__)
	arch = get_env("architecture")
	distri = get_env("distribution")
	reponame = get_env("REPONAME")
	repositorypath = get_env("REPOSITORY")
	rp = createrepo(config, distribution=distri, architecture=arch, repopath=repositorypath, reponame=reponame)
	if not rp.add_to_repo(glob.glob('*.rpm')):
		logger.error("Failed adding files to the repository")
		sys.exit(1)

# vim:foldmethod=marker ts=2 ft=python ai sw=2
