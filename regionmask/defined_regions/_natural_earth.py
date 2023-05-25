import os
import warnings
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass

import numpy as np
import pooch
from packaging.version import Version
from shapely.geometry import MultiPolygon

from regionmask.defined_regions._ressources import _get_cache_dir

from ..core.regions import Regions
from ..core.utils import _flatten_polygons

try:
    import pyogrio  # noqa: F401

    engine = "pyogrio"
except ImportError:
    engine = "fiona"

# TODO: remove deprecated (v0.9.0) natural_earth class and instance & clean up

ALTERNATIVE = (
    "Please use ``regionmask.defined_regions.natural_earth_v4_1_0`` or "
    "``regionmask.defined_regions.natural_earth_v5_0_0`` instead"
)


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

    import geopandas

    # read the file with geopandas
    df = geopandas.read_file(shpfilename, encoding="utf8", bbox=bbox, engine=engine)

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


VERSIONS = ["v4.1.0", "v5.0.0"]


@dataclass
class _NaturalEarthFeature:

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


_countries_110 = _NaturalEarthFeature(
    resolution="110m",
    category="cultural",
    name="admin_0_countries",
)
_countries_50 = _NaturalEarthFeature(
    resolution="50m",
    category="cultural",
    name="admin_0_countries",
)
_countries_10 = _NaturalEarthFeature(
    resolution="10m",
    category="cultural",
    name="admin_0_countries",
)
_us_states_50 = _NaturalEarthFeature(
    resolution="50m",
    category="cultural",
    name="admin_1_states_provinces_lakes",
)
_us_states_10 = _NaturalEarthFeature(
    resolution="10m",
    category="cultural",
    name="admin_1_states_provinces_lakes",
)
_land_110 = _NaturalEarthFeature(
    resolution="110m",
    category="physical",
    name="land",
)
_land_50 = _NaturalEarthFeature(
    resolution="50m",
    category="physical",
    name="land",
)
_land_10 = _NaturalEarthFeature(
    resolution="10m",
    category="physical",
    name="land",
)
_ocean_basins_50 = _NaturalEarthFeature(
    resolution="50m",
    category="physical",
    name="geography_marine_polys",
)


class NaturalEarth(ABC):
    """class combining all natural_earth features/ geometries

    Because data must be downloaded, we organise it as a class so that
    we only download it on demand.
    """

    def __init__(self):

        self._countries_110 = None
        self._countries_50 = None
        self._countries_10 = None

        self._us_states_50 = None
        self._us_states_10 = None

        self._land_110 = None
        self._land_50 = None
        self._land_10 = None

        self._ocean_basins_50 = None

    @abstractmethod
    def _obtain_ne(self, natural_earth_feature, **kwargs):
        ...

    @property
    def countries_110(self):
        if self._countries_110 is None:

            opt = dict(title="Natural Earth Countries: 110m")

            self._countries_110 = self._obtain_ne(_countries_110, **opt)

        return self._countries_110

    @property
    def countries_50(self):
        if self._countries_50 is None:

            opt = dict(title="Natural Earth Countries: 50m")

            self._countries_50 = self._obtain_ne(_countries_50, **opt)

        return self._countries_50

    @property
    def countries_10(self):
        if self._countries_10 is None:
            opt = dict(title="Natural Earth Countries: 10m")

            self._countries_10 = self._obtain_ne(_countries_10, **opt)

        return self._countries_10

    @property
    def us_states_50(self):
        if self._us_states_50 is None:

            opt = dict(
                title="Natural Earth: US States 50m",
                query="admin == 'United States of America'",
                bbox=(-180, 18, -45, 72),
            )

            self._us_states_50 = self._obtain_ne(_us_states_50, **opt)
        return self._us_states_50

    @property
    def us_states_10(self):
        if self._us_states_10 is None:

            opt = dict(
                title="Natural Earth: US States 10m",
                query="admin == 'United States of America'",
                bbox=(-180, 18, -45, 72),
            )

            self._us_states_10 = self._obtain_ne(_us_states_10, **opt)
        return self._us_states_10

    @property
    def land_110(self):
        if self._land_110 is None:

            opt = dict(
                title="Natural Earth: landmask 110m",
                names=["land"],
                abbrevs=["lnd"],
                numbers=[0],
                combine_coords=True,
            )

            self._land_110 = self._obtain_ne(_land_110, **opt)
        return self._land_110

    @property
    def land_50(self):
        if self._land_50 is None:

            opt = dict(
                title="Natural Earth: landmask 50m",
                names=["land"],
                abbrevs=["lnd"],
                numbers=[0],
                combine_coords=True,
            )

            self._land_50 = self._obtain_ne(_land_50, **opt)
        return self._land_50

    @property
    def land_10(self):
        if self._land_10 is None:

            opt = dict(
                title="Natural Earth: landmask 10m",
                names=["land"],
                abbrevs=["lnd"],
                numbers=[0],
                combine_coords=True,
            )

            self._land_10 = self._obtain_ne(_land_10, **opt)
        return self._land_10

    @property
    def ocean_basins_50(self):
        if self._ocean_basins_50 is None:

            opt = dict(
                title="Natural Earth: ocean basins 50m",
                names="name",
                abbrevs="name",
                preprocess=self._fix_ocean_basins_50,
            )

            regs = self._obtain_ne(_ocean_basins_50, **opt)

            self._ocean_basins_50 = regs

        return self._ocean_basins_50

    def __repr__(self):
        return "Region Definitions from 'http://www.naturalearthdata.com'."


