import xarray as xr

try:
    import cf_xarray  # noqa: F401

    has_cf_xarray = True
except ImportError:
    has_cf_xarray = False


def _get_coords(lon_or_obj, lat, lon_name, lat_name, use_cf):

    if lat is not None:
        return lon_or_obj, lat

    is_xr_object = isinstance(lon_or_obj, (xr.Dataset, xr.DataArray))

    if use_cf is None and has_cf_xarray and is_xr_object:
        return _get_coords_cf_or_name(lon_or_obj, lon_name, lat_name)

    if use_cf:
        return _get_coords_cf(lon_or_obj)

    return lon_or_obj[lon_name], lon_or_obj[lat_name]


def _get_cf_coords(obj, name, required=False):

    coord_name = obj.cf.coordinates.get(name)

    if not coord_name:
        if required:
            raise ValueError(f"Found no coords for {name}")
        return None

    if len(coord_name) > 1:
        raise ValueError(
            f"Found more than one candidate for '{name}'. Either pass the lon and lat "
            "coords directly or only pass the DataArray (instead of Dataset) the mask "
            "method."
        )

    return coord_name[0]


def _get_coords_cf_or_name(obj, lon_name, lat_name):

    x_name = _get_cf_coords(obj, "longitude", required=False) or lon_name
    y_name = _get_cf_coords(obj, "latitude", required=False) or lat_name

    _check_coords(obj, x_name, lon_name)
    _check_coords(obj, y_name, lat_name)

    return obj[x_name], obj[y_name]


def _check_coords(obj, cf_name, name):

    if cf_name != name and name in obj.coords:
        raise ValueError(
            f"Ambigous name for coordinates: cf_xarray determined '{cf_name}' but "
            f"'{name}' is also on the {type(obj).__name__}. Please set use_cf to "
            "True or False to resolve this conflict."
        )


def _get_coords_cf(obj):

    if not has_cf_xarray:
        raise ImportError("``cf_xarray`` required")

    if not isinstance(obj, (xr.Dataset, xr.DataArray)):
        raise TypeError(f"Expected a ``Dataset`` or ``DataArray``, got {type(obj)}")

    x_name = _get_cf_coords(obj, "longitude", required=True)
    y_name = _get_cf_coords(obj, "latitude", required=True)

    return obj[x_name], obj[y_name]
