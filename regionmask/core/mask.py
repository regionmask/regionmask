import numpy as np
import warnings
import xarray as xr

from .utils import _wrapAngle, _is_180, equally_spaced


def _mask(
    self,
    lon_or_obj,
    lat=None,
    lon_name="lon",
    lat_name="lat",
    method=None,
    xarray=None,
    wrap_lon=None,
):
    """
    create a grid as mask of a set of regions for given lat/ lon grid

    Parameters
    ----------
    lon_or_obj : array_like or object
        Can either be (1) a longitude array and then lat needs to be
        given. Or an object where the longitude and latitude can be
        retrived as:
        lon = lon_or_obj[lon_name]
        lat = lon_or_obj[lat_name]
    lat : array_like, (optional)
        If 'lon_or_obj' is a longitude array, the latitude needs to be
        specified here.
    lon_name, optional
        Name of longitude in 'lon_or_obj'. Default: 'lon'.
    lat_name, optional
        Name of latgitude in 'lon_or_obj'. Default: 'lat'
    method : None | "rasterize" | "legacy"
        Set method used to determine wether a gridpoint lies in a region.
    xarray : None | bool, optional
        Deprecated. If None or True returns an xarray DataArray, if False returns a
        numpy ndarray. Default: None.
    wrap_lon : None | bool | 180 | 360, optional
        If the regions and the provided longitude do not have the same
        base (i.e. one is -180..180 and the other 0..360) one of them
        must be wrapped. This can be done with wrap_lon.
        If wrap_lon is None autodetects whether the longitude needs to be
        wrapped. If wrap_lon is False, nothing is done. If wrap_lon is True,
        longitude data is wrapped to 360 if its minimum is smaller
        than 0 and wrapped to 180 if its maximum is larger than 180.
    Returns
    -------
    mask : ndarray or xarray DataSet

    Method - rasterize
    ------------------
    "rasterize" uses `rasterio.features.rasterize`. This method offers a 50 to 100
    speedup compared to "legacy". It only works for equally spaced lon and lat grids.

    Method - legacy
    ---------------
    Uses the following:
    >>> from matplotlib.path import Path
    >>> bbPath = Path(((0, 0), (0, 1), (1, 1.), (1, 0)))
    >>> bbPath.contains_point((0.5, 0.5))

    This method is slower than the others and its edge behaviour is inconsistent
    (see https://github.com/matplotlib/matplotlib/issues/9704).

    """

    lat_orig = lat

    lon, lat = _extract_lon_lat(lon_or_obj, lat, lon_name, lat_name)

    lon = np.array(lon)
    lat = np.array(lat)

    # automatically detect whether wrapping is necessary
    if wrap_lon is None:
        regions_is_180 = self.lon_180
        grid_is_180 = _is_180(lon.min(), lon.max())

        wrap_lon = not regions_is_180 == grid_is_180

    if wrap_lon:
        lon_old = lon.copy()
        lon = _wrapAngle(lon, wrap_lon)

    if method is None:
        method = "rasterize" if equally_spaced(lon, lat) else "legacy"
    elif method == "rasterize":
        if not equally_spaced(lon, lat):
            raise ValueError(
                "`lat` and `lon` must be equally spaced to use" "`method='rasterize'`"
            )

    if method == "legacy":
        func = create_mask_contains
        data = self.coords
    elif method == "rasterize":
        func = _create_mask_rasterize_fasttrack
        data = self.polygons
        # subtract a tiny offset: https://github.com/mapbox/rasterio/issues/1844
        lon -= 1*10 ** -9
        lat -= 1*10 ** -9
    else:
        msg = "Only methods 'rasterize' and 'legacy' are implemented"
        raise NotImplementedError(msg)

    mask = func(lon, lat, data, numbers=self.numbers)

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
        # wrap the angle back
        if wrap_lon:
            lon = lon_old

        if lon.ndim == 1:
            mask = _create_xarray(mask, lon, lat, lon_name, lat_name)
        else:
            mask = _create_xarray_2D(mask, lon_or_obj, lat_orig, lon_name, lat_name)

    return mask


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
    import matplotlib.path as mplPath

    lon, lat, numbers = _parse_input(lon, lat, coords, fill, numbers)

    if lon.ndim == 2:
        LON, LAT = lon, lat
    else:
        LON, LAT = np.meshgrid(lon, lat)

    # get all combinations if lat lon points
    lonlat = list(zip(LON.ravel(), LAT.ravel()))

    shape = LON.shape

    # create output variable
    out = np.empty(shape=shape).ravel()
    out.fill(fill)

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


def create_mask_rasterize(lon, lat, coords, fill=np.NaN, numbers=None):
    """
    create the mask of a list of regions, given the lat and lon coords

    Parameters
    ----------
    lon : ndarray
        Numpy array containing the midpoints of the longitude.
    lat : ndarray
        Numpy array containing the midpoints of the latitude.
    coords : list shapely Polygon/ MultiPolygon
        List of the coordinates outlining the regions
    fill : float, optional
        Fill value for  for Default: np.NaN.
    numbers : list of int, optional
        If not given 0:n_coords - 1 is used.

    """

    if not equally_spaced(lon, lat):
        msg = "'lat' and 'lon' must be equally spaced."
        raise ValueError(msg)

    lon, lat, numbers = _parse_input(lon, lat, coords, fill, numbers)

    # subtract a tiny offset: https://github.com/mapbox/rasterio/issues/1844
    lon -= 1*10 ** -9
    lat -= 1*10 ** -9

    return _create_mask_rasterize_fasttrack(lon, lat, coords, numbers, fill)


def _create_mask_rasterize_fasttrack(lon, lat, coords, numbers, fill=np.NaN):
    """ for internal use: does not check valitity of input
    """

    shapes = zip(coords, numbers)

    return _rasterize(shapes, lon, lat, fill=fill)


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


def _rasterize(shapes, lon, lat, fill=np.nan, **kwargs):
    """ Rasterize a list of (geometry, fill_value) tuples onto the given coordinates.

        This only works for 1D lat and lon arrays.
    """

    from rasterio import features

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

    # xr.DataArray(raster, coords=(lat, lon), dims=('lat', 'lon'), name='region')
