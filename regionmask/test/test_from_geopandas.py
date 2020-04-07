import geopandas as gp
import numpy as np
import pandas as pd
import pytest

from shapely.geometry import Polygon

import regionmask
from regionmask.defined_regions.from_geopandas import (
    _check_duplicates,
    _construct_abbrevs,
    from_geopandas
)

# create dummy Polygons for testing
poly1 = Polygon(((0, 0), (0, 1), (1, 1.0), (1, 0)))
poly2 = Polygon(((0, 1), (0, 2), (1, 2.0), (1, 1)))
geometries = [poly1, poly2]


@pytest.fixture
def geodataframe_clean():

    numbers = [1, 2]
    names = ["Unit Square1", "Unit Square2"]
    abbrevs = ["uSq1", "uSq2"]

    d = dict(names=names, abbrevs=abbrevs, numbers=numbers, geometry=geometries)

    return gp.GeoDataFrame.from_dict(d)


@pytest.fixture
def geodataframe_missing():

    numbers = [1, None]
    names = ["Unit Square1", None]
    abbrevs = ["uSq1", None]

    d = dict(names=names, abbrevs=abbrevs, numbers=numbers, geometry=geometries)

    return gp.GeoDataFrame.from_dict(d)


@pytest.fixture
def geodataframe_duplicates():

    numbers = [1, 1.1]
    names = ["Unit Square", "Unit Square"]
    abbrevs = ["uSq1", "uSq1"]

    d = dict(names=names, abbrevs=abbrevs, numbers=numbers, geometry=geometries)

    return gp.GeoDataFrame.from_dict(d)


def test_from_geopandas_wrong_input():

    with pytest.raises(
        ValueError, match="'geodataframe' must be a geopandas.GeoDataFrame"
    ):
        from_geopandas(None)


def test_from_geopandas_use_columns(geodataframe_clean):

    result = from_geopandas(
        geodataframe_clean,
        numbers="numbers",
        names="names",
        abbrevs="abbrevs",
        name="name",
        source="source",
    )

    assert isinstance(result, regionmask.core.regions.Regions)

    assert result.polygons[0].equals(poly1)
    assert result.polygons[1].equals(poly2)
    assert result.numbers == [1, 2]
    assert result.names == ["Unit Square1", "Unit Square2"]
    assert result.abbrevs == ["uSq1", "uSq2"]
    assert result.name == "name"
    assert result.source == "source"


def test_from_geopandas_default(geodataframe_clean):

    # note: you can just pass None to Regions
    result = from_geopandas(geodataframe_clean)

    assert isinstance(result, regionmask.core.regions.Regions)

    assert result.polygons[0].equals(poly1)
    assert result.polygons[1].equals(poly2)
    assert result.numbers == [0, 1]
    assert result.names == ["Region0", "Region1"]
    assert result.abbrevs == ["r0", "r1"]
    assert result.name == "unnamed"
    assert result.source is None


@pytest.mark.parametrize("arg", ["names", "abbrevs", "numbers"])
def test_from_geopandas_missing_error(geodataframe_missing, arg):

    with pytest.raises(
        ValueError, match="{arg} cannot contain missing values".format(arg)
    ):
        from_geopandas(geodataframe_missing, **{arg: arg})


@pytest.mark.parametrize("arg", ["names", "abbrevs", "numbers"])
def test_from_geopandas_duplicates_error(geodataframe_duplicates, arg):

    with pytest.raises(
        ValueError, match="{arg} cannot contain duplicate values".format(arg)
    ):
        from_geopandas(geodataframe_duplicates, **{arg: arg})


list_duplicates = [1, 1, 2, 3, 4]
list_unique = list(np.arange(2, 5))


@pytest.mark.parametrize(
    "to_check",
    [list_duplicates, pd.Series(list_duplicates), np.array(list_duplicates)],
    ids=["list", "pd.Series", "np.array"],
)
def test_check_duplicates_raise_ValueError(to_check):
    with pytest.raises(ValueError):
        _check_duplicates(to_check)


@pytest.mark.parametrize(
    "to_check", [list_unique, pd.Series(list_unique)], ids=["list", "pd.Series"]
)
def test_check_duplicates_return_True(to_check):
    assert _check_duplicates(to_check)


def test_construct_abbrevs(geodataframe_clean):
    _construct_abbrevs(geodataframe_clean, "names")