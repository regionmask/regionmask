from __future__ import annotations

import warnings
from collections.abc import Sequence
from typing import Literal

import numpy as np
import shapely
import xarray as xr
from affine import Affine

from regionmask.core.coords import _get_coords
from regionmask.core.utils import (
    _equally_spaced_on_split_lon,
    _find_splitpoint,
    _is_180,
    _is_numeric,
    _sample_coords,
    _total_bounds,
    _wrapAngle,
    equally_spaced,
    unpackbits,
)

_MASK_DOCSTRING_TEMPLATE = """\
create a {nd} {qualifier} mask of a set of regions for the given lat/ lon grid

Parameters
----------
{gp_doc}lon_or_obj : object or array_like
    Can either be a longitude array and then ``lat`` needs to be
    given. Or an object where the longitude and latitude can be
    retrieved from, either using cf_xarray or by the names "lon"
    and "lat". See also ``use_cf``.

lat : array_like, optional
    If ``lon_or_obj`` is a longitude array, the latitude needs to be
    passed.

{drop_doc}{numbers_doc}wrap_lon : None | bool | 180 | 360, default: None
    Whether to wrap the longitude around, inferred automatically.
    If the regions and the provided longitude do not have the same
    base (i.e. one is -180..180 and the other 0..360) one of them
    must be wrapped. This can be achieved with wrap_lon:

    - ``None``: autodetects whether the longitude needs to be wrapped
    - ``False``: nothing is done. This is useful when working with coordinates that are
      not in lat/ lon format.
    - ``True``: longitude data is wrapped to `[0, 360[` if its minimum is smaller than 0
      and wrapped to `[-180, 180[` if its maximum is larger than 180.
    - ``180``: Wraps longitude coordinates to `[-180, 180[`
    - ``360``: Wraps longitude coordinates to `[0, 360[`

{overlap}{flags}use_cf : bool, default: None
    Whether to use ``cf_xarray`` to infer the names of the x and y coordinates. If None
    uses cf_xarray if the coord names are unambiguous. If True requires cf_xarray if
    False does not use cf_xarray.

Returns
-------
mask_{nd} : {dtype} xarray.DataArray

See Also
--------
{see_also}

References
----------
See https://regionmask.readthedocs.io/en/stable/notebooks/method.html
"""

_GP_DOCSTRING = """\
geodataframe : GeoDataFrame or GeoSeries
    Object providing the region definitions (polygons).

"""

_NUMBERS_DOCSTRING = """\
numbers : str, optional
    Name of the column to use for numbering the regions.
    This column must not have duplicates. If None (default),
    takes ``geodataframe.index.values``.

"""


_DROP_DOCSTRING = """\
drop : boolean, default: True
    If True (default) drops slices where all elements are False (i.e no
    gridpoints are contained in a region). If False returns one slice per
    region.

"""

_OVERLAP_DOCSTRING = """\
overlap : bool | None, default: None
    Indicates if (some of) the regions overlap.

    - If True ``mask_3D_geopandas`` ensures overlapping regions are correctly assigned
      to grid points, while ``mask_geopandas`` raises an Error (because overlapping
      regions cannot be represented by a 2 dimensional mask).
    - If False assumes non-overlapping regions. Grid points are silently assigned to the
      region with the higher number.
    - If None (default) checks if any gridpoint belongs to more than one region.
      If this is the case ``mask_3D_geopandas`` correctly assigns them and ``mask_geopandas``
      raises an Error.

"""

_FLAG_DOCSTRING = """\
flag : str, default: "abbrevs"
    Indicates if the "abbrevs" (abbreviations) or "names" should be added as
    `flag_values` and `flag_meanings` to the attributes (`attrs`) of the mask. If None
    nothing is added. Using cf_xarray these can be used to select single
    (``mask.cf == "CNA"``) or multiple (``mask.cf.isin``) regions. Note that spaces are
    replaced by underscores.

"""


