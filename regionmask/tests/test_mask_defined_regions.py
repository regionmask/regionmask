from operator import attrgetter

import numpy as np
import pytest

from regionmask import defined_regions
from regionmask.core.utils import create_lon_lat_dataarray_from_bounds

from . import has_pygeos
from .utils import REGIONS

# =============================================================================

ds_glob_1 = create_lon_lat_dataarray_from_bounds(*(-180, 181, 1), *(90, -91, -1))
ds_glob_2 = create_lon_lat_dataarray_from_bounds(*(-180, 181, 2), *(90, -91, -2))
# for _mask_rasterize_flip
ds_glob_360_2 = create_lon_lat_dataarray_from_bounds(*(0, 361, 2), *(90, -91, -2))
# for _mask_rasterize_split
ds_glob_360_2_part = create_lon_lat_dataarray_from_bounds(*(0, 220, 2), *(90, -91, -2))

DATASETS = [ds_glob_1, ds_glob_2, ds_glob_360_2, ds_glob_360_2_part]


def _test_mask_equal_defined_regions(region, ds, mask_method):

    mask = getattr(region, mask_method)

    rasterize = mask(ds, method="rasterize")
    shapely = mask(ds, method="shapely")

    assert np.allclose(rasterize, shapely, equal_nan=True)

    if has_pygeos:
        pygeos = mask(ds, method="pygeos")

        assert np.allclose(rasterize, pygeos, equal_nan=True)


@pytest.mark.filterwarnings("ignore:pygeos is deprecated")
@pytest.mark.parametrize("defined_region", REGIONS, ids=str)
@pytest.mark.parametrize("ds", DATASETS)
def test_mask_equal_defined_regions(defined_region, ds):

    if defined_region.skip_mask_test:
        pytest.skip(reason=f"Manally skipping {defined_region.region_name}")

    # a loop over DATASETS is not faster - due to caching of the regions
    region = attrgetter(defined_region.region_name)(defined_regions)
    mask_method = "mask_3D" if defined_region.overlap else "mask"
    _test_mask_equal_defined_regions(region, ds, mask_method)
