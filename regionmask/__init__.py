# __init__.py file

# flake8: noqa


from . import core, defined_regions
from .core.mask import create_mask_contains
from .core.regions import Region_cls, Regions, Regions_cls, _OneRegion
from .defined_regions.from_geopandas import from_geopandas
from .version import version

__version__ = version
