import warnings
from dataclasses import dataclass
from functools import partial

import numpy as np
import pytest
import xarray as xr

from regionmask import Regions

outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0))
outl2 = ((0, 1), (0, 2), (1, 2.0), (1, 1))
# no gridpoint in outl3
outl3 = ((0, 2), (0, 3), (1, 3.0), (1, 2))

dummy_region = Regions([outl1, outl2, outl3])
dummy_region_overlap = Regions([outl1, outl1, outl2, outl3], overlap=True)

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


def expected_mask_3D(drop, coords=None, overlap=False):

    a = [[True, False], [False, False]]
    b = [[False, False], [True, False]]
    c = [[False, False], [False, False]]

    if overlap:
        mask = np.array([a, a, b, c])
    else:
        mask = np.array([a, b, c])

    if coords is None:
        coords = {"lon": _dummy_lon, "lat": _dummy_lat}

    numbers = list(range(4)) if overlap else list(range(3))

    coords.update(
        {
            "region": ("region", numbers),
            "abbrevs": ("region", [f"r{i}" for i in numbers]),
            "names": ("region", [f"Region{i}" for i in numbers]),
        }
    )
    dims = ("region",) + ("lat", "lon")

    expected = xr.DataArray(mask, coords=coords, dims=dims)

    return expected.drop_sel(region=numbers[-1]) if drop else expected


@dataclass
class DefinedRegion:

    region_name: str
    n_regions: int
    overlap: bool = False


REGIONS = [
    DefinedRegion("ar6.all", 58),
    DefinedRegion("ar6.land", 46),
    DefinedRegion("ar6.ocean", 15),
    DefinedRegion("giorgi", 21),
    DefinedRegion("prudence", 8, True),
    DefinedRegion("srex", 26),
]

_REGIONS_NATURAL_EARTH = [
    # v4.1.0
    DefinedRegion("natural_earth_v4_1_0.countries_110", 177),
    DefinedRegion("natural_earth_v4_1_0.countries_50", 241),
    DefinedRegion("natural_earth_v4_1_0.us_states_50", 51),
    DefinedRegion("natural_earth_v4_1_0.us_states_10", 51),
    DefinedRegion("natural_earth_v4_1_0.land_110", 1),
    DefinedRegion("natural_earth_v4_1_0.land_50", 1),
    DefinedRegion("natural_earth_v4_1_0.land_10", 1),
    DefinedRegion("natural_earth_v4_1_0.ocean_basins_50", 119),
    # v5.0.0
    DefinedRegion("natural_earth_v5_0_0.countries_110", 177),
    DefinedRegion("natural_earth_v5_0_0.countries_50", 242),
    DefinedRegion("natural_earth_v5_0_0.us_states_50", 51),
    DefinedRegion("natural_earth_v5_0_0.us_states_10", 51),
    DefinedRegion("natural_earth_v5_0_0.land_110", 1),
    DefinedRegion("natural_earth_v5_0_0.land_50", 1),
    DefinedRegion("natural_earth_v5_0_0.land_10", 1),
    DefinedRegion("natural_earth_v5_0_0.ocean_basins_50", 117),
]

REGIONS += _REGIONS_NATURAL_EARTH


REGIONS_DEPRECATED = [
    DefinedRegion("_ar6_pre_revisions.all", 55),
    DefinedRegion("_ar6_pre_revisions.land", 43),
    DefinedRegion("_ar6_pre_revisions.ocean", 12),
    DefinedRegion("_ar6_pre_revisions.separate_pacific", 58),
]

REGIONS_REQUIRING_CARTOPY = [
    DefinedRegion("natural_earth.countries_110", 177),
    DefinedRegion("natural_earth.countries_50", 242),
    DefinedRegion("natural_earth.us_states_50", 51),
    DefinedRegion("natural_earth.us_states_10", 51),
    DefinedRegion("natural_earth.land_110", 1),
    DefinedRegion("natural_earth.land_50", 1),
    DefinedRegion("natural_earth.land_10", 1),
    DefinedRegion("natural_earth.ocean_basins_50", 117),
]


def download_naturalearth_region_or_skip(monkeypatch, natural_earth_feature):

    from urllib.request import URLError, urlopen

    import cartopy
    from cartopy.io import shapereader

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
        shapereader.natural_earth(
            natural_earth_feature.resolution,
            natural_earth_feature.category,
            natural_earth_feature.name,
        )
    except URLError as e:
        warnings.warn(str(e))
        warnings.warn("naturalearth donwload timeout - test not run!")
        pytest.skip()
