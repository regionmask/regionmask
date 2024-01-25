from importlib.metadata import version as _get_version

from regionmask import core, defined_regions
from regionmask.core._geopandas import from_geopandas, mask_3D_geopandas, mask_geopandas
from regionmask.core.options import get_options, set_options
from regionmask.core.plot import plot_3D_mask
from regionmask.core.regions import Regions, _OneRegion
from regionmask.core.utils import flatten_3D_mask

__all__ = [
    "_OneRegion",
    "core",
    "defined_regions",
    "flatten_3D_mask",
    "from_geopandas",
    "get_options",
    "mask_3D_geopandas",
    "mask_geopandas",
    "plot_3D_mask",
    "Regions",
    "set_options",
]

try:
    __version__ = _get_version("regionmask")
except Exception:  # pragma: no cover
    # Local copy or not installed with setuptools.
    # Disable minimum version checks on downstream libraries.
    __version__ = "999"