def _inject_mask_docstring(*, which, is_gpd):

    qualifier = {"2D": "float", "3D": "boolean", "frac": "fractional"}[which]

    dtype = {"2D": "float", "3D": "boolean", "frac": "float"}[which]

    is_3D = which in ["3D", "frac"]

    nd = "3D" if is_3D else "2D"
    drop_doc = _DROP_DOCSTRING if is_3D else ""
    numbers_doc = _NUMBERS_DOCSTRING if is_gpd else ""
    gp_doc = _GP_DOCSTRING if is_gpd else ""
    overlap = _OVERLAP_DOCSTRING if is_gpd else ""
    flags = _FLAG_DOCSTRING if not (is_gpd or is_3D) else ""

    see_also = {
        "2D": "Regions.mask_3D, Regions.mask_3D_frac_approx",
        "3D": "Regions.mask, Regions.mask_3D_frac_approx",
        "frac": "Regions.mask, Regions.mask_3D",
    }[which]

    mask_docstring = _MASK_DOCSTRING_TEMPLATE.format(
        qualifier=qualifier,
        dtype=dtype,
        nd=nd,
        drop_doc=drop_doc,
        numbers_doc=numbers_doc,
        gp_doc=gp_doc,
        overlap=overlap,
        flags=flags,
        see_also=see_also,
    )

    return mask_docstring


def _mask(
    polygons: Sequence[shapely.Polygon | shapely.MultiPolygon],
    numbers: Sequence[float] | np.ndarray,
    lon_or_obj: np.typing.ArrayLike | xr.DataArray | xr.Dataset,
    lat: np.typing.ArrayLike | xr.DataArray | None = None,
    *,
    method: None | Literal["rasterize", "shapely"] = None,
    wrap_lon: None | bool | Literal[180, 360] = None,
    as_3D: bool = False,
    use_cf: bool | None = None,
) -> xr.DataArray:
    """
    internal function to create a mask
    """

    if not _is_numeric(numbers):
        raise ValueError("'numbers' must be numeric")

    lon, lat = _get_coords(lon_or_obj, lat, "lon", "lat", use_cf)

    # determine whether unstructured grid
    # have to do this before np.asarray
    is_unstructured = False
    if isinstance(lon, xr.DataArray) and isinstance(lat, xr.DataArray):
        if lon.ndim == 1 and lat.ndim == 1:
            if lon.name != lon.dims[0] and lat.name != lat.dims[0]:
                is_unstructured = True

        has_radians = any(c.attrs.get("units") == "radian" for c in (lon, lat))
        if has_radians and wrap_lon is not False:
            warnings.warn(
                "lon or lat is given as 'radian' (see the 'units' attrs). Should they "
                "be converted to degree?"
            )

    lon_arr = np.asarray(lon, dtype=float)
    lat_arr = np.asarray(lat, dtype=float)

    # automatically detect whether wrapping is necessary
    wrap_lon_: Literal[180, 360] | bool
    if wrap_lon is None:

        lon_bounds = _total_bounds(polygons)[::2]

        regions_is_180 = _is_180(
            *lon_bounds, msg_add="Set `wrap_lon=False` to skip this check."
        )

        wrap_lon_ = 180 if regions_is_180 else 360
    else:
        wrap_lon_ = wrap_lon

    if wrap_lon_:
        lon_arr = _wrapAngle(lon_arr, wrap_lon_, is_unstructured=is_unstructured)

    if method == "pygeos":
        raise ValueError("pygeos is no longer supported")

    if method not in (None, "rasterize", "shapely"):
        msg = "Method must be None or one of 'rasterize', and 'shapely'."
        raise ValueError(msg)

    if method is not None:
        # warn private v0.10.0
        warnings.warn(
            "The ``method`` argument is internal and  will be removed in the future."
            " Setting the ``method`` (i.e. backend) should not be necessary. Please"
            " raise an issue if you require it.",
            FutureWarning,
            stacklevel=5,
        )

    if method is None:
        selected_method = _determine_method(lon_arr, lat_arr)
    elif method == "rasterize":
        selected_method = _determine_method(lon_arr, lat_arr)
        if "rasterize" not in selected_method:
            msg = "`lat` and `lon` must be equally spaced to use `method='rasterize'`"
            raise ValueError(msg)
    else:
        selected_method = method

    kwargs = {}
    if selected_method == "rasterize":
        mask_func = _mask_rasterize
    elif selected_method == "rasterize_flip":
        mask_func = _mask_rasterize_flip
    elif selected_method == "rasterize_split":
        mask_func = _mask_rasterize_split
    elif selected_method == "shapely":
        mask_func = _mask_shapely  # type:ignore[assignment]
        kwargs = {"is_unstructured": is_unstructured}

    mask = mask_func(lon_arr, lat_arr, polygons, numbers=numbers, as_3D=as_3D, **kwargs)

    # not False required
    if wrap_lon is not False:
        # treat the points at -180°E/0°E and -90°N
        mask = _mask_edgepoints_shapely(
            mask,
            lon_arr,
            lat_arr,
            polygons,
            numbers,
            is_unstructured=is_unstructured,
            as_3D=as_3D,
        )

    return _mask_to_dataarray(mask, lon, lat)


