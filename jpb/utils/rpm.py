#!/usr/bin/env python

from __future__ import absolute_import
import os
import shutil
import re
import rpm

TOPDIR = "rpmbuild"


def prepare_rootdir(topdir):
    try:
        os.mkdir(topdir)
        for d in ("SOURCES", "SPECS", "BUILD", "RPMS", "SRPMS"):
            os.mkdir(os.path.join(topdir, d))
    except OSError:
        pass


def clean_rootdir(topdir):
    shutil.rmtree(topdir, True)


def get_rpm_information(filename):
    ts = rpm.ts()
    f = open(filename, "r")
    ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)
    hdr = ts.hdrFromFdno(f)
    f.close()
    return {
        "name": hdr[rpm.RPMTAG_NAME],
        "version": hdr[rpm.RPMTAG_VERSION],
        "release": hdr[rpm.RPMTAG_RELEASE],
        "epoch": hdr[rpm.RPMTAG_EPOCH],
        "arch": hdr[rpm.RPMTAG_ARCH],
    }


class SpecFile:
    def __init__(self, specfile):
        self.specfile = specfile
        f = open(specfile, "r")
        self.content = f.readlines()
        f.close()
        self.sources = []
        self.patches = []
        self.source_name = ""
        self.source_line = ""
        name = re.compile(r"Name:\s*(.*)$")
        version = re.compile(r"Version:\s*(.*)$")
        release = re.compile(r"Release:\s*(.*)$")
        source = re.compile(r"Source(\d*):\s*(\S+)$")
        patch = re.compile(r"Patch(\d*):\s*(\S+)$")
        line = 0
        for i in self.content:
            match = version.match(i)
            if match:
                self.version = match.group(1)
                self.version_line = line

            match = release.match(i)
            if match:
                self.release = match.group(1)
                self.release_line = line

            match = source.match(i)
            if match:
                first = match.group(1)
                if first == "" or first == "0":
                    self.source_line = line
                    self.source_name = match.group(2)
                else:
                    self.sources.append(match.group(2))

            match = name.match(i)
            if match:
                self.name = match.group(1)

            match = patch.match(i)
            if match:
                self.patches.append(match.group(2))

            line = line + 1

    def get_additional_sources(self):
        return self.sources + self.patches

    def get_source_name(self):
        return self.source_name

    def write(self, outfile, tarball, release):
        # 		self.content[self.version_line] = "Version: " + version
        self.content[self.release_line] = "Release:  %s\n" % (release)
        if self.source_line:
            self.content[self.source_line] = "Source0: %s\n" % tarball
        f = open(outfile, "w")
        for i in self.content:
            f.write(i)
        f.close()


# vim:foldmethod=marker ts=2 ft=python ai sw=2
