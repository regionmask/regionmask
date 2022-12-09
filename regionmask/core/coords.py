import xarray as xr

try:
    import cf_xarray

    has_cf_xarray = True
except ImportError:
    has_cf_xarray = False


def _get_coords(lon_or_obj, lat, lon_name, lat_name, use_cf):

    if lat is not None:
        return lon_or_obj, lat

    if has_cf_xarray and isinstance(lon_or_obj, (xr.Dataset, xr.DataArray)):

        return _get_coords_da_ds(lon_or_obj, lon_name, lat_name, use_cf)

    return lon_or_obj[lon_name], lon_or_obj[lat_name]


def _get_cf_coords(obj, name, required=False):

    coord_name = obj.cf.coordinates.get(name)

    if not coord_name:
        if required:
            raise ValueError(f"Found no coords for {name}")
        return None

    if len(coord_name) > 1:
        raise ValueError(f"Found more than one candidate for {name}")

    return coord_name[0]


def _get_coords_da_ds(obj, lon_name, lat_name, use_cf):

    if use_cf is None:

        x_name = _get_cf_coords(obj, "longitude", required=False) or lon_name
        y_name = _get_cf_coords(obj, "latitude", required=False) or lat_name

        if x_name != lon_name and lon_name in obj.coords:
            raise ValueError("Ambigous name")

        if y_name != lat_name and lat_name in obj.coords:
            raise ValueError("Ambigous name")

    elif use_cf is True:
        x_name = _get_cf_coords(obj, "longitude", required=True)
        y_name = _get_cf_coords(obj, "latitude", required=True)

    elif use_cf is False:
        x_name = lon_name
        y_name = lat_name
    else:
        raise ValueError("")

    return obj[x_name], obj[y_name]
