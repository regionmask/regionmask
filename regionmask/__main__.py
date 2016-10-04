import sys
import docopt

import numpy as np

from .version import version

import regionmask

def main(args=None):
    """
    regionmask

    Usage:
      regionmask [options] <region> [<infile> [<outfile>]]
      regionmask -h | --help
      regionmask --version

    Options:
      -h --help    Show this screen.
      --version    Show version.
      --wrap=w     Wrap longitude [default: False].
      --lon=str    Name of longitude axis [default: lon].
      --lat=str    Name of latitude axis [default: lat].

    Parameters
    region :    must be one of: srex, giorgi, countries_110, countries_50,
                us_states_50 or us_states_10. If only region is given, plots
                them.
    inputfile:  must be an existing netCDF file. If only regions and
                inputfile is given, plots the calculated regions.
    outputfile: filename to write out a netCDF

    Examples:
      regionmask srex
      regionmask srex inputfile.nc
      regionmask srex --wrap True inputfile.nc
      regionmask srex --lon=longitude --lat=latitude inputfile.nc
      regionmask srex inputfile.nc outputfile.nc


    """

    # parse cmd line arguments
    options = docopt.docopt(main.__doc__, version=version)
    

    region_name = options['<region>']
    infile = options['<infile>']
    outfile = options['<outfile>']
    lon_name = options['--lon']
    lat_name = options['--lat']

    wrap = options['--wrap']
    try:
        wrap_lon = int(wrap)
    except ValueError:
        wrap_lon = bool(wrap)

    # ------------------------------------------------------------------

    # get the correct Regions_cls by name
    region = _maybe_get_region(region_name)    

    # if no file is given to mask, we plot the regions
    if infile is None:
        import matplotlib.pyplot as plt
        region.plot()
        plt.show()

        return 0

    # get lon and lat to mask
    lon, lat = _get_lonlat(infile, lon_name, lat_name)

    # create the mask
    mask = region.mask(lon, lat, wrap_lon=wrap_lon)

    # if we have not outfile, we plot the obtained mask
    if outfile is None:
        import matplotlib.pyplot as plt
        
        import cartopy.crs as ccrs

        ax = plt.axes(projection=ccrs.PlateCarree())

        m = np.ma.masked_invalid(mask)

        region.plot(add_ocean=False, ax=ax, add_label=False)

        _lon = _maybe_infer_interval_breaks(lon)
        _lat = _maybe_infer_interval_breaks(lat)

        ax.pcolormesh(_lon, _lat, m)
        ax.coastlines()
        plt.show()

    raise NotImplementedError("saving outfile not yet available")


def _maybe_get_region(region_name):
    """get the correct Regions_cls by name"""

    # defined regions
    sc_regions = ('srex', 'giorgi')
    ne_regions = ('countries_110', 'countries_50', 'us_states_50',
                  'us_states_10')

    # check if the region name is valid
    valid_regions = sc_regions + ne_regions

    if region_name not in valid_regions:
        r = "'{}'".format("', '".join(valid_regions))
        msg = "'{}' is not a valid region name, must be one of {}"
        msg = msg.format(region_name, r)
        
        raise ValueError(msg)

    # is it a natural_earth or a scientific region
    if region_name in sc_regions:
        def_reg = regionmask.defined_regions
    else:
        def_reg = regionmask.defined_regions.natural_earth

    return getattr(def_reg, region_name)


def _get_lonlat(infile, lon_name, lat_name):
    import netCDF4 as nc

    with nc.Dataset(infile) as ncf:
        lon = ncf.variables[lon_name][:]
        lat = ncf.variables[lat_name][:]

    return lon, lat


def _maybe_infer_interval_breaks(coord):
    
    if coord.ndim == 1:
        coord = _infer_interval_breaks(coord)

    return coord


def _infer_interval_breaks(coord):
    """
    >>> _infer_interval_breaks(np.arange(5))
    array([-0.5,  0.5,  1.5,  2.5,  3.5,  4.5])
    """
    coord = np.asarray(coord)
    deltas = 0.5 * (coord[1:] - coord[:-1])
    first = coord[0] - deltas[0]
    last = coord[-1] + deltas[-1]
    return np.r_[[first], coord[:-1] + deltas, [last]]


if __name__ == "__main__":
    main()