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

_MASK_DOCSTRING_TEMPLATE = """\
create a {nd} {dtype} mask of a set of regions for the given lat/ lon grid

Parameters
----------
{gp_doc}lon_or_obj : object or array_like
    Can either be a longitude array and then ``lat`` needs to be
    given. Or an object where the longitude and latitude can be
    retrived as: ``lon = lon_or_obj[lon_name]`` and
    ``lat = lon_or_obj[lat_name]``
lat : array_like, optional
    If ``lon_or_obj`` is a longitude array, the latitude needs to be
    specified here.
{drop_doc}lon_name : str, optional
    Name of longitude in ``lon_or_obj``. Default: "lon".
lat_name : str, optional
    Name of latgitude in ``lon_or_obj``. Default: "lat"
{numbers_doc}method : "rasterize" | "shapely", optional
    Method used to determine whether a gridpoint lies in a region.
    Both methods should lead to the same result. If None (default)
    autoselects the method depending on the grid spacing.
wrap_lon : bool | 180 | 360, optional
    Whether to wrap the longitude around, inferred automatically.
    If the regions and the provided longitude do not have the same
    base (i.e. one is -180..180 and the other 0..360) one of them
    must be wrapped. This can be achieved with wrap_lon.
    If wrap_lon is None autodetects whether the longitude needs to be
    wrapped. If wrap_lon is False, nothing is done. If wrap_lon is True,
    longitude data is wrapped to 360 if its minimum is smaller
    than 0 and wrapped to 180 if its maximum is larger than 180.

Returns
-------
mask_{nd} : {dtype} xarray.DataArray

References
----------
See https://regionmask.readthedocs.io/en/stable/notebooks/method.html
"""

_GP_DOCSTRING = """\
geodataframe : GeoDataFrame or GeoSeries
    Object providing the region definitions (outlines).
"""

_NUMBERS_DOCSTRING = """\
numbers : str, optional
    Name of the column to use for numbering the regions.
    This column must not have duplicates. If None (default),
    takes ``geodataframe.index.values``.
"""


_DROP_DOCSTRING = """\
drop : boolean, optional
    If True (default) drops slices where all elements are False (i.e no
    gridpoints are contained in a region). If False returns one slice per
    region.
"""


def _inject_mask_docstring(is_3D, gp_method):

    dtype = "float" if is_3D else "boolean"
    nd = "3D" if is_3D else "2D"
    drop_doc = _DROP_DOCSTRING if is_3D else ""
    numbers_doc = _NUMBERS_DOCSTRING if gp_method else ""
    gp_doc = _GP_DOCSTRING if gp_method else ""

    mask_docstring = _MASK_DOCSTRING_TEMPLATE.format(
        dtype=dtype, nd=nd, drop_doc=drop_doc, numbers_doc=numbers_doc, gp_doc=gp_doc
    )

    return mask_docstring


