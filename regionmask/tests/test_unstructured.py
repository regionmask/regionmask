import os
import warnings

import numpy as np
import pytest
import xarray as xr

import regionmask


def rad_to_deg(ds):
    """Convert radian units to deg."""
    with xr.set_options(keep_attrs=True):
        for c in ds.coords:
            if "units" in ds[c].attrs:
                if ds[c].attrs["units"] == "radian":
                    ds[c] = np.rad2deg(ds[c])
                    ds[c].attrs["units"] = "degrees"
                    warnings.warn(f"convert {c} from radian to degrees")
    return ds


@pytest.mark.parametrize(
    "url,lon_name,lat_name,nregions",
    [
        (
            "https://github.com/psyplot/psy-simple/raw/master/tests/icon_test.nc",
            "clon",
            "clat",
            58,
        ),
        (
            "https://github.com/NCAR/geocat-datafiles/raw/main/netcdf_files/MPAS.nc",
            "lonCell",
            "latCell",
            2,
        ),
        (
            "https://github.com/NCAR/geocat-datafiles/raw/main/netcdf_files/camse_unstructured_grid.nc",
            "lon",
            "lat",
            40,
        ),
    ],
)
@pytest.mark.parametrize("method", ["shapely", "pygeos"])
def test_unstructured_icon(url, lon_name, lat_name, nregions, method):
    """Test regionmask for unstructured grids."""
    path = url.split("/")[-1]

    if not os.path.exists(path):
        os.system(f"wget {url}")

    ds = xr.open_dataset(path)
    ds = rad_to_deg(ds)

    region = regionmask.defined_regions.ar6.all

    masked = region.mask(
        ds, lon_name=lon_name, lat_name=lat_name, wrap_lon=False, method=method
    )

    ds_regions = ds.groupby(masked).mean()
    assert ds_regions.region.size == nregions
