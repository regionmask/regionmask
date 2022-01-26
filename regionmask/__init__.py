# flake8: noqa

import os

import pkg_resources

from . import core, defined_regions
from .core._geopandas import from_geopandas, mask_3D_geopandas, mask_geopandas
from .core.plot import plot_3D_mask
from .core.regions import Regions, _OneRegion

try:
    __version__ = pkg_resources.get_distribution("regionmask").version
except Exception:
    # Local copy or not installed with setuptools.
    # Disable minimum version checks on downstream libraries.
    __version__ = "999"

# hack for https://github.com/readthedocs/readthedocs.org/issues/8201
# rtd creates a 'dirty' repo even for tags
if os.environ.get("READTHEDOCS", None) == "True":
    __version__ == __version__.split(".dev0+")[0]
