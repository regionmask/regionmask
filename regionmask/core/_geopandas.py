import numpy as np

from ..defined_regions.natural_earth import _maybe_get_column
from .mask import _mask_2D, _mask_3D
from .regions import Regions
from .utils import _is_180


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
        Breaks for duplicates. If ``_from_name``, a combination of the first letters
        of region name is taken. If None (default) uses "r0", .., "rN".
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

    outlines = geodataframe["geometry"]

    return Regions(
        outlines,
        numbers=numbers,
        names=names,
        abbrevs=abbrevs,
        name=name,
        source=source,
    )


def _prepare_gdf_for_mask(geodataframe, method, numbers):

    from geopandas import GeoDataFrame, GeoSeries

    if not isinstance(geodataframe, (GeoDataFrame, GeoSeries)):
        raise TypeError("input must be a geopandas 'GeoDataFrame' or 'GeoSeries'")

    if method == "legacy":
        raise ValueError("method 'legacy' not supported in 'mask_geopandas'")

    lon_min = geodataframe.bounds["minx"].min()
    lon_max = geodataframe.bounds["maxx"].max()
    is_180 = _is_180(lon_min, lon_max)

    polygons = geodataframe.geometry.tolist()

    if numbers is not None:
        numbers = geodataframe[numbers]
        _check_missing(numbers, "numbers")
        _check_duplicates(numbers, "numbers")
    else:
        numbers = geodataframe.index.values

    return polygons, is_180, numbers


def mask_geopandas(
    geodataframe,
    lon_or_obj,
    lat=None,
    lon_name="lon",
    lat_name="lat",
    numbers=None,
    method=None,
    wrap_lon=None,
):
    """
    create a grid as mask of a set of regions for given lat/ lon grid

    Parameters
    ----------
    geodataframe : GeoDataFrame or GeoSeries
        Object providing the region definitions (outlines).
    lon_or_obj : object or array_like
        Can either be a longitude array and then ``lat`` needs to be
        given. Or an object where the longitude and latitude can be
        retrived as: ``lon = lon_or_obj[lon_name]`` and
        ``lat = lon_or_obj[lat_name]``
    lat : array_like, optional
        If ``lon_or_obj`` is a longitude array, the latitude needs to be
        specified here.
    lon_name : str, optional
        Name of longitude in 'lon_or_obj'. Default: 'lon'.
    lat_name : str, optional
        Name of latgitude in 'lon_or_obj'. Default: 'lat'.
    numbers : str, optional
        Name of the column to use for numbering the regions.
        This column must not have duplicates. If None (default),
        takes ``geodataframe.index.values``.
    method : None | "rasterize" | "shapely"
        Method used to determine whether a gridpoint lies in a region.
        Both methods should lead to the same result. If None (default)
        automatically choosen depending on the grid spacing.
    wrap_lon : None | bool | 180 | 360, optional
        Whether to wrap the longitude around, inferred automatically.
        If the regions and the provided longitude do not have the same
        base (i.e. one is -180..180 and the other 0..360) one of them
        must be wrapped. If wrap_lon is None autodetects whether the
        longitude needs to be wrapped. If wrap_lon is False, nothing
        is done. If wrap_lon is True, longitude data is wrapped to 360
        if its minimum is smaller than 0 and wrapped to 180 if its maximum
        is larger than 180.

    Returns
    -------
    mask : ndarray or xarray DataArray

    References
    ----------
    See https://regionmask.readthedocs.io/en/stable/notebooks/method.html

    """

    polygons, is_180, numbers = _prepare_gdf_for_mask(
        geodataframe, method=method, numbers=numbers
    )

    return _mask_2D(
        outlines=polygons,
        regions_is_180=is_180,
        numbers=numbers,
        lon_or_obj=lon_or_obj,
        lat=lat,
        lon_name=lon_name,
        lat_name=lat_name,
        method=method,
        wrap_lon=wrap_lon,
    )


def mask_3D_geopandas(
    geodataframe,
    lon_or_obj,
    lat=None,
    drop=True,
    lon_name="lon",
    lat_name="lat",
    numbers=None,
    method=None,
    wrap_lon=None,
):
    """
    create a 3D boolean mask of a set of regions for the given lat/ lon grid

    Parameters
    ----------
    geodataframe : GeoDataFrame or GeoSeries
        Object providing the region definitions (outlines).
    lon_or_obj : object or array_like
        Can either be a longitude array and then ``lat`` needs to be
        given. Or an object where the longitude and latitude can be
        retrived as: ``lon = lon_or_obj[lon_name]`` and
        ``lat = lon_or_obj[lat_name]``
    lat : array_like, optional
        If ``lon_or_obj`` is a longitude array, the latitude needs to be
        specified here.
    drop : boolean, optional
        If True (default) drops slices where all elements are False (i.e no gridpoints
        are contained in a region). If False returns one slice per region.
    lon_name : str, optional
        Name of longitude in ``lon_or_obj``. Default: "lon".
    lat_name : str, optional
        Name of latgitude in ``lon_or_obj``. Default: "lat"
    numbers : str, optional
        Name of the column to use for numbering the regions.
        This column must not have duplicates. If None (default),
        takes ``geodataframe.index.values``.
    method : None | "rasterize" | "shapely", optional
        Set method used to determine wether a gridpoint lies in a region.
        Both methods should lead to the same result. If None (default)
        automatically choosen depending on the grid spacing.
    wrap_lon : None | bool | 180 | 360, optional
        Whether to wrap the longitude around, should be inferred automatically.
        If the regions and the provided longitude do not have the same
        base (i.e. one is -180..180 and the other 0..360) one of them
        must be wrapped. This can be done with wrap_lon.
        If wrap_lon is None autodetects whether the longitude needs to be
        wrapped. If wrap_lon is False, nothing is done. If wrap_lon is True,
        longitude data is wrapped to 360 if its minimum is smaller
        than 0 and wrapped to 180 if its maximum is larger than 180.

    Returns
    -------
    mask_3D : boolean xarray.DataArray

    """

    polygons, is_180, numbers = _prepare_gdf_for_mask(
        geodataframe, method=method, numbers=numbers
    )

    mask_3D = _mask_3D(
        outlines=polygons,
        regions_is_180=is_180,
        numbers=numbers,
        lon_or_obj=lon_or_obj,
        lat=lat,
        drop=drop,
        lon_name=lon_name,
        lat_name=lat_name,
        method=method,
        wrap_lon=wrap_lon,
    )

    return mask_3D
