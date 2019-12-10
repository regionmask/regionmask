import numpy as np
import warnings

import regionmask
from regionmask import Regions
from regionmask import create_mask_contains, create_mask_rasterize

import pytest

import xarray as xr
from affine import Affine

from regionmask.core.utils import create_lon_lat_dataarray_from_bounds
from regionmask.core.mask import _transform_from_latlon, _rasterize

# =============================================================================


outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0))
outl2 = ((0, 1), (0, 2), (1, 2.0), (1, 1))
outlines = [outl1, outl2]

r1 = Regions(outlines)

outlines_poly = r1.polygons

lon = [0.5, 1.5]
lat = [0.5, 1.5]

# in this example the result looks:
# a fill
# b fill


def expected_mask(a=0, b=1, fill=np.NaN):
    return np.array([[a, fill], [b, fill]])


@pytest.mark.parametrize(
    "func, outlines",
    [(create_mask_contains, outlines), (create_mask_rasterize, outlines_poly)],
)
def test_create_mask_function(func, outlines):

    # standard
    result = func(lon, lat, outlines)
    expected = expected_mask()
    assert np.allclose(result, expected, equal_nan=True)

    result = func(lon, lat, outlines, fill=5)
    expected = expected_mask(fill=5)
    assert np.allclose(result, expected, equal_nan=True)

    result = func(lon, lat, outlines, numbers=[5, 6])
    expected = expected_mask(a=5, b=6)
    assert np.allclose(result, expected, equal_nan=True)

    with pytest.raises(AssertionError):
        func(lon, lat, outlines, fill=0)

    with pytest.raises(AssertionError):
        func(lon, lat, outlines, numbers=[5])


@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "legacy"])
def test__mask(method):

    expected = expected_mask()
    result = r1.mask(lon, lat, method=method, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)


@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "legacy"])
def test__mask_xarray(method):

    expected = expected_mask()
    result = r1.mask(lon, lat, method=method, xarray=True)

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.allclose(result.lat, lat)
    assert np.allclose(result.lon, lon)


@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "legacy"])
def test__mask_xarray_name(method):

    msk = r1.mask(lon, lat, method=method, xarray=True)

    assert msk.name == "region"


@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "legacy"])
def test__mask_obj(method):

    expected = expected_mask()

    obj = dict(lon=lon, lat=lat)
    result = r1.mask(obj, method=method, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)

    obj = dict(longitude=lon, latitude=lat)
    result = r1.mask(obj, lon_name="longitude", lat_name="latitude", xarray=False)

    assert np.allclose(result, expected, equal_nan=True)


@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "legacy"])
def test_mask_wrap(method):

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

    result = r.mask(lon, lat, method=method, xarray=False, wrap_lon=False)
    assert np.all(np.isnan(result))

    # this is the wron wrapping
    result = r.mask(lon, lat, method=method, xarray=False, wrap_lon=180)
    assert np.all(np.isnan(result))

    expected = expected_mask()

    # determine the wrap automatically
    result = r.mask(lon, lat, method=method, xarray=False, wrap_lon=True)
    assert np.allclose(result, expected, equal_nan=True)

    # determine the wrap by hand
    result = r.mask(lon, lat, method=method, xarray=False, wrap_lon=360)
    assert np.allclose(result, expected, equal_nan=True)


@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "legacy"])
def test_mask_autowrap(method):

    expected = expected_mask()

    # create a test case where the outlines and the lon coordinates
    # are different - or the same - should work either way

    # 1. -180..180 regions and -180..180 lon
    lon = [0.5, 1.5]
    lat = [0.5, 1.5]
    result = r1.mask(lon, lat, method=method, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)

    # 2. -180..180 regions and 0..360 lon
    # outline -180..180
    outl1 = ((-180, 0), (-180, 1), (-1, 1.0), (-1, 0))
    outl2 = ((-180, 1), (-180, 2), (-1, 2.0), (-1, 1))
    outlines = [outl1, outl2]

    r = Regions(outlines)

    # lon -180..179.9
    lon = [358.5, 359.5]
    lat = [0.5, 1.5]

    result = r.mask(lon, lat, method=method, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)

    # 3. 0..360 regions and -180..180 lon

    # outline 0..359.9
    outl1 = ((359, 0), (359, 1), (0, 1.0), (0, 0))
    outl2 = ((359, 1), (359, 2), (0, 2.0), (0, 1))
    outlines = [outl1, outl2]

    r = Regions(outlines)

    # lon -180..179.9
    lon = [-1.5, -0.5]
    lat = [0.5, 1.5]

    result = r.mask(lon, lat, method=method, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)

    # 3. 0..360 regions and 0..360 lon

    # lon 0..359.9
    lon = [0.5, 359.5]
    lat = [0.5, 1.5]

    result = r.mask(lon, lat, method=method, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)


# ======================================================================

# test 2D array
lon_2D = [[0.5, 1.5], [0.5, 1.5]]
lat_2D = [[0.5, 0.5], [1.5, 1.5]]


def test_create_mask_contains_2D():
    result = create_mask_contains(lon_2D, lat_2D, outlines)
    expected = expected_mask()
    assert np.allclose(result, expected, equal_nan=True)


@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
def test_mask_2D():

    expected = expected_mask()
    result = r1.mask(lon_2D, lat_2D, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)


@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
def test__mask_xarray_out_2D():

    expected = expected_mask()
    result = r1.mask(lon_2D, lat_2D, xarray=True)

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)

    assert np.allclose(result.lat.values, lat_2D)
    assert np.allclose(result.lon.values, lon_2D)

    assert np.allclose(result.lat_idx, [0, 1])
    assert np.allclose(result.lon_idx, [0, 1])


@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("lon", [lon_2D, [0, 1, 3], 0])
@pytest.mark.parametrize("lat", [lat_2D, [0, 1, 3], 0])
@pytest.mark.parametrize("xarray", [None, True, False])
def test_mask_rasterize_irrecular(lon, lat, xarray):

    with pytest.raises(ValueError, match="`lat` and `lon` must be equally spaced"):
        result = r1.mask(lon, lat, method="rasterize", xarray=xarray)


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


@pytest.mark.parametrize("xarray", [True, False])
def test_xarray_keyword_deprection_warning(xarray):

    with pytest.warns(FutureWarning, match="Passing the `xarray` keyword"):
        r1.mask(lon, lat, xarray=xarray)


@pytest.mark.parametrize("lon_start", [0, 1, -5])
@pytest.mark.parametrize("dlon", [1, 2])
@pytest.mark.parametrize("lat_start", [0, 1, -5])
@pytest.mark.parametrize("dlat", [1, 2])
def test_transform_from_latlon(lon_start, dlon, lat_start, dlat):

    lon = np.arange(lon_start, 20, dlon)
    lat = np.arange(lat_start, 20, dlat)

    r = _transform_from_latlon(lon, lat)

    assert isinstance(r, Affine)

    expected = np.array(
        [dlon, 0, lon_start - dlon / 2, 0, dlat, lat_start - dlat / 2, 0, 0, 1]
    )

    assert np.allclose(np.array(r), expected)


@pytest.mark.parametrize("a, b", [(0, 1), (4, 5)])
@pytest.mark.parametrize("fill", [np.NaN, 3])
def test_rasterize(a, b, fill):

    expected = expected_mask(a=a, b=b, fill=fill)

    shapes = zip(outlines_poly, [a, b])
    result = _rasterize(shapes, lon, lat, fill=fill)

    assert np.allclose(result, expected, equal_nan=True)
