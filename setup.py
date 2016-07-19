#!/usr/bin/env python

from setuptools import setup

version = '0.9.0'

setup(
    name='region_mask',
    version=version,
    description='plotting and creation of masks for spatial regions',
    author='mathause',
    author_email='mathause@ethz.com',
    packages=['region_mask'],
    url='https://github.com/mathause/region_mask',
    install_requires=open('requirements.txt').read().split(),
    long_description='See https://github.com/mathause/region_mask'
)


