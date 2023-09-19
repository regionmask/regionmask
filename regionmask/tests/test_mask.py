import copy

import numpy as np
import pytest
import xarray as xr
from affine import Affine
from shapely.geometry import Polygon, box

from regionmask import Regions
from regionmask.core.mask import (
    _determine_method,
    _inject_mask_docstring,
    _mask_pygeos,
    _mask_rasterize,
    _mask_rasterize_no_offset,
    _mask_shapely,
    _mask_shapely_v2,
    _transform_from_latlon,
)
from regionmask.core.utils import _wrapAngle, create_lon_lat_dataarray_from_bounds

from . import (
    assert_no_warnings,
    has_pygeos,
    has_shapely_2,
    requires_pygeos,
    requires_shapely_2,
)
from .utils import (
    dummy_ds,
    dummy_region,
    dummy_region_overlap,
    expected_mask_1D,
    expected_mask_2D,
    expected_mask_3D,
)

MASK_FUNCS = [
    _mask_rasterize,
    _mask_shapely,
    pytest.param(_mask_shapely_v2, marks=requires_shapely_2),
    pytest.param(_mask_pygeos, marks=requires_pygeos),
]

no_pygeos_depr_warning = pytest.mark.filterwarnings("ignore:pygeos is deprecated")

MASK_METHODS = [
    "rasterize",
    "shapely",
    pytest.param("pygeos", marks=[requires_pygeos, no_pygeos_depr_warning]),
]

MASK_METHODS_IRREGULAR = [
    "shapely",
    pytest.param("pygeos", marks=[requires_pygeos, no_pygeos_depr_warning]),
]

# =============================================================================


@pytest.mark.parametrize("func", MASK_FUNCS)
def test_mask_func(func):

    # standard
    result = func(dummy_ds.lon, dummy_ds.lat, dummy_region.polygons, numbers=[0, 1, 2])
    expected = expected_mask_2D()
    np.testing.assert_equal(result, expected)

    result = func(
        dummy_ds.lon, dummy_ds.lat, dummy_region.polygons, numbers=[0, 1, 2], fill=5
    )
    expected = expected_mask_2D(fill=5)
    np.testing.assert_equal(result, expected)

    result = func(dummy_ds.lon, dummy_ds.lat, dummy_region.polygons, numbers=[5, 6, 7])
    expected = expected_mask_2D(a=5, b=6)
    np.testing.assert_equal(result, expected)


@pytest.mark.parametrize("func", MASK_FUNCS)
def test_mask_wrong_number_fill(func):

    with pytest.raises(ValueError, match="The fill value should not"):
        func(
            dummy_ds.lon, dummy_ds.lat, dummy_region.polygons, numbers=[0, 1, 2], fill=0
        )

    with pytest.raises(ValueError, match="`numbers` and `coords` must have"):
        func(dummy_ds.lon, dummy_ds.lat, dummy_region.coords, numbers=[5])


@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask(method):

    expected = expected_mask_2D()
    result = dummy_region.mask(dummy_ds.lon, dummy_ds.lat, method=method)
    xr.testing.assert_identical(result, expected)


# @pytest.mark.filterwarnings("error:The ``method`` argument is internal")
@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_method_internal(method):

    with pytest.warns(FutureWarning, match="The ``method`` argument is internal"):
        dummy_region.mask(dummy_ds, method=method)


@pytest.mark.skipif(has_pygeos, reason="Only errors if pygeos is missing")
def test_missing_pygeos_error():

    with pytest.raises(ModuleNotFoundError, match="No module named 'pygeos'"):
        dummy_region.mask(dummy_ds.lon, dummy_ds.lat, method="pygeos")


@pytest.mark.skipif(
    not has_pygeos or not has_shapely_2, reason="depr pygeos if shapely 2"
)
def test_deprecate_pygeos():

    with pytest.warns(
        FutureWarning, match="pygeos is deprecated in favour of shapely 2.0"
    ):
        dummy_region.mask(dummy_ds.lon, dummy_ds.lat, method="pygeos")


