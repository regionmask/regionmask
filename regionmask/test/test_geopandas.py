import geopandas as gp
import numpy as np
import pandas as pd
import pytest
import xarray as xr

from regionmask import Regions, from_geopandas, mask_3D_geopandas, mask_geopandas
from regionmask.core._geopandas import (
    _check_duplicates,
    _construct_abbrevs,
    _enumerate_duplicates,
)

from .utils import (
    dummy_lat,
    dummy_ll_dict,
    dummy_lon,
    dummy_outlines_poly,
    expected_mask_2D,
    expected_mask_3D,
)


@pytest.fixture
def geodataframe_clean():

    numbers = [1, 2, 3]
    names = ["Unit Square1", "Unit Square2", "Unit Square3"]
    abbrevs = ["uSq1", "uSq2", "uSq3"]

    d = dict(
        names=names, abbrevs=abbrevs, numbers=numbers, geometry=dummy_outlines_poly
    )

    return gp.GeoDataFrame.from_dict(d)


@pytest.fixture
def geodataframe_missing():

    numbers = [1, None, None]
    names = ["Unit Square1", None, None]
    abbrevs = ["uSq1", None, None]

    d = dict(
        names=names, abbrevs=abbrevs, numbers=numbers, geometry=dummy_outlines_poly
    )

    return gp.GeoDataFrame.from_dict(d)


@pytest.fixture
def geodataframe_duplicates():

    numbers = [1, 1, 1]
    names = ["Unit Square", "Unit Square", "Unit Square"]
    abbrevs = ["uSq", "uSq", "uSq"]

    d = dict(
        names=names, abbrevs=abbrevs, numbers=numbers, geometry=dummy_outlines_poly
    )

    return gp.GeoDataFrame.from_dict(d)


