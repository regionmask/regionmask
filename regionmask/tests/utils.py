import warnings
from functools import partial
from operator import attrgetter

import numpy as np
import pytest
import xarray as xr

from regionmask import Regions, defined_regions

outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0))
outl2 = ((0, 1), (0, 2), (1, 2.0), (1, 1))
# no gridpoint in outl3
outl3 = ((0, 2), (0, 3), (1, 3.0), (1, 2))

dummy_region = Regions([outl1, outl2, outl3])

_dummy_lon = [0.5, 1.5]
_dummy_lat = [0.5, 1.5]
dummy_ds = xr.Dataset(coords={"lon": _dummy_lon, "lat": _dummy_lat})


# in this example the result looks:
# | a fill |
# | b fill |


def expected_mask_2D(a=0, b=1, fill=np.NaN, flatten=False, coords=None, dims=None):

    mask = np.array([[a, fill], [b, fill]])

    if flatten:
        mask = mask.flatten()

    if coords is None:
        coords = {"lon": _dummy_lon, "lat": _dummy_lat}

    if dims is None:
        dims = ("lat", "lon")

    return xr.DataArray(mask, dims=dims, coords=coords, name="region")


def expected_mask_3D(drop, coords=None):

    a = [[True, False], [False, False]]
    b = [[False, False], [True, False]]
    c = [[False, False], [False, False]]
    mask = np.array([a, b, c])

    if coords is None:
        coords = {"lon": _dummy_lon, "lat": _dummy_lat}

    coords.update(
        {
            "region": ("region", [0, 1, 2]),
            "abbrevs": ("region", ["r0", "r1", "r2"]),
            "names": ("region", ["Region0", "Region1", "Region2"]),
        }
    )
    dims = ("region",) + ("lat", "lon")

    expected = xr.DataArray(mask, coords=coords, dims=dims)

    return expected.isel(region=[0, 1]) if drop else expected


REGIONS = {
    "ar6.all": 58,
    "ar6.land": 46,
    "ar6.ocean": 15,
    "giorgi": 21,
    "prudence": 8,
    "srex": 26,
}

REGIONS_DEPRECATED = {
    "_ar6_pre_revisions.all": 55,
    "_ar6_pre_revisions.land": 43,
    "_ar6_pre_revisions.ocean": 12,
    "_ar6_pre_revisions.separate_pacific": 58,
}

REGIONS_REQUIRING_CARTOPY = {
    "natural_earth.countries_110": 177,
    "natural_earth.countries_50": 242,
    "natural_earth.us_states_50": 51,
    "natural_earth.us_states_10": 51,
    "natural_earth.land_110": 1,
    "natural_earth.land_50": 1,
    "natural_earth.land_10": 1,
    "natural_earth.ocean_basins_50": 117,
}


def get_naturalearth_region_or_skip(monkeypatch, region_name):

    from urllib.request import URLError, urlopen

    import cartopy

    # add a timeout to cartopy.io.urlopen else it can run indefinitely
    monkeypatch.setattr(cartopy.io, "urlopen", partial(urlopen, timeout=5))

    # natural earth data has moved to amazon, older version of cartopy still have the
    # old url
    # https://github.com/SciTools/cartopy/pull/1833
    # https://github.com/nvkelso/natural-earth-vector/issues/445
    # remove again once the minimum cartopy version is v0.19

    url_template = (
        "https://naturalearth.s3.amazonaws.com/"
        "{resolution}_{category}/ne_{resolution}_{name}.zip"
    )

    downloader = cartopy.config["downloaders"][("shapefiles", "natural_earth")]
    monkeypatch.setattr(downloader, "url_template", url_template)

    try:
        region = attrgetter(region_name)(defined_regions)
    except URLError as e:
        warnings.warn(str(e))
        warnings.warn("naturalearth donwload timeout - test not run!")
        pytest.skip()

    return region
