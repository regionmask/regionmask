import numpy as np

import hashlib


    # save : bool, optional
    #     If True saves the mask to a netCDF file for faster performance.
    #     Default: True.
    # folder : string, optional
    #     Folder to store the masks. Default: '~/.regionmasks/'.


# , save=True, folder='~/.region_masks/'

# if save:
#     # get the filename
#     filename = filename_mask(lat, lon, name, method, folder)
    
#     # check if the file exists and load data
#     if path.isfile(filename):
#         import netCDF4 as nc
#         with nc.Dataset(filename) as ncf:
#             mask = ncf.variables['mask'][:]
    
#     else:
#         # create it
#         mask = func(lat, lon, data, self.numbers)
#         _create_file(filename, mask, lat, lon)
# else:
#     mask = func(lat, lon, data, self.numbers)

# create netcdf file
def _create_file(filename, mask, lat, lon):
    """create the netcdf file to store the srex mask"""
    import netCDF4 as nc
    with nc.Dataset(filename, 'w') as ncf:

        ncf.createDimension('lat', size=lat.size)
        ncf.createDimension('lon', size=lon.size)

        ncf.createVariable('lat', 'f', 'lat')
        ncf.createVariable('lon', 'f', 'lon')
        ncf.createVariable('mask', 'f', ('lat', 'lon'))

        ncf.variables['lat'][:] = lat
        ncf.variables['lon'][:] = lon
        ncf.variables['mask'][:] = mask


# create unique filename for the mask
def filename_mask(lat, lon, name, method, folder):
    """unique filename for each grid"""

    # ~ -> /home/user
    folder = path.expanduser(folder)

    # try to create the folder if it does not exist
    if not path.exists(folder):
        mkdir(folder)

    # get the grid description
    dlat, dlon, coord_hash = _griddes(lat, lon)

    name = name.replace(' ', '_')

    # construct the name
    file_name = (name + '_' + method + '_mask_dlat_' + dlat + '_dlon_'
                 + dlon + '_' + coord_hash + '.nc')

    # whole filename
    return path.join(folder, file_name)



# describe the grid uniquely
def _griddes(lon, lat, precision=6):
    """
    create hash of the grid and determine d_lat and d_lon

    this is used for the naming of the file
    """

    lon = np.array(lon)
    lat = np.array(lat)

    dlon = _dcoord(lon)
    dlat = _dcoord(lat)

    # numpy print options
    old_print_opt = np.get_printoptions()
    new_print_opt = {'edgeitems': 3,
                     'formatter': None,
                     'infstr': 'inf',
                     'linewidth': np.inf,
                     'nanstr': 'nan',
                     'precision': precision,
                     'suppress': False,
                     'threshold': np.inf}

    # make sure the printoptions are reset to the default
    try:
        np.set_printoptions(**new_print_opt)
        # create string with all lat and lon elements

        lat_str = 'lat: ' + lat.__str__() 
        lon_str = 'lon: ' + lon.__str__()
    except Exception as e:
        raise
    finally:
        np.set_printoptions(**old_print_opt)

    string = lat_str + '\n' + lon_str

    print string

    coord_hash = hashlib.md5(string.encode()).hexdigest()



    return dlon, dlat, coord_hash

# distance
def _dcoord(coord):
    """determine the spacing of a coordinate"""

    coord = np.array(coord)

    if coord.ndim > 1:
        msg = 'Only 1D coordinates are supported'
        raise AssertionError(msg)

    dcoord = np.unique(np.round(np.diff(coord), 4))

    # irregularly spaced
    if dcoord.size > 1:
        dcoord_str = 'irr'
    # regularly spaced
    else:
        dcoord_str = '{:0.2f}'.format(np.asscalar(dcoord))

    return dcoord_str
