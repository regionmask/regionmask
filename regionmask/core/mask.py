import warnings

import numpy as np
import xarray as xr

from .utils import (
    _equally_spaced_on_split_lon,
    _find_splitpoint,
    _is_180,
    _is_numeric,
    _wrapAngle,
    equally_spaced,
)

try:
    import pygeos

    has_pygeos = True
except ModuleNotFoundError:
    has_pygeos = False


_MASK_DOCSTRING_TEMPLATE = """\
create a {nd} {dtype} mask of a set of regions for the given lat/ lon grid

Parameters
----------
{gp_doc}lon_or_obj : object or array_like
    Can either be a longitude array and then ``lat`` needs to be
    given. Or an object where the longitude and latitude can be
    retrieved as: ``lon = lon_or_obj[lon_name]`` and
    ``lat = lon_or_obj[lat_name]``.
lat : array_like, optional
    If ``lon_or_obj`` is a longitude array, the latitude needs to be
    specified here.
{drop_doc}lon_name : str, optional
    Name of longitude in ``lon_or_obj``, default: "lon".
lat_name : str, optional
    Name of latgitude in ``lon_or_obj``, default: "lat"
{numbers_doc}method : "rasterize" | "shapely" | "pygeos". Default: None
    Method used to determine whether a gridpoint lies in a region.
    All methods lead to the same mask. If None (default)
    autoselects the method.
wrap_lon : bool | 180 | 360, optional
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
{overlap}

Returns
-------
mask_{nd} : {dtype} xarray.DataArray

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
overlap : bool, default: False
    Indicates if (some of) the regions overlap. If True ``mask_3D_geopandas`` will
    ensure overlapping regions are correctly assigned to grid points.

    If False (default) assumes non-overlapping regions. Grid points will silently be
    assigned to the region with the higher number (this may change in a future version).

    There is (currently) no automatic detection of overlapping regions.
"""


def _inject_mask_docstring(is_3D, gp_method):

    dtype = "float" if is_3D else "boolean"
    nd = "3D" if is_3D else "2D"
    drop_doc = _DROP_DOCSTRING if is_3D else ""
    numbers_doc = _NUMBERS_DOCSTRING if gp_method else ""
    gp_doc = _GP_DOCSTRING if gp_method else ""
    overlap = _OVERLAP_DOCSTRING if (gp_method and is_3D) else ""

    mask_docstring = _MASK_DOCSTRING_TEMPLATE.format(
        dtype=dtype,
        nd=nd,
        drop_doc=drop_doc,
        numbers_doc=numbers_doc,
        gp_doc=gp_doc,
        overlap=overlap,
    )

    return mask_docstring


def _mask(
    outlines,
    lon_bounds,
    numbers,
    lon_or_obj,
    lat=None,
    lon_name="lon",
    lat_name="lat",
    method=None,
    wrap_lon=None,
    as_3D=False,
):
    """
    internal function to create a mask
    """

    if not _is_numeric(numbers):
        raise ValueError("'numbers' must be numeric")

    lat_orig = lat
    lon, lat = _extract_lon_lat(lon_or_obj, lat, lon_name, lat_name)

    # determine whether unstructured grid
    # have to do this before np.asarray
    is_unstructured = False
    if isinstance(lon, xr.DataArray) and isinstance(lat, xr.DataArray):
        if len(lon.dims) == 1 and len(lat.dims) == 1:
            if lon.name != lon.dims[0] and lat.name != lat.dims[0]:
                is_unstructured = True

    lon = np.asarray(lon)
    lat = np.asarray(lat)

    # automatically detect whether wrapping is necessary
    if wrap_lon is None:
        msg_add = "Set `wrap_lon=False` to skip this check."
        regions_is_180 = _is_180(*lon_bounds, msg_add=msg_add)

        wrap_lon_ = 180 if regions_is_180 else 360
    else:
        wrap_lon_ = wrap_lon

    if wrap_lon_:
        lon = _wrapAngle(lon, wrap_lon_, is_unstructured=is_unstructured)

    if method not in (None, "rasterize", "shapely", "pygeos"):
        msg = "Method must be None or one of 'rasterize', 'shapely' and 'pygeos'."
        raise ValueError(msg)

    if method is None:
        method = _determine_method(lon, lat)
    elif method == "rasterize":
        method = _determine_method(lon, lat)
        if "rasterize" not in method:
            msg = "`lat` and `lon` must be equally spaced to use `method='rasterize'`"
            raise ValueError(msg)
    elif method == "pygeos" and not has_pygeos:
        raise ModuleNotFoundError("No module named 'pygeos'")

    kwargs = {}
    if method == "rasterize":
        mask_func = _mask_rasterize
    elif method == "rasterize_flip":
        mask_func = _mask_rasterize_flip
    elif method == "rasterize_split":
        mask_func = _mask_rasterize_split
    elif method == "pygeos":
        mask_func = _mask_pygeos
        kwargs = {"is_unstructured": is_unstructured, "as_3D": as_3D}
    elif method == "shapely":
        mask_func = _mask_shapely
        kwargs = {"is_unstructured": is_unstructured, "as_3D": as_3D}

    if as_3D and method not in ["shapely", "pygeos"]:
        masks = list()
        for outline, number in zip(outlines, numbers):
            mask = mask_func(lon, lat, [outline], numbers=[number], **kwargs)
            masks.append(mask == number)

        mask = np.stack(masks, axis=0)

    else:
        mask = mask_func(lon, lat, outlines, numbers=numbers, **kwargs)

    # not False required
    if wrap_lon is not False:
        # treat the points at -180°E/0°E and -90°N
        mask = _mask_edgepoints_shapely(
            mask,
            lon,
            lat,
            outlines,
            numbers,
            is_unstructured=is_unstructured,
            as_3D=as_3D,
        )

    return mask_to_dataarray(mask, lon_or_obj, lat_orig, lon_name, lat_name)


