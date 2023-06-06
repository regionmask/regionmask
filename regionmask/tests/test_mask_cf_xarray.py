import pytest
import xarray as xr

from . import has_cf_xarray, requires_cf_xarray
from .utils import (
    dummy_ds,
    dummy_ds_cf,
    dummy_region,
    expected_mask_2D,
    expected_mask_3D,
)

MASK_METHODS = ["mask", "mask_3D"]


@pytest.mark.skipif(has_cf_xarray, reason="must not have cf_xarray")
@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_use_cf_required(method):

    mask = getattr(dummy_region, method)

    with pytest.raises(ImportError, match="cf_xarray required"):
        mask(dummy_ds, use_cf=True)


@requires_cf_xarray
@pytest.mark.parametrize("method", MASK_METHODS)
def test_mask_use_cf_requires_da_ds(method):

    mask = getattr(dummy_region, method)

    with pytest.raises(TypeError, match="Expected a ``Dataset`` or ``DataArray``"):
        mask(dummy_ds.lon.values, use_cf=True)


@requires_cf_xarray
@pytest.mark.parametrize("method", MASK_METHODS)
@pytest.mark.parametrize("coords", ["latitude", "longitude"])
def test_mask_use_cf_no_coords_found(method, coords):

    ds = dummy_ds_cf.copy()
    del ds[coords].attrs["standard_name"]

    mask = getattr(dummy_region, method)

    with pytest.raises(ValueError, match=f"Found no coords for {coords}"):
        mask(ds, use_cf=True)


@requires_cf_xarray
@pytest.mark.parametrize("method", MASK_METHODS)
@pytest.mark.parametrize("drop", ([], "lon", "longitude", ["lon", "longitude"]))
def test_mask_use_cf_ambigous_name(method, drop):

    ds = xr.merge([dummy_ds_cf, dummy_ds])
    ds = ds.drop_vars(drop)

    mask = getattr(dummy_region, method)

    with pytest.raises(ValueError, match="Ambigous name for coordinates"):
        mask(ds, use_cf=None)


@requires_cf_xarray
@pytest.mark.parametrize("method", MASK_METHODS)
@pytest.mark.parametrize("coords, name", (("lon", "longitude"), ("lat", "latitude")))
@pytest.mark.parametrize("use_cf", (True, None))
def test_mask_use_cf_two_cf_coords(method, coords, name, use_cf):

    ds = xr.merge([dummy_ds_cf, dummy_ds])

    ds[coords].attrs["standard_name"] = name

    mask = getattr(dummy_region, method)

    with pytest.raises(ValueError, match=f"Found more than one candidate for '{name}'"):
        mask(ds, use_cf=use_cf)


@requires_cf_xarray
@pytest.mark.parametrize("method", MASK_METHODS)
@pytest.mark.parametrize("use_cf", (True, False))
def test_mask_use_cf_ambigous_name_resolved(method, use_cf):

    ds = xr.merge([dummy_ds_cf, dummy_ds])

    mask = getattr(dummy_region, method)

    result = mask(ds, use_cf=use_cf)

    if use_cf:
        assert "longitude" in result.coords
        assert "latitude" in result.coords
    else:
        assert "lon" in result.coords
        assert "lat" in result.coords


@requires_cf_xarray
@pytest.mark.parametrize("use_cf", (True, None))
def test_mask_use_cf_mask_2D(use_cf):

    result = dummy_region.mask(dummy_ds_cf, use_cf=use_cf)

    expected = expected_mask_2D(lon_name="longitude", lat_name="latitude")
    xr.testing.assert_equal(result, expected)


@requires_cf_xarray
@pytest.mark.parametrize("use_cf", (True, None))
def test_mask_use_cf_mask_3D(use_cf):

    result = dummy_region.mask_3D(dummy_ds_cf, use_cf=use_cf)

    expected = expected_mask_3D(drop=True, lon_name="longitude", lat_name="latitude")
    xr.testing.assert_equal(result, expected)
