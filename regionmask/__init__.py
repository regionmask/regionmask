# __init__.py file

# get version
from .version import version
__version__ = version

# try to load matplotlib and set backend to Agg on rtd
import os as _os
_on_rtd = _os.environ.get("READTHEDOCS", None) == "True"
if _on_rtd:
    import matplotlib
    matplotlib.use('Agg')

# import
from .core.regions import Regions_cls, Region_cls

from . import defined_regions

# for testing
from .core.plot import _subsample 
from .core.mask import (create_mask_contains, _wrapAngle360, _wrapAngle180,
                   _wrapAngle)

