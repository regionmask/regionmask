# -*- coding: utf-8 -*-

from pytest import raises

from regionmask import Regions, defined_regions
from regionmask.defined_regions import _maybe_get_column


def _defined_region(regions, n_regions):

    assert isinstance(regions, Regions)
    assert len(regions) == n_regions

    # currently all regions are -180..180
    assert regions.lon_180


def test_giorgi():
    regions = defined_regions.giorgi
    _defined_region(regions, 21)


def test_srex():
    regions = defined_regions.srex
    _defined_region(regions, 26)


def test_countries_110():
    regions = defined_regions.natural_earth.countries_110
    _defined_region(regions, 177)


def test_countries_50():
    regions = defined_regions.natural_earth.countries_50
    _defined_region(regions, 241)


def test_us_states_50():
    regions = defined_regions.natural_earth.us_states_50
    _defined_region(regions, 51)


def test_us_states_10():
    regions = defined_regions.natural_earth.us_states_10
    _defined_region(regions, 51)


def test_land_110():
    regions = defined_regions.natural_earth.land_110
    _defined_region(regions, 1)


def test_ocean_basins_50():
    regions = defined_regions.natural_earth.ocean_basins_50
    _defined_region(regions, 119)


def test_natural_earth_loaded_as_utf8():
    # GH 95
    regions = defined_regions.natural_earth.ocean_basins_50
    r = regions[90]

    assert r.name == u"Río de la Plata"


def test_ar6():
    regions = defined_regions.ar6.all
    _defined_region(regions, 58)


def test_ar6_land():
    regions = defined_regions.ar6.land
    _defined_region(regions, 46)


def test_ar6_ocean():
    regions = defined_regions.ar6.ocean
    _defined_region(regions, 15)


def test_ar6_pre_revisions():
    regions = defined_regions._ar6_pre_revisions.all
    _defined_region(regions, 55)


def test_ar6_pre_revisions_land():
    regions = defined_regions._ar6_pre_revisions.land
    _defined_region(regions, 43)


def test_ar6_pre_revisions_ocean():
    regions = defined_regions._ar6_pre_revisions.ocean
    _defined_region(regions, 12)


def test_ar6_pre_revisions_separate_pacific():
    regions = defined_regions._ar6_pre_revisions.separate_pacific
    _defined_region(regions, 58)


def test_maybe_get_column():
    class lowercase(object):
        @property
        def name(self):
            return 1

    class uppercase(object):
        @property
        def NAME(self):
            return 2

    assert _maybe_get_column(lowercase(), "name") == 1
    assert _maybe_get_column(uppercase(), "name") == 2
    assert _maybe_get_column(uppercase(), "NAME") == 2

    with raises(KeyError, match="not on the geopandas dataframe"):
        _maybe_get_column(lowercase, "not_a_column")
