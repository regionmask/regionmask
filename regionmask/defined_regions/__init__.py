# flake8: noqa

from . import _natural_earth, _ressources
from ._ar6 import ar6
from ._natural_earth import natural_earth_v4_1_0, natural_earth_v5_0_0
from .giorgi import giorgi
from .prudence import prudence
from .srex import srex


def __getattr__(attr_name):
    # TODO: remove in v0.14.0 or so (added in v0.12.0)

    if attr_name == "natural_earth":
        raise AttributeError(
            "The `natural_earth` regions have been removed. Use ``natural_earth_v4_1_0`` "
            " or ``natural_earth_v5_0_0`` instead."
        )

    raise AttributeError(
        f"module 'regionmask.defined_regions' has no attribute '{attr_name}'"
    )
