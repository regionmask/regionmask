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
                    print(f"convert {c} from rad to deg")
                    ds[c] = np.rad2deg(ds[c])
                    ds[c].attrs["units"] = "degrees"
                    warnings.warn(f"convert {c} from radian to degrees")
    return ds


@pytest.mark.parametrize("method", ["shapely", "pygeos"])
def test_unstructured_icon(method):
    """Test regionmask for unstructured grids."""
    icon_url = "https://github.com/psyplot/psy-simple/raw/master/tests/icon_test.nc"
    icon_path = icon_url.split("/")[-1]

    if not os.path.exists(icon_path):
        os.system(f"wget {icon_url}")

    ds = xr.open_dataset(icon_path).isel(time=0, lev=0)
    ds = rad_to_deg(ds)

    region = regionmask.defined_regions.ar6.ocean

    masked = region.mask(
        ds, lon_name="clon", lat_name="clat", wrap_lon=False, method=method
    )

    ds_regions = ds.groupby(masked).mean()
    assert ds_regions.region.size == 15