@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_xr_keep_name(method):

    ds = xr.Dataset(
        coords={"longitude": dummy_ds.lon.values, "latitude": dummy_ds.lat.values}
    )

    expected = expected_mask_2D(lat_name="latitude", lon_name="longitude")

    result = dummy_region.mask(ds.longitude, ds.latitude, method=method)

    xr.testing.assert_identical(result, expected)


@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_poly_z_value(method):

    outl1 = Polygon(((0, 0, 1), (0, 1, 1), (1, 1.0, 1), (1, 0, 1)))
    outl2 = Polygon(((0, 1, 1), (0, 2, 1), (1, 2.0, 1), (1, 1, 1)))
    r_z = Regions([outl1, outl2])

    expected = expected_mask_2D()
    result = r_z.mask(dummy_ds, method=method)

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_xarray_name(method):

    msk = dummy_region.mask(dummy_ds, method=method)
    assert msk.name == "mask"


@pytest.mark.parametrize("ndims", [(2, 1), (1, 2)])
def test_mask_unequal_ndim(ndims):

    lon = np.arange(ndims[0] * 2).reshape(ndims[0] * (2,))
    lat = np.arange(ndims[1] * 2).reshape(ndims[1] * (2,))

    with pytest.raises(ValueError, match="Equal number of dimensions required"):
        dummy_region.mask(lon, lat)


def test_mask_unequal_2D_shapes():

    lon = np.zeros(shape=(2, 3))
    lat = np.zeros(shape=(2, 4))

    with pytest.raises(
        ValueError, match="2D lon and lat coordinates need to have the same shape"
    ):
        dummy_region.mask(lon, lat)


@pytest.mark.parametrize("ndim", [0, 3, 4])
def test_mask_ndim_ne_1_2(ndim):

    lon = np.zeros(shape=ndim * (2,))
    lat = np.zeros(shape=ndim * (2,))

    with pytest.raises(ValueError, match="1D or 2D data required"):
        dummy_region.mask(lon, lat)


@pytest.mark.parametrize("lon_name", ["lon", "longitude"])
@pytest.mark.parametrize("lat_name", ["lat", "latitude"])
@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_obj(lon_name, lat_name, method):

    expected = expected_mask_2D(lat_name=lat_name, lon_name=lon_name)

    obj = {lon_name: dummy_ds.lon.values, lat_name: dummy_ds.lat.values}
    with pytest.warns(
        FutureWarning, match="Passing 'lon_name' and 'lat_name' was deprecated"
    ):
        result = dummy_region.mask(
            obj, method=method, lon_name=lon_name, lat_name=lat_name
        )

    xr.testing.assert_equal(result, expected)


@pytest.mark.filterwarnings("ignore:No gridpoint belongs to any region.")
@pytest.mark.parametrize("method", MASK_METHODS)
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

    result = r.mask(lon, lat, method=method, wrap_lon=False)
    assert result.isnull().all()

    # this is the wrong wrapping
    result = r.mask(lon, lat, method=method, wrap_lon=180)
    assert result.isnull().all()

    expected = expected_mask_2D(coords={"lon": lon, "lat": lat})

    # determine the wrap automatically
    result = r.mask(lon, lat, method=method, wrap_lon=True)
    xr.testing.assert_equal(result, expected)

    # determine the wrap by hand
    result = r.mask(lon, lat, method=method, wrap_lon=360)
    xr.testing.assert_equal(result, expected)


@pytest.mark.filterwarnings("ignore:No gridpoint belongs to any region.")
@pytest.mark.parametrize("meth", ["mask", "mask_3D"])
def test_wrap_lon_no_error_wrap_lon_false(meth):

    # regions that exceed 360° longitude
    r = Regions([[[-180, 0], [-180, 10], [360, 10], [360, 0]]], numbers=[1])

    # lons that exceed 360° longitude
    lon = np.arange(-175, 360, 2.5)
    lat = np.arange(10, 1, -3)

    mask = getattr(r, meth)(lon, lat, wrap_lon=False)

    # the region index is 1 -> thus this works for 2D and 3D masks
    assert (mask == 1).all()
    np.testing.assert_equal(lon, mask.lon)
    np.testing.assert_equal(lat, mask.lat)

    # -180° is not special cased (no _mask_edgepoints_shapely)
    lon = [-180]
    mask = getattr(r, meth)(lon, lat, wrap_lon=False)
    assert (mask != 1).all()
    np.testing.assert_equal(lon, mask.lon)
    np.testing.assert_equal(lat, mask.lat)


