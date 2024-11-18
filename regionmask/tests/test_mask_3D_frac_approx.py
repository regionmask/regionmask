from typing import Any, Literal, TypedDict

import numpy as np
import pytest
import shapely
import xarray as xr

import regionmask
from regionmask.core.mask import InvalidCoordsError
from regionmask.core.utils import _sample_coords
from regionmask.tests.utils import dummy_region


def test_sample_coords() -> None:

    actual = _sample_coords([0, 10])
    expected = np.arange(-4.5, 14.6, 1)
    np.testing.assert_allclose(actual, expected)

    actual = _sample_coords([0, 1, 2])
    expected = np.arange(-0.45, 2.46, 0.1)
    np.testing.assert_allclose(actual, expected)


@pytest.mark.parametrize("dim", ["lon_or_obj", "lat"])
@pytest.mark.parametrize("invalid_coords", ([0, 1, 3], [[0, 1, 2]]))
def test_mask_percentage_wrong_coords(
    dim: Literal["lon_or_obj", "lat"], invalid_coords
) -> None:

    class LATLON(TypedDict):
        lon_or_obj: Any
        lat: Any

    valid_coords = [0, 1, 2]
    latlon: LATLON = {"lon_or_obj": valid_coords, "lat": valid_coords}
    # replace one of the coords with invalid values
    latlon[dim] = invalid_coords

    with pytest.raises(
        InvalidCoordsError, match="'lon' and 'lat' must be 1D and equally spaced."
    ):
        dummy_region.mask_3D_frac_approx(**latlon)


@pytest.mark.parametrize("lat", ((-91, 90), (-90, 92), (-91, 92)))
def test_mask_percentage_lon_beyond_90(lat) -> None:

    lat = np.arange(*lat)
    lon = np.arange(0, 360, 10)

    with pytest.raises(InvalidCoordsError, match=r"lat must be between \-90 and \+90"):
        dummy_region.mask_3D_frac_approx(lon, lat)


def test_mask_percentage_coords() -> None:
    # ensure coords are the same (as they might by averaged)

    lat = np.arange(90, -90, -1)
    lon = np.arange(0, 120, 1)

    r = shapely.geometry.box(0, -90, 120, 90)
    r = regionmask.Regions([r])

    result = r.mask_3D_frac_approx(lon, lat)

    np.testing.assert_equal(result.lon.values, lon)
    np.testing.assert_equal(result.lat.values, lat)

    assert result.abbrevs.item() == "r0"
    assert result.names.item() == "Region0"
    assert result.region.item() == 0


def test_mask_percentage_poles() -> None:
    # all points should be 1 for a global mask

    lat = np.arange(90, -91, -5)
    lon = np.arange(0, 360, 5)

    r = shapely.geometry.box(0, -90, 360, 90)
    r = regionmask.Regions([r])

    result = r.mask_3D_frac_approx(lon, lat)
    assert (result == 1).all()


def test_mask_percentage_southpole() -> None:
    # all at the southpole should be 1 - irrespective of where exactly the southernmost
    # latitude is

    lon = np.arange(0, 31, 5)

    r = shapely.geometry.box(0, -90, 360, -85)
    r = regionmask.Regions([r])

    for offset in np.arange(0, 1, 0.05):
        lat = np.arange(-90, -80, 1) + offset
        result = r.mask_3D_frac_approx(lon, lat)
        assert (result.isel(lat=0) == 1).all()


def test_mask_percentage_northpole() -> None:
    # all at the southpole should be 1 - irrespective of where exactly the southernmost
    # latitude is

    lon = np.arange(0, 31, 5)

    r = shapely.geometry.box(0, 85, 360, 90)
    r = regionmask.Regions([r])

    for offset in np.arange(0, 1, 0.05):
        lat = np.arange(90, 80, -1) - offset
        result = r.mask_3D_frac_approx(lon, lat)
        assert (result.isel(lat=0) == 1).all()