def _mask_2D(
    outlines,
    lon_bounds,
    numbers,
    lon_or_obj,
    lat=None,
    lon_name="lon",
    lat_name="lat",
    method=None,
    wrap_lon=None,
):

    mask = _mask(
        outlines=outlines,
        lon_bounds=lon_bounds,
        numbers=numbers,
        lon_or_obj=lon_or_obj,
        lat=lat,
        lon_name=lon_name,
        lat_name=lat_name,
        method=method,
        wrap_lon=wrap_lon,
    )

    if np.all(np.isnan(mask)):
        msg = "No gridpoint belongs to any region. Returning an all-NaN mask."
        warnings.warn(msg, UserWarning, stacklevel=3)

    return mask


def _mask_3D(
    outlines,
    lon_bounds,
    numbers,
    lon_or_obj,
    lat=None,
    drop=True,
    lon_name="lon",
    lat_name="lat",
    method=None,
    wrap_lon=None,
    as_3D=False,
):

    mask = _mask(
        outlines=outlines,
        lon_bounds=lon_bounds,
        numbers=numbers,
        lon_or_obj=lon_or_obj,
        lat=lat,
        lon_name=lon_name,
        lat_name=lat_name,
        method=method,
        wrap_lon=wrap_lon,
        as_3D=as_3D,
    )

    if as_3D:
        mask_3D = _unpack_3D_mask(mask, numbers, drop)
    else:
        mask_3D = _unpack_2D_mask(mask, numbers, drop)

    return mask_3D


def _unpack_2D_mask(mask, numbers, drop):

    isnan = np.isnan(mask.values)

    if drop:
        numbers = np.unique(mask.values[~isnan])
        numbers = numbers.astype(int)

    # if no regions are found return a 0 x lat x lon mask
    if len(numbers) == 0:
        mask_3D = mask.expand_dims("region", axis=0).sel(region=slice(0, 0))
        mask_3D = mask_3D.assign_coords(region=("region", numbers))
        msg = (
            "No gridpoint belongs to any region. Returning an empty mask"
            f" with shape {mask.shape}"
        )
        warnings.warn(msg, UserWarning, stacklevel=3)
        return mask_3D

    mask_3D = list()
    for num in numbers:
        mask_3D.append(mask == num)

    mask_3D = xr.concat(mask_3D, dim="region", compat="override", coords="minimal")
    mask_3D = mask_3D.assign_coords(region=("region", numbers))

    if np.all(isnan):
        msg = "No gridpoint belongs to any region. Returning an all-False mask."
        warnings.warn(msg, UserWarning, stacklevel=3)

    return mask_3D