@pytest.mark.parametrize("meth", ["mask", "mask_3D"])
def test_wrap_lon_error_wrap_lon(meth):

    # regions that exceed 360° longitude
    r = Regions([[[-180, 0], [-180, 10], [360, 10], [360, 0]]])

    # lons that exceed 360° longitude
    lon = np.arange(-180, 360, 2.5)
    lat = np.arange(10, 1, -3)

    with pytest.raises(ValueError, match="Set `wrap_lon=False` to skip this check."):
        getattr(r, meth)(lon, lat)


@pytest.mark.parametrize("method", MASK_METHODS)
@pytest.mark.parametrize(
    "lon, extent",
    (
        ([358.5, 359.5], (-180, -1)),
        ([-1.5, -0.5], (-180, -1)),
        ([-1.5, -0.5], (359, 0)),
        ([358.5, 359.5], (359, 0)),
    ),
)
def test_mask_autowrap(method, lon, extent):

    # outlines and lon are different - or the same - should work either way

    lat = [0.5, 1.5]

    r_from, r_to = extent
    outl1 = ((r_from, 0), (r_from, 1), (r_to, 1.0), (r_to, 0))
    outl2 = ((r_from, 1), (r_from, 2), (r_to, 2.0), (r_to, 1))
    r = Regions([outl1, outl2])

    expected = expected_mask_2D(coords={"lon": lon, "lat": lat})

    result = r.mask(lon, lat, method=method)
    xr.testing.assert_equal(result, expected)


def test_mask_wrong_method():

    msg = "Method must be None or one of 'rasterize', 'shapely' and 'pygeos'."
    with pytest.raises(ValueError, match=msg):
        dummy_region.mask(dummy_ds, method="wrong")


@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_2D_overlap_error(method):

    match = "Creating a 2D mask with overlapping regions yields wrong results"
    with pytest.raises(ValueError, match=match):
        dummy_region_overlap.mask(dummy_ds, method=method)


@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_2D_overlap_false(method):

    # make a copy to ensure dummy_region_overlap.overlap is not overwritten
    region = copy.copy(dummy_region_overlap)
    expected = expected_mask_2D(a=1, b=2)

    region.overlap = False
    result = region.mask(dummy_ds, method=method)

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_2D_overlap_none(method):

    # make a copy to ensure dummy_region_overlap.overlap is not overwritten
    region = copy.copy(dummy_region_overlap)

    region.overlap = None

    with pytest.raises(
        ValueError, match="Found overlapping regions for ``overlap=None``"
    ):
        region.mask(dummy_ds, method=method)


@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_2D_overlap_default(method):

    region = Regions(dummy_region_overlap.polygons)

    with pytest.raises(
        ValueError, match="Found overlapping regions for ``overlap=None``"
    ):
        region.mask(dummy_ds, method=method)


@pytest.mark.parametrize("drop", [True, False])
@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_3D_overlap(drop, method):

    expected = expected_mask_3D(drop=drop, overlap=True)
    result = dummy_region_overlap.mask_3D(dummy_ds, drop=drop, method=method)

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("drop", [True, False])
@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_3D_overlap_one(drop, method):

    # make a copy to ensure dummy_region_overlap.overlap is not overwritten
    region = copy.copy(dummy_region_overlap)

    region.overlap = None

    expected = expected_mask_3D(drop=drop, overlap=True)
    result = dummy_region_overlap.mask_3D(dummy_ds, drop=drop, method=method)

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("wrap_lon", [None, True, False])
@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_3D_overlap_more_than_64(wrap_lon, method):

    polygon = box(0, 0, 5, 5)

    lon = np.arange(0.5, 5)
    lat = np.arange(0.5, 5)

    region = Regions([polygon] * 65, overlap=True)

    result = region.mask_3D(lon, lat, wrap_lon=wrap_lon, method=method)

    expected = xr.ones_like(result, dtype=bool)

    xr.testing.assert_identical(expected, result)