class InvalidCoordsError(ValueError):
    pass


def _mask_3D_frac_approx(
    polygons: Sequence[shapely.Polygon | shapely.MultiPolygon],
    numbers: Sequence[float] | np.ndarray,
    lon_or_obj: np.typing.ArrayLike | xr.DataArray | xr.Dataset,
    lat: np.typing.ArrayLike | xr.DataArray | None = None,
    *,
    drop: bool = True,
    wrap_lon: None | bool | Literal[180, 360] = None,
    overlap: bool | None = None,
    use_cf: bool | None = None,
) -> xr.DataArray:

    # directly creating 3D masks seems to be faster in general (strangely due to the
    # memory layout of the reshaped mask)
    as_3D = True
    n = 10

    lon_, lat_ = _get_coords(lon_or_obj, lat, "lon", "lat", use_cf)
    lon_arr, lat_arr = np.asarray(lon_), np.asarray(lat_)

    backend = _determine_method(lon_arr, lat_arr)

    if backend not in ("rasterize", "rasterize_flip"):
        raise InvalidCoordsError("'lon' and 'lat' must be 1D and equally spaced.")

    if np.nanmin(lat_) < -90 or np.nanmax(lat_) > 90:
        raise InvalidCoordsError("lat must be between -90 and +90")

    lon_sampled, lat_sampled = _sample_coords(lon_arr), _sample_coords(lat_arr)

    ds_sampled = xr.Dataset(coords={"lon": lon_sampled, "lat": lat_sampled})

    mask_sampled = _mask(
        polygons,
        numbers,
        ds_sampled.lon,
        ds_sampled.lat,
        wrap_lon=wrap_lon,
        as_3D=as_3D,
        use_cf=use_cf,
    ).values

    mask_reshaped = mask_sampled.reshape(-1, lat_arr.size, n, lon_arr.size, n)
    mask = mask_reshaped.mean(axis=(2, 4))

    # maybe fix edges as 90°N/ S
    sel = np.abs(lat_sampled) <= 90
    if wrap_lon is not False and sel.any():

        e1 = mask_reshaped[:, 0].mean(axis=(1, 3), where=sel[:n].reshape(-1, 1, 1))
        e2 = mask_reshaped[:, -1].mean(axis=(1, 3), where=sel[-n:].reshape(-1, 1, 1))

        mask[:, 0] = e1
        mask[:, -1] = e2

    mask = _mask_to_dataarray(mask, lon_, lat_)

    mask_3D = _3D_to_3D_mask(mask, numbers, drop=drop)

    mask_3D.attrs = {"standard_name": "region"}

    return mask_3D


