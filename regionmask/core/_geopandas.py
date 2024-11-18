from __future__ import annotations

import warnings
from typing import Literal

import geopandas as gp
import numpy as np
import pandas as pd
import xarray as xr

from regionmask.core.mask import _inject_mask_docstring, _mask_2D, _mask_3D
from regionmask.core.regions import Regions


def _check_duplicates(data: pd.Series, name: str) -> None:
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


def _check_missing(data: pd.Series, name: str):
    if data.isnull().any():
        raise ValueError(f"{name} cannot contain missing values")


def _enumerate_duplicates(series, keep=False):
    """append numbers to duplicates."""
    sel = series.duplicated(keep)
    duplicates = series.loc[sel]

    cumcount = duplicates.groupby(duplicates).cumcount().astype(str)

    return series.str.cat(cumcount, na_rep="", join="left")


def _construct_abbrevs(geodataframe: gp.GeoDataFrame, names: str | None) -> pd.Series:
    """Construct unique abbreviations based on geodataframe.names."""
    if names is None:
        raise ValueError(
            "names is None, but should be a valid column name of"
            f"geodataframe, choose from {geodataframe.columns}"
        )

    names_: pd.Series = geodataframe[names]
    names_ = names_.str.replace(r"[(\[\]).]", "", regex=True)
    names_ = names_.str.replace("[/-]", " ", regex=True)
    abbrevs = names_.str.split(" ").map(lambda x: "".join([y[:3] for y in x]))
    abbrevs = _enumerate_duplicates(abbrevs)
    return abbrevs


def from_geopandas(
    geodataframe: gp.GeoDataFrame,
    *,
    numbers: str | None = None,
    names: str | None = None,
    abbrevs: str | None = None,
    name: str = "unnamed",
    source: str | None = None,
    overlap: bool | None = None,
) -> Regions:
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

    overlap : bool | None, default: None
        Indicates if (some of) the regions overlap and determines the behaviour of the
        ``mask`` methods.

        - If True ``mask_3D`` ensures overlapping regions are correctly assigned
          to grid points, while ``mask`` raises an Error (because overlapping
          regions cannot be represented by a 2 dimensional mask).
        - If False assumes non-overlapping regions. Grid points are silently assigned to the
          region with the higher number.
        - If None (default) checks if any gridpoint belongs to more than one region.
          If this is the case ``mask_3D`` correctly assigns them and ``mask``
          raises an Error.

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
    geodataframe: gp.GeoDataFrame,
    numbers: str | None = None,
    names: str | None = None,
    abbrevs: str | None = None,
    name: str = "unnamed",
    source: str | None = None,
    overlap: bool | None = False,
) -> Regions:

    if numbers is not None:
        # sort, otherwise breaks
        geodataframe = geodataframe.sort_values(numbers)
        numbers_ = geodataframe[numbers]
        _check_missing(numbers_, "numbers")
        _check_duplicates(numbers_, "numbers")
    else:
        numbers_ = geodataframe.index.values

    # make sure numbers is an array
    numbers_ = np.array(numbers_)

    names_ = None
    if names is not None:
        names_ = geodataframe[names]
        _check_missing(names_, "names")
        _check_duplicates(names_, "names")

    abbrevs_ = None
    if abbrevs is not None:
        if abbrevs != "_from_name":
            abbrevs_ = geodataframe[abbrevs]
            _check_missing(abbrevs_, "abbrevs")
            _check_duplicates(abbrevs_, "abbrevs")
        else:
            abbrevs_ = _construct_abbrevs(geodataframe, names)

    outlines = geodataframe["geometry"]

    return Regions(
        outlines,
        numbers=numbers_,
        names=names_,
        abbrevs=abbrevs_,
        name=name,
        source=source,
        overlap=overlap,
    )


def _prepare_gdf_for_mask(geodataframe, numbers):

    from geopandas import GeoDataFrame, GeoSeries

    if not isinstance(geodataframe, GeoDataFrame | GeoSeries):
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


def mask_geopandas(
    geodataframe: gp.GeoDataFrame,
    lon_or_obj: np.typing.ArrayLike | xr.DataArray | xr.Dataset,
    lat: np.typing.ArrayLike | xr.DataArray | None = None,
    *,
    numbers: str | None = None,
    method=None,
    wrap_lon: None | bool | Literal[180, 360] = None,
    use_cf: bool | None = None,
    overlap: bool | None = None,
) -> xr.DataArray:

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
        method=method,
        wrap_lon=wrap_lon,
        overlap=overlap,
        use_cf=use_cf,
    )


mask_geopandas.__doc__ = _inject_mask_docstring(which="2D", is_gpd=True)


def mask_3D_geopandas(
    geodataframe: gp.GeoDataFrame,
    lon_or_obj: np.typing.ArrayLike | xr.DataArray | xr.Dataset,
    lat: np.typing.ArrayLike | xr.DataArray | None = None,
    *,
    drop: bool = True,
    numbers: str | None = None,
    method=None,
    wrap_lon: None | bool | Literal[180, 360] = None,
    use_cf: bool | None = None,
    overlap: bool | None = None,
) -> xr.DataArray:

    polygons, numbers = _prepare_gdf_for_mask(geodataframe, numbers=numbers)

    mask_3D = _mask_3D(
        polygons=polygons,
        numbers=numbers,
        lon_or_obj=lon_or_obj,
        lat=lat,
        drop=drop,
        method=method,
        wrap_lon=wrap_lon,
        overlap=overlap,
        use_cf=use_cf,
    )

    return mask_3D


mask_3D_geopandas.__doc__ = _inject_mask_docstring(which="3D", is_gpd=True)