@pytest.mark.parametrize("drop", [True, False])
@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_3D_overlap_default(drop, method):

    region = Regions(dummy_region_overlap.polygons)

    expected = expected_mask_3D(drop=drop, overlap=True)

    with pytest.warns(UserWarning, match="Detected overlapping regions"):
        result = region.mask_3D(dummy_ds, drop=drop, method=method)

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_3D_overlap_empty(method):

    match = "No gridpoint belongs to any region. "

    lon = lat = [10, 11]
    with pytest.warns(UserWarning, match=match + "Returning an empty mask"):
        result = dummy_region_overlap.mask_3D(lon, lat, drop=True, method=method)

    coords = {"lat": lat, "lon": lon}
    expected = expected_mask_3D(False, coords=coords, overlap=True).isel(
        region=slice(0, 0)
    )

    assert result.shape == (0, 2, 2)
    xr.testing.assert_equal(result, expected)

    with pytest.warns(UserWarning, match=match + "Returning an all-False mask."):
        result = dummy_region_overlap.mask_3D(lon, lat, drop=False, method=method)

    assert result.shape == (4, 2, 2)
    assert not result.any()


@pytest.mark.parametrize("drop", [True, False])
@pytest.mark.parametrize("method", MASK_METHODS_IRREGULAR)
def test_mask_overlap_unstructured(drop, method):
    """Test for unstructured output."""
    lat = [0.5, 0.5, 1.5, 1.5]
    lon = [0.5, 1.5, 0.5, 1.5]

    coords = {"lon": ("cells", lon), "lat": ("cells", lat)}
    grid = xr.Dataset(coords=coords)

    result = dummy_region_overlap.mask_3D(grid, drop=drop, method=method)

    expected = expected_mask_3D(drop=drop, overlap=True)
    expected = expected.stack(cells=("lat", "lon")).reset_index("cells")

    xr.testing.assert_equal(result, expected)


def test_mask_flag():

    expected = expected_mask_2D()
    result = dummy_region.mask(dummy_ds)
    xr.testing.assert_identical(result, expected)

    result = dummy_region.mask(dummy_ds, flag="names")
    expected.attrs["flag_meanings"] = "Region0 Region1"
    xr.testing.assert_identical(result, expected)

    result = dummy_region.mask(dummy_ds, flag=None)
    del expected.attrs["flag_meanings"]
    del expected.attrs["flag_values"]

    xr.testing.assert_identical(result, expected)


def test_mask_flag_space():

    r = Regions(dummy_region.polygons, names=["name with space", "another", "last"])

    expected = expected_mask_2D()
    expected.attrs["flag_meanings"] = "name_with_space another"

    result = r.mask(dummy_ds, flag="names")
    xr.testing.assert_identical(result, expected)


def test_mask_flag_only_found():

    result = dummy_region.mask([0.5], [0.5])

    assert result.attrs["flag_meanings"] == "r0"
    np.testing.assert_equal(result.attrs["flag_values"], np.array([0]))


# ======================================================================

# test 2D array
lon_2D = [[0.5, 1.5], [0.5, 1.5]]
lat_2D = [[0.5, 0.5], [1.5, 1.5]]


@pytest.mark.parametrize("method", MASK_METHODS_IRREGULAR)
def test_mask_2D(method):

    dims = ("lat_idx", "lon_idx")
    lat_name, lon_name = dims
    coords = {"lat": (dims, lat_2D), "lon": (dims, lon_2D)}

    expected = expected_mask_2D(coords=coords, lat_name=lat_name, lon_name=lon_name)
    result = dummy_region.mask(lon_2D, lat_2D, method=method)

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("lon", [lon_2D, [0, 1, 3], 0])
@pytest.mark.parametrize("lat", [lat_2D, [0, 1, 3], 0])
def test_mask_rasterize_irregular(lon, lat):

    with pytest.raises(ValueError, match="`lat` and `lon` must be equally spaced"):
        dummy_region.mask(lon, lat, method="rasterize")