def _mask_2D(
    polygons: Sequence[shapely.Polygon | shapely.MultiPolygon],
    numbers: Sequence[float] | np.ndarray,
    lon_or_obj: np.typing.ArrayLike | xr.DataArray | xr.Dataset,
    lat: np.typing.ArrayLike | xr.DataArray | None = None,
    *,
    method: None | Literal["rasterize", "shapely"] = None,
    wrap_lon: None | bool | Literal[180, 360] = None,
    use_cf: bool | None = None,
    overlap: bool | None = None,
) -> xr.DataArray:

    # NOTE: this is already checked in Regions.mask, and mask_geopandas
    # double check here if this method is ever made public
    # if overlap:
    #     raise ValueError(
    #         "Creating a 2D mask with overlapping regions yields wrong results. "
    #         "Please use ``region.mask_3D(...)`` instead. "
    #         "To create a 2D mask anyway, set ``overlap=False``."
    #     )

    # if as_3D is not explicitly given - set it to True
    as_3D = overlap is None

    mask = _mask(
        polygons=polygons,
        numbers=numbers,
        lon_or_obj=lon_or_obj,
        lat=lat,
        method=method,
        wrap_lon=wrap_lon,
        use_cf=use_cf,
        as_3D=as_3D,
    )

    # only happens for (overlap == None)
    if as_3D:
        mask = _3D_to_2D_mask(mask, numbers)

    if np.all(np.isnan(mask)):
        msg = "No gridpoint belongs to any region. Returning an all-NaN mask."
        warnings.warn(msg, UserWarning, stacklevel=3)

    mask.attrs = {"standard_name": "region"}

    return mask


def _mask_3D(
    polygons: Sequence[shapely.Polygon | shapely.MultiPolygon],
    numbers: Sequence[float] | np.ndarray,
    lon_or_obj: np.typing.ArrayLike | xr.DataArray | xr.Dataset,
    lat: np.typing.ArrayLike | xr.DataArray | None = None,
    *,
    drop: bool = True,
    method: None | Literal["rasterize", "shapely"] = None,
    wrap_lon: None | bool | Literal[180, 360] = None,
    overlap: bool | None = None,
    use_cf: bool | None = None,
) -> xr.DataArray:

    as_3D = overlap or overlap is None

    mask = _mask(
        polygons=polygons,
        numbers=numbers,
        lon_or_obj=lon_or_obj,
        lat=lat,
        method=method,
        wrap_lon=wrap_lon,
        as_3D=as_3D,
        use_cf=use_cf,
    )

    if as_3D:
        mask_3D = _3D_to_3D_mask(mask, numbers, drop=drop)
    else:
        mask_3D = _2D_to_3D_mask(mask, numbers, drop=drop)

    if overlap is None and (mask_3D.sum("region") > 1).any():
        warnings.warn(
            "Detected overlapping regions. As of v0.11.0 these are correctly taken into"
            " account. Note, however, that a different mask is returned than with older"
            " versions of regionmask. To suppress this warning, set `overlap=True` (to"
            " restore the old, incorrect, behaviour, set `overlap=False`)."
        )

    mask_3D.attrs = {"standard_name": "region"}

    return mask_3D


def _2D_to_3D_mask(
    mask: xr.DataArray, numbers: Sequence[float] | np.ndarray, *, drop: bool
) -> xr.DataArray:
    # TODO: unify with _3D_to_3D_mask

    isnan = np.isnan(mask.values)

    numbers_ = np.asarray(numbers)

    if drop:
        numbers_ = np.unique(mask.values[~isnan])
        numbers_ = numbers_.astype(int)

    # if no regions are found return a `0 x lat x lon` mask
    if len(numbers_) == 0:
        mask_3D = mask.expand_dims("region", axis=0).sel(region=slice(0, 0))
        mask_3D = mask_3D.assign_coords(region=("region", numbers_))

        warnings.warn(
            "No gridpoint belongs to any region. Returning an empty mask"
            f" with shape {mask.shape}",
            UserWarning,
            stacklevel=3,
        )

        return mask_3D

    lst_msk = [(mask == num) for num in numbers_]
    mask_3D = xr.concat(lst_msk, dim="region", compat="override", coords="minimal")
    mask_3D = mask_3D.assign_coords(region=("region", numbers_))

    if np.all(isnan):
        warnings.warn(
            "No gridpoint belongs to any region. Returning an all-False mask.",
            UserWarning,
            stacklevel=3,
        )

    return mask_3D


