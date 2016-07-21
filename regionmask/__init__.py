# from .regions import outline, short_name, name

# from .plot import plot_SREX

# from .mask import mask, mask_xr

# import pkg_resources  # part of setuptools
# __version__ = pkg_resources.require("regionmask")[0].version

__version__ = '0.9.0'

# import defined regions
from .defined_regions.srex import srex
from .defined_regions.giorgi import giorgi
# from .defined_regions.naturalearth import natural_earth

# for testing

from .regions import Region_cls as _Region_cls
from .regions import Regions_cls as _Regions_cls

from .regions import Regions_cls, Region_cls

# the cheap way
Regions = _Regions_cls

from .plot import _subsample 
from .mask import (create_mask_contains, _wrapAngle360, _wrapAngle180,
                   _wrapAngle)

from .save_utils import _griddes, _dcoord