@pytest.mark.parametrize("method", MASK_METHODS_IRREGULAR)
def test_mask_xarray_in_out_2D(method):
    # create xarray DataArray with 2D dims

    dims = ("lat_1D", "lon_1D")
    lat_name, lon_name = dims
    coords = {
        "lat_1D": [1, 2],
        "lon_1D": [1, 2],
        "lat_2D": (dims, lat_2D),
        "lon_2D": (dims, lon_2D),
    }

    data = xr.Dataset(coords=coords)

    expected = expected_mask_2D(coords=coords, lat_name=lat_name, lon_name=lon_name)
    result = dummy_region.mask(data.lon_2D, data.lat_2D, method=method)

    xr.testing.assert_equal(result, expected)


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
@pytest.mark.parametrize("fill", [np.nan, 3])
def test_rasterize(a, b, fill):

    expected = expected_mask_2D(a=a, b=b, fill=fill)

    result = _mask_rasterize(
        dummy_ds.lon, dummy_ds.lat, dummy_region.polygons, numbers=[a, b, -1], fill=fill
    )

    np.testing.assert_equal(result, expected)


@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_empty(method):

    lon = lat = [10, 11]
    with pytest.warns(UserWarning, match="No gridpoint belongs to any region."):
        result = dummy_region.mask(lon, lat, method=method)

    expected = expected_mask_2D(coords={"lon": lon, "lat": lat})

    xr.testing.assert_equal(result, expected * np.nan)


# =============================================================================
# =============================================================================
# test unstructured


@pytest.mark.parametrize("method", MASK_METHODS_IRREGULAR)
def test_mask_unstructured(method):
    """Test for unstructured output."""
    lat = [0.5, 0.5, 1.5, 1.5]
    lon = [0.5, 1.5, 0.5, 1.5]

    coords = {"lon": ("cells", lon), "lat": ("cells", lat)}
    grid = xr.Dataset(coords=coords)

    result = dummy_region.mask(grid, method=method)
    expected = expected_mask_1D()

    xr.testing.assert_equal(result, expected)


# =============================================================================
# =============================================================================
# test mask_3D: only basics (same algorithm as mask)


@pytest.mark.parametrize("drop", [True, False])
@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_3D(drop, method):

    expected = expected_mask_3D(drop)
    result = dummy_region.mask_3D(dummy_ds.lon, dummy_ds.lat, drop=drop, method=method)

    xr.testing.assert_identical(result, expected)


@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_3D_empty(method):

    match = "No gridpoint belongs to any region. "

    lon = lat = [10, 11]
    with pytest.warns(UserWarning, match=match + "Returning an empty mask"):
        result = dummy_region.mask_3D(lon, lat, drop=True, method=method)

    coords = {"lat": lat, "lon": lon}
    expected = expected_mask_3D(False, coords=coords).isel(region=slice(0, 0))

    assert result.shape == (0, 2, 2)
    xr.testing.assert_equal(result, expected)

    with pytest.warns(UserWarning, match=match + "Returning an all-False mask."):
        result = dummy_region.mask_3D(lon, lat, drop=False, method=method)

    assert result.shape == (3, 2, 2)
    assert not result.any()