def _3D_to_3D_mask(
    mask_3D: xr.DataArray, numbers: Sequence[float] | np.ndarray, *, drop: bool
) -> xr.DataArray:
    # TODO: unify with _2D_to_3D_mask

    any_masked = mask_3D.any(mask_3D.dims[1:])

    if drop:
        mask_3D = mask_3D.isel(region=any_masked)

        numbers = np.asarray(numbers)[any_masked.values]

    if len(numbers) == 0:

        mask_3D = mask_3D.assign_coords(region=("region", numbers))

        warnings.warn(
            "No gridpoint belongs to any region. Returning an empty mask"
            f" with shape {mask_3D.shape}",
            UserWarning,
            stacklevel=3,
        )
        return mask_3D

    mask_3D = mask_3D.assign_coords(region=("region", numbers))

    if not np.any(any_masked):
        warnings.warn(
            "No gridpoint belongs to any region. Returning an all-False mask.",
            UserWarning,
            stacklevel=3,
        )

    return mask_3D


def _3D_to_2D_mask(mask_3D: xr.DataArray, numbers) -> xr.DataArray:

    # NOTE: very similar to regionmask.core.utils.flatten_3D_mask

    is_masked = mask_3D.sum("region")

    if (is_masked > 1).any():
        raise ValueError(
            "Found overlapping regions for ``overlap=None``. Please create a 3D mask. "
            "You may want to explicitly set ``overlap`` to ``True`` or ``False``."
        )

    # reshape because region is the first dim
    numbers = np.asarray(numbers)

    # I transform so it broadcasts (mask_3D can actually be 2D for unstructured grids,
    # so reshape would need some logic)
    mask_2D = (mask_3D.T * numbers).T.sum("region")

    # mask all gridpoints not belonging to any region

    # older xarray versions do not have `keep_attrs` argument (needed to keep the name)
    # mask_2D = xr.where(is_masked, mask_2D, np.nan, keep_attrs=True)

    mask_2D.values = np.where(is_masked.values, mask_2D, np.nan)

    return mask_2D


def _determine_method(
    lon: np.ndarray, lat: np.ndarray
) -> Literal["rasterize", "rasterize_flip", "rasterize_split", "shapely"]:
    """find method to be used -> prefers faster methods"""

    if equally_spaced(lon, lat):
        return "rasterize"

    if _equally_spaced_on_split_lon(lon) and equally_spaced(lat):

        split_point = _find_splitpoint(lon)
        flipped_lon = np.hstack((lon[split_point:], lon[:split_point]))

        if equally_spaced(flipped_lon):
            return "rasterize_flip"
        else:
            return "rasterize_split"

    return "shapely"


def _mask_to_dataarray(
    mask: np.ndarray,
    lon: np.typing.ArrayLike | xr.DataArray,
    lat: np.typing.ArrayLike | xr.DataArray,
) -> xr.DataArray:

    if sum(isinstance(c, xr.DataArray) for c in (lon, lat)) == 1:
        raise ValueError("Cannot handle coordinates with mixed types!")

    if not isinstance(lon, xr.DataArray) or not isinstance(lat, xr.DataArray):
        lon, lat = _numpy_coords_to_dataarray(lon, lat)

    ds = lat.coords.merge(lon.coords)

    dims = xr.broadcast(lat, lon)[0].dims

    # unstructured grids are 1D
    if mask.ndim - 1 == len(dims):
        dims = ("region",) + dims

    return ds.assign(mask=(dims, mask)).mask


