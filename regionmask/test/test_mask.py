import numpy as np
import pytest
import xarray as xr
from affine import Affine
from shapely.geometry import Polygon

from regionmask import Regions, create_mask_contains
from regionmask.core.mask import (
    _mask_rasterize,
    _mask_rasterize_no_offset,
    _mask_shapely,
    _transform_from_latlon,
)
from regionmask.core.utils import create_lon_lat_dataarray_from_bounds

# =============================================================================


outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0))
outl2 = ((0, 1), (0, 2), (1, 2.0), (1, 1))
outlines = [outl1, outl2]

r1 = Regions(outlines)

outlines_poly = r1.polygons

lon = [0.5, 1.5]
lat = [0.5, 1.5]

# in this example the result looks:
# | a fill |
# | b fill |


def expected_mask(a=0, b=1, fill=np.NaN):
    return np.array([[a, fill], [b, fill]])


@pytest.mark.filterwarnings("ignore:The function `create_mask_contains` is deprecated")
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

    with pytest.raises(AssertionError):
        create_mask_contains(lon, lat, outlines, fill=0)

    with pytest.raises(AssertionError):
        create_mask_contains(lon, lat, outlines, numbers=[5])


def test_create_mask_contains_warns():

    with pytest.warns(
        FutureWarning, match="The function `create_mask_contains` is deprecated"
    ):
        create_mask_contains(lon, lat, outlines)


@pytest.mark.parametrize("func", [_mask_rasterize, _mask_shapely])
def test_mask_func(func):

    # standard
    result = func(lon, lat, outlines_poly, numbers=[0, 1])
    expected = expected_mask()
    assert np.allclose(result, expected, equal_nan=True)

    result = func(lon, lat, outlines_poly, numbers=[0, 1], fill=5)
    expected = expected_mask(fill=5)
    assert np.allclose(result, expected, equal_nan=True)

    result = func(lon, lat, outlines_poly, numbers=[5, 6])
    expected = expected_mask(a=5, b=6)
    assert np.allclose(result, expected, equal_nan=True)


def test_mask_shapely_wrong_number_fill():

    with pytest.raises(AssertionError):
        _mask_shapely(lon, lat, outlines_poly, numbers=[0, 1], fill=0)

    with pytest.raises(AssertionError):
        _mask_shapely(lon, lat, outlines, numbers=[5])


@pytest.mark.xfail(reason="Not implemented")
@pytest.mark.parametrize("numbers, fill", [[[0, 1], [0]], [[0], [np.NaN]]])
def test_mask_rasterize_wrong_number_fill(numbers, fill):

    with pytest.raises(AssertionError):
        _mask_rasterize(lon, lat, outlines_poly, numbers=numbers, fill=fill)


@pytest.mark.filterwarnings("ignore:The method 'legacy' will be removed")
@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "legacy", "shapely"])
def test_mask(method):

    expected = expected_mask()
    result = r1.mask(lon, lat, method=method, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)


@pytest.mark.filterwarnings("ignore:The method 'legacy' will be removed")
@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "legacy", "shapely"])
def test_mask_xarray(method):

    expected = expected_mask()
    result = r1.mask(lon, lat, method=method, xarray=True)

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.all(np.equal(result.lat.values, lat))
    assert np.all(np.equal(result.lon.values, lon))


@pytest.mark.filterwarnings("ignore:The method 'legacy' will be removed")
@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "legacy", "shapely"])
def test_mask_poly_z_value(method):

    if method == "legacy":
        pytest.xfail("legacy does not support z-coordinates")

    outl1 = Polygon(((0, 0, 1), (0, 1, 1), (1, 1.0, 1), (1, 0, 1)))
    outl2 = Polygon(((0, 1, 1), (0, 2, 1), (1, 2.0, 1), (1, 1, 1)))
    outlines = [outl1, outl2]

    r_z = Regions(outlines)

    expected = expected_mask()
    result = r_z.mask(lon, lat, method=method, xarray=True)

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.all(np.equal(result.lat.values, lat))
    assert np.all(np.equal(result.lon.values, lon))


@pytest.mark.filterwarnings("ignore:The method 'legacy' will be removed")
@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "legacy", "shapely"])
def test_mask_xarray_name(method):

    msk = r1.mask(lon, lat, method=method, xarray=True)

    assert msk.name == "region"


@pytest.mark.filterwarnings("ignore:The method 'legacy' will be removed")
@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "legacy", "shapely"])
def test_mask_obj(method):

    expected = expected_mask()

    obj = dict(lon=lon, lat=lat)
    result = r1.mask(obj, method=method, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)

    obj = dict(longitude=lon, latitude=lat)
    result = r1.mask(
        obj, method=method, lon_name="longitude", lat_name="latitude", xarray=False
    )

    assert np.allclose(result, expected, equal_nan=True)


@pytest.mark.filterwarnings("ignore:The method 'legacy' will be removed")
@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "legacy", "shapely"])
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


@pytest.mark.filterwarnings("ignore:The method 'legacy' will be removed")
@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "legacy", "shapely"])
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


