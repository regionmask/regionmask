from operator import attrgetter

import pytest

from regionmask import Regions, defined_regions
from regionmask.defined_regions import _maybe_get_column

from . import has_cartopy, requires_cartopy
from .utils import all_defined_regions


@pytest.mark.parametrize(
    "region_name, n_regions", all_defined_regions(return_n=True, return_all=True)
)
def test_defined_region(region_name, n_regions):

    region = attrgetter(region_name)(defined_regions)

    assert isinstance(region, Regions)
    assert len(region) == n_regions

    # currently all regions are -180..180
    assert region.lon_180


@requires_cartopy
def test_natural_earth_loaded_as_utf8():
    # GH 95
    regions = defined_regions.natural_earth.ocean_basins_50
    r = regions[90]

    assert r.name == "Río de la Plata"


def test_maybe_get_column():
    class lowercase:
        @property
        def name(self):
            return 1

    class uppercase:
        @property
        def NAME(self):
            return 2

    assert _maybe_get_column(lowercase(), "name") == 1
    assert _maybe_get_column(uppercase(), "name") == 2
    assert _maybe_get_column(uppercase(), "NAME") == 2

    with pytest.raises(KeyError, match="not on the geopandas dataframe"):
        _maybe_get_column(lowercase, "not_a_column")


@pytest.mark.skipif(has_cartopy, reason="should run if cartopy is _not_ installed")
def test_natural_earth_raises_without_cartopy():

    with pytest.raises(ImportError, match="cartopy is required"):
        defined_regions.natural_earth.countries_110
