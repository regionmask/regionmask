import numpy as np

from regionmask import Regions
from regionmask import create_mask_contains

from pytest import raises

import xarray as xr

# =============================================================================


outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0))
outl2 = ((0, 1), (0, 2), (1, 2.0), (1, 1))
outlines = [outl1, outl2]

r1 = Regions(outlines)


lon = [0.5, 1.5]
lat = [0.5, 1.5]

# in this example the result looks:
# a fill
# b fill


def expected_mask(a=0, b=1, fill=np.NaN):
    return np.array([[a, fill], [b, fill]])


def test_create_mask_contains():

    # standard
    result = create_mask_contains(lon, lat, outlines)
    expected = expected_mask()
    assert np.allclose(result, expected, equal_nan=True)

    result = create_mask_contains(lon, lat, outlines, fill=5)
    expected = expected_mask(fill=5)
    assert np.allclose(result, expected, equal_nan=True)

    result = create_mask_contains(lon, lat, outlines, numbers=[5, 6])
    expected = expected_mask(a=5, b=6)
    assert np.allclose(result, expected, equal_nan=True)

    raises(AssertionError, create_mask_contains, lon, lat, outlines, fill=0)

    raises(AssertionError, create_mask_contains, lon, lat, outlines, numbers=[5])


def test__mask():

    expected = expected_mask()
    result = r1.mask(lon, lat, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)


def test__mask_xarray():

    expected = expected_mask()
    result = r1.mask(lon, lat, xarray=True)

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.allclose(result.lat, lat)
    assert np.allclose(result.lon, lon)


def test__mask_xarray_name():
    msk = r1.mask(lon, lat, xarray=True)

    assert msk.name == "region"


def test__mask_obj():

    expected = expected_mask()

    obj = dict(lon=lon, lat=lat)
    result = r1.mask(obj, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)

    obj = dict(longitude=lon, latitude=lat)
    result = r1.mask(obj, lon_name="longitude", lat_name="latitude", xarray=False)

    assert np.allclose(result, expected, equal_nan=True)


def test_mask_wrap():

    # create a test case where the outlines and the lon coordinates
    # are different

    # outline 0..359.9
    outl1 = ((359, 0), (359, 1), (0, 1.0), (0, 0))
    outl2 = ((359, 1), (359, 2), (0, 2.0), (0, 1))
    outlines = [outl1, outl2]

    r = Regions(outlines)

    # lon -180..179.9
    lon = [-1.5, -0.5]
    lat = [0.5, 1.5]

    result = r.mask(lon, lat, xarray=False)
    assert np.all(np.isnan(result))

    # this is the wron wrapping
    result = r.mask(lon, lat, xarray=False, wrap_lon=180)
    assert np.all(np.isnan(result))

    expected = expected_mask()

    # determine the wrap automatically
    result = r.mask(lon, lat, xarray=False, wrap_lon=True)
    assert np.allclose(result, expected, equal_nan=True)

    # determine the wrap by hand
    result = r.mask(lon, lat, xarray=False, wrap_lon=360)
    assert np.allclose(result, expected, equal_nan=True)


# ======================================================================

# test 2D array
lon_2D = [[0.5, 1.5], [0.5, 1.5]]
lat_2D = [[0.5, 0.5], [1.5, 1.5]]


def test_create_mask_contains_2D():
    result = create_mask_contains(lon_2D, lat_2D, outlines)
    expected = expected_mask()
    assert np.allclose(result, expected, equal_nan=True)


def test__mask_2D():

    expected = expected_mask()
    result = r1.mask(lon_2D, lat_2D, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)


def test__mask_xarray_out_2D():

    expected = expected_mask()
    result = r1.mask(lon_2D, lat_2D, xarray=True)

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)

    assert np.allclose(result.lat.values, lat_2D)
    assert np.allclose(result.lon.values, lon_2D)

    assert np.allclose(result.lat_idx, [0, 1])
    assert np.allclose(result.lon_idx, [0, 1])


def test__mask_xarray_in_out_2D():
    # create xarray DataArray with 2D dims

    coords = {
        "lat_1D": [1, 2],
        "lon_1D": [1, 2],
        "lat_2D": (("lat_1D", "lon_1D"), lat_2D),
        "lon_2D": (("lat_1D", "lon_1D"), lon_2D),
    }

    d = np.random.rand(2, 2)

    data = xr.DataArray(d, coords=coords, dims=("lat_1D", "lon_1D"))

    expected = expected_mask()
    result = r1.mask(data, lon_name="lon_2D", lat_name="lat_2D")

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.allclose(result.lat_2D, lat_2D)
    assert np.allclose(result.lon_2D, lon_2D)

    assert np.allclose(result.lat_1D, [1, 2])
    assert np.allclose(result.lon_1D, [1, 2])