def test_mask_wrong_method():

    msg = "Method must be None or one of 'rasterize', 'shapely', or 'legacy'."
    with pytest.raises(ValueError, match=msg):

        r1.mask(lon, lat, method="method")


# ======================================================================

# test 2D array
lon_2D = [[0.5, 1.5], [0.5, 1.5]]
lat_2D = [[0.5, 0.5], [1.5, 1.5]]


@pytest.mark.filterwarnings("ignore:The function `create_mask_contains` is deprecated")
def test_create_mask_function_2D():
    result = create_mask_contains(lon_2D, lat_2D, outlines)
    expected = expected_mask()
    assert np.allclose(result, expected, equal_nan=True)


@pytest.mark.filterwarnings("ignore:The method 'legacy' will be removed")
@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["legacy", "shapely"])
def test_mask_2D(method):

    expected = expected_mask()
    result = r1.mask(lon_2D, lat_2D, method=method, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)


@pytest.mark.filterwarnings("ignore:The method 'legacy' will be removed")
@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["legacy", "shapely"])
def test_mask_xarray_out_2D(method):

    expected = expected_mask()
    result = r1.mask(lon_2D, lat_2D, method=method, xarray=True)

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)

    assert np.all(np.equal(result.lat.values, lat_2D))
    assert np.all(np.equal(result.lon.values, lon_2D))

    assert np.all(np.equal(result.lat_idx.values, [0, 1]))
    assert np.all(np.equal(result.lon_idx.values, [0, 1]))


@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("lon", [lon_2D, [0, 1, 3], 0])
@pytest.mark.parametrize("lat", [lat_2D, [0, 1, 3], 0])
@pytest.mark.parametrize("xarray", [None, True, False])
def test_mask_rasterize_irregular(lon, lat, xarray):

    with pytest.raises(ValueError, match="`lat` and `lon` must be equally spaced"):
        r1.mask(lon, lat, method="rasterize", xarray=xarray)


@pytest.mark.filterwarnings("ignore:The method 'legacy' will be removed")
@pytest.mark.parametrize("method", ["legacy", "shapely"])
def test_mask_xarray_in_out_2D(method):
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
    result = r1.mask(data, lon_name="lon_2D", lat_name="lat_2D", method=method)

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.all(np.equal(result.lat_2D.values, lat_2D))
    assert np.all(np.equal(result.lon_2D.values, lon_2D))

    assert np.all(np.equal(result.lat_1D.values, [1, 2]))
    assert np.all(np.equal(result.lon_1D.values, [1, 2]))


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

    result = _mask_rasterize(lon, lat, outlines_poly, numbers=[a, b], fill=fill)

    assert np.allclose(result, expected, equal_nan=True)


# =============================================================================
# =============================================================================
# =============================================================================

# create a region such that the edge falls exactly on the lat/ lon coordinates
# ===

# TODO: use func(*(-161, -29, 2),  *(75, 13, -2)) after dropping py27
ds_US_180 = create_lon_lat_dataarray_from_bounds(*(-161, -29, 2) + (75, 13, -2))
ds_US_360 = create_lon_lat_dataarray_from_bounds(
    *(360 + -161, 360 + -29, 2) + (75, 13, -2)
)

outline_180 = np.array([[-100.0, 50.0], [-100.0, 28.0], [-80.0, 28.0], [-80.0, 50.0]])
outline_360 = outline_180 + [360, 0]

outline_hole_180 = np.array(
    [[-86.0, 44.0], [-86.0, 34.0], [-94.0, 34.0], [-94.0, 44.0]]
)
outline_hole_360 = outline_hole_180 + [360, 0]


r_US_180_ccw = Regions([outline_180])  # counter clockwise
r_US_180_cw = Regions([outline_180[::-1]])  # clockwise

r_US_360_ccw = Regions([outline_360])  # counter clockwise
r_US_360_cw = Regions([outline_360[::-1]])  # clockwise

# define poylgon with hole
poly = Polygon(outline_180, [outline_hole_180])
r_US_hole_180_cw = Regions([poly])  # clockwise
poly = Polygon(outline_180, [outline_hole_180[::-1]])
r_US_hole_180_ccw = Regions([poly])  # counter clockwise

poly = Polygon(outline_360, [outline_hole_360])
r_US_hole_360_cw = Regions([poly])  # clockwise
poly = Polygon(outline_360, [outline_hole_360[::-1]])
r_US_hole_360_ccw = Regions([poly])  # counter clockwise


def _expected_rectangle(ds, lon_min, lon_max, lat_min, lat_max, is_360):

    if is_360:
        lon_min += 360
        lon_max += 360

    LON = ds.LON
    LAT = ds.LAT

    expected = (LAT > lat_min) & (LAT <= lat_max)
    return expected & (LON > lon_min) & (LON <= lon_max)


def expected_mask_edge(ds, is_360, number=0, fill=np.NaN):

    expected = _expected_rectangle(ds, -100, -80, 28, 50, is_360)

    # set number and fill value
    expected = expected.where(expected, fill)
    expected = expected.where(expected != 1, number)

    return expected


