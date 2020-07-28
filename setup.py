#!/usr/bin/env python

from setuptools import find_packages, setup

# get version
with open("regionmask/version.py") as f:
    line = f.readline().strip().replace(" ", "").replace('"', "")
    version = line.split("=")[1]
    __version__ = version


setup(
    name="regionmask",
    version=__version__,
    description="plotting and creation of masks for spatial regions",
    author="mathause",
    author_email="mathias.hauser@env.ethz.com",
    packages=find_packages(),
    url="https://github.com/mathause/regionmask",
    install_requires=open("requirements.txt").read().split(),
    extras_require={"docs": ["numpydoc", "jupyter", "nbconvert"]},
    long_description="See https://regionmask.readthedocs.io",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    python_requires=">=2.7",
)