def _numpy_coords_to_dataarray(
    lon: np.typing.ArrayLike, lat: np.typing.ArrayLike
) -> tuple[xr.DataArray, xr.DataArray]:

    lon_name, lat_name = "lon", "lat"

    dims2D = (f"{lat_name}_idx", f"{lon_name}_idx")

    lon = np.asarray(lon)
    dims = dims2D if lon.ndim == 2 else lon_name
    lon_ = xr.Dataset(coords={lon_name: (dims, lon)})[lon_name]

    lat = np.asarray(lat)
    dims = dims2D if lat.ndim == 2 else lat_name
    lat_ = xr.Dataset(coords={lat_name: (dims, lat)})[lat_name]

    return lon_, lat_


def _mask_edgepoints_shapely(
    mask: np.ndarray,
    lon: np.ndarray,
    lat: np.ndarray,
    polygons: Sequence[shapely.Polygon | shapely.MultiPolygon],
    numbers: Sequence[float] | np.ndarray,
    *,
    is_unstructured: bool = False,
    as_3D: bool = False,
) -> np.ndarray:

    LON, LAT, shape = _get_LON_LAT_shape(
        lon, lat, numbers, is_unstructured=is_unstructured, as_3D=as_3D
    )

    if as_3D:
        mask = mask.reshape(mask.shape[0], -1)
        # assume no points are assigned
        mask_unassigned = True
    else:
        mask = mask.flatten()
        mask_unassigned = np.isnan(mask)

    # find points at -180°E/0°E
    if np.nanmin(lon) < 0:
        LON_180W_or_0E = np.isclose(LON, -180.0) & mask_unassigned
    else:
        LON_180W_or_0E = np.isclose(LON, 0.0) & mask_unassigned

    # find points at -90°N
    LAT_90S = np.isclose(LAT, -90) & mask_unassigned

    borderpoints = LON_180W_or_0E | LAT_90S

    # return if there are no unassigned gridpoints at -180°E/0°E and -90°N
    if not borderpoints.any():
        return mask.reshape(shape)

    # add a tiny offset to get a consistent edge behaviour
    LON = LON[borderpoints] - 1 * 10**-8
    LAT = LAT[borderpoints] - 1 * 10**-10

    # wrap points LON_180W_or_0E: -180°E -> 180°E and 0°E -> 360°E
    LON[LON_180W_or_0E[borderpoints]] += 360
    # shift points at -90°N to -89.99...°N
    LAT[LAT_90S[borderpoints]] = -90 + 1 * 10**-10

    # "mask[borderpoints][sel] = number" does not work, need to use np.where
    idx = np.where(borderpoints)[0]

    polys = np.array(polygons).reshape(-1, 1)
    arr = shapely.contains_xy(polys, LON, LAT)

    if as_3D:
        for i in range(len(polygons)):
            mask[i, idx[arr[i, :]]] = True

    else:
        for i in range(len(polygons)):
            mask[idx[arr[i, :]]] = numbers[i]

    return mask.reshape(shape)


def _mask_shapely(
    lon: np.ndarray,
    lat: np.ndarray,
    polygons: Sequence[shapely.Polygon | shapely.MultiPolygon],
    numbers: Sequence[float] | np.ndarray,
    *,
    fill: float = np.nan,
    is_unstructured: bool = False,
    as_3D: bool = False,
) -> np.ndarray:
    """create a mask using shapely.STRtree"""

    lon, lat = _parse_input(lon, lat, polygons, fill, numbers)

    LON, LAT, shape = _get_LON_LAT_shape(
        lon, lat, numbers, is_unstructured=is_unstructured, as_3D=as_3D
    )
    out = _get_out(shape, fill, as_3D=as_3D)

    # add a tiny offset to get a consistent edge behaviour
    LON = LON - 1 * 10**-8
    LAT = LAT - 1 * 10**-10

    # convert to points
    points = shapely.points(LON, LAT)

    tree = shapely.STRtree(points)
    a, b = tree.query(polygons, predicate="contains")

    if as_3D:
        for i in range(len(numbers)):
            out[i, b[a == i]] = True
    else:
        for i, number in enumerate(numbers):
            out[b[a == i]] = number

    return out.reshape(shape)


