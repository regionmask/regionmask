import numpy as np
import matplotlib.path as mplPath


from shapely.geometry import Polygon, MultiPolygon

try:
    import xarray as xr 
    has_xarray = True
except ImportError:
    has_xarray = False


def _mask(self, lon_or_obj, lat=None, lon_name='lon', lat_name='lat',
          xarray=None):
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



    # extract lon/ lat via __getitem__
    if lat is None:
        lon = np.array(lon_or_obj[lon_name])
        lat = np.array(lon_or_obj[lat_name])
    else:
        lon = lon_or_obj

    # https://gist.github.com/shoyer/0eb96fa8ab683ef078eb
    method='contains'
    if method == 'contains':
        func = create_mask_contains
        data = self.coords
    else:
        raise NotImplementedError("Only method 'contains' is implemented")

    mask = func(lon, lat, data, numbers=self.numbers)

    if xarray is None:
        xarray = has_xarray

    if xarray :
        mask = _create_xarray(mask, lat, lon, lat_name, lon_name)

    return mask



def _create_xarray(mask, lat, lon, lat_name, lon_name):
    """create an xarray DataArray"""
    
    # create the xarray output
    coords = {lat_name : lat, lon_name : lon}
    mask = xr.DataArray(mask, coords=coords,
                             dims=(lat_name, lon_name))

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
    
    n_coords = len(coords)

    if numbers is None:
        numbers = range(n_coords)
    else:
        assert len(numbers) == n_coords

    # the fill value should not be one of the numbers
    assert not fill in numbers

    # get all combinations if lat lon points
    LON, LAT = np.meshgrid(lon, lat)
    lonlat = zip(LON.ravel(), LAT.ravel())

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

