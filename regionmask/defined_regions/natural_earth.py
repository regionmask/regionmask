import warnings

import numpy as np
from shapely.geometry import MultiPolygon

from ..core.regions import Regions
from ..core.utils import _flatten_polygons


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
    resolution,
    category,
    name,
    title,
    names="name",
    abbrevs="postal",
    numbers="index",
    coords="geometry",
    query=None,
    combine_coords=False,
    preprocess=None,
):
    """
    create Regions object from naturalearth data

    http://www.naturalearthdata.com

    Parameters
    ----------
    resolution : "10m" | "50m" | "110m"
        Resolution of the dataset.
    category : "cultural" | "physical"
        Natural earth categories.
    name : string
        Name of natural earth dataset.
    title : string
        Displayed text in Regions.
    names : string or list, optional
        Names of the single regions. If string, obtains them from the geopandas
        DataFrame, else uses the provided list. Default: "name".
    abbrevs : string or list, optional
        Abbreviations of the single regions. If string obtains them from the
        geopandas DataFrame, else uses the provided list. Default: "postal".
    numbers : string or list, optional
        Numbers of the single regions. If string obtains them from the geopandas
        DataFrame, else uses the provided list. Default: "index".
    coords : string or list, optional
        Coordinates of the single regions. If string obtains them from the
        geopandas DataFrame, else uses the provided list. Default: "geometry".
    query : None or string, optional
        If given, the geopandas DataFrame is subset with df.query(query).
        Default: None.
    combine_coords : bool, optional
        If False, uses the coords as is, else combines them all to a shapely
        MultiPolygon (used to combine all land Polygons). Default: False.
    """
    import geopandas

    try:
        from cartopy.io import shapereader
    except ImportError as e:
        msg = "cartopy is required to download/ access NaturalEarth data"
        raise ImportError(msg) from e

    # maybe download natural_earth feature and return filename
    shpfilename = shapereader.natural_earth(resolution, category, name)

    # read the file with geopandas
    df = geopandas.read_file(shpfilename, encoding="utf8")

    # subset the whole dataset if necessary
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
        coords, numbers=numbers, names=names, abbrevs=abbrevs, name=title, source=source
    )


# =============================================================================
# =============================================================================


class NaturalEarth:
    """
    class combining all natural_earth features/ geometries

    Because data must be downloaded, we organise it as a class so that
    we only download it on demand.

    """

    def __init__(self):

        self._countries_110 = None
        self._countries_50 = None

        self._us_states_50 = None
        self._us_states_10 = None

        self._land_110 = None
        self._land_50 = None
        self._land_10 = None

        self._ocean_basins_50 = None

    def __repr__(self):
        return "Combines Region Definitions from 'http://www.naturalearthdata.com'."

    @property
    def countries_110(self):
        if self._countries_110 is None:

            opt = dict(
                resolution="110m",
                category="cultural",
                name="admin_0_countries",
                title="Natural Earth Countries: 110m",
            )

            self._countries_110 = _obtain_ne(**opt)
        return self._countries_110

    @property
    def countries_50(self):
        if self._countries_50 is None:

            opt = dict(
                resolution="50m",
                category="cultural",
                name="admin_0_countries",
                title="Natural Earth Countries: 50m",
            )

            self._countries_50 = _obtain_ne(**opt)
        return self._countries_50

    @property
    def us_states_50(self):
        if self._us_states_50 is None:

            opt = dict(
                resolution="50m",
                category="cultural",
                name="admin_1_states_provinces_lakes",
                title="Natural Earth: US States 50m",
                query="admin == 'United States of America'",
            )

            self._us_states_50 = _obtain_ne(**opt)
        return self._us_states_50

    @property
    def us_states_10(self):
        if self._us_states_10 is None:

            opt = dict(
                resolution="10m",
                category="cultural",
                name="admin_1_states_provinces_lakes",
                title="Natural Earth: US States 10m",
                query="admin == 'United States of America'",
            )

            self._us_states_10 = _obtain_ne(**opt)
        return self._us_states_10

    @property
    def land_110(self):
        if self._land_110 is None:

            opt = dict(
                resolution="110m",
                category="physical",
                name="land",
                title="Natural Earth: landmask 110m",
                names=["land"],
                abbrevs=["lnd"],
                numbers=[0],
                combine_coords=True,
            )

            self._land_110 = _obtain_ne(**opt)
        return self._land_110

    @property
    def land_50(self):
        if self._land_50 is None:

            opt = dict(
                resolution="50m",
                category="physical",
                name="land",
                title="Natural Earth: landmask 50m",
                names=["land"],
                abbrevs=["lnd"],
                numbers=[0],
                combine_coords=True,
            )

            self._land_50 = _obtain_ne(**opt)
        return self._land_50

    @property
    def land_10(self):
        if self._land_10 is None:

            opt = dict(
                resolution="10m",
                category="physical",
                name="land",
                title="Natural Earth: landmask 10m",
                names=["land"],
                abbrevs=["lnd"],
                numbers=[0],
                combine_coords=True,
            )

            self._land_10 = _obtain_ne(**opt)
        return self._land_10

    @property
    def ocean_basins_50(self):
        if self._ocean_basins_50 is None:

            opt = dict(
                resolution="50m",
                category="physical",
                name="geography_marine_polys",
                title="Natural Earth: ocean basins 50m",
                names="name",
                abbrevs="name",
                preprocess=_fix_ocean_basins_50,
            )

            regs = _obtain_ne(**opt)

            self._ocean_basins_50 = regs
        return self._ocean_basins_50


class natural_earth_cls(NaturalEarth):
    def __init__(self):

        warnings.warn(
            "The ``natural_earth_cls`` class has been renamed to ``NaturalEarth``"
        )
        super().__init__()


natural_earth = NaturalEarth()


def _fix_ocean_basins_50(df):
    """ocean basins 50 has duplicate entries

    Version 4.0
    - Mediterranean Sea and Ross Sea is split in two - these were renamed to Eastern and
      Western basin

    Version 5.0
    - Mediterranean Sea and Ross Sea is **no longer** split in two.
    - There are two regions named Great Barrier Reef - these are now merged
    - The numbers/ indices are different from Version 4.0!
    """

    names_v4 = {
        14: ("Mediterranean Sea", "Mediterranean Eastern Basin Sea"),
        30: ("Mediterranean Sea", "Mediterranean Western Basin Sea"),
        26: ("Ross Sea", "Ross Eastern Basin Sea"),
        29: ("Ross Sea", "Ross Western Basin Sea"),
    }

    names_v5 = {
        74: "Great Barrier Reef",
        114: "Great Barrier Reef",
    }

    is_v4 = all(df.loc[idx]["name"] == name[0] for idx, name in names_v4.items())
    is_v5 = all(df.loc[idx]["name"] == name for idx, name in names_v5.items())

    if is_v4:

        # rename duplicated regions
        for idx, (__, new_name) in names_v4:
            df.loc[idx, "name"] = new_name

    elif is_v5:
        # merge the two Great Barrier Reef polygons - 74 <<< 114
        poly = df.loc[[74]].union(df.loc[[114]], False).item()
        df.at[74, "geometry"] = poly
        # remove the now merged row
        df.drop(labels=114).reset_index()

    else:
        raise ValueError(
            "Unkown version of the ocean basins 50m data from naturalearth. Please "
            "raise an issue in regionmask."
        )

    return df
