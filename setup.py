#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="jpb",
    version="0.0.2",
    packages=find_packages(),
    # package_dir = {'':"lib"},
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "jpb_generate_source_package = jpb.cli:generate_source_package",
            "jpb_generate_binary_package = jpb.cli:generate_binary_package",
            "jpb_provide_package = jpb.cli:provide_package",
        ],
    },
    author="Bernhard Miklautz",
    author_email="bernhard.miklautz@shacknet.at",
    license="MIT",
    python_requires=">=3.5",
    install_requires=[
        "distro",
    ],
    # keywords=
    # url=
)

# vim:foldmethod=marker ts=2 ft=python ai sw=2
