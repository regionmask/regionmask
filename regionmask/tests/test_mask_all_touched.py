# import numpy as np
import pytest

from . import has_gdal_3_7_3
from .utils import dummy_ds, dummy_region

# import shapely

# import regionmask


@pytest.mark.skipif(has_gdal_3_7_3, reason="only errors if gdal<3.7.3")
def test_mask_all_touched_requires_gdal_3_7_3():

    with pytest.raises(
        NotImplementedError,
        match="Using ``all_touched`` requires gdal v3.7.3 or higher.",
    ):
        dummy_region.mask_3D(dummy_ds, all_touched=True)


# def test_mask_all_touched_():


#     p = shapely.box(2.5, 2.5, 10.5, 10.5)
#     lon = np.arange(0, 18, 1)
#     lat = np.arange(15, -1, -1)
#     r = regionmask.Regions([p])
#     r
#     r.mask_3D(lon, lat, all_touched=True)