@pytest.mark.filterwarnings("ignore:rename .* does not create an index")
@pytest.mark.parametrize("lon_name", ["lon", "longitude"])
@pytest.mark.parametrize("lat_name", ["lat", "latitude"])
@pytest.mark.parametrize("drop", [True, False])
@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_3D_obj(lon_name, lat_name, drop, method):

    expected = expected_mask_3D(drop, lon_name=lon_name, lat_name=lat_name)

    obj = dummy_ds.rename(lon=lon_name, lat=lat_name)
    with pytest.warns(
        FutureWarning, match="Passing 'lon_name' and 'lat_name' was deprecated"
    ):
        result = dummy_region.mask_3D(
            obj, method=method, drop=drop, lon_name=lon_name, lat_name=lat_name
        )

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("meth", ["mask", "mask_3D"])
def test_mask_warn_radian(meth):

    lon = dummy_ds.lon.copy()
    lat = dummy_ds.lat.copy()
    mask_func = getattr(dummy_region, meth)

    with assert_no_warnings():
        mask_func(lon, lat)

    lon.attrs["units"] = "radian"
    with pytest.warns(UserWarning, match="given as 'radian'"):
        mask_func(lon, lat)

    lat.attrs["units"] = "radian"
    with pytest.warns(UserWarning, match="given as 'radian'"):
        mask_func(lon, lat)

    # no warnings with 'wrap_lon=False'
    with assert_no_warnings():
        mask_func(lon, lat, wrap_lon=False)


# =============================================================================
# =============================================================================
# =============================================================================

# create a region such that the edge falls exactly on the lat/ lon coordinates
# ===

