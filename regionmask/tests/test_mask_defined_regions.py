from operator import attrgetter

import numpy as np
import pytest

from regionmask import defined_regions
from regionmask.core.utils import create_lon_lat_dataarray_from_bounds

from . import has_pygeos
from .utils import all_defined_regions

# =============================================================================

ds_glob_1 = create_lon_lat_dataarray_from_bounds(*(-180, 181, 1), *(90, -91, -1))
ds_glob_2 = create_lon_lat_dataarray_from_bounds(*(-180, 181, 2), *(90, -91, -2))
# for _mask_rasterize_flip
ds_glob_360_2 = create_lon_lat_dataarray_from_bounds(*(0, 361, 2), *(90, -91, -2))
# for _mask_rasterize_split
ds_glob_360_2_part = create_lon_lat_dataarray_from_bounds(*(0, 220, 2), *(90, -91, -2))


@pytest.mark.parametrize("region_name", all_defined_regions(return_n=False))
@pytest.mark.parametrize(
    "ds", [ds_glob_1, ds_glob_2, ds_glob_360_2, ds_glob_360_2_part]
)
def test_mask_equal_defined_regions(region_name, ds):

    region = attrgetter(region_name)(defined_regions)

    rasterize = region.mask(ds, method="rasterize")
    shapely = region.mask(ds, method="shapely")

    assert np.allclose(rasterize, shapely, equal_nan=True)

    if has_pygeos:
        pygeos = region.mask(ds, method="pygeos")

        assert np.allclose(rasterize, pygeos, equal_nan=True)