def _mask(
    outlines,
    regions_is_180,
    numbers,
    lon_or_obj,
    lat=None,
    lon_name="lon",
    lat_name="lat",
    method=None,
    wrap_lon=None,
    central_rotated_longitude=None, 
    pole_latitude=None, 
    pole_longitude=None, 
    globe=None,
    crs=None,
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
    if method not in (None, "rasterize", "shapely", "legacy", "weights_default","weights_rot_pole", "weights_irregular"):
        msg = "Method must be None or one of 'rasterize', 'shapely', 'weights_default', 'weights_rot_pole' or 'weights_irregular'."
        raise ValueError(msg)

    if method is None:
        method = _determine_method(lon, lat)
    elif method == "rasterize":
        method = _determine_method(lon, lat)
        if "rasterize" not in method:
            msg = "`lat` and `lon` must be equally spaced to use `method='rasterize'`"
            raise ValueError(msg)

    if method == "rasterize":
        mask = _mask_rasterize(lon, lat, outlines, numbers=numbers)
    elif method == "rasterize_flip":
        mask = _mask_rasterize_flip(lon, lat, outlines, numbers=numbers)
    elif method == "rasterize_split":
        mask = _mask_rasterize_split(lon, lat, outlines, numbers=numbers)
    elif method == "shapely":
        mask = _mask_shapely(lon, lat, outlines, numbers=numbers)
    # Edited by Pablo
    elif method == "weights_default":
        mask = _mask_weights(lon, lat, outlines, numbers=numbers)
    elif method == "weights_rot_pole":
        mask = _Rotated_Pole(lon, lat, outlines, numbers=numbers, central_rotated_longitude = central_rotated_longitude, pole_latitude= pole_latitude, pole_longitude= pole_longitude, globe= globe,crs=crs) 
    elif method == "weights_irregular":
        msg = "Method is under construction."
        warnings.warn(msg, UserWarning, stacklevel=3)
        mask = _mask_weights_irregular(lon, lat, outlines, numbers=numbers) 
        
    # we need to treat the points at -180°E/0°E and -90°N
    mask = _mask_edgepoints_shapely(mask, lon, lat, outlines, numbers)

    # create an xr.DataArray
    if lon.ndim == 1:
        mask = _create_xarray(mask, lon_orig, lat, lon_name, lat_name)
    else:
        mask = _create_xarray_2D(mask, lon_or_obj, lat_orig, lon_name, lat_name)

    return mask


def _mask_2D(
    outlines,
    regions_is_180,
    numbers,
    lon_or_obj,
    lat=None,
    lon_name="lon",
    lat_name="lat",
    method=None,
    wrap_lon=None,
    central_rotated_longitude=None, 
    pole_latitude=None, 
    pole_longitude=None, 
    globe=None,
    crs=None,
):

    mask = _mask(
        outlines=outlines,
        regions_is_180=regions_is_180,
        numbers=numbers,
        lon_or_obj=lon_or_obj,
        lat=lat,
        lon_name=lon_name,
        lat_name=lat_name,
        method=method,
        wrap_lon=wrap_lon,
        central_rotated_longitude= central_rotated_longitude, 
        pole_latitude= pole_latitude, 
        pole_longitude= pole_longitude, 
        globe= globe,
        crs=crs,
    )

    if np.all(np.isnan(mask)):
        msg = "No gridpoint belongs to any region. Returning an all-NaN mask."
        warnings.warn(msg, UserWarning, stacklevel=3)

    return mask


def _mask_3D(
    outlines,
    regions_is_180,
    numbers,
    lon_or_obj,
    lat=None,
    drop=True,
    lon_name="lon",
    lat_name="lat",
    method=None,
    wrap_lon=None,
):

    mask = _mask(
        outlines=outlines,
        regions_is_180=regions_is_180,
        numbers=numbers,
        lon_or_obj=lon_or_obj,
        lat=lat,
        lon_name=lon_name,
        lat_name=lat_name,
        method=method,
        wrap_lon=wrap_lon,
    )

    isnan = np.isnan(mask.values)

    if drop:
        numbers = np.unique(mask.values[~isnan])
        numbers = numbers.astype(int)

    # if no regions are found return a 0 x lat x lon mask
    if len(numbers) == 0:
        mask = mask.expand_dims("region", axis=0).sel(region=slice(0, 0))
        msg = (
            "No gridpoint belongs to any region. Returning an empty mask"
            " with shape {}".format(mask.shape)
        )
        warnings.warn(msg, UserWarning, stacklevel=3)
        return mask

    mask_3D = list()
    for num in numbers:
        mask_3D.append(mask == num)

    mask_3D = xr.concat(mask_3D, dim="region", compat="override", coords="minimal")
    mask_3D = mask_3D.assign_coords(region=("region", numbers))

    if np.all(isnan):
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


def _mask_edgepoints_shapely(mask, lon, lat, polygons, numbers, fill=np.NaN):

    import shapely.vectorized as shp_vect

    # not sure if this is really necessary
    lon, lat, numbers = _parse_input(lon, lat, polygons, fill, numbers)

    LON, LAT, out, shape = _get_LON_LAT_out_shape(lon, lat, fill)

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
    LON = LON[borderpoints] - 1 * 10 ** -8
    LAT = LAT[borderpoints] - 1 * 10 ** -10

    # wrap points LON_180W_or_0E: -180°E -> 180°E and 0°E -> 360°E
    LON[LON_180W_or_0E[borderpoints]] += 360
    # shift points at -90°N to -89.99...°N
    LAT[LAT_90S[borderpoints]] = -90 + 1 * 10 ** -10

    # "mask[borderpoints][sel] = number" does not work, need to use np.where
    idx = np.where(borderpoints)[0]
    for i, polygon in enumerate(polygons):
        sel = shp_vect.contains(polygon, LON, LAT)
        mask[idx[sel]] = numbers[i]

    return mask.reshape(shape)


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

def _Rotated_Pole(lon, lat, polygons, numbers, central_rotated_longitude , pole_latitude, pole_longitude, globe,crs, fill=np.NaN):
    """
    Projects shapefile in the rotated pole projection of the given lat/lon- grid and creates a weighted mask.

    Parameters
    ----------
    lon : Longitude; xarray.core.dataarray.DataArray
    lat : Latitude; xarray.core.dataarray.DataArray
    polygons: geopandas.geodataframe.GeoDataFrame, geopandas.geoseries.GeoSeries or list
    
    Input
    -------
    projection: string; "+proj=ob_tran +o_proj=longlat +o_lon_p=... +o_lat_p=... +lon_0=... +to_meter=... +ellps=...: "
    "+proj": "ob_tran"; projection wanted - rotated pole projection
    "+o_proj": "latlon"; original projection - lat/lon-Grid
    "+o_lon_p": central rotated longitude 
    "+o_lat_p": pole latitude
    "+lon_0": pole longitude + 180
    "+to_meter": math.radians(1) =  0.017453292519943295
    "+ellps": Globe; WGS84
    
    Return
    -------
    _mask_weights : Function for computation of the weighted mask.

    """
    import geopandas as gpd   
    from shapely.ops import unary_union 
    shapefile_region =gpd.GeoSeries(unary_union(polygons),crs=crs)

    projection ="+proj=ob_tran +o_proj=longlat +o_lon_p={} +o_lat_p={} +lon_0={} +to_meter={} +ellps={}".format(central_rotated_longitude,pole_latitude, 180.+ pole_longitude, 0.017453292519943295, globe )
    proj_shp_region=shapefile_region.to_crs(projection)
    return _mask_weights(lon, lat, proj_shp_region, numbers, fill=np.NaN)


def _mask_weights_irregular(lon, lat, polygons, numbers, fill=np.NaN):
    
    from shapely.geometry import Polygon

    #Creating grid as polygons to intersect with shapefile
    Y,X=np.shape(lon)

    grid_cells_coords = []
    for i in range(X-1):
        for j in range(Y-1):
            x11=float(lon[j,i])     # + (float(ds1.lon[j,i+1])-float(ds1.lon[j,i]))/2.
            x12=float(lon[j,i+1])   # + (float(ds1.lon[j,i+1+1])-float(ds1.lon[j,i+1]))/2.
            x21=float(lon[j+1,i])   # + (float(ds1.lon[j+1,i+1])-float(ds1.lon[j+1,i]))/2.
            x22=float(lon[j+1,i+1]) # + (float(ds1.lon[j+1,i+1+1])-float(ds1.lon[j+1,i+1]))/2.

            y11=float(lat[j,i])     # + (float(ds1.lat[j+1,i])-float(ds1.lat[j,i]))/2.
            y12=float(lat[j,i+1])   # + (float(ds1.lat[j+1,i+1])-float(ds1.lat[j,i+1]))/2.
            y21=float(lat[j+1,i])   # + (float(ds1.lat[j+1+1,i])-float(ds1.lat[j+1,i]))/2.
            y22=float(lat[j+1,i+1]) # + (float(ds1.lat[j+1+1,i+1])-float(ds1.lat[j+1,i+1]))/2.

            grid_cells_coords.append(Polygon([[x11, y11],[x12,y12],[x22,y22], [x21, y21],[x11,y11]]))

    grid_cells_polys = []
    for i in range(len(grid_cells_coords)-int(np.sqrt(len(grid_cells_coords)))-1):
        if (i+1) % (int(np.sqrt(len(grid_cells_coords)))) == 0:
            continue
        x11,y11= grid_cells_coords[i+0].centroid.coords[0]
        x12,y12= grid_cells_coords[i+1].centroid.coords[0]
        x21,y21= grid_cells_coords[i+int(np.sqrt(len(grid_cells_coords)))].centroid.coords[0]
        x22,y22= grid_cells_coords[i+int(np.sqrt(len(grid_cells_coords)))+1].centroid.coords[0]
        grid_cells_polys.append(Polygon([[x11, y11],[x12,y12],[x22,y22], [x21, y21],[x11,y11]]))

    #Calculating the areal weights as intersection between shapefile and grided polygon
    areas=[]
    for r in grid_cells_polys:
        intersect = polygons[0].intersection(r)
        areas.append(intersect.area)
    poly_area=areas

    #Truning result in 2D array with right dimensions
    
    pol=np.reshape(poly_area, (X-2, Y-2))

    poly=np.zeros((X, Y))
    poly[1:-1,1:-1]=pol
    
    poly_pol=np.nan_to_num(poly)

    out=poly_pol.T/(sum(sum(poly_pol.T)))
    return out


def _mask_weights(lon, lat, polygons, numbers, fill=np.NaN):
    """
    Returns an array with the weighted areal mask.  

    """
    from shapely.geometry import Polygon
    lon, lat, numbers = _parse_input(lon, lat, polygons, fill, numbers)
    #Creating grid as polygons to intersect with shapefile
    
    # Creat lon-grid indexing for the case of wrap_lon needed.
    ind=np.argsort(lon)
    lon=np.sort(lon)
    x1,y1,x2,y2=polygons[0].bounds
    lon1=int(np.abs(lon - x1).argmin())
    lon2=int(np.abs(lon - x2).argmin())
    lat1=int(np.abs(lat - y1).argmin())
    lat2=int(np.abs(lat - y2).argmin())
    
    lon,lat=np.float64(lon),np.float64(lat)
    grid_cells = []
    for i in range(lon1-1,lon2):
        for j in range(lat1-1,lat2):
        # bounds
            cell_size_x=(lon[i+1])-(lon[i])
            cell_size_y=(lat[j+1])-(lat[j])

            x0=(lon[i])+cell_size_x/2.
            y0=(lat[j])+cell_size_y/2.
            
            cell_size_x=(lon[i+2])-(lon[i+1])
            cell_size_y=(lat[j+2])-(lat[j+1])
            
            x1 =(lon[i+1])+cell_size_x/2.
            y1 =(lat[j+1])+cell_size_y/2.
            grid_cells.append(Polygon([[x0, y0],[x1,y0],[x1,y1], [x0, y1],[x0,y0]]))

    #Calculating the areal weights as intersection between shapefile and grided polygon
    areas=[]
    for r in grid_cells:
        areas.append((polygons[0].intersection(r)).area)

    #Truning result in 2D array with right dimensions
    
    poly=np.zeros((len(lon), len(lat)))
    poly[lon1:lon2+1,lat1:lat2+1]=np.reshape(areas, (lon2-lon1+1, lat2-lat1+1))
    
    poly_pol=np.nan_to_num(poly)
    
    #Rearange accordint to lon-grid indexing
    out=np.take_along_axis(poly_pol.T/(sum(sum(poly_pol.T))), (np.zeros((len(lon), len(lat))).T+ind).astype(int), axis=1)
    return out

def _parse_input(lon, lat, coords, fill, numbers):

    lon = np.asarray(lon)
    lat = np.asarray(lat)

    n_coords = len(coords)

    if numbers is None:
        numbers = range(n_coords)
    else:
        if len(numbers) != n_coords:
            raise ValueError("`numbers` and `coords` must have the same length")

    if fill in numbers:
        raise ValueError("The fill value should not be one of the region numbers.")

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
    """Rasterize a list of (geometry, fill_value) tuples onto the given coordinates.

    This only works for 1D lat and lon arrays.

    for internal use: does not check valitity of input
    """
    # subtract a tiny offset: https://github.com/mapbox/rasterio/issues/1844
    lon = np.asarray(lon) - 1 * 10 ** -8
    lat = np.asarray(lat) - 1 * 10 ** -10

    return _mask_rasterize_no_offset(lon, lat, polygons, numbers, fill, **kwargs)


def _mask_rasterize_no_offset(lon, lat, polygons, numbers, fill=np.NaN, **kwargs):
    """Rasterize a list of (geometry, fill_value) tuples onto the given coordinates.

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
        dtype=float,
        **kwargs
    )

    return raster
