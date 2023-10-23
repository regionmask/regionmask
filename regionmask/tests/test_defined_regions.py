from operator import attrgetter

import numpy as np
import pytest

from regionmask import Regions, defined_regions
from regionmask.defined_regions._natural_earth import _maybe_get_column

from . import requires_cartopy
from .utils import REGIONS_ALL


def _test_region(defined_region):

    region = attrgetter(defined_region.region_name)(defined_regions)

    assert isinstance(region, Regions)
    assert len(region) == defined_region.n_regions

    assert region.overlap is defined_region.overlap

    # currently all regions are -180..180
    assert region.lon_180

    if defined_region.bounds is not None:
        np.testing.assert_allclose(defined_region.bounds, region.bounds_global)


@pytest.mark.parametrize("defined_region", REGIONS_ALL, ids=str)
def test_defined_region(defined_region):

    _test_region(defined_region)


def test_defined_regions_natural_earth_informative_error():

    with pytest.raises(
        AttributeError, match="The `natural_earth` regions have been removed."
    ):
        defined_regions.natural_earth


def test_defined_regions_attribute_error():

    with pytest.raises(
        AttributeError,
        match="module 'regionmask.defined_regions' has no attribute 'attr'",
    ):
        defined_regions.attr


def test_fix_ocean_basins_50():

    region = defined_regions.natural_earth_v4_1_0.ocean_basins_50
    assert "Mediterranean Sea Eastern Basin" in region.names
    assert "Ross Sea Eastern Basin" in region.names

    region = defined_regions.natural_earth_v5_0_0.ocean_basins_50
    assert "Mediterranean Sea" in region.names
    assert "Ross Sea" in region.names


@requires_cartopy
def test_natural_earth_loaded_as_utf8():
    # GH 95

    region = defined_regions.natural_earth_v5_0_0.ocean_basins_50

    assert "Río de la Plata" in region.names


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
