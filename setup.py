#!/usr/bin/env python

from setuptools import setup

version = '0.9.0'

setup(
    name='regionmask',
    version=version,
    description='plotting and creation of masks for spatial regions',
    author='mathause',
    author_email='mathause@ethz.com',
    packages=['regionmask'],
    url='https://github.com/mathause/regionmask',
    install_requires=open('requirements.txt').read().split(),
    long_description='See https://github.com/mathause/regionmask'
)


