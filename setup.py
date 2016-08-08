#!/usr/bin/env python

from setuptools import setup, find_packages

# get version
with open("regionmask/version.py") as f:
    l = f.readline().strip().replace(' ', '').replace('"', '')
    version = l.split('=')[1]
    __version__ = version


setup(
    name='regionmask',
    version=__version__,
    description='plotting and creation of masks for spatial regions',
    author='mathause',
    author_email='mathause@ethz.com',
    packages=find_packages(),
    url='https://github.com/mathause/regionmask',
    install_requires=open('requirements.txt').read().split(),
    long_description='See https://github.com/mathause/regionmask'
)