def test_mask_percentage() -> None:

    lon = np.array([15, 30])
    lat = np.array([15, 30])

    # the center of the region is at 15°
    r = shapely.geometry.box(0, 0, 30, 30)
    r = regionmask.Regions([r])

    result = r.mask_3D_frac_approx(lon, lat)

    expected_ = [[[1, 0.5], [0.5, 0.25]]]
    expected = xr.DataArray(
        expected_,
        dims=("region", "lat", "lon"),
        coords={
            "lat": lat,
            "lon": lon,
            "abbrevs": ("region", ["r0"]),
            "region": [0],
            "names": ("region", ["Region0"]),
        },
    )

    xr.testing.assert_allclose(result, expected)


def test_mask_percentage_poly() -> None:

    lon = np.array([10, 20])
    lat = np.array([10, 20])

    p = [[5, 5], [15, 15], [25, 20], [25, 15], [22.5, 15], [22.5, 5]]

    p = shapely.geometry.Polygon(p)
    r = regionmask.Regions([p])

    result = r.mask_3D_frac_approx(lon, lat)

    # these should be [[[0.5, 0.75], ]] but due to the method they are maximally wrong
    expected_ = [[[0.45, 0.8], [0.0, 0.25]]]
    expected = xr.DataArray(
        expected_,
        dims=("region", "lat", "lon"),
        coords={
            "lat": lat,
            "lon": lon,
            "abbrevs": ("region", ["r0"]),
            "region": [0],
            "names": ("region", ["Region0"]),
        },
    )

    xr.testing.assert_allclose(result, expected)


@pytest.mark.parametrize("lat_name", ("lat", "y"))
@pytest.mark.parametrize("lon_name", ("lon", "x"))
def test_mask_percentage_coord_names(lat_name, lon_name) -> None:

    lon = np.array([15, 30])
    lat = np.array([15, 30])
    ds = xr.Dataset(coords={lon_name: lon, lat_name: lat})

    # the center of the region is at 15°
    r = shapely.geometry.box(0, 0, 30, 30)
    r = regionmask.Regions([r])

    result = r.mask_3D_frac_approx(ds[lon_name], ds[lat_name])

    expected_ = [[[1, 0.5], [0.5, 0.25]]]
    expected = xr.DataArray(
        expected_,
        dims=("region", lat_name, lon_name),
        coords={
            lat_name: lat,
            lon_name: lon,
            "abbrevs": ("region", ["r0"]),
            "region": [0],
            "names": ("region", ["Region0"]),
        },
    )

    xr.testing.assert_allclose(result, expected)


def test_mask_percentage_overlap() -> None:
    # all points should be 1 for a global mask

    lat = np.arange(90, -91, -5)
    lon = np.arange(0, 360, 5)

    r = shapely.geometry.box(0, -90, 360, 90)
    r = regionmask.Regions([r, r])

    expected_ = np.ones((2,) + lat.shape + lon.shape)
    expected = xr.DataArray(
        expected_,
        dims=("region", "lat", "lon"),
        coords={
            "region": [0, 1],
            "abbrevs": ("region", ["r0", "r1"]),
            "names": ("region", ["Region0", "Region1"]),
            "lat": lat,
            "lon": lon,
        },
    )

    result = r.mask_3D_frac_approx(lon, lat)

    xr.testing.assert_equal(result, expected)


@pytest.mark.parametrize("lon_range", ((0, 360), (-180, 180)))
def test_mask_percentage_maybe_flip(lon_range: tuple[int, int]) -> None:
    # all points should be 1 for a global mask

    lat = np.arange(90, -91, -5)
    lon = np.arange(*lon_range, 5)

    r = shapely.geometry.box(0, -90, 360, 90)
    r = regionmask.Regions([r])

    expected_ = np.ones((1,) + lat.shape + lon.shape, dtype=bool)
    expected = xr.DataArray(
        expected_,
        dims=("region", "lat", "lon"),
        coords={
            "region": [0],
            "abbrevs": ("region", ["r0"]),
            "names": ("region", ["Region0"]),
            "lat": lat,
            "lon": lon,
        },
    )

    result = r.mask_3D_frac_approx(lon, lat)

    xr.testing.assert_equal(result, expected)
