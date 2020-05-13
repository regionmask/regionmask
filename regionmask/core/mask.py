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


def _mask(
    outlines,
    regions_is_180,
    numbers,
    lon_or_obj,
    lat=None,
    lon_name="lon",
    lat_name="lat",
    method=None,
    xarray=None,
    wrap_lon=None,
):
    """
    internal function to create a mask
    """

    if not _is_numeric(numbers):
        raise ValueError("'numbers' must be numeric")

    lat_orig = lat

    lon, lat = _extract_lon_lat(lon_or_obj, lat, lon_name, lat_name)

    lon = np.asarray(lon)
    lat = np.asarray(lat)

    # automatically detect whether wrapping is necessary
    if wrap_lon is None:
        grid_is_180 = _is_180(lon.min(), lon.max())

        wrap_lon = not regions_is_180 == grid_is_180

    lon_orig = lon.copy()
    if wrap_lon:
        lon = _wrapAngle(lon, wrap_lon)

    if method not in (None, "rasterize", "shapely", "legacy"):
        msg = "Method must be None or one of 'rasterize', 'shapely', or 'legacy'."
        raise ValueError(msg)

    if method is None:
        method = _determine_method(method, lon, lat)
    elif method == "rasterize":
        method = _determine_method(method, lon, lat)
        if "rasterize" not in method:
            msg = "`lat` and `lon` must be equally spaced to use `method='rasterize'`"
            raise ValueError(msg)
    elif method == "legacy":
        msg = "The method 'legacy' will be removed in a future version."
        warnings.warn(msg, FutureWarning, stacklevel=3)

    if method == "legacy":
        mask = _mask_contains(lon, lat, outlines, numbers=numbers)
    elif method == "rasterize":
        mask = _mask_rasterize(lon, lat, outlines, numbers=numbers)
    elif method == "rasterize_flip":
        mask = _mask_rasterize_flip(lon, lat, outlines, numbers=numbers)
    elif method == "rasterize_split":
        mask = _mask_rasterize_split(lon, lat, outlines, numbers=numbers)
    elif method == "shapely":
        mask = _mask_shapely(lon, lat, outlines, numbers=numbers)

    if np.all(np.isnan(mask)):
        msg = "All elements of mask are NaN. Try to set 'wrap_lon=True'."
        print(msg)

    if xarray is None:
        xarray = True
    else:
        msg = (
            "Passing the `xarray` keyword is deprecated. Future versions of regionmask will"
            " always return an xarray Dataset. Use `mask.values` to obtain a numpy grid."
        )
        warnings.warn(msg, FutureWarning, stacklevel=3)

    if xarray:

        if lon.ndim == 1:
            mask = _create_xarray(mask, lon_orig, lat, lon_name, lat_name)
        else:
            mask = _create_xarray_2D(mask, lon_or_obj, lat_orig, lon_name, lat_name)

    return mask


def _determine_method(lon, lat):

    if equally_spaced(lon, lat):
        return "rasterize"
    elif _equally_spaced_on_split_lon(lon, lat):

        split_point = _find_splitpoint(lon)
        flipped_lon = np.hstack((lon[split_point:], lon[:split_point]))

        if equally_spaced(flipped_lon, lat):
            return "rasterize_flip"
        else:
            return "rasterize_split"
    else:
        return "shapely"


def _extract_lon_lat(lon_or_obj, lat, lon_name, lat_name):
    # extract lon/ lat via __getitem__
    if lat is None:
        lon = lon_or_obj[lon_name]
        lat = lon_or_obj[lat_name]
    else:
        lon = lon_or_obj

    return lon, lat


def _create_xarray(mask, lon, lat, lon_name, lat_name):
    """create an xarray DataArray"""

    # create the xarray output
    coords = {lat_name: lat, lon_name: lon}
    mask = xr.DataArray(mask, coords=coords, dims=(lat_name, lon_name), name="region")

    return mask


def _create_xarray_2D(mask, lon_or_obj, lat, lon_name, lat_name):
    """create an xarray DataArray for 2D fields"""

    lon2D, lat2D = _extract_lon_lat(lon_or_obj, lat, lon_name, lat_name)

    if isinstance(lon2D, xr.DataArray):
        dim1D_names = lon2D.dims
        dim1D_0 = lon2D[dim1D_names[0]]
        dim1D_1 = lon2D[dim1D_names[1]]
    else:
        dim1D_names = (lon_name + "_idx", lat_name + "_idx")
        dim1D_0 = np.arange(np.array(lon2D).shape[0])
        dim1D_1 = np.arange(np.array(lon2D).shape[1])

    # dict with the coordinates
    coords = {
        dim1D_names[0]: dim1D_0,
        dim1D_names[1]: dim1D_1,
        lat_name: (dim1D_names, lat2D),
        lon_name: (dim1D_names, lon2D),
    }

    mask = xr.DataArray(mask, coords=coords, dims=dim1D_names)

    return mask