def _fix_ocean_basins_50_cartopy(self, df):
    """ocean basins 50 has duplicate entries"""

    names_v4_1_0 = {
        14: "Mediterranean Sea",
        30: "Mediterranean Sea",
        26: "Ross Sea",
        29: "Ross Sea",
    }

    names_v5_0_0 = {
        74: "Great Barrier Reef",
        114: "Great Barrier Reef",
    }

    names_v5_1_2 = {
        74: "Great Barrier Reef",
        113: "Great Barrier Reef",
    }

    is_v4_1_0 = all(df.loc[idx]["name"] == name for idx, name in names_v4_1_0.items())
    is_v5_0_0 = all(df.loc[idx]["name"] == name for idx, name in names_v5_0_0.items())
    is_v5_1_2 = all(df.loc[idx]["name"] == name for idx, name in names_v5_1_2.items())

    if is_v4_1_0:
        df = _fix_ocean_basins_50_v4_1_0(self, df)
    elif is_v5_0_0:
        df = _fix_ocean_basins_50_v5_0_0(self, df)
    elif is_v5_1_2:
        df = _fix_ocean_basins_50_v5_1_2(self, df)
    else:
        raise ValueError(
            "Unknown version of the ocean basins 50m data from naturalearth. "
            f"{ALTERNATIVE}."
        )

    return df


def _fix_ocean_basins_50_v4_1_0(self, df):
    """fix ocean basins 50 for naturalearth v4.1.0

    - Mediterranean Sea and Ross Sea have two parts: renamed to Eastern and Western
      Basin
    """

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


def _unify__great_barrier_reef(df, idx1, idx2):

    p1 = df.loc[idx1].geometry
    p2 = df.loc[idx2].geometry

    # merge the two Great Barrier Reef polygons - idx1 <<< idx2
    poly = p1.union(p2)
    df.at[idx1, "geometry"] = poly
    # remove the now merged row
    df = df.drop(labels=idx2).reset_index()

    return df


def _fix_ocean_basins_50_v5_0_0(self, df):
    """fix ocean basins 50 for naturalearth v5.0.0

    - Mediterranean Sea and Ross Sea is **no longer** split in two.
    - There are two regions named Great Barrier Reef - these are now merged
    - The numbers/ indices are different from Version 4.0!
    """

    return _unify__great_barrier_reef(df, 74, 114)


def _fix_ocean_basins_50_v5_1_2(self, df):
    """fix ocean basins 50 for naturalearth v5.1.2

    - Sea of Japan & Korea Strait geometries are different
    - the rest (including the split of the Great Barrier Reef) is as in v5.0.0
    - but the regions are ordered different
    """

    return _unify__great_barrier_reef(df, 74, 113)


class NaturalEarthCartopy(NaturalEarth):

    _fix_ocean_basins_50 = _fix_ocean_basins_50_cartopy

    def _obtain_ne(self, natural_earth_feature, **kwargs):

        shapefilename = _get_shapefilename_cartopy(
            natural_earth_feature.resolution,
            natural_earth_feature.category,
            natural_earth_feature.name,
        )

        return _obtain_ne(shapefilename, **kwargs)


class NaturalEarth_v4_1_0(NaturalEarth):

    _fix_ocean_basins_50 = _fix_ocean_basins_50_v4_1_0
    version = "v4.1.0"

    def _obtain_ne(self, natural_earth_feature, **kwargs):
        shapefilename = natural_earth_feature.shapefilename(self.version)
        return _obtain_ne(shapefilename, **kwargs)


class NaturalEarth_v5_0_0(NaturalEarth):

    _fix_ocean_basins_50 = _fix_ocean_basins_50_v5_0_0
    version = "v5.0.0"

    def _obtain_ne(self, natural_earth_feature, **kwargs):
        shapefilename = natural_earth_feature.shapefilename(self.version)
        return _obtain_ne(shapefilename, **kwargs)


natural_earth = NaturalEarthCartopy()

natural_earth_v4_1_0 = NaturalEarth_v4_1_0()
natural_earth_v5_0_0 = NaturalEarth_v5_0_0()


def _get_shapefilename_cartopy(resolution, category, name):

    try:
        import cartopy
    except ImportError as e:
        msg = (
            "``regionmask.defined_regions.natural_earth`` requires cartopy and is "
            f"deprecated.\n{ALTERNATIVE} (which do not require cartopy)."
        )
        raise ImportError(msg) from e

    _cartopy_data_dir = cartopy.config["data_dir"]

    # check if cartopy has already downloaded the file
    cartopy_file = os.path.join(
        _cartopy_data_dir,
        "shapefiles",
        "natural_earth",
        f"{category}",
        f"ne_{resolution}_{name}.shp",
    )

    if not os.path.exists(cartopy_file):
        raise ValueError(
            "``regionmask.defined_regions.natural_earth`` is deprecated. Will not "
            f"download new files via this interface. {ALTERNATIVE}."
        )

    warnings.warn(
        f"``regionmask.defined_regions.natural_earth`` is deprecated. {ALTERNATIVE}.",
        FutureWarning,
    )

    return cartopy_file


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

    if Version(pooch.__version__) < Version("1.4"):
        # extract_dir not available
        unzipper = pooch.Unzip()
    else:
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
