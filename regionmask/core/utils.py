import numpy as np
import six
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
        if not len(numbers) == len(values):
            raise ValueError("`numbers` and `values` do not have the same length.")

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


def create_lon_lat_dataarray_from_bounds(
    lon_start, lon_stop, lon_step, lat_start, lat_stop, lat_step
):
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

    LON, LAT = np.meshgrid(lon, lat)

    ds = xr.Dataset(
        coords=dict(
            lon=lon,
            lat=lat,
            lon_bnds=lon_bnds,
            lat_bnds=lat_bnds,
            LON=(("lat", "lon"), LON),
            LAT=(("lat", "lon"), LAT),
        )
    )

    return ds


def _is_numeric(numbers):

    numbers = np.asarray(numbers)
    return np.issubdtype(numbers.dtype, np.number)


def equally_spaced(*args):

    args = [np.asarray(arg) for arg in args]

    if any(arg.ndim > 1 for arg in args):
        return False

    if any(arg.size < 2 for arg in args):
        return False

    d_args = (np.diff(arg) for arg in args)

    return all(np.allclose(d_arg[0], d_arg) for d_arg in d_args)


def _equally_spaced_on_split_lon(lon):

    lon = np.asarray(lon)

    if lon.ndim > 1 or lon.size < 2:
        return False

    d_lon = np.diff(lon)
    d_lon_not_isclose = ~np.isclose(d_lon[0], d_lon)

    # there can only be one breakpoint
    return (d_lon_not_isclose.sum() == 1) and not d_lon_not_isclose[-1]


def _find_splitpoint(lon):

    lon = np.asarray(lon)
    d_lon = np.diff(lon)

    d_lon_not_isclose = ~np.isclose(d_lon[0], d_lon)

    split_point = np.argwhere(d_lon_not_isclose)

    if len(split_point) != 1:
        raise ValueError("more or less than one split point found")

    return split_point.squeeze() + 1