def create_mask_contains(lon, lat, coords, fill=np.NaN, numbers=None):
    """
    create the mask of a list of regions, given the lat and lon coords

    Parameters
    ----------
    lon : ndarray
        Numpy array containing the midpoints of the longitude.
    lat : ndarray
        Numpy array containing the midpoints of the latitude.
    coords : list of nx2 arays
        List of the coordinates outlining the regions
    fill : float, optional
        Fill value for  for Default: np.NaN.
    numbers : list of int, optional
        If not given 0:n_coords - 1 is used.

    """

    msg = (
        "The function `create_mask_contains` is deprecated and will be removed in a"
        "  future version. Please use ``regionmask.Regions(coords).mask(lon, lat)``"
        " instead."
    )
    warnings.warn(msg, FutureWarning, stacklevel=3)

    lon, lat, numbers = _parse_input(lon, lat, coords, fill, numbers)

    return _mask_contains(lon, lat, coords, numbers, fill=fill)


def _mask_contains(lon, lat, coords, numbers, fill=np.NaN):

    import matplotlib.path as mplPath

    LON, LAT, out, shape = _get_LON_LAT_out_shape(lon, lat, fill)

    # get all combinations if lat lon points
    lonlat = list(zip(LON, LAT))

    # loop through all polygons
    for i in range(len(coords)):
        cs = np.array(coords[i])

        isnan = np.isnan(cs[:, 0])

        if np.any(isnan):
            cs = np.split(cs, np.nonzero(isnan)[0])
        else:
            cs = [cs]

        for c in cs:
            bbPath = mplPath.Path(c)
            sel = bbPath.contains_points(lonlat)
            out[sel] = numbers[i]

    return out.reshape(shape)


def _mask_shapely(lon, lat, polygons, numbers, fill=np.NaN):
    """
    create a mask using shapely.vectorized.contains
    """

    import shapely.vectorized as shp_vect

    lon, lat, numbers = _parse_input(lon, lat, polygons, fill, numbers)

    LON, LAT, out, shape = _get_LON_LAT_out_shape(lon, lat, fill)

    # add a tiny offset to get a consistent edge behaviour
    LON = LON - 1 * 10 ** -8
    LAT = LAT - 1 * 10 ** -10

    for i, polygon in enumerate(polygons):
        sel = shp_vect.contains(polygon, LON, LAT)
        out[sel] = numbers[i]

    return out.reshape(shape)


def _parse_input(lon, lat, coords, fill, numbers):

    lon = np.asarray(lon)
    lat = np.asarray(lat)

    n_coords = len(coords)

    if numbers is None:
        numbers = range(n_coords)
    else:
        assert len(numbers) == n_coords

    msg = "The fill value should not be one of the region numbers."
    assert fill not in numbers, msg

    return lon, lat, numbers


def _get_LON_LAT_out_shape(lon, lat, fill):

    if lon.ndim == 2:
        LON, LAT = lon, lat
    else:
        LON, LAT = np.meshgrid(lon, lat)

    shape = LON.shape

    LON, LAT = LON.flatten(), LAT.flatten()

    # create output variable
    out = np.empty(shape=shape).flatten()
    out.fill(fill)

    return LON, LAT, out, shape


def _transform_from_latlon(lon, lat):
    """perform an affine tranformation to the latitude/longitude coordinates"""

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

    mask = _mask_rasterize(flipped_lon, lat, polygons, numbers=numbers)

    # revert the mask
    return np.hstack((mask[:, split_point:], mask[:, :split_point]))


def _mask_rasterize_split(lon, lat, polygons, numbers, fill=np.NaN, **kwargs):

    split_point = _find_splitpoint(lon)
    lon_l, lon_r = lon[:split_point], lon[split_point:]

    mask_l = _mask_rasterize(lon_l, lat, polygons, numbers=numbers)
    mask_r = _mask_rasterize(lon_r, lat, polygons, numbers=numbers)

    return np.hstack((mask_l, mask_r))


def _mask_rasterize(lon, lat, polygons, numbers, fill=np.NaN, **kwargs):
    """ Rasterize a list of (geometry, fill_value) tuples onto the given coordinates.

        This only works for 1D lat and lon arrays.

        for internal use: does not check valitity of input
    """
    # subtract a tiny offset: https://github.com/mapbox/rasterio/issues/1844
    lon = np.asarray(lon) - 1 * 10 ** -8
    lat = np.asarray(lat) - 1 * 10 ** -10

    return _mask_rasterize_no_offset(lon, lat, polygons, numbers, fill, **kwargs)


def _mask_rasterize_no_offset(lon, lat, polygons, numbers, fill=np.NaN, **kwargs):
    """ Rasterize a list of (geometry, fill_value) tuples onto the given coordinates.

        This only works for 1D lat and lon arrays.

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
        dtype=np.float,
        **kwargs
    )

    return raster