def _unpack_3D_mask(mask_3D, numbers, drop):

    any_masked = mask_3D.any(mask_3D.dims[1:])

    if drop:
        mask_3D = mask_3D.isel(region=any_masked)

        numbers = np.asarray(numbers)[any_masked.values]

    if len(numbers) == 0:

        mask_3D = mask_3D.assign_coords(region=("region", numbers))
        msg = (
            "No gridpoint belongs to any region. Returning an empty mask"
            f" with shape {mask_3D.shape}"
        )
        warnings.warn(msg, UserWarning, stacklevel=3)
        return mask_3D

    mask_3D = mask_3D.assign_coords(region=("region", numbers))

    if not np.any(any_masked):
        msg = "No gridpoint belongs to any region. Returning an all-False mask."
        warnings.warn(msg, UserWarning, stacklevel=3)

    return mask_3D


def _determine_method(lon, lat):
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

    if has_pygeos:
        return "pygeos"

    return "shapely"


def _extract_lon_lat(lon_or_obj, lat, lon_name, lat_name):
    # extract lon/ lat via __getitem__
    if lat is None:
        lon = lon_or_obj[lon_name]
        lat = lon_or_obj[lat_name]
    else:
        lon = lon_or_obj

    return lon, lat


def mask_to_dataarray(mask, lon_or_obj, lat=None, lon_name="lon", lat_name="lat"):

    lon, lat = _extract_lon_lat(lon_or_obj, lat, lon_name, lat_name)

    if sum(isinstance(c, xr.DataArray) for c in (lon, lat)) == 1:
        raise ValueError("Cannot handle coordinates with mixed types!")

    if not isinstance(lon, xr.DataArray) or not isinstance(lat, xr.DataArray):
        lon, lat = _numpy_coords_to_dataarray(lon, lat, lon_name, lat_name)

    ds = lat.coords.merge(lon.coords)

    dims = xr.core.variable.broadcast_variables(lat.variable, lon.variable)[0].dims

    # unstructured grids are 1D
    if mask.ndim - 1 == len(dims):
        dims = ("region",) + dims

    return ds.assign(mask=(dims, mask)).mask


def _numpy_coords_to_dataarray(lon, lat, lon_name, lat_name):
    # TODO: simplify if passing lon_name and lat_name is no longer supported

    dims2D = (f"{lat_name}_idx", f"{lon_name}_idx")

    lon = np.asarray(lon)
    dims = dims2D if lon.ndim == 2 else lon_name
    lon = xr.Dataset(coords={lon_name: (dims, lon)})[lon_name]

    lat = np.asarray(lat)
    dims = dims2D if lat.ndim == 2 else lat_name
    lat = xr.Dataset(coords={lat_name: (dims, lat)})[lat_name]

    return lon, lat


def _mask_edgepoints_shapely(
    mask,
    lon,
    lat,
    polygons,
    numbers,
    is_unstructured=False,
    as_3D=False,
):

    import shapely.vectorized as shp_vect

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
    if lon.min() < 0:
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

    if as_3D:
        for i, polygon in enumerate(polygons):
            sel = shp_vect.contains(polygon, LON, LAT)
            mask[i, idx[sel]] = True
    else:
        for i, polygon in enumerate(polygons):
            sel = shp_vect.contains(polygon, LON, LAT)
            mask[idx[sel]] = numbers[i]

    return mask.reshape(shape)


def _mask_pygeos(
    lon, lat, polygons, numbers, fill=np.NaN, is_unstructured=False, as_3D=False
):
    """create a mask using pygeos.STRtree"""

    lon, lat = _parse_input(lon, lat, polygons, fill, numbers)

    LON, LAT, shape = _get_LON_LAT_shape(
        lon, lat, numbers, is_unstructured=is_unstructured, as_3D=as_3D
    )
    out = _get_out(shape, fill, as_3D=as_3D)

    # add a tiny offset to get a consistent edge behaviour
    LON = LON - 1 * 10**-8
    LAT = LAT - 1 * 10**-10

    # convert shapely points to pygeos
    poly_pygeos = pygeos.from_shapely(polygons)
    points_pygeos = pygeos.points(LON, LAT)

    tree = pygeos.STRtree(points_pygeos)
    a, b = tree.query_bulk(poly_pygeos, predicate="contains")

    if as_3D:
        for i in range(len(numbers)):
            out[i, b[a == i]] = True
    else:
        for i, number in enumerate(numbers):
            out[b[a == i]] = number

    return out.reshape(shape)


