#!/usr/bin/env python
from setuptools import setup

# get version
with open("regionmask/version.py") as f:
    line = f.readline().strip().replace(" ", "").replace('"', "")
    version = line.split("=")[1]
    __version__ = version

setup(version=__version__)
