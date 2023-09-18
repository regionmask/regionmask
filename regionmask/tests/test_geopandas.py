import geopandas as gp
import numpy as np
import pandas as pd
import pytest
import shapely
import xarray as xr

from regionmask import Regions, from_geopandas, mask_3D_geopandas, mask_geopandas
from regionmask.core._geopandas import (
    _check_duplicates,
    _construct_abbrevs,
    _enumerate_duplicates,
)

from . import requires_cf_xarray
from .utils import (
    dummy_ds,
    dummy_ds_cf,
    dummy_region,
    dummy_region_overlap,
    expected_mask_2D,
    expected_mask_3D,
)


@pytest.fixture
def geodataframe_clean():

    numbers = [0, 1, 2]
    names = ["Unit Square1", "Unit Square2", "Unit Square3"]
    abbrevs = ["uSq1", "uSq2", "uSq3"]

    d = dict(
        names=names, abbrevs=abbrevs, numbers=numbers, geometry=dummy_region.polygons
    )

    return gp.GeoDataFrame.from_dict(d)


@pytest.fixture
def geodataframe_clean_overlap():

    d = dict(
        names=dummy_region_overlap.names,
        abbrevs=dummy_region_overlap.abbrevs,
        numbers=dummy_region_overlap.numbers,
        geometry=dummy_region_overlap.polygons,
    )

    return gp.GeoDataFrame.from_dict(d)


@pytest.fixture
def geodataframe_missing():

    numbers = [1, None, None]
    names = ["Unit Square1", None, None]
    abbrevs = ["uSq1", None, None]

    d = dict(
        names=names, abbrevs=abbrevs, numbers=numbers, geometry=dummy_region.polygons
    )

    return gp.GeoDataFrame.from_dict(d)


