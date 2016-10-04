import numpy as np
import matplotlib.path as mplPath


from shapely.geometry import Polygon, MultiPolygon

try:
    import xarray as xr 
    has_xarray = True
except ImportError:
    has_xarray = False


def _wrapAngle360(lon):
    """wrap angle to [0, 360[."""
    lon = np.array(lon)
    return np.mod(lon, 360)

# -----------------------------------------------------------------------------

def _wrapAngle180(lon):
    """wrap angle to [-180,180[."""
    lon = np.array(lon)
    sel = (lon < -180) | (180 <= lon);
    lon[sel] = _wrapAngle360(lon[sel] + 180) - 180;
    return lon


def _wrapAngle(lon, wrap_lon=True):
    """wrap the angle to the other base

        If lon is from -180 to 180 wraps them to 0..360
        If lon is from 0 to 360 wraps them to -180..180
    """

    if np.isscalar(lon):
        lon = [lon]

    lon = np.array(lon)
    new_lon = lon


    if wrap_lon is True:
        if lon.min() < 0  and lon.max() > 180:
            msg = ('lon has both data that is larger than 180 and '
                   'smaller than 0. Cannot infer the transformation.')
            raise RuntimeError(msg)


    wl = int(wrap_lon)

    if wl == 180 or (lon.max() > 180 and not wl == 360):
        new_lon = _wrapAngle180(lon.copy())
    
    if wl == 360 or (lon.min() < 0 and not wl == 180):
        new_lon = _wrapAngle360(lon.copy())

    # check if they are still unique
    if new_lon.ndim == 1:
        if new_lon.shape != np.unique(new_lon).shape:
            msg = 'There are equal longitude coordinates (when wrapped)!'
            raise IndexError(msg)

    return new_lon


def _mask(self, lon_or_obj, lat=None, lon_name='lon', lat_name='lat',
          xarray=None, wrap_lon=False):
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
    xarray : bool or None, optional
        If True returns an xarray DataArray, if False returns a numpy
        ndarray. If None, checks if xarray can be imported and if yes
        returns a xarray DataArray else a numpy ndarray. Default: None.
    wrap_lon : bool | 180 | 360, optional
        If the regions and the provided longitude do not have the same 
        base (i.e. one is -180..180 and the other 0..360) one of them 
        must be wrapped around. This can be done with wrap_lon. If 
        wrap_lon is False, nothing is done. If wrap_lon is True, 
        longitude data is wrapped to 360 if its minimum is smaller 
        than 0 and wrapped to 180 if its maximum is larger than

    Returns
    -------
    mask : ndarray or xarray DataSet

    Method
    -------
    Uses the following:
    >>> from matplotlib.path import Path
    >>> bbPath = Path(((0, 0), (0, 1), (1, 1.), (1, 0)))
    >>> bbPath.contains_point((0.5, 0.5))
    
    """    

    # method : string, optional
    #     Method to use in for the masking. Default: 'contains'.

    lat_orig = lat

    lon, lat = _extract_lon_lat(lon_or_obj, lat, lon_name, lat_name)

    lon = np.array(lon)
    lat = np.array(lat)

    if wrap_lon:
        lon_old = lon.copy()
        lon = _wrapAngle(lon, wrap_lon)

    # https://gist.github.com/shoyer/0eb96fa8ab683ef078eb
    method='contains'
    if method == 'contains':
        func = create_mask_contains
        data = self.coords
    else:
        raise NotImplementedError("Only method 'contains' is implemented")

    mask = func(lon, lat, data, numbers=self.numbers)

    if np.all(np.isnan(mask)):
        msg = "All elements of mask are NaN. Try to set 'wrap_lon=True'."
        print(msg)

    if xarray is None:
        xarray = has_xarray

    if xarray:
        # wrap the angle back
        if wrap_lon:
            lon = lon_old

        if lon.ndim == 1:
            mask = _create_xarray(mask, lon, lat, lon_name, lat_name)
        else:
            mask = _create_xarray_2D(mask, lon_or_obj, lat_orig,
                                      lon_name, lat_name)

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
    coords = {lat_name : lat, lon_name : lon}
    mask = xr.DataArray(mask, coords=coords,
                        dims=(lat_name, lon_name), name='region')

    return mask


def _create_xarray_2D(mask, lon_or_obj, lat, lon_name, lat_name):
    """create an xarray DataArray for 2D fields"""

    lon2D, lat2D = _extract_lon_lat(lon_or_obj, lat, lon_name, lat_name)

    if isinstance(lon2D, xr.DataArray):
        dim1D_names = lon2D.dims
        dim1D_0 = lon2D[dim1D_names[0]]
        dim1D_1 = lon2D[dim1D_names[1]]
    else:
        dim1D_names = (lon_name + '_idx', lat_name + '_idx')
        dim1D_0 = np.arange(np.array(lon2D).shape[0])
        dim1D_1 = np.arange(np.array(lon2D).shape[1])

    # dict with the coordinates
    coords = {dim1D_names[0]: dim1D_0,
              dim1D_names[1]: dim1D_1,
              lat_name: (dim1D_names, lat2D),
              lon_name: (dim1D_names, lon2D)}
    
    mask = xr.DataArray(mask, coords = coords, dims=dim1D_names)

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

    lon = np.array(lon)
    lat = np.array(lat)
    
    n_coords = len(coords)

    if numbers is None:
        numbers = range(n_coords)
    else:
        assert len(numbers) == n_coords

    # the fill value should not be one of the numbers
    assert not fill in numbers

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
    for i in range(n_coords):
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