def _parse_input(
    lon: np.typing.ArrayLike,
    lat: np.typing.ArrayLike,
    polygons: Sequence[shapely.Polygon | shapely.MultiPolygon],
    fill: float,
    numbers: Sequence[float] | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:

    lon = np.asarray(lon)
    lat = np.asarray(lat)

    n_coords = len(polygons)

    if len(numbers) != n_coords:
        raise ValueError("`numbers` and `coords` must have the same length.")

    if fill in numbers:
        raise ValueError("The fill value should not be one of the region numbers.")

    return lon, lat


def _get_LON_LAT_shape(
    lon: np.ndarray,
    lat: np.ndarray,
    numbers: Sequence[float] | np.ndarray,
    *,
    is_unstructured: bool = False,
    as_3D: bool = False,
) -> tuple[np.ndarray, np.ndarray, tuple[int, ...]]:

    if lon.ndim != lat.ndim:
        raise ValueError(
            "Equal number of dimensions required, found "
            f"lon.ndim={lon.ndim} & lat.ndim={lat.ndim}."
        )

    ndim = lon.ndim

    if ndim == 2 and lon.shape != lat.shape:
        raise ValueError(
            "2D lon and lat coordinates need to have the same shape, found "
            f"lon.shape={lon.shape} & lat.shape={lat.shape}."
        )

    if is_unstructured:
        LON, LAT = lon, lat
    elif ndim == 1:
        LON, LAT = np.meshgrid(lon, lat)
    elif ndim == 2:
        LON, LAT = lon, lat
    else:
        raise ValueError(
            f"1D or 2D data required - found {ndim} dimensions. Use `squeeze` to remove"
            " axes of length 1 - e.g. `mask(lon.squeeze(), lat.squeeze())`."
        )

    shape = LON.shape

    if as_3D:
        shape = (len(numbers),) + shape

    LON, LAT = LON.ravel(), LAT.ravel()

    return LON, LAT, shape


def _get_out(shape: tuple[int, ...], fill: float, *, as_3D: bool) -> np.ndarray:
    # create flattened output variable
    if as_3D:
        out = np.full(shape[:1] + (np.prod(shape[1:]).item(),), False, bool)
    else:
        out = np.full(np.prod(shape), fill, float)

    return out


def _transform_from_latlon(
    lon: np.typing.ArrayLike, lat: np.typing.ArrayLike
) -> Affine:
    """perform an affine transformation to the latitude/longitude coordinates"""

    lat = np.asarray(lat)
    lon = np.asarray(lon)

    d_lon = lon[1] - lon[0]
    d_lat = lat[1] - lat[0]

    trans = Affine.translation(lon[0] - d_lon / 2, lat[0] - d_lat / 2)
    scale = Affine.scale(d_lon, d_lat)
    return trans * scale


def _mask_rasterize_flip(
    lon: np.ndarray,
    lat: np.ndarray,
    polygons: Sequence[shapely.Polygon | shapely.MultiPolygon],
    numbers: Sequence[float] | np.ndarray,
    *,
    fill: float = np.nan,
    as_3D=False,
    **kwargs,
) -> np.ndarray:

    split_point = _find_splitpoint(lon)
    flipped_lon = np.hstack((lon[split_point:], lon[:split_point]))

    mask = _mask_rasterize(
        flipped_lon, lat, polygons, numbers=numbers, as_3D=as_3D, **kwargs
    )

    # revert the mask
    return np.concatenate((mask[..., -split_point:], mask[..., :-split_point]), axis=-1)


def _mask_rasterize_split(
    lon: np.ndarray,
    lat: np.ndarray,
    polygons: Sequence[shapely.Polygon | shapely.MultiPolygon],
    numbers: Sequence[float] | np.ndarray,
    *,
    fill=np.nan,
    as_3D=False,
    **kwargs,
) -> np.ndarray:

    split_point = _find_splitpoint(lon)
    lon_l, lon_r = lon[:split_point], lon[split_point:]

    mask_l = _mask_rasterize(
        lon_l, lat, polygons, numbers=numbers, as_3D=as_3D, **kwargs
    )
    mask_r = _mask_rasterize(
        lon_r, lat, polygons, numbers=numbers, as_3D=as_3D, **kwargs
    )

    return np.concatenate((mask_l, mask_r), axis=-1)


def _mask_rasterize(
    lon: np.ndarray,
    lat: np.ndarray,
    polygons: Sequence[shapely.Polygon | shapely.MultiPolygon],
    numbers: Sequence[float] | np.ndarray,
    *,
    fill=np.nan,
    as_3D=False,
    **kwargs,
):

    if as_3D:
        return _mask_rasterize_3D_internal(lon, lat, polygons, **kwargs)

    return _mask_rasterize_internal(lon, lat, polygons, numbers, fill=fill, **kwargs)


def _mask_rasterize_3D_internal(
    lon: np.ndarray,
    lat: np.ndarray,
    polygons: Sequence[shapely.Polygon | shapely.MultiPolygon],
    **kwargs,
) -> np.ndarray:

    # rasterize always returns a flat mask, so we use "bits" and MergeAlg.add to
    # determine overlapping regions. For three regions we use numbers 1, 2, 4 and then
    # 1 -> 1
    # 3 -> 1 & 2
    # 6 -> 2 & 4
    # etc

    import rasterio

    numbers = 2 ** np.arange(32)
    n_polygons = len(polygons)

    out = list()

    # rasterize only supports uint32 -> rasterize in batches of 32
    for i in range(np.ceil(n_polygons / 32).astype(int)):

        sel = slice(32 * i, 32 * (i + 1))

        result = _mask_rasterize_internal(
            lon,
            lat,
            polygons[sel],
            numbers[: min(32, n_polygons - i * 32)],
            fill=0,
            dtype=np.uint32,
            merge_alg=rasterio.enums.MergeAlg.add,
            **kwargs,
        )

        # disentangle the regions
        result = unpackbits(result, 32)

        # the region dim must be the first one
        result = result.transpose([2, 0, 1])
        out.append(result)

    return np.concatenate(out, axis=0)[:n_polygons, ...]


def _mask_rasterize_internal(
    lon: np.typing.ArrayLike,
    lat: np.typing.ArrayLike,
    polygons: Sequence[shapely.Polygon | shapely.MultiPolygon],
    numbers: Sequence[float] | np.ndarray,
    *,
    fill=np.nan,
    **kwargs,
) -> np.ndarray:
    """Rasterize a list of (geometry, fill_value) tuples onto the given coordinates.

    This only works for regularly spaced 1D lat and lon arrays.
    """

    lon, lat = _parse_input(lon, lat, polygons, fill, numbers)

    # subtract a tiny offset: https://github.com/mapbox/rasterio/issues/1844
    lon = lon - 1 * 10**-8
    lat = lat - 1 * 10**-10

    return _mask_rasterize_no_offset(lon, lat, polygons, numbers, fill=fill, **kwargs)


def _mask_rasterize_no_offset(
    lon: np.ndarray,
    lat: np.ndarray,
    polygons: Sequence[shapely.Polygon | shapely.MultiPolygon],
    numbers: Sequence[float] | np.ndarray,
    *,
    fill: float = np.nan,
    dtype: np.typing.DTypeLike = float,
    **kwargs,
) -> np.ndarray:
    """Rasterize a list of (geometry, fill_value) tuples onto the given coordinates.

    This only works for regularly spaced 1D lat and lon arrays.

    for internal use: does not check valitity of input
    """
    # TODO: use only this function once https://github.com/mapbox/rasterio/issues/1844
    # is resolved

    from rasterio import features

    shapes = zip(polygons, numbers, strict=True)

    transform = _transform_from_latlon(lon, lat)
    out_shape = (len(lat), len(lon))

    # can remove once https://github.com/rasterio/rasterio/issues/3043 is fixed
    dtype = dtype if dtype is None else np.dtype(dtype).name

    raster = features.rasterize(
        shapes,
        out_shape=out_shape,
        fill=fill,
        transform=transform,
        dtype=dtype,
        **kwargs,
    )

    return raster