@pytest.fixture
def geodataframe_duplicates():

    numbers = [1, 1, 1]
    names = ["Unit Square", "Unit Square", "Unit Square"]
    abbrevs = ["uSq", "uSq", "uSq"]

    d = dict(
        names=names, abbrevs=abbrevs, numbers=numbers, geometry=dummy_region.polygons
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

    assert result.polygons[0].equals(dummy_region.polygons[0])
    assert result.polygons[1].equals(dummy_region.polygons[1])
    assert result.polygons[2].equals(dummy_region.polygons[2])
    assert result.numbers == [0, 1, 2]
    assert result.names == ["Unit Square1", "Unit Square2", "Unit Square3"]
    assert result.abbrevs == ["uSq1", "uSq2", "uSq3"]
    assert result.name == "name"
    assert result.source == "source"


@pytest.mark.parametrize("attr", ["name", "source", "overlap"])
def test_from_geopandas_not_roundtrip_warning(attr, geodataframe_clean):

    geodataframe_clean.attrs = {attr: "x"}

    with pytest.warns(
        UserWarning,
        match="Use ``regionmask.Regions.from_geodataframe`` to round-trip ``Regions``",
    ):
        from_geopandas(geodataframe_clean)


def test_from_geopandas_default(geodataframe_clean):

    result = from_geopandas(geodataframe_clean)

    assert isinstance(result, Regions)

    assert result.polygons[0].equals(dummy_region.polygons[0])
    assert result.polygons[1].equals(dummy_region.polygons[1])
    assert result.polygons[2].equals(dummy_region.polygons[2])
    assert result.numbers == [0, 1, 2]
    assert result.names == ["Region0", "Region1", "Region2"]
    assert result.abbrevs == ["r0", "r1", "r2"]
    assert result.name == "unnamed"
    assert result.source is None


@pytest.mark.parametrize("arg", ["names", "abbrevs", "numbers"])
def test_from_geopandas_missing_error(geodataframe_missing, arg):

    with pytest.raises(ValueError, match=f"{arg} cannot contain missing values"):
        from_geopandas(geodataframe_missing, **{arg: arg})


@pytest.mark.parametrize("arg", ["names", "abbrevs", "numbers"])
def test_from_geopandas_duplicates_error(geodataframe_duplicates, arg):

    with pytest.raises(ValueError, match=f"{arg} cannot contain duplicate values"):
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


@pytest.mark.parametrize("lon_lat", [(dummy_ds.lon, dummy_ds.lat), (dummy_ds, None)])
@pytest.mark.parametrize("method", ["rasterize", "shapely"])
def test_mask_geopandas(geodataframe_clean, lon_lat, method):

    lon, lat = lon_lat
    result = mask_geopandas(geodataframe_clean, lon, lat, method=method)
    expected = expected_mask_2D()

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("drop", [True, False])
@pytest.mark.parametrize("lon_lat", [(dummy_ds.lon, dummy_ds.lat), (dummy_ds, None)])
@pytest.mark.parametrize("method", ["rasterize", "shapely"])
def test_mask_3D_geopandas(geodataframe_clean, drop, lon_lat, method):

    lon, lat = lon_lat
    result = mask_3D_geopandas(geodataframe_clean, lon, lat, drop=drop, method=method)
    expected = expected_mask_3D(drop=drop).drop_vars(["names", "abbrevs"])

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("method", ["rasterize", "shapely"])
def test_mask_geopandas_numbers(geodataframe_clean, method):

    result = mask_geopandas(
        geodataframe_clean, dummy_ds.lon, dummy_ds.lat, method=method, numbers="numbers"
    )
    expected = expected_mask_2D()

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("method", ["rasterize", "shapely"])
def test_mask_geopandas_warns_empty(geodataframe_clean, method):

    lon = lat = [10, 11]
    with pytest.warns(UserWarning, match="No gridpoint belongs to any region."):
        result = mask_geopandas(
            geodataframe_clean, lon, lat, method=method, numbers="numbers"
        )

    expected = expected_mask_2D(coords={"lon": lon, "lat": lat})

    xr.testing.assert_equal(result, expected * np.nan)


@pytest.mark.parametrize("drop", [True, False])
@pytest.mark.parametrize("method", ["rasterize", "shapely"])
def test_mask_3D_geopandas_numbers(geodataframe_clean, drop, method):

    expected = expected_mask_3D(drop).drop_vars(["names", "abbrevs"])
    result = mask_3D_geopandas(
        geodataframe_clean,
        dummy_ds.lon,
        dummy_ds.lat,
        drop=drop,
        method=method,
        numbers="numbers",
    )

    xr.testing.assert_equal(result, expected)


@pytest.mark.filterwarnings("ignore:Detected overlapping regions")
@pytest.mark.parametrize("drop", [True, False])
@pytest.mark.parametrize("method", ["rasterize", "shapely"])
@pytest.mark.parametrize("overlap", [True, None])
def test_mask_3D_geopandas_overlap(geodataframe_clean_overlap, drop, method, overlap):

    expected = expected_mask_3D(drop, overlap=True).drop_vars(["names", "abbrevs"])
    result = mask_3D_geopandas(
        geodataframe_clean_overlap,
        dummy_ds.lon,
        dummy_ds.lat,
        drop=drop,
        method=method,
        numbers="numbers",
        overlap=overlap,
    )

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("drop", [True, False])
@pytest.mark.parametrize("method", ["rasterize", "shapely"])
def test_mask_3D_geopandas_overlap_false(geodataframe_clean_overlap, drop, method):

    # NOTE: we need to adapt the expected da
    expected = expected_mask_3D(drop, overlap=True).drop_vars(["names", "abbrevs"])
    result = mask_3D_geopandas(
        geodataframe_clean_overlap,
        dummy_ds.lon,
        dummy_ds.lat,
        drop=drop,
        method=method,
        numbers="numbers",
        overlap=False,
    )

    if drop:
        expected = expected.drop_isel(region=0)
    else:
        expected[{"region": 0}] = False

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("method", ["rasterize", "shapely"])
@pytest.mark.parametrize("overlap", [None, True])
def test_mask_2D_geopandas_overlap(geodataframe_clean_overlap, method, overlap):

    # overlap None / True raises a different error
    with pytest.raises(ValueError):
        mask_geopandas(
            geodataframe_clean_overlap,
            dummy_ds.lon,
            dummy_ds.lat,
            method=method,
            numbers="numbers",
            overlap=overlap,
        )


@pytest.mark.parametrize("drop", [True, False])
def test_mask_3D_geopandas_warns_empty(geodataframe_clean, drop):

    lon = lat = [10, 11]
    with pytest.warns(UserWarning, match="No gridpoint belongs to any region."):
        result = mask_3D_geopandas(geodataframe_clean, lon, lat, drop=drop)

    coords = {"lat": lat, "lon": lon}
    expected = expected_mask_3D(False, coords=coords).drop_vars(["names", "abbrevs"])
    expected = expected.isel(region=slice(0, 0)) if drop else expected

    xr.testing.assert_equal(result, expected * False)


@pytest.mark.parametrize("func", [mask_geopandas, mask_3D_geopandas])
def test_wrap_lon_maybe_error(func):

    # regions that exceed 360° longitude
    p = shapely.geometry.Polygon([[-180, 0], [-180, 10], [360, 10], [360, 0]])
    gs = gp.GeoSeries(p, index=[1])
    # lons that exceed 360° longitude
    lon = np.arange(-175, 360, 2.5)
    lat = np.arange(10, 1, -3)

    mask = func(gs, lon, lat, wrap_lon=False)

    # the region index is 1 -> thus this works for 2D and 3D masks
    assert (mask == 1).all()
    np.testing.assert_equal(lon, mask.lon)
    np.testing.assert_equal(lat, mask.lat)

    with pytest.raises(ValueError, match="Set `wrap_lon=False` to skip this check."):
        func(gs, lon, lat)


@pytest.mark.parametrize("func", [mask_geopandas, mask_3D_geopandas])
def test_mask_geopandas_wrong_input(func):

    with pytest.raises(TypeError, match="'GeoDataFrame' or 'GeoSeries'"):
        func(None, dummy_ds.lon, dummy_ds.lat)


@pytest.mark.parametrize("func", [mask_geopandas, mask_3D_geopandas])
def test_mask_geopandas_wrong_numbers(geodataframe_clean, func):

    with pytest.raises(KeyError):
        func(geodataframe_clean, dummy_ds.lon, dummy_ds.lat, numbers="not_a_column")


@pytest.mark.parametrize("func", [mask_geopandas, mask_3D_geopandas])
def test_mask_geopandas_missing_error(geodataframe_missing, func):

    with pytest.raises(ValueError, match="cannot contain missing values"):
        func(geodataframe_missing, dummy_ds.lon, dummy_ds.lat, numbers="numbers")


@pytest.mark.parametrize("func", [mask_geopandas, mask_3D_geopandas])
def test_mask_geopandas_duplicates_error(geodataframe_duplicates, func):

    with pytest.raises(ValueError, match="cannot contain duplicate values"):
        func(geodataframe_duplicates, dummy_ds.lon, dummy_ds.lat, numbers="numbers")


@pytest.mark.parametrize("func", [mask_geopandas, mask_3D_geopandas])
def test_raise_on_non_numeric_numbers(geodataframe_clean, func):

    with pytest.raises(ValueError, match="'numbers' must be numeric"):
        func(geodataframe_clean, dummy_ds.lon, dummy_ds.lat, numbers="abbrevs")


@requires_cf_xarray
@pytest.mark.parametrize("use_cf", (True, None))
def test_mask_use_cf_mask_2D(geodataframe_clean, use_cf):

    result = mask_geopandas(geodataframe_clean, dummy_ds_cf, use_cf=use_cf)

    expected = expected_mask_2D(lon_name="longitude", lat_name="latitude")
    xr.testing.assert_equal(result, expected)


@requires_cf_xarray
@pytest.mark.parametrize("use_cf", (True, None))
def test_mask_use_cf_mask_3D(geodataframe_clean, use_cf):

    result = mask_3D_geopandas(geodataframe_clean, dummy_ds_cf, use_cf=use_cf)

    expected = expected_mask_3D(drop=True, lon_name="longitude", lat_name="latitude")
    expected = expected.drop_vars(["names", "abbrevs"])
    xr.testing.assert_equal(result, expected)
