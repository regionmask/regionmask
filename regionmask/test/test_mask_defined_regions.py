import numpy as np
import pytest

from regionmask import defined_regions
from regionmask.core.utils import create_lon_lat_dataarray_from_bounds

regions = [
    defined_regions.ar6.all,
    defined_regions.ar6.land,
    defined_regions.ar6.ocean,
    defined_regions.giorgi,
    defined_regions.srex,
    defined_regions.natural_earth.countries_110,
    defined_regions.natural_earth.countries_50,
    defined_regions.natural_earth.us_states_50,
    defined_regions.natural_earth.us_states_10,
    defined_regions.natural_earth.land_110,
    defined_regions.natural_earth.ocean_basins_50,
]


# =============================================================================

# TODO: use func(*(-161, -29, 2),  *(75, 13, -2)) after dropping py27
ds_glob_1 = create_lon_lat_dataarray_from_bounds(*(-180, 181, 1) + (90, -91, -1))
ds_glob_2 = create_lon_lat_dataarray_from_bounds(*(-180, 181, 2) + (90, -91, -2))
# for _mask_rasterize_flip
ds_glob_360_2 = create_lon_lat_dataarray_from_bounds(*(0, 361, 2) + (90, -91, -2))
# for _mask_rasterize_split
ds_glob_360_2_part = create_lon_lat_dataarray_from_bounds(*(0, 220, 2) + (90, -91, -2))


@pytest.mark.parametrize("region", regions)
@pytest.mark.parametrize(
    "ds", [ds_glob_1, ds_glob_2, ds_glob_360_2, ds_glob_360_2_part]
)
def test_mask_equal_defined_regions(region, ds):

    rasterize = region.mask(ds, method="rasterize")
    shapely = region.mask(ds, method="shapely")

    assert np.allclose(rasterize, shapely, equal_nan=True)
