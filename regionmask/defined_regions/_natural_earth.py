import warnings
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cache

import geopandas
import numpy as np
import pooch
from shapely.geometry import MultiPolygon

from regionmask.defined_regions._ressources import _get_cache_dir

from ..core.regions import Regions
from ..core.utils import _flatten_polygons

try:
    import pyogrio  # noqa: F401

    ENGINE = "pyogrio"
except ImportError:
    ENGINE = "fiona"


def _maybe_get_column(df, colname):
    """return column of the df or not"""

    if isinstance(colname, str):
        # getattr also works for index (df['index'] does not)
        # try lower and upper, github #25
        if hasattr(df, colname):
            return getattr(df, colname)
        elif hasattr(df, colname.swapcase()):
            return getattr(df, colname.swapcase())
        else:
            msg = "'{}' (and '{}') not on the geopandas dataframe."
            raise KeyError(msg.format(colname, colname.swapcase()))

    else:
        return colname


def _obtain_ne(
    shpfilename,
    title,
    names="name",
    abbrevs="postal",
    numbers="index",
    coords="geometry",
    query=None,
    combine_coords=False,
    preprocess=None,
    bbox=None,
):
    """
    create Regions object from naturalearth data

    http://www.naturalearthdata.com

    Parameters
    ----------
    shpfilename : string
        Filename to read.
    title : string
        Displayed text in Regions.
    names : str or list, default: "name"
        Names of the single regions. If string, obtains them from the geopandas
        DataFrame, else uses the provided list.
    abbrevs : str or list, default: "postal".
        Abbreviations of the single regions. If string obtains them from the
        geopandas DataFrame, else uses the provided list.
    numbers : str or list, default: "index".
        Numbers of the single regions. If string obtains them from the geopandas
        DataFrame, else uses the provided list.
    coords : string or list, default: "geometry".
        Coordinates of the single regions. If string obtains them from the
        geopandas DataFrame, else uses the provided list.
    query : None or string, optional
        If given, the geopandas DataFrame is subset with df.query(query).
        Default: None.
    combine_coords : bool, optional
        If False, uses the coords as is, else combines them all to a shapely
        MultiPolygon (used to combine all land Polygons). Default: False.
    preprocess : callable, optional
        If provided, call this function on the geodataframe.
    bbox : tuple | GeoDataFrame or GeoSeries | shapely Geometry, default None
        Filter features by given bounding box, GeoSeries, GeoDataFrame or a shapely
        geometry. See ``geopandas.read_file`` for defails.
    """

    # read the file with geopandas
    df = geopandas.read_file(shpfilename, encoding="utf8", bbox=bbox, engine=ENGINE)

    if query is not None:
        df = df.query(query).reset_index(drop=True)

    if preprocess is not None:
        df = preprocess(df)

    # get necessary data for Regions_cls
    numbers = _maybe_get_column(df, numbers)
    names = _maybe_get_column(df, names)
    abbrevs = _maybe_get_column(df, abbrevs)
    coords = _maybe_get_column(df, coords)

    # create one MultiPolygon of all Polygons (used for land)
    if combine_coords:
        coords = _flatten_polygons(coords)
        coords = [MultiPolygon(coords)]

    # make sure numbers is a list
    numbers = np.array(numbers)

    source = "http://www.naturalearthdata.com"

    return Regions(
        coords,
        numbers=numbers,
        names=names,
        abbrevs=abbrevs,
        name=title,
        source=source,
        overlap=False,
    )


VERSIONS = ["v4.1.0", "v5.0.0", "v5.1.2"]


@dataclass
class _NaturalEarthFeature:

    short_name: str
    title: str
    resolution: str
    category: str
    name: str

    def fetch(self, version):

        if version not in VERSIONS:

            versions = ", ".join(VERSIONS)
            raise ValueError(f"version must be one of {versions}. Got {version}.")

        return _fetch_aws(version, self.resolution, self.category, self.name)

    def shapefilename(self, version):

        fNs = self.fetch(version)

        # the comma is required
        (fN,) = filter(lambda x: x.endswith(".shp"), fNs)

        return fN

    def read(self, version, bbox=None):

        shpfilename = self.shapefilename(version=version)
        df = geopandas.read_file(shpfilename, encoding="utf8", bbox=bbox, engine=ENGINE)
        return df


