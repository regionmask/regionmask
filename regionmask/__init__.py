# __init__.py file

# flake8: noqa

# get version
from .version import version

__version__ = version

# import
from .core.regions import Regions_cls, Region_cls, Regions, _OneRegion

from . import defined_regions

from .core.mask import create_mask_contains

# for testing
from . import core
