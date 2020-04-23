import numpy as np

from ..defined_regions.natural_earth import _maybe_get_column
from .regions import Regions
from .mask import _mask

def _check_duplicates(data, name):
    """Checks if `data` has duplicates.

    Parameters
    ----------
    data : pd.core.series.Series
    name : str
        Name of the column (extracted from geopandas.GeoDataFrame) to check duplicates.

    Returns
    -------
    bool : True if no duplicates in data.

    Raises
    ------
    """
    if data.duplicated().any():
        duplicates = data[data.duplicated(keep=False)]
        raise ValueError(
            "{} cannot contain duplicate values, found {}".format(name, duplicates)
        )
    return True


def _check_missing(data, name):
    if data.isnull().any():
        raise ValueError("{} cannot contain missing values".format(name))


def _enumerate_duplicates(series, keep=False):
    """append numbers to duplicates."""
    sel = series.duplicated(keep)
    duplicates = series.loc[sel]

    cumcount = duplicates.groupby(duplicates).cumcount().astype(str)

    return series.str.cat(cumcount, na_rep="", join="left")


def _construct_abbrevs(geodataframe, names):
    """Construct unique abbreviations based on geodataframe.names."""
    if names is None:
        raise ValueError(
            "names is None, but should be a valid column name of"
            "geodataframe, choose from {}".format(geodataframe.columns)
        )
    abbrevs = []
    names = _maybe_get_column(geodataframe, names)
    names = names.str.replace(r"[(\[\]).]", "")
    names = names.str.replace("[/-]", " ")
    abbrevs = names.str.split(" ").map(lambda x: "".join([y[:3] for y in x]))
    abbrevs = _enumerate_duplicates(abbrevs)
    return abbrevs


def from_geopandas(
    geodataframe, numbers=None, names=None, abbrevs=None, name="unnamed", source=None
):
    """
    Create ``regionmask.Region`` from ``geopandas.geodataframe.GeoDataFrame``.

    Parameters
    ----------
    geodataframe : geopandas.geodataframe.GeoDataFrame
        GeoDataFrame to be transformed to a Regions class.
    numbers : str, optional
        Name of the column in geodataframe that gives each region its number.
        This column must not have duplicates. If None (default), takes
        ``geodataframe.index.values``.
    names : str, optional
        Name of the column in shapefile that names a region. Breaks for duplicates.
        If None (default) uses "Region0", .., "RegionN".
    abbrevs : str, optional
        Name of the column in shapefile that five a region its abbreviation.
        Breaks for duplicates. If ``construct``, a combination of the first letters of
        region name is taken. If None (default) uses "r0", .., "rN".
    name : str, optional
        name of the ``regionmask.Region`` instance created
    source : str, optional
        source of the shapefile

    Returns
    -------
    regionmask.core.regions.Regions

    """
    from geopandas import GeoDataFrame

    if not isinstance(geodataframe, (GeoDataFrame)):
        raise TypeError("`geodataframe` must be a geopandas 'GeoDataFrame'")

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


def mask_geopandas(
    geodataframe,
    lon_or_obj,
    lat=None,
    lon_name="lon",
    lat_name="lat",
    method=None,
    wrap_lon=None,
):

    from geopandas import GeoDataFrame, GeoSeries

    if not isinstance(geodataframe, (GeoDataFrame, GeoSeries)):
        raise TypeError("input must be a geopandas 'GeoDataFrame' or 'GeoSeries'")

    if method == "legacy":
        raise ValueError("method 'legacy' not supported in 'mask_geopandas'")

    lon_min = geodataframe.bounds["minx"].min()
    lon_max = geodataframe.bounds["maxx"].max()
    is_180 = regionmask.core.utils._is_180(lon_min, lon_max)

    polygons = geodataframe["geometry"].tolist()

    numbers = geodataframe.index.values.tolist()

    # _mask requires 'dot' attributes - create a dummy class for now...
    class dummy(object):
        def __init__(self, polygons, is_180, numbers):
            self.polygons = polygons
            self.lon_180 = is_180
            self.numbers = numbers

    return _mask(
        dummy(polygons, is_180, numbers),
        lon_or_obj,
        lat=lat,
        lon_name=lon_name,
        lat_name=lat_name,
        method=method,
        xarray=xarray,
        wrap_lon=wrap_lon,
    )
