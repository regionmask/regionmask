import numpy as np
import pytest
import xarray as xr

from . import has_pygeos
from .utils import dummy_region, expected_mask_2D


@pytest.mark.skipif(not has_pygeos, reason="Only errors if pygeos is missing")
@pytest.mark.parametrize("method", ["shapely", "pygeos"])
def test_unstructured_dummy(method):
    """Test for unstructured output."""
    lat = [0.5, 0.5, 1.5, 1.5]
    lon = [0.5, 1.5, 0.5, 1.5]
    grid = xr.Dataset(coords={"lon": ("cells", lon), "lat": ("cells", lat)})

    result = dummy_region.mask(grid, method=method)

    expected = expected_mask_2D().flatten()
    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    for c in ["lon", "lat"]:
        assert np.all(np.equal(grid.coords[c], result.coords[c]))
