import six
import numpy as np
import xarray as xr


def _maybe_to_dict(keys, values):
    """convert iterable to dict if necessary"""

    if not isinstance(values, dict):
        values = {key: value for key, value in zip(keys, values)}

    return values


def _create_dict_of_numbered_string(numbers, string):

    return {number: string + str(number) for number in numbers}


def _sanitize_names_abbrevs(numbers, values, default):

    if isinstance(values, six.string_types):
        values = _create_dict_of_numbered_string(numbers, values)
    elif values is None:
        values = _create_dict_of_numbered_string(numbers, default)
    else:

        assert len(numbers) == len(values)

        values = _maybe_to_dict(numbers, values)

    return values


# -----------------------------------------------------------------------------


def _wrapAngle360(lon):
    """wrap angle to [0, 360[."""
    lon = np.array(lon)
    return np.mod(lon, 360)


# -----------------------------------------------------------------------------


def _wrapAngle180(lon):
    """wrap angle to [-180,180[."""
    lon = np.array(lon)
    sel = (lon < -180) | (180 <= lon)
    lon[sel] = _wrapAngle360(lon[sel] + 180) - 180
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
        if lon.min() < 0 and lon.max() > 180:
            msg = (
                "lon has both data that is larger than 180 and "
                "smaller than 0. Cannot infer the transformation."
            )
            raise RuntimeError(msg)

    wl = int(wrap_lon)

    if wl == 180 or (lon.max() > 180 and not wl == 360):
        new_lon = _wrapAngle180(lon.copy())

    if wl == 360 or (lon.min() < 0 and not wl == 180):
        new_lon = _wrapAngle360(lon.copy())

    # check if they are still unique
    if new_lon.ndim == 1:
        if new_lon.shape != np.unique(new_lon).shape:
            msg = "There are equal longitude coordinates (when wrapped)!"
            raise IndexError(msg)

    return new_lon


# -----------------------------------------------------------------------------


def _is_180(lon_min, lon_max):

    lon_min = np.round(lon_min, 6)
    lon_max = np.round(lon_max, 6)

    if (lon_min < 0) and (lon_max > 180):
        msg = "lon has both data that is larger than 180 and smaller than 0."
        raise ValueError(msg)

    return lon_max <= 180


def create_lon_lat_dataarray_from_bounds(lon_start,
                                         lon_stop,
                                         lon_step,
                                         lat_start,
                                         lat_stop,
                                         lat_step,):
    """ example xarray Dataset

        Parameters
        ==========
        lon_start : number
            Start of lon bounds. The bounds includes this value.
        lon_stop : number
            End of lon bounds. The bounds does not include this value.
        lon_step : number
            Spacing between values.
        lat_start : number
            Start of lat bounds. The bounds includes this value.
        lat_stop : number
            End of lat bounds. The bounds does not include this value.
        lat_step : number
            Spacing between values.

        Returns
        =======
        ds : xarray Dataarray
            Example dataset including, lon, lat, lon_bnds, lat_bnds.

    """

    lon_bnds = np.arange(lon_start, lon_stop, lon_step)
    lon = (lon_bnds[:-1] + lon_bnds[1:]) / 2

    lat_bnds = np.arange(lat_start, lat_stop, lat_step)
    lat = (lat_bnds[:-1] + lat_bnds[1:]) / 2

    ds = xr.Dataset(  
               coords=dict(lon=lon,
                           lat=lat,
                           lon_bnds=lon_bnds,
                           lat_bnds=lat_bnds,))



    return ds