def expected_mask_interior_and_edge(ds, is_360, number=0, fill=np.NaN):

    expected_outerior = _expected_rectangle(ds, -100, -80, 28, 50, is_360)
    expected_interior = _expected_rectangle(ds, -94, -86, 34, 44, is_360)

    expected = expected_outerior & ~expected_interior

    # set number and fill value
    expected = expected.where(expected, fill)
    expected = expected.where(expected != 1, number)

    return expected


@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "shapely"])
@pytest.mark.parametrize(
    "regions", [r_US_180_ccw, r_US_180_cw, r_US_360_ccw, r_US_360_cw]
)
@pytest.mark.parametrize("ds_US, is_360", [(ds_US_180, False), (ds_US_360, True)])
def test_mask_edge(method, regions, ds_US, is_360):

    expected = expected_mask_edge(ds_US, is_360)
    result = regions.mask(ds_US, method=method, xarray=True)

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.all(np.equal(result.lat, ds_US.lat))
    assert np.all(np.equal(result.lon, ds_US.lon))


@pytest.mark.filterwarnings("ignore:Passing the `xarray` keyword")
@pytest.mark.parametrize("method", ["rasterize", "shapely"])
@pytest.mark.parametrize(
    "regions",
    [r_US_hole_180_cw, r_US_hole_180_ccw, r_US_hole_360_cw, r_US_hole_360_ccw],
)
@pytest.mark.parametrize("ds_US, is_360", [(ds_US_180, False), (ds_US_360, True)])
def test_mask_interior_and_edge(method, regions, ds_US, is_360):

    expected = expected_mask_interior_and_edge(ds_US, is_360)
    result = regions.mask(ds_US, method=method, xarray=True)

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.all(np.equal(result.lat.values, ds_US.lat))
    assert np.all(np.equal(result.lon.values, ds_US.lon))


@pytest.mark.xfail(
    raises=AssertionError, reason="https://github.com/mapbox/rasterio/issues/1844"
)
def test_rasterize_edge():

    lon = ds_US_180.lon
    lat = ds_US_180.lat

    expected = expected_mask_edge(ds_US_180, is_360=False)
    result = _mask_rasterize_no_offset(lon, lat, r_US_180_ccw.polygons, numbers=[0])

    assert np.allclose(result, expected, equal_nan=True)


ds_for_45_deg = create_lon_lat_dataarray_from_bounds(*(-0.5, 16, 1) + (10.5, -0.5, -1))

# add a small offset to y to avoid https://github.com/mapbox/rasterio/issues/1844
outline_45_deg = np.array([[0, 10.1], [0, 0.1], [5.1, 0.1], [15.1, 10.1]])

r_45_def_ccw = Regions([outline_45_deg])
r_45_def_cw = Regions([outline_45_deg[::-1]])


@pytest.mark.parametrize("regions", [r_45_def_ccw, r_45_def_cw])
def test_deg45_rasterize_shapely_equal(regions):
    # https://github.com/mathause/regionmask/issues/80

    shapely = regions.mask(ds_for_45_deg, method="shapely")
    rasterize = regions.mask(ds_for_45_deg, method="rasterize")

    xr.testing.assert_equal(shapely, rasterize)


@pytest.mark.parametrize("regions", [r_45_def_ccw, r_45_def_cw])
def test_deg45_rasterize_offset_equal(regions):
    # https://github.com/mathause/regionmask/issues/80

    polygons = regions.polygons
    lon = ds_for_45_deg.lon
    lat = ds_for_45_deg.lat

    result_no_offset = _mask_rasterize_no_offset(lon, lat, polygons, numbers=[0])
    result_offset = _mask_rasterize(lon, lat, polygons, numbers=[0])

    assert np.allclose(result_no_offset, result_offset, equal_nan=True)


# =============================================================================

# the whole globe -> can be re-arranged
ds_GLOB_360 = create_lon_lat_dataarray_from_bounds(*(0, 360, 2) + (75, 13, -2))
# not all lon -> must be masked twice
ds_GLOB_360_part = create_lon_lat_dataarray_from_bounds(*(0, 300, 2) + (75, 13, -2))


@pytest.mark.parametrize("ds_360", [ds_GLOB_360, ds_GLOB_360_part])
@pytest.mark.parametrize("regions_180", [r_US_180_ccw, r_US_180_cw])
def test_rasterize_on_split_lon(ds_360, regions_180):
    # https://github.com/mathause/regionmask/issues/127

    # using regions_180 and ds_360 lon must be wrapped, making it
    # NOT equally_spaced
    result = regions_180.mask(ds_360, method="rasterize")

    expected = expected_mask_edge(ds_360, is_360=True)
    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.all(np.equal(result.lat, expected.lat))
    assert np.all(np.equal(result.lon, expected.lon))

    expected_shapely = regions_180.mask(ds_360, method="shapely")
    xr.testing.assert_equal(result, expected_shapely)
