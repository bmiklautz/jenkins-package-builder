#!/usr/bin/env python

import time
import os


def create_timestamp():
    return time.strftime("%Y%m%d%H%M%S")


def increase_version_number(version):
    return version + "+0"


def generate_build_version(origversion, build_number, commitversion):
    return "%s~%s.%s%s" % (
        increase_version_number(origversion),
        create_timestamp(),
        build_number,
        commitversion,
    )


def get_env(name):
    if name not in os.environ:
        return ""
    return os.environ[name]


def cleanup_workspace(types, excludes=[]):
    files = os.listdir(".")
    for i in files:
        ignore = False
        for e in excludes:
            if i.endswith(e):
                ignore = True
        if ignore:
            continue
        for t in types:
            if i.endswith(t):
                os.unlink(i)


# vim:foldmethod=marker ts=2 ft=python ai sw=2
