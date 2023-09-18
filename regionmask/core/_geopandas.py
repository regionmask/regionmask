import warnings

import numpy as np

from ..defined_regions._natural_earth import _maybe_get_column
from ._deprecate import _deprecate_positional_args
from .mask import _inject_mask_docstring, _mask_2D, _mask_3D
from .regions import Regions


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

    """
    if data.duplicated().any():
        duplicates = data[data.duplicated(keep=False)]
        raise ValueError(f"{name} cannot contain duplicate values, found {duplicates}")
    return True


def _check_missing(data, name):
    if data.isnull().any():
        raise ValueError(f"{name} cannot contain missing values")


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
    names = names.str.replace(r"[(\[\]).]", "", regex=True)
    names = names.str.replace("[/-]", " ", regex=True)
    abbrevs = names.str.split(" ").map(lambda x: "".join([y[:3] for y in x]))
    abbrevs = _enumerate_duplicates(abbrevs)
    return abbrevs


@_deprecate_positional_args("0.10.0")
def from_geopandas(
    geodataframe,
    *,
    numbers=None,
    names=None,
    abbrevs=None,
    name="unnamed",
    source=None,
    overlap=False,
):
    """
    Create ``regionmask.Regions`` from a ``geopandas.GeoDataFrame``.

    Parameters
    ----------
    geodataframe : geopandas.GeoDataFrame
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
        Breaks for duplicates. If ``_from_name``, a combination of the first letters
        of region name is taken. If None (default) uses "r0", .., "rN".

    name : str, optional
        name of the ``regionmask.Region`` instance created

    source : str, optional
        source of the shapefile

    overlap : bool, default: False
        Indicates if (some of) the regions overlap. If True ``mask_3D`` will ensure
        overlapping regions are correctly assigned to grid points while ``mask`` will
        error (because overlapping regions cannot be represented by a 2D mask).

        If False (default) assumes non-overlapping regions. Grid points will
        silently be assigned to the region with the higher number (this may change
        in a future version).

        There is (currently) no automatic detection of overlapping regions.

    Returns
    -------
    regionmask.core.regions.Regions

    See Also
    --------
    Regions.to_dataframe, Regions.to_geodataframe, Regions.to_geoseries, Regions.from_geodataframe
    """

    from geopandas import GeoDataFrame

    if not isinstance(geodataframe, (GeoDataFrame)):
        raise TypeError(
            "`geodataframe` must be a geopandas 'GeoDataFrame',"
            f" found {type(geodataframe)}"
        )

    if any(x in geodataframe.attrs for x in ["name", "source", "overlap"]):
        warnings.warn(
            "Use ``regionmask.Regions.from_geodataframe`` to round-trip ``Regions``"
        )

    return _from_geopandas(
        geodataframe,
        numbers=numbers,
        names=names,
        abbrevs=abbrevs,
        name=name,
        source=source,
        overlap=overlap,
    )


def _from_geopandas(
    geodataframe,
    numbers=None,
    names=None,
    abbrevs=None,
    name="unnamed",
    source=None,
    overlap=False,
):

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

    outlines = geodataframe["geometry"]

    return Regions(
        outlines,
        numbers=numbers,
        names=names,
        abbrevs=abbrevs,
        name=name,
        source=source,
        overlap=overlap,
    )


def _prepare_gdf_for_mask(geodataframe, numbers):

    from geopandas import GeoDataFrame, GeoSeries

    if not isinstance(geodataframe, (GeoDataFrame, GeoSeries)):
        raise TypeError("input must be a geopandas 'GeoDataFrame' or 'GeoSeries'")

    polygons = geodataframe.geometry.tolist()

    if numbers is not None:
        numbers = geodataframe[numbers]
        _check_missing(numbers, "numbers")
        _check_duplicates(numbers, "numbers")
    else:
        numbers = geodataframe.index.values

    return polygons, numbers


# TODO: switch order of use_cf and overlap once the deprecation is finished


@_deprecate_positional_args("0.10.0")
def mask_geopandas(
    geodataframe,
    lon_or_obj,
    lat=None,
    *,
    lon_name=None,
    lat_name=None,
    numbers=None,
    method=None,
    wrap_lon=None,
    use_cf=None,
    overlap=None,
):

    if overlap:
        raise ValueError(
            "Creating a 2D mask with overlapping regions yields wrong results. "
            "Please use ``mask_3D_geopandas(...)`` instead. "
            "To create a 2D mask anyway, set ``overlap=False``."
        )

    polygons, numbers = _prepare_gdf_for_mask(geodataframe, numbers=numbers)

    return _mask_2D(
        polygons=polygons,
        numbers=numbers,
        lon_or_obj=lon_or_obj,
        lat=lat,
        lon_name=lon_name,
        lat_name=lat_name,
        method=method,
        wrap_lon=wrap_lon,
        overlap=overlap,
        use_cf=use_cf,
    )


mask_geopandas.__doc__ = _inject_mask_docstring(is_3D=False, is_gpd=True)


@_deprecate_positional_args("0.10.0")
def mask_3D_geopandas(
    geodataframe,
    lon_or_obj,
    lat=None,
    *,
    drop=True,
    lon_name=None,
    lat_name=None,
    numbers=None,
    method=None,
    wrap_lon=None,
    use_cf=None,
    overlap=None,
):

    polygons, numbers = _prepare_gdf_for_mask(geodataframe, numbers=numbers)

    mask_3D = _mask_3D(
        polygons=polygons,
        numbers=numbers,
        lon_or_obj=lon_or_obj,
        lat=lat,
        drop=drop,
        lon_name=lon_name,
        lat_name=lat_name,
        method=method,
        wrap_lon=wrap_lon,
        overlap=overlap,
        use_cf=use_cf,
    )

    return mask_3D


mask_3D_geopandas.__doc__ = _inject_mask_docstring(is_3D=True, is_gpd=True)