def test_from_geopandas_wrong_input():
    with pytest.raises(
        TypeError, match="`geodataframe` must be a geopandas 'GeoDataFrame'"
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

    assert isinstance(result, Regions)

    assert result.polygons[0].equals(dummy_outlines_poly[0])
    assert result.polygons[1].equals(dummy_outlines_poly[1])
    assert result.polygons[2].equals(dummy_outlines_poly[2])
    assert result.numbers == [1, 2, 3]
    assert result.names == ["Unit Square1", "Unit Square2", "Unit Square3"]
    assert result.abbrevs == ["uSq1", "uSq2", "uSq3"]
    assert result.name == "name"
    assert result.source == "source"


def test_from_geopandas_default(geodataframe_clean):

    result = from_geopandas(geodataframe_clean)

    assert isinstance(result, Regions)

    assert result.polygons[0].equals(dummy_outlines_poly[0])
    assert result.polygons[1].equals(dummy_outlines_poly[1])
    assert result.polygons[2].equals(dummy_outlines_poly[2])
    assert result.numbers == [0, 1, 2]
    assert result.names == ["Region0", "Region1", "Region2"]
    assert result.abbrevs == ["r0", "r1", "r2"]
    assert result.name == "unnamed"
    assert result.source is None


@pytest.mark.parametrize("arg", ["names", "abbrevs", "numbers"])
def test_from_geopandas_missing_error(geodataframe_missing, arg):

    with pytest.raises(
        ValueError, match="{} cannot contain missing values".format(arg)
    ):
        from_geopandas(geodataframe_missing, **{arg: arg})


@pytest.mark.parametrize("arg", ["names", "abbrevs", "numbers"])
def test_from_geopandas_duplicates_error(geodataframe_duplicates, arg):

    with pytest.raises(
        ValueError, match="{} cannot contain duplicate values".format(arg)
    ):
        from_geopandas(geodataframe_duplicates, **{arg: arg})


@pytest.mark.parametrize("arg", ["names", "abbrevs", "numbers"])
def test_from_geopandas_column_missing(geodataframe_clean, arg):

    with pytest.raises(KeyError):
        from_geopandas(geodataframe_clean, **{arg: "not_a_column"})


series_duplicates = pd.Series([1, 1, 2, 3, 4])
series_unique = pd.Series(list(np.arange(2, 5)))


def test_check_duplicates_raise_ValueError():
    with pytest.raises(ValueError):
        _check_duplicates(series_duplicates, "name")


def test_check_duplicates_return_True():
    assert _check_duplicates(series_unique, "name")


def test_construct_abbrevs_wrong_name(geodataframe_clean):
    with pytest.raises(KeyError):
        _construct_abbrevs(geodataframe_clean, "wrong_name")


def test_construct_abbrevs_two_words(geodataframe_clean):
    abbrevs = _construct_abbrevs(geodataframe_clean, "names")
    assert abbrevs[0] == "UniSqu0"
    assert abbrevs[1] == "UniSqu1"
    assert abbrevs[2] == "UniSqu2"


def test_enumerate_duplicates():

    data = pd.Series(["a", "a", "b"])

    result = _enumerate_duplicates(data)
    expected = pd.Series(["a0", "a1", "b"])
    pd.testing.assert_series_equal(result, expected)

    result = _enumerate_duplicates(data, keep="first")
    expected = pd.Series(["a", "a0", "b"])
    pd.testing.assert_series_equal(result, expected)

    result = _enumerate_duplicates(data, keep="last")
    expected = pd.Series(["a0", "a", "b"])
    pd.testing.assert_series_equal(result, expected)


def test_construct_abbrevs():
    strings = ["A", "Bcef", "G[hi]", "J(k)", "L.mn", "Op/Qr", "Stuvw-Xyz"]

    df = pd.DataFrame(strings, columns=["strings"])
    result = _construct_abbrevs(df, "strings")
    expected = ["A", "Bce", "Ghi", "Jk", "Lmn", "OpQr", "StuXyz"]
    for i in range(len(result)):
        assert result[i] == expected[i]


# ==============================================================================
# uses the same function as `Regions.mask` - only do minimal tests here


@pytest.mark.parametrize("lon_lat", [(dummy_lon, dummy_lat), (dummy_ll_dict, None)])
@pytest.mark.parametrize("method", ["rasterize", "shapely"])
def test_mask_geopandas(geodataframe_clean, lon_lat, method):

    lon, lat = lon_lat
    result = mask_geopandas(geodataframe_clean, lon, lat, method=method)
    expected = expected_mask_2D()

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.all(np.equal(result.lat.values, dummy_lat))
    assert np.all(np.equal(result.lon.values, dummy_lon))


@pytest.mark.parametrize("drop", [True, False])
@pytest.mark.parametrize("lon_lat", [(dummy_lon, dummy_lat), (dummy_ll_dict, None)])
@pytest.mark.parametrize("method", ["rasterize", "shapely"])
def test_mask_3D_geopandas(geodataframe_clean, drop, lon_lat, method):

    lon, lat = lon_lat
    result = mask_3D_geopandas(geodataframe_clean, lon, lat, drop=drop, method=method)
    expected = expected_mask_3D(drop=drop)

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.all(np.equal(result.lat.values, dummy_lat))
    assert np.all(np.equal(result.lon.values, dummy_lon))

    numbers = [0, 1] if drop else [0, 1, 2]
    assert np.all(np.equal(result.region.values, numbers))


@pytest.mark.parametrize("method", ["rasterize", "shapely"])
def test_mask_geopandas_numbers(geodataframe_clean, method):

    result = mask_geopandas(
        geodataframe_clean, dummy_lon, dummy_lat, method=method, numbers="numbers"
    )
    expected = expected_mask_2D(1, 2)

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.all(np.equal(result.lat.values, dummy_lat))
    assert np.all(np.equal(result.lon.values, dummy_lon))


@pytest.mark.parametrize("method", ["rasterize", "shapely"])
def test_mask_geopandas_warns_empty(geodataframe_clean, method):

    with pytest.warns(UserWarning, match="No gridpoint belongs to any region."):
        result = mask_geopandas(
            geodataframe_clean, [10, 11], [10, 11], method=method, numbers="numbers"
        )

    assert isinstance(result, xr.DataArray)
    assert result.isnull().all()
    assert np.all(np.equal(result.lat.values, [10, 11]))
    assert np.all(np.equal(result.lon.values, [10, 11]))


@pytest.mark.parametrize("drop", [True, False])
@pytest.mark.parametrize("method", ["rasterize", "shapely"])
def test_mask_3D_geopandas_numbers(geodataframe_clean, drop, method):

    expected = expected_mask_3D(drop)
    result = mask_3D_geopandas(
        geodataframe_clean,
        dummy_lon,
        dummy_lat,
        drop=drop,
        method=method,
        numbers="numbers",
    )

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.all(np.equal(result.lat.values, dummy_lat))
    assert np.all(np.equal(result.lon.values, dummy_lon))

    numbers = geodataframe_clean.numbers[:2] if drop else geodataframe_clean.numbers
    assert np.all(np.equal(result.region.values, numbers))


@pytest.mark.parametrize("drop", [True, False])
def test_mask_3D_geopandas_warns_empty(geodataframe_clean, drop):

    with pytest.warns(UserWarning, match="No gridpoint belongs to any region."):
        result = mask_3D_geopandas(geodataframe_clean, [10], [10], drop=drop)

    assert isinstance(result, xr.DataArray)
    shape = (0, 1, 1) if drop else (3, 1, 1)
    assert result.shape == shape
    assert np.all(np.equal(result.lat.values, [10]))
    assert np.all(np.equal(result.lon.values, [10]))


@pytest.mark.parametrize("func", [mask_geopandas, mask_3D_geopandas])
def test_mask_geopandas_wrong_input(func):

    with pytest.raises(TypeError, match="'GeoDataFrame' or 'GeoSeries'"):
        func(None, dummy_lon, dummy_lat)


@pytest.mark.parametrize("func", [mask_geopandas, mask_3D_geopandas])
def test_mask_geopandas_raises_legacy(geodataframe_clean, func):

    with pytest.raises(ValueError, match="method 'legacy' not supported"):
        func(geodataframe_clean, dummy_lon, dummy_lat, method="legacy")


@pytest.mark.parametrize("func", [mask_geopandas, mask_3D_geopandas])
def test_mask_geopandas_wrong_numbers(geodataframe_clean, func):

    with pytest.raises(KeyError):
        func(geodataframe_clean, dummy_lon, dummy_lat, numbers="not_a_column")


@pytest.mark.parametrize("func", [mask_geopandas, mask_3D_geopandas])
def test_mask_geopandas_missing_error(geodataframe_missing, func):

    with pytest.raises(ValueError, match="cannot contain missing values"):
        func(geodataframe_missing, dummy_lon, dummy_lat, numbers="numbers")


@pytest.mark.parametrize("func", [mask_geopandas, mask_3D_geopandas])
def test_mask_geopandas_duplicates_error(geodataframe_duplicates, func):

    with pytest.raises(ValueError, match="cannot contain duplicate values"):
        func(geodataframe_duplicates, dummy_lon, dummy_lat, numbers="numbers")


@pytest.mark.parametrize("func", [mask_geopandas, mask_3D_geopandas])
def test_raise_on_non_numeric_numbers(geodataframe_clean, func):

    with pytest.raises(ValueError, match="'numbers' must be numeric"):
        func(geodataframe_clean, dummy_lon, dummy_lat, numbers="abbrevs")