def _mask_shapely(
    lon, lat, polygons, numbers, fill=np.NaN, is_unstructured=False, as_3D=False
):
    """create a mask using shapely.vectorized.contains"""

    import shapely.vectorized as shp_vect

    lon, lat = _parse_input(lon, lat, polygons, fill, numbers)

    LON, LAT, shape = _get_LON_LAT_shape(
        lon, lat, numbers, is_unstructured=is_unstructured, as_3D=as_3D
    )
    out = _get_out(shape, fill, as_3D=as_3D)

    # add a tiny offset to get a consistent edge behaviour
    LON = LON - 1 * 10**-8
    LAT = LAT - 1 * 10**-10

    if as_3D:
        for i, polygon in enumerate(polygons):
            sel = shp_vect.contains(polygon, LON, LAT)
            out[i, sel] = True

    else:
        for i, polygon in enumerate(polygons):
            sel = shp_vect.contains(polygon, LON, LAT)
            out[sel] = numbers[i]

    return out.reshape(shape)


def _parse_input(lon, lat, coords, fill, numbers):

    lon = np.asarray(lon)
    lat = np.asarray(lat)

    n_coords = len(coords)

    if len(numbers) != n_coords:
        raise ValueError("`numbers` and `coords` must have the same length.")

    if fill in numbers:
        raise ValueError("The fill value should not be one of the region numbers.")

    return lon, lat


def _get_LON_LAT_shape(lon, lat, numbers, is_unstructured=False, as_3D=False):

    if lon.ndim != lat.ndim:
        raise ValueError(
            f"Equal number of dimensions required, found "
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


def _get_out(shape, fill, as_3D):
    # create flattened output variable
    if as_3D:
        out = np.full(shape[:1] + (np.prod(shape[-2:]).item(),), False, bool)
    else:
        out = np.full(np.prod(shape), fill, float)

    return out


def _transform_from_latlon(lon, lat):
    """perform an affine transformation to the latitude/longitude coordinates"""

    from affine import Affine

    lat = np.asarray(lat)
    lon = np.asarray(lon)

    d_lon = lon[1] - lon[0]
    d_lat = lat[1] - lat[0]

    trans = Affine.translation(lon[0] - d_lon / 2, lat[0] - d_lat / 2)
    scale = Affine.scale(d_lon, d_lat)
    return trans * scale


def _mask_rasterize_flip(lon, lat, polygons, numbers, fill=np.NaN, **kwargs):

    split_point = _find_splitpoint(lon)
    flipped_lon = np.hstack((lon[split_point:], lon[:split_point]))

    mask = _mask_rasterize(flipped_lon, lat, polygons, numbers=numbers, **kwargs)

    # revert the mask
    return np.hstack((mask[:, -split_point:], mask[:, :-split_point]))


def _mask_rasterize_split(lon, lat, polygons, numbers, fill=np.NaN, **kwargs):

    split_point = _find_splitpoint(lon)
    lon_l, lon_r = lon[:split_point], lon[split_point:]

    mask_l = _mask_rasterize(lon_l, lat, polygons, numbers=numbers, **kwargs)
    mask_r = _mask_rasterize(lon_r, lat, polygons, numbers=numbers, **kwargs)

    return np.hstack((mask_l, mask_r))


def _mask_rasterize(lon, lat, polygons, numbers, fill=np.NaN, **kwargs):
    """Rasterize a list of (geometry, fill_value) tuples onto the given coordinates.

    This only works for regularly spaced 1D lat and lon arrays.
    """

    lon, lat = _parse_input(lon, lat, polygons, fill, numbers)

    # subtract a tiny offset: https://github.com/mapbox/rasterio/issues/1844
    lon = lon - 1 * 10**-8
    lat = lat - 1 * 10**-10

    return _mask_rasterize_no_offset(lon, lat, polygons, numbers, fill, **kwargs)


def _mask_rasterize_no_offset(
    lon, lat, polygons, numbers, fill=np.NaN, dtype=float, **kwargs
):
    """Rasterize a list of (geometry, fill_value) tuples onto the given coordinates.

    This only works for regularly spaced 1D lat and lon arrays.

    for internal use: does not check valitity of input
    """
    # TODO: use only this function once https://github.com/mapbox/rasterio/issues/1844
    # is resolved

    from rasterio import features

    shapes = zip(polygons, numbers)

    transform = _transform_from_latlon(lon, lat)
    out_shape = (len(lat), len(lon))

    raster = features.rasterize(
        shapes,
        out_shape=out_shape,
        fill=fill,
        transform=transform,
        dtype=dtype,
        **kwargs,
    )

    return raster