ds_US_180 = create_lon_lat_dataarray_from_bounds(*(-161, -29, 2), *(75, 13, -2))
ds_US_360 = create_lon_lat_dataarray_from_bounds(
    *(360 + -161, 360 + -29, 2), *(75, 13, -2)
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


def expected_mask_edge(ds, is_360, number=0, fill=np.nan):

    expected = _expected_rectangle(ds, -100, -80, 28, 50, is_360)

    # set number and fill value
    expected = expected.where(expected, fill)
    expected = expected.where(expected != 1, number)

    coords = {"lat": ds.lat, "lon": ds.lon}
    expected = xr.DataArray(expected, dims=("lat", "lon"), coords=coords)
    return expected


def expected_mask_interior_and_edge(ds, is_360, number=0, fill=np.nan):

    expected_outerior = _expected_rectangle(ds, -100, -80, 28, 50, is_360)
    expected_interior = _expected_rectangle(ds, -94, -86, 34, 44, is_360)

    expected = expected_outerior & ~expected_interior

    # set number and fill value
    expected = expected.where(expected, fill)
    expected = expected.where(expected != 1, number)

    coords = {"lat": ds.lat, "lon": ds.lon}
    expected = xr.DataArray(expected, dims=("lat", "lon"), coords=coords)
    return expected


@pytest.mark.parametrize("method", MASK_METHODS)
@pytest.mark.parametrize(
    "regions", [r_US_180_ccw, r_US_180_cw, r_US_360_ccw, r_US_360_cw]
)
@pytest.mark.parametrize("ds_US, is_360", [(ds_US_180, False), (ds_US_360, True)])
def test_mask_edge(method, regions, ds_US, is_360):

    expected = expected_mask_edge(ds_US, is_360)
    result = regions.mask(ds_US, method=method)

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("method", MASK_METHODS)
@pytest.mark.parametrize(
    "regions",
    [r_US_hole_180_cw, r_US_hole_180_ccw, r_US_hole_360_cw, r_US_hole_360_ccw],
)
@pytest.mark.parametrize("ds_US, is_360", [(ds_US_180, False), (ds_US_360, True)])
def test_mask_interior_and_edge(method, regions, ds_US, is_360):

    expected = expected_mask_interior_and_edge(ds_US, is_360)
    result = regions.mask(ds_US, method=method)

    xr.testing.assert_equal(result, expected)


@pytest.mark.xfail(
    raises=AssertionError, reason="https://github.com/mapbox/rasterio/issues/1844"
)
def test_rasterize_edge():

    lon = ds_US_180.lon
    lat = ds_US_180.lat

    expected = expected_mask_edge(ds_US_180, is_360=False)
    result = _mask_rasterize_no_offset(lon, lat, r_US_180_ccw.polygons, numbers=[0])

    np.testing.assert_equal(result, expected)


ds_for_45_deg = create_lon_lat_dataarray_from_bounds(*(-0.5, 16, 1), *(10.5, -0.5, -1))

# add a small offset to y to avoid https://github.com/mapbox/rasterio/issues/1844
outline_45_deg = np.array([[0, 10.1], [0, 0.1], [5.1, 0.1], [15.1, 10.1]])

r_45_deg_ccw = Regions([outline_45_deg])
r_45_deg_cw = Regions([outline_45_deg[::-1]])


@no_pygeos_depr_warning
@pytest.mark.parametrize("regions", [r_45_deg_ccw, r_45_deg_cw])
def test_deg45_rasterize_shapely_equal(regions):
    # https://github.com/regionmask/regionmask/issues/80

    shapely = regions.mask(ds_for_45_deg, method="shapely")
    rasterize = regions.mask(ds_for_45_deg, method="rasterize")

    xr.testing.assert_equal(shapely, rasterize)

    if has_pygeos:
        pygeos = regions.mask(ds_for_45_deg, method="pygeos")
        xr.testing.assert_equal(pygeos, rasterize)


@pytest.mark.parametrize("regions", [r_45_deg_ccw, r_45_deg_cw])
def test_deg45_rasterize_offset_equal(regions):
    # https://github.com/regionmask/regionmask/issues/80

    polygons = regions.polygons
    lon = ds_for_45_deg.lon
    lat = ds_for_45_deg.lat

    result_no_offset = _mask_rasterize_no_offset(lon, lat, polygons, numbers=[0])
    result_offset = _mask_rasterize(lon, lat, polygons, numbers=[0])

    np.testing.assert_equal(result_no_offset, result_offset)


# =============================================================================

# the whole globe -> can be re-arranged (_mask_rasterize_flip)
ds_GLOB_360 = create_lon_lat_dataarray_from_bounds(*(0, 360, 2), *(75, 13, -2))
# not all lon -> must be masked twice (_mask_rasterize_split)
ds_GLOB_360_part = create_lon_lat_dataarray_from_bounds(*(0, 300, 2), *(75, 13, -2))


@pytest.mark.parametrize("ds_360", [ds_GLOB_360, ds_GLOB_360_part])
@pytest.mark.parametrize("regions_180", [r_US_180_ccw, r_US_180_cw])
def test_rasterize_on_split_lon(ds_360, regions_180):
    # https://github.com/regionmask/regionmask/issues/127

    # using regions_180 and ds_360 lon must be wrapped, making it
    # NOT equally_spaced
    result = regions_180.mask(ds_360, method="rasterize")

    expected = expected_mask_edge(ds_360, is_360=True)
    xr.testing.assert_equal(result, expected)

    expected_shapely = regions_180.mask(ds_360, method="shapely")
    xr.testing.assert_equal(result, expected_shapely)


def test_rasterize_on_split_lon_asymmetric():
    # https://github.com/regionmask/regionmask/issues/266

    # for _mask_rasterize_flip: split_point not in the middle
    lon = np.hstack([np.arange(-90, 20, 2), np.arange(-180, -90, 2)])
    lat = np.arange(75, 13, -2)
    ds = xr.Dataset(coords=dict(lon=lon, lat=lat))

    assert _determine_method(ds.lon, ds.lat) == "rasterize_flip"

    result = r_US_180_cw.mask(ds, method="rasterize")
    expected = r_US_180_cw.mask(ds, method="shapely")
    xr.testing.assert_equal(result, expected)


METHOD_IRREGULAR = "pygeos" if has_pygeos else "shapely"

if has_shapely_2:
    METHOD_IRREGULAR = "shapely_2"
elif has_pygeos:
    METHOD_IRREGULAR = "pygeos"
else:
    METHOD_IRREGULAR = "shapely"


METHODS = {
    0: "rasterize",
    1: "rasterize_flip",
    2: "rasterize_split",
    3: METHOD_IRREGULAR,
}

equal = np.arange(0.5, 360)
grid_2D = np.arange(10).reshape(2, 5)
un_equal = [0, 1, 2, 4, 5, 6.1]
close_to_equal = equal + np.random.randn(*equal.shape) * 10**-6


@pytest.mark.parametrize(
    "lon, m_lon",
    [
        (equal, 0),
        (close_to_equal, 0),
        (_wrapAngle(equal), 1),
        (_wrapAngle(equal)[:-1], 2),
        ([1], 3),
        (grid_2D, 3),
        (un_equal, 3),
    ],
)
@pytest.mark.parametrize(
    "lat, m_lat",
    [(equal, 0), (close_to_equal, 0), ([1], 3), (grid_2D, 3), (un_equal, 3)],
)
def test_determine_method(lon, m_lon, lat, m_lat):

    expected = METHODS[max((m_lon, m_lat))]

    assert _determine_method(lon, lat) == expected


# =============================================================================
# =============================================================================
# =============================================================================

# ensure a global region includes all gridpoints - also the ones at
# 0°E/ -180°E and -90°N (#GH159)

outline_GLOB_180 = np.array(
    [[-180.0, 90.0], [-180.0, -90.0], [180.0, -90.0], [180.0, 90.0]]
)
outline_GLOB_360 = outline_GLOB_180 + [180, 0]

r_GLOB_180 = Regions([outline_GLOB_180])
r_GLOB_360 = Regions([outline_GLOB_360])

lon180 = np.arange(-180, 180, 10)
lon360 = np.arange(0, 360, 10)


@pytest.mark.parametrize("method", MASK_METHODS)
@pytest.mark.parametrize("regions", [r_GLOB_180, r_GLOB_360])
@pytest.mark.parametrize("lon", [lon180, lon360])
def test_mask_whole_grid(method, regions, lon):

    lat = np.arange(90, -91, -10)
    mask = regions.mask(lon, lat, method=method)

    assert (mask == 0).all()

    # with wrap_lon=False the edges are not masked
    mask = regions.mask(lon, lat, method=method, wrap_lon=False)
    assert mask.sel(lat=-90).isnull().all()


@pytest.mark.parametrize("regions", [r_GLOB_180, r_GLOB_360])
@pytest.mark.parametrize("lon", [lon180, lon360])
def test_mask_whole_grid_nan_lon(regions, lon):
    # https://github.com/regionmask/regionmask/issues/426

    lat = np.arange(90, -91, -10)
    lon = np.concatenate([lon, [np.nan]])
    mask = regions.mask(lon, lat)

    assert mask.isel(lon=-1).isnull().all()

    assert (mask.isel(lon=slice(None, -1)) == 0).all()


@pytest.mark.parametrize("method", MASK_METHODS)
@pytest.mark.parametrize("regions", [r_GLOB_180, r_GLOB_360])
def test_mask_whole_grid_unusual_lon(method, regions):
    # https://github.com/regionmask/regionmask/issues/213

    lat = np.arange(90, -91, -2.5)
    lon = np.arange(-300, 60, 2.5)
    mask = regions.mask(lon, lat, method=method)

    assert (mask == 0).all()


@pytest.mark.parametrize("method", MASK_METHODS)
@pytest.mark.parametrize("outline", [outline_GLOB_180, outline_GLOB_360])
@pytest.mark.parametrize("lon", [lon180, lon360])
def test_mask_whole_grid_overlap(method, outline, lon):

    regions = Regions([outline, outline], overlap=True)

    lat = np.arange(90, -91, -10)
    mask = regions.mask_3D(lon, lat, method=method)
    assert mask.all()

    # with wrap_lon=False the edges are not masked
    mask = regions.mask_3D(lon, lat, method=method, wrap_lon=False)
    assert not mask.sel(lat=-90).any()


def test_inject_mask_docstring():

    result = _inject_mask_docstring(is_3D=True, is_gpd=True)

    assert "3D" in result
    assert "2D" not in result
    assert "boolean" in result
    assert "drop :" in result
    assert "geodataframe" in result
    assert "overlap" in result
    assert "flag" not in result

    result = _inject_mask_docstring(is_3D=False, is_gpd=False)

    assert "2D" in result
    assert "float" in result
    assert "drop :" not in result
    assert "geodataframe" not in result
    assert "overlap" not in result
    assert "flag" in result
