# flake8: noqa

from . import core, defined_regions
from .core._geopandas import from_geopandas, mask_3D_geopandas, mask_geopandas
from .core.options import get_options, set_options
from .core.plot import plot_3D_mask
from .core.regions import Regions, _OneRegion
from .core.utils import flatten_3D_mask

try:
    from importlib.metadata import version as _get_version
except ImportError:
    # importlib.metadata not available in python 3.7
    import pkg_resources

    _get_version = lambda pkg: pkg_resources.get_distribution(pkg).version

try:
    __version__ = _get_version("regionmask")
except Exception:
    # Local copy or not installed with setuptools.
    # Disable minimum version checks on downstream libraries.
    __version__ = "999"
