from dataclasses import dataclass

import numpy as np
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

dummy_ds_cf = dummy_ds.rename(lat="latitude", lon="longitude")
dummy_ds_cf.latitude.attrs["standard_name"] = "latitude"
dummy_ds_cf.longitude.attrs["standard_name"] = "longitude"


# in this example the result looks:
# | a fill |
# | b fill |


def expected_mask_1D():
    expected = expected_mask_2D()

    return expected.stack(cells=("lat", "lon")).reset_index("cells")


def expected_mask_2D(
    a=0, b=1, fill=np.nan, coords=None, lon_name="lon", lat_name="lat"
):

    mask = np.array([[a, fill], [b, fill]])

    if coords is None:
        coords = {lon_name: _dummy_lon, lat_name: _dummy_lat}

    dims = (lat_name, lon_name)

    flag_values = np.array([a, b])
    flag_meanings = "r0 r1"

    attrs = {"standard_name": "region"}

    attrs["flag_values"] = flag_values
    attrs["flag_meanings"] = flag_meanings

    return xr.DataArray(mask, dims=dims, coords=coords, name="mask", attrs=attrs)


def expected_mask_3D(drop, coords=None, overlap=False, lon_name="lon", lat_name="lat"):

    a = [[True, False], [False, False]]
    b = [[False, False], [True, False]]
    c = [[False, False], [False, False]]

    if overlap:
        mask = np.array([a, a, b, c])
    else:
        mask = np.array([a, b, c])

    if coords is None:
        coords = {lon_name: _dummy_lon, lat_name: _dummy_lat}

    numbers = list(range(4)) if overlap else list(range(3))

    coords.update(
        {
            "region": ("region", numbers),
            "abbrevs": ("region", [f"r{i}" for i in numbers]),
            "names": ("region", [f"Region{i}" for i in numbers]),
        }
    )
    dims = ("region", lat_name, lon_name)
    attrs = {"standard_name": "region"}

    expected = xr.DataArray(mask, coords=coords, dims=dims, name="mask", attrs=attrs)

    return expected.drop_sel(region=numbers[-1]) if drop else expected


@dataclass
class DefinedRegion:

    region_name: str
    n_regions: int
    overlap: bool = False
    skip_mask_test: bool = False
    warn_bounds: bool | None = False
    bounds: dict[str, float] | None = None

    def __str__(self):
        # used as name (`ids`) for parametrize
        return self.region_name


bounds_lon_min_180 = {"min_lon": -180.0}
bounds_lat_min_90 = {"min_lat": -90.0}
bounds_lon_max_180 = {"max_lon": 180.0}
bounds_lat_max_90 = {"max_lat": 90.0}

bounds_lon_global = bounds_lon_min_180 | bounds_lon_max_180
bounds_lat_global = bounds_lat_min_90 | bounds_lat_max_90

bounds_global = bounds_lon_global | bounds_lat_global


bounds_EW_S = bounds_lon_global | bounds_lat_min_90
bounds_EW_N = bounds_lon_global | bounds_lat_max_90


REGIONS = [
    DefinedRegion("ar6.all", 58, bounds=bounds_global),
    DefinedRegion("ar6.land", 46, bounds=bounds_EW_S),
    DefinedRegion("ar6.ocean", 15, bounds=bounds_EW_N),
    DefinedRegion("giorgi", 21, bounds=bounds_lon_max_180),
    DefinedRegion("prudence", 8, True),
    DefinedRegion("srex", 26, bounds=bounds_lon_max_180),
]


states10_bounds = {
    "min_lon": -179.1435033839999,
    "min_lat": 18.906117143000074,
    "max_lon": 179.78093509200005,
    "max_lat": 71.41250234600005,
}

us_states_50_bounds = {
    "min_lon": -178.19451843993753,
    "min_lat": 18.963909185849403,
    "max_lon": -66.98702205598455,
    "max_lat": 71.40768682118639,
}


_REGIONS_NATURAL_EARTH_v4_1_0 = [
    DefinedRegion("natural_earth_v4_1_0.countries_110", 177, bounds=bounds_EW_S),
    DefinedRegion(
        "natural_earth_v4_1_0.countries_50",
        241,
        bounds=bounds_lon_global,
        warn_bounds=True,
    ),
    DefinedRegion("natural_earth_v4_1_0.countries_10", 258, bounds=bounds_EW_S),
    DefinedRegion("natural_earth_v4_1_0.us_states_50", 51, bounds=us_states_50_bounds),
    DefinedRegion("natural_earth_v4_1_0.us_states_10", 51, bounds=states10_bounds),
    DefinedRegion("natural_earth_v4_1_0.land_110", 1, bounds=bounds_EW_S),
    DefinedRegion(
        "natural_earth_v4_1_0.land_50", 1, bounds=bounds_lon_global, warn_bounds=True
    ),
    DefinedRegion("natural_earth_v4_1_0.land_10", 1, bounds=bounds_EW_S),
    DefinedRegion("natural_earth_v4_1_0.ocean_basins_50", 119, warn_bounds=True),
]

_REGIONS_NATURAL_EARTH_v5_0_0 = [
    DefinedRegion("natural_earth_v5_0_0.countries_110", 177, bounds=bounds_EW_S),
    DefinedRegion(
        "natural_earth_v5_0_0.countries_50",
        242,
        bounds=bounds_lon_global,
        warn_bounds=True,
    ),
    DefinedRegion(
        "natural_earth_v5_0_0.countries_10",
        258,
        bounds=bounds_EW_S,
        skip_mask_test=True,
    ),
    DefinedRegion("natural_earth_v5_0_0.us_states_50", 51, bounds=us_states_50_bounds),
    DefinedRegion("natural_earth_v5_0_0.us_states_10", 51, bounds=states10_bounds),
    DefinedRegion("natural_earth_v5_0_0.land_110", 1, bounds=bounds_EW_S),
    DefinedRegion(
        "natural_earth_v5_0_0.land_50", 1, bounds=bounds_lon_global, warn_bounds=True
    ),
    DefinedRegion("natural_earth_v5_0_0.land_10", 1, bounds=bounds_EW_S),
    DefinedRegion("natural_earth_v5_0_0.ocean_basins_50", 117, warn_bounds=True),
]

_REGIONS_NATURAL_EARTH_v5_1_2 = [
    DefinedRegion("natural_earth_v5_1_2.countries_110", 177, bounds=bounds_EW_S),
    DefinedRegion("natural_earth_v5_1_2.countries_50", 242, bounds=bounds_EW_S),
    DefinedRegion(
        "natural_earth_v5_1_2.countries_10",
        258,
        bounds=bounds_EW_S,
        skip_mask_test=True,
    ),
    DefinedRegion("natural_earth_v5_1_2.us_states_50", 51, bounds=us_states_50_bounds),
    DefinedRegion("natural_earth_v5_1_2.us_states_10", 51, bounds=states10_bounds),
    DefinedRegion("natural_earth_v5_1_2.land_110", 1, bounds=bounds_EW_S),
    DefinedRegion("natural_earth_v5_1_2.land_50", 1, bounds=bounds_EW_S),
    DefinedRegion("natural_earth_v5_1_2.land_10", 1, bounds=bounds_EW_S),
    DefinedRegion("natural_earth_v5_1_2.ocean_basins_50", 117, bounds=bounds_EW_N),
]


REGIONS += _REGIONS_NATURAL_EARTH_v5_1_2


REGIONS_ALL = REGIONS.copy()
REGIONS_ALL += _REGIONS_NATURAL_EARTH_v4_1_0
REGIONS_ALL += _REGIONS_NATURAL_EARTH_v5_0_0
