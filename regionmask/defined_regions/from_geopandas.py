import geopandas
import numpy as np
import pandas as pd

from ..core.regions import Regions
from .natural_earth import _maybe_get_column


def _check_duplicates(data, name=""):
    """Checks if `data` has duplicates. Checks column `name` if given and data is DataFrame. If so, raises error. If not, return True."""
    if (
        isinstance(data, (pd.core.frame.DataFrame, geopandas.geodataframe.GeoDataFrame))
        and name != ""
    ):
        data = data[name]
    if len(set(data)) == len(data):
        return True
    else:
        if isinstance(data, list):
            duplicates = set([x for x in data if data.count(x) > 1])
        elif isinstance(data, pd.core.series.Series):
            duplicates = data[data.duplicated(keep=False)]
        else:
            raise ValueError(
                "data not in [list, pd.Series], found {}".format(type(data))
            )
        raise ValueError(
            "{} cannot contain duplicate values, found {}".format(name, duplicates)
        )


def _check_missing(data, name):
    if data.isnull().any():
        raise ValueError("{} cannot contain missing values".format(name))


def _construct_abbrevs(geodataframe, names):
    """Construct unique abbreviations based on geodataframe.names."""
    if names is None:
        raise ValueError(
            "names is None, but should be a valid column name of"
            "geodataframe, choose from {}".format(geodataframe.columns)
        )
    abbrevs = []
    names = geodataframe[names]
    names = names.str.replace("[().]", "")
    for name in names:
        # only one word, take first three letters
        if len(name.split(" ")) == 1:
            abbrev = name[:3]
        else:  # combine initial letters
            abbrev = " ".join(word[0] for word in name.split(" "))
        # if find duplicates, add counter
        counter = 2
        if abbrev in abbrevs:
            while (abbrev + str(counter)) in abbrevs:
                counter += 1
            abbrev = abbrev + str(counter)
        abbrevs.append(abbrev)
    return abbrevs


def from_geopandas(
    geodataframe, numbers=None, names=None, abbrevs=None, name="unnamed", source=None
):
    """
    Create ``regionmask.Region`` from ``geopandas.geodataframe.GeoDataFrame``.

    Parameters
    ----------
    geodataframe : geopandas.geodataframe.GeoDataFrame
        Shapefile to be downloaded. File has extensions ``.shp`` or ``.zip``.
    numbers : str (optional)
        Number of the column in shapefile that gives a region its number.
        This column shouldnt have duplicates. If None (default), takes
        ``geodataframe.index.values``.
    names : str
        Name of the column in shapefile that names a region. Breaks for duplicates.
    abbrevs : str
        Name of the column in shapefile that five a region its abbreviation.
        Breaks for duplicates. If ``construct``, a combination of the first letters of
        region name is taken.
    name : str (optional)
        name of the ``regionmask.Region`` instance created
    source : str (optional)
        source of the shapefile

    Returns
    -------
    regionmask.core.regions.Regions

    """
    # get necessary data for Regions

    if not isinstance(
        geodataframe, (geopandas.geodataframe.GeoDataFrame, geopandas.GeoSeries)
    ):
        raise TypeError("`geodataframe` must be a geopandas.geodataframe.GeoDataFrame")

    if numbers is not None:
        # sort, otherwise breaks
        geodataframe = geodataframe.sort_values(numbers)
        numbers = _maybe_get_column(geodataframe, numbers)
        _check_missing(numbers, "numbers")
        _check_duplicates(numbers, "numbers")
    else:
        numbers = geodataframe.index.values
    # make sure numbers is a list
    numbers = np.array(numbers)

    if names is not None:
        names = _maybe_get_column(geodataframe, names)
        _check_missing(names, "names")
        _check_duplicates(names, "names")

    if abbrevs is not None:
        if abbrevs == "_from_name":
            abbrevs = _construct_abbrevs(geodataframe, names)
        else:
            abbrevs = _maybe_get_column(geodataframe, abbrevs)
        _check_missing(abbrevs, "abbrevs")
        _check_duplicates(abbrevs, "abbrevs")

    outlines = _maybe_get_column(geodataframe, "geometry")

    return Regions(
        outlines,
        numbers=numbers,
        names=names,
        abbrevs=abbrevs,
        name=name,
        source=source,
    )
