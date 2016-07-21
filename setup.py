#!/usr/bin/env python

from setuptools import setup

# get version
with open("regionmask/version.py") as f:
    __version__ = f.read().strip()


setup(
    name='regionmask',
    version=__version__,
    description='plotting and creation of masks for spatial regions',
    author='mathause',
    author_email='mathause@ethz.com',
    packages=['regionmask'],
    url='https://github.com/mathause/regionmask',
    install_requires=open('requirements.txt').read().split(),
    long_description='See https://github.com/mathause/regionmask'
)