_countries_110 = _NaturalEarthFeature(
    short_name="countries_110",
    title="Natural Earth Countries: 110m",
    resolution="110m",
    category="cultural",
    name="admin_0_countries",
)
_countries_50 = _NaturalEarthFeature(
    short_name="countries_50",
    title="Natural Earth Countries: 50m",
    resolution="50m",
    category="cultural",
    name="admin_0_countries",
)
_countries_10 = _NaturalEarthFeature(
    short_name="countries_10",
    title="Natural Earth Countries: 10m",
    resolution="10m",
    category="cultural",
    name="admin_0_countries",
)
_us_states_50 = _NaturalEarthFeature(
    short_name="us_states_50",
    title="Natural Earth: US States 50m",
    resolution="50m",
    category="cultural",
    name="admin_1_states_provinces_lakes",
)
_us_states_10 = _NaturalEarthFeature(
    short_name="us_states_10",
    title="Natural Earth: US States 10m",
    resolution="10m",
    category="cultural",
    name="admin_1_states_provinces_lakes",
)
_land_110 = _NaturalEarthFeature(
    short_name="land_110",
    title="Natural Earth: landmask 110m",
    resolution="110m",
    category="physical",
    name="land",
)
_land_50 = _NaturalEarthFeature(
    short_name="land_50",
    title="Natural Earth: landmask 50m",
    resolution="50m",
    category="physical",
    name="land",
)
_land_10 = _NaturalEarthFeature(
    short_name="land_10",
    title="Natural Earth: landmask 10m",
    resolution="10m",
    category="physical",
    name="land",
)
_ocean_basins_50 = _NaturalEarthFeature(
    short_name="ocean_basins_50",
    title="Natural Earth: ocean basins 50m",
    resolution="50m",
    category="physical",
    name="geography_marine_polys",
)


class NaturalEarth:
    """class combining all natural_earth features/ geometries

    Because data must be downloaded, we organise it as a class so that
    we only download it on demand.
    """

    def __init__(self, version, preprocessors):
        self.version = version
        self._preprocessors = preprocessors

    def _obtain_ne(self, feature, **kwargs):
        shapefilename = feature.shapefilename(self.version)

        preprocess = self._preprocessors.get(feature.short_name)

        return _obtain_ne(shapefilename, feature.title, preprocess=preprocess, **kwargs)

    @property
    @cache
    def countries_110(self):

        return self._obtain_ne(_countries_110)

    @property
    @cache
    def countries_50(self):

        return self._obtain_ne(_countries_50)

    @property
    @cache
    def countries_10(self):

        return self._obtain_ne(_countries_10)

    @property
    @cache
    def us_states_50(self):

        opt = dict(
            query="admin == 'United States of America'", bbox=(-180, 18, -45, 72)
        )

        return self._obtain_ne(_us_states_50, **opt)

    @property
    @cache
    def us_states_10(self):

        opt = dict(
            query="admin == 'United States of America'", bbox=(-180, 18, -45, 72)
        )

        return self._obtain_ne(_us_states_10, **opt)

    @property
    @cache
    def land_110(self):

        opt = dict(names=["land"], abbrevs=["lnd"], numbers=[0], combine_coords=True)

        return self._obtain_ne(_land_110, **opt)

    @property
    @cache
    def land_50(self):

        opt = dict(names=["land"], abbrevs=["lnd"], numbers=[0], combine_coords=True)

        return self._obtain_ne(_land_50, **opt)

    @property
    @cache
    def land_10(self):

        opt = dict(names=["land"], abbrevs=["lnd"], numbers=[0], combine_coords=True)

        return self._obtain_ne(_land_10, **opt)

    @property
    @cache
    def ocean_basins_50(self):

        opt = dict(names="name", abbrevs="name")

        return self._obtain_ne(_ocean_basins_50, **opt)

    def __repr__(self):
        return f"Region definitions from 'http://www.naturalearthdata.com' - {self.version}"


def _unify_great_barrier_reef(df, idx1, idx2):

    p1 = df.loc[idx1].geometry
    p2 = df.loc[idx2].geometry

    # merge the two Great Barrier Reef polygons - idx1 <<< idx2
    poly = p1.union(p2)
    df.at[idx1, "geometry"] = poly
    # remove the now merged row
    df = df.drop(labels=idx2).reset_index(drop=True)

    return df


def _snap_polygon(polygon, to, atol, xy_col):
    """

    idx: x or y coordinate
    - 0: x-coord
    - 1: y-coord

    """
    import shapely

    arr = shapely.get_coordinates(polygon)

    sel = np.isclose(arr[:, xy_col], to, atol=atol)
    arr[sel, xy_col] = to

    return shapely.set_coordinates(polygon, arr)


def _snap(df, idx, to, atol, xy_col):

    polygons = df.loc[idx].geometry.tolist()

    polygons = [_snap_polygon(poly, to, atol, xy_col) for poly in polygons]
    df.loc[idx, "geometry"] = polygons

    return df


def _snap_to_90S(df, idx, atol):

    return _snap(df, idx, to=-90, atol=atol, xy_col=1)


def _snap_to_180E(df, idx, atol):

    return _snap(df, idx, to=180, atol=atol, xy_col=0)


