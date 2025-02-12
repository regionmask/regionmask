from regionmask.defined_regions import _natural_earth, _resources
from regionmask.defined_regions._ar6 import ar6
from regionmask.defined_regions._natural_earth import (
    natural_earth_v4_1_0,
    natural_earth_v5_0_0,
    natural_earth_v5_1_2,
)
from regionmask.defined_regions.giorgi import giorgi
from regionmask.defined_regions.prudence import prudence
from regionmask.defined_regions.srex import srex

__all__ = [
    "_natural_earth",
    "_resources",
    "ar6",
    "natural_earth_v4_1_0",
    "natural_earth_v5_0_0",
    "natural_earth_v5_1_2",
    "giorgi",
    "prudence",
    "srex",
]


def __getattr__(attr_name):
    # TODO: remove in v0.14.0 or so (added in v0.12.0)

    if attr_name == "natural_earth":
        raise AttributeError(
            "The `natural_earth` regions have been removed. Use"
            " ``natural_earth_v4_1_0``  or ``natural_earth_v5_0_0`` instead."
        )

    raise AttributeError(
        f"module 'regionmask.defined_regions' has no attribute '{attr_name}'"
    )
