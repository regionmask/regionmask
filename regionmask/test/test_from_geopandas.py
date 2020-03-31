import geopandas
import numpy as np
import pandas as pd
import pytest

import regionmask
from regionmask.defined_regions.from_geopandas import (
    _check_duplicates,
    _construct_abbrevs,
)


@pytest.fixture
def MEOW_geodataframe():
    return geopandas.read_file('http://maps.tnc.org/files/shp/MEOW-TNC.zip')


source = 'http://maps.tnc.org/gis_data.html'
name = 'MEOW'


def test_from_geopandas_is_region(MEOW_geodataframe):
    region = regionmask.from_geopandas(MEOW_geodataframe,
                                       numbers=None,
                                       names='ECOREGION',
                                       abbrevs='construct',
                                       name=name,
                                       source=source)
    assert isinstance(region, regionmask.core.regions.Regions)


def test_from_geopandas_is_region_provide_numbers(MEOW_geodataframe):
    region = regionmask.from_geopandas(MEOW_geodataframe,
                                       numbers='ECO_CODE_X',
                                       names='ECOREGION',
                                       abbrevs='construct',
                                       name=name,
                                       source=source)
    assert isinstance(region, regionmask.core.regions.Regions)


@pytest.mark.xfail
def test_from_geopandas_fail_no_abbrevs(MEOW_geodataframe):
    regionmask.from_geopandas(MEOW_geodataframe,
                              numbers=None,
                              names='ECOREGION',
                              abbrevs=None,
                              name=name,
                              source=source)


@pytest.mark.xfail
def test_from_geopandas_fail_no_names(MEOW_geodataframe):
    regionmask.from_geopandas(MEOW_geodataframe,
                              numbers=None,
                              names=None,
                              abbrevs='construct',
                              name=name,
                              source=source)


my_list = [1, 1, 2, 3, 4]


@pytest.mark.parametrize("to_check",
                         [my_list, pd.Series(my_list)],
                         ids=["list", "pd.Series"])
def test_check_duplicates_raise_ValueError(to_check):
    with pytest.raises(ValueError):
        _check_duplicates(to_check)


my_list = list(np.arange(2, 5))


@pytest.mark.parametrize("to_check",
                         [my_list, pd.Series(my_list)],
                         ids=["list", "pd.Series"])
def test_check_duplicates_return_True(to_check):
    assert _check_duplicates(to_check)


def test_construct_abbrevs_unique(MEOW_geodataframe):
    abbrevs = _construct_abbrevs(MEOW_geodataframe, 'ECOREGION')
    assert _check_duplicates(abbrevs)
