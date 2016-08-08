# from .regions import outline, short_name, name

# from .plot import plot_SREX

# from .mask import mask, mask_xr

# import pkg_resources  # part of setuptools
# __version__ = pkg_resources.require("regionmask")[0].version

#with open("version.py") as f:
#    __version__ = f.read().strip()

from .version import version
__version__ = version

# try to load matplotlib and set backend to Agg on rtd
import os
on_rtd = os.environ.get("READTHEDOCS", None) == "True"
if on_rtd:
    import matplotlib
    matplotlib.use('Agg')

from .core.regions import Regions_cls, Region_cls

from . import defined_regions

# for testing
from .core.plot import _subsample 
from .core.mask import (create_mask_contains, _wrapAngle360, _wrapAngle180,
                   _wrapAngle)

# from .save_utils import _griddes, _dcoord