def _fix_ocean_basins_50_v4_1_0(df):
    """fix ocean basins 50 for naturalearth v4.1.0

    - Mediterranean Sea and Ross Sea have two parts: renamed to Eastern and Western
    Basin
    """

    warnings.warn(
        "`natural_earth_v4_1_0.ocean_basins_50` does not quite extend to 180°E - it's "
        "recommended to use `natural_earth_v5_1_2.ocean_basins_50` instead. "
        "See https://github.com/regionmask/regionmask/issues/410.",
        stacklevel=5,
    )

    new_names = {
        14: "Mediterranean Sea Eastern Basin",
        30: "Mediterranean Sea Western Basin",
        26: "Ross Sea Eastern Basin",
        29: "Ross Sea Western Basin",
    }

    # rename duplicated regions
    for idx, new_name in new_names.items():
        df.loc[idx, "name"] = new_name

    return df


def _fix_ocean_basins_50_v5_0_0(df):
    """fix ocean basins 50 for naturalearth v5.0.0

    - Mediterranean Sea and Ross Sea is **no longer** split in two.
    - There are two regions named Great Barrier Reef - these are now merged
    - The numbers/ indices are different from Version 4.0!
    """

    warnings.warn(
        "`natural_earth_v5_0_0.ocean_basins_50` does not quite extend to 180°E - it's "
        "recommended to use `natural_earth_v5_1_2.ocean_basins_50` instead. "
        "See https://github.com/regionmask/regionmask/issues/410.",
        stacklevel=5,
    )

    return _unify_great_barrier_reef(df, 74, 114)


def _fix_ocean_basins_50_v5_1_2(df):
    """fix ocean basins 50 for naturalearth v5.1.2

    - Sea of Japan & Korea Strait geometries are different
    - the rest (including the split of the Great Barrier Reef) is as in v5.0.0
    - but the regions are ordered different
    """

    df = _unify_great_barrier_reef(df, 74, 113)

    # fix regions not extending to 180°E
    idx = df.loc[df.bounds["maxx"] > 179].index.tolist()
    df = _snap_to_180E(df, idx, atol=1.03e-4)

    return df


def _warn_countries_50(df):

    warnings.warn(
        "`land_50` of `natural_earth_v4_1_0` and `natural_earth_v5_0_0` does not quite "
        "extend to 90°S - it's recommended to use `natural_earth_v5_1_2` instead. "
        "See https://github.com/regionmask/regionmask/issues/487",
        stacklevel=5,
    )

    return df


def _warn_land_50(df):

    warnings.warn(
        "`land_50` of `natural_earth_v4_1_0` and `natural_earth_v5_0_0` does not quite "
        "extend to 90°S - it's recommended to use `natural_earth_v5_1_2` instead. "
        "See https://github.com/regionmask/regionmask/issues/487",
        stacklevel=5,
    )

    return df


def _fix_land_50(df):

    return _snap_to_90S(df, [1378], 1.1e-3)


def _fix_countries_50(df):

    return _snap_to_90S(df, [239], 1.1e-3)


natural_earth_v4_1_0 = NaturalEarth(
    "v4.1.0",
    preprocessors={
        "ocean_basins_50": _fix_ocean_basins_50_v4_1_0,
        "land_50": _warn_land_50,
        "countries_50": _warn_countries_50,
    },
)
natural_earth_v5_0_0 = NaturalEarth(
    "v5.0.0",
    preprocessors={
        "ocean_basins_50": _fix_ocean_basins_50_v5_0_0,
        "land_50": _warn_land_50,
        "countries_50": _warn_countries_50,
    },
)
natural_earth_v5_1_2 = NaturalEarth(
    "v5.1.2",
    preprocessors={
        "ocean_basins_50": _fix_ocean_basins_50_v5_1_2,
        "land_50": _fix_land_50,
        "countries_50": _fix_countries_50,
    },
)


@contextmanager
def set_pooch_log_level():

    logger = pooch.get_logger()
    level = logger.level
    logger.setLevel("WARNING")

    try:
        yield
    finally:
        logger.setLevel(level)


def _fetch_aws(version, resolution, category, name):

    base_url = "https://naturalearth.s3.amazonaws.com"

    bname = f"ne_{resolution}_{name}"
    fname = f"{bname}.zip"

    aws_version = version.replace("v", "")
    # the 4.1.0 data is available under 4.1.1
    aws_version = aws_version.replace("4.1.0", "4.1.1")

    url = f"{base_url}/{aws_version}/{resolution}_{category}/{bname}.zip"

    path = _get_cache_dir() / f"natural_earth/{version}"
    unzipper = pooch.Unzip(extract_dir=bname)

    with set_pooch_log_level():
        fNs = pooch.retrieve(
            url,
            None,
            fname=fname,
            path=path,
            processor=unzipper,
        )

    return fNs
