import numpy as np
import pytest
import xarray as xr

from regionmask.core.mask import _numpy_coords_to_dataarray, mask_to_dataarray


def test_mask_to_dataarray_mixed_types():

    ds = xr.Dataset(coords={"lon": [0], "lat": [0]})

    with pytest.raises(ValueError, match="Cannot handle coordinates with mixed types!"):
        mask_to_dataarray(None, ds.lon.values, ds.lon)

    with pytest.raises(ValueError, match="Cannot handle coordinates with mixed types!"):
        mask_to_dataarray(None, ds.lon, ds.lon.values)


def create_test_datasets():

    mask = np.arange(6).reshape(2, 3)
    mask1D = np.arange(2)

    lon2 = [0, 1]
    lon3 = [0, 1, 3]
    lat = [2, 3]

    lon_2D = [[0, 1, 3], [0, 1, 3]]
    lat_2D = [[1, 1, 1], [0, 0, 0]]

    ds0 = xr.Dataset(coords={"lon": lon3, "lat": lat})
    ds1 = xr.Dataset(coords={"longitude": lon3, "latitude": lat})
    ds2 = xr.Dataset(coords={"lon": ("cells", lon2), "lat": ("cells", lat)})
    ds3 = xr.Dataset(
        coords={"lon": ("cells", lon2), "lat": ("cells", lat), "cells": ["a", "b"]}
    )
    ds4 = xr.Dataset(coords={"lon": (("y", "x"), lon_2D), "lat": (("y", "x"), lat_2D)})
    ds5 = xr.Dataset(
        coords={
            "lon": (("y", "x"), lon_2D),
            "lat": (("y", "x"), lat_2D),
            "y": ["y0", "y1"],
            "x": ["x0", "x1", "x2"],
        }
    )

    # pass x coords before the y coords https://github.com/regionmask/regionmask/issues/295
    ds6 = xr.Dataset(
        coords={
            "x": ["x0", "x1", "x2"],
            "y": ["y0", "y1"],
            "lon": (("y", "x"), lon_2D),
            "lat": (("y", "x"), lat_2D),
        }
    )

    DATASETS = (
        (ds0, "lon", "lat", mask),
        (ds1, "longitude", "latitude", mask),
        (ds2, "lon", "lat", mask1D),
        (ds3, "lon", "lat", mask1D),
        (ds4, "lon", "lat", mask),
        (ds5, "lon", "lat", mask),
        (ds6, "lon", "lat", mask),
    )
    return DATASETS


@pytest.mark.parametrize("ds, lon_name, lat_name, mask", create_test_datasets())
def test_mask_to_dataarray_ds_indiv(ds, lon_name, lat_name, mask):

    actual = mask_to_dataarray(mask, ds[lon_name], ds[lat_name])
    expected = ds.coords.to_dataset()
    xr.testing.assert_equal(expected, actual.coords.to_dataset())
    np.testing.assert_equal(mask, actual.values)


@pytest.mark.parametrize("n_regions", [1, 2, 3])
@pytest.mark.parametrize("ds, lon_name, lat_name, mask", create_test_datasets())
def test_mask_to_dataarray_3D_mask(n_regions, ds, lon_name, lat_name, mask):

    mask_3D = np.stack([mask] * n_regions, 0)
    actual = mask_to_dataarray(mask_3D, ds[lon_name], ds[lat_name])
    expected = ds.coords.to_dataset()
    xr.testing.assert_equal(expected, actual.coords.to_dataset())
    np.testing.assert_equal(mask_3D, actual.values)
    assert "region" in actual.dims
    assert actual.region.size == n_regions


@pytest.mark.parametrize("lon", ([0, 1], np.array([0.1, 2.3])))
@pytest.mark.parametrize("lat", ([2, 3], np.array([-1.75, 23.85])))
@pytest.mark.parametrize("lon_name", ("lon", "longitude"))
@pytest.mark.parametrize("lat_name", ("lat", "latitude"))
def test_mask_to_dataarray_numpy_1D(lon, lat, lon_name, lat_name):

    mask = np.arange(4).reshape(2, 2)
    actual = mask_to_dataarray(mask, lon, lat, lon_name, lat_name)
    expected = xr.DataArray(
        mask, dims=(lat_name, lon_name), coords={lat_name: lat, lon_name: lon}
    )
    xr.testing.assert_equal(expected, actual)


@pytest.mark.parametrize("lon_name", ("lon", "longitude", "x"))
@pytest.mark.parametrize("lat_name", ("lat", "latitude", "y"))
def test_mask_to_dataarray_numpy_2D(lon_name, lat_name):

    lon = [[0, 1], [0, 1]]
    lat = [[1, 1], [0, 0]]

    mask = np.arange(4).reshape(2, 2)
    actual = mask_to_dataarray(mask, lon, lat, lon_name, lat_name)
    dims = (f"{lat_name}_idx", f"{lon_name}_idx")
    expected = xr.DataArray(
        mask, dims=dims, coords={lat_name: (dims, lat), lon_name: (dims, lon)}
    )
    xr.testing.assert_equal(expected, actual)


@pytest.mark.parametrize("lon_name", ("lon", "longitude", "x"))
@pytest.mark.parametrize("lat_name", ("lat", "latitude", "y"))
def test_numpy_coords_to_dataarray_1D(lon_name, lat_name):

    lon = [0, 1]
    lat = [0, 1]

    lon_actual, lat_actual = _numpy_coords_to_dataarray(lon, lat, lon_name, lat_name)

    lon_expected = xr.Dataset(coords={lon_name: lon})[lon_name]
    lat_expected = xr.Dataset(coords={lat_name: lat})[lat_name]

    xr.testing.assert_equal(lon_expected, lon_actual)
    xr.testing.assert_equal(lat_expected, lat_actual)


@pytest.mark.parametrize("lon_name", ("lon", "longitude", "x"))
@pytest.mark.parametrize("lat_name", ("lat", "latitude", "y"))
def test_numpy_coords_to_dataarray_2D(lon_name, lat_name):

    lon = [[0, 1]]
    lat = [[0, 1]]

    lon_actual, lat_actual = _numpy_coords_to_dataarray(lon, lat, lon_name, lat_name)

    dims = (f"{lat_name}_idx", f"{lon_name}_idx")
    lon_expected = xr.Dataset(coords={lon_name: (dims, lon)})[lon_name]
    lat_expected = xr.Dataset(coords={lat_name: (dims, lat)})[lat_name]

    xr.testing.assert_equal(lon_expected, lon_actual)
    xr.testing.assert_equal(lat_expected, lat_actual)
