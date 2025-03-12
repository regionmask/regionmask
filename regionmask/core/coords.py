import numpy as np
import xarray as xr

try:
    import cf_xarray  # noqa: F401

    has_cf_xarray = True
except ImportError:
    has_cf_xarray = False


# TODO: use overloads?
def _get_coords(
    lon_or_obj: np.typing.ArrayLike | xr.DataArray | xr.Dataset,
    lat: np.typing.ArrayLike | xr.DataArray | None,
    lon_name: str,
    lat_name: str,
    use_cf: bool | None,
) -> (
    tuple[xr.DataArray, xr.DataArray] | tuple[np.typing.ArrayLike, np.typing.ArrayLike]
):

    if lat is not None:
        return lon_or_obj, lat

    if (
        use_cf is None
        and has_cf_xarray
        and isinstance(lon_or_obj, xr.Dataset | xr.DataArray)
    ):
        return _get_coords_cf_or_name(lon_or_obj, lon_name, lat_name)

    if use_cf:
        return _get_coords_cf(lon_or_obj)

    return _from_mapping(lon_or_obj, lon_name), _from_mapping(lon_or_obj, lat_name)


def _from_mapping(lon_or_obj, name):

    try:
        return lon_or_obj[name]
    except KeyError:

        msg = (
            f"Could not get ``{name}`` from ``lon_or_obj``. Please pass lon and lat "
            "directly"
        )

        msg += "." if has_cf_xarray else " or try installing cf_xarray."

        raise KeyError(msg)


def _get_cf_coords(
    obj: xr.Dataset | xr.DataArray, name: str, required: bool = False
) -> None | str:

    coord_name = obj.cf.coordinates.get(name)

    if not coord_name:
        if required:
            raise ValueError(f"Found no coords for {name}")
        return None

    if len(coord_name) > 1:
        raise ValueError(
            f"Found more than one candidate for '{name}'. Either pass the lon and lat "
            "coords directly or only pass a DataArray (instead of a Dataset) to the "
            "mask method."
        )

    return coord_name[0]


def _get_coords_cf_or_name(
    obj: xr.Dataset | xr.DataArray, lon_name: str, lat_name: str
) -> tuple[xr.DataArray, xr.DataArray]:

    x_name = _get_cf_coords(obj, "longitude", required=False) or lon_name
    y_name = _get_cf_coords(obj, "latitude", required=False) or lat_name

    _assert_unambiguous_coord_names(obj, x_name, lon_name)
    _assert_unambiguous_coord_names(obj, y_name, lat_name)

    return obj[x_name], obj[y_name]


def _assert_unambiguous_coord_names(
    obj: xr.Dataset | xr.DataArray, cf_name: str, name: str
) -> None:

    if cf_name != name and name in obj.coords:
        raise ValueError(
            f"Ambiguous name for coordinates: cf_xarray determined '{cf_name}' but "
            f"'{name}' is also on the {type(obj).__name__}. Please set ``use_cf`` to "
            "True or False to resolve this conflict."
        )


def _get_coords_cf(
    obj: np.typing.ArrayLike | xr.Dataset | xr.DataArray,
) -> tuple[xr.DataArray, xr.DataArray]:

    if not has_cf_xarray:
        raise ImportError("cf_xarray required")

    if not isinstance(obj, xr.Dataset | xr.DataArray):
        raise TypeError(
            "Expected a ``Dataset`` or ``DataArray`` for ``use_cf=True``, got"
            f" {type(obj)}"
        )

    x_name = _get_cf_coords(obj, "longitude", required=True)
    y_name = _get_cf_coords(obj, "latitude", required=True)

    return obj[x_name], obj[y_name]
