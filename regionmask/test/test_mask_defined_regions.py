import numpy as np

from regionmask import Regions

import pytest

import xarray as xr
from affine import Affine
from shapely.geometry import Polygon

from regionmask.core.utils import create_lon_lat_dataarray_from_bounds
from regionmask import defined_regions


regions = [
    defined_regions.giorgi,
    defined_regions.srex,
    defined_regions.natural_earth.countries_110,
    defined_regions.natural_earth.countries_50,
    defined_regions.natural_earth.us_states_50,
    defined_regions.natural_earth.us_states_10,
    defined_regions.natural_earth.land_110,
]


# =============================================================================

# TODO: use func(*(-161, -29, 2),  *(75, 13, -2)) after dropping py27
ds_glob_1 = create_lon_lat_dataarray_from_bounds(*(-180, 181, 1) + (90, -91, -1))
ds_glob_2 = create_lon_lat_dataarray_from_bounds(*(-180, 181, 2) + (90, -91, -2))


@pytest.mark.parametrize("region", regions)
@pytest.mark.parametrize("ds", [ds_glob_1, ds_glob_2])
def test_mask_equal_defined_regions(region, ds):

    rasterize = region.mask(ds, method="rasterize")
    shapely = region.mask(ds, method="shapely")

    assert np.allclose(rasterize, shapely, equal_nan=True)
