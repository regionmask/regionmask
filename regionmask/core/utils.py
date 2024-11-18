from __future__ import annotations

import warnings
from typing import Literal

import numpy as np
import shapely
import xarray as xr
from numpy.typing import ArrayLike


def _total_bounds(polygons) -> np.ndarray:

    return shapely.total_bounds(polygons)


def _flatten_polygons(polygons, error="raise") -> list[shapely.Polygon]:

    from shapely.geometry import MultiPolygon, Polygon

    if error not in ("raise", "skip"):
        raise ValueError("'error' must be one of 'raise' and 'skip'")

    polys = []
    for p in polygons:
        if isinstance(p, MultiPolygon):
            polys += list(p.geoms)
        elif isinstance(p, Polygon):
            polys += [p]
        else:
            if error == "raise":
                msg = f"Expected 'Polygon' or 'MultiPolygon', found {type(p)}"
                raise TypeError(msg)

    return polys


def _maybe_to_dict(keys, values) -> dict:
    """convert iterable to dict if necessary"""

    if not isinstance(values, dict):
        values = {key: value for key, value in zip(keys, values)}

    return values


def _create_dict_of_numbered_string(numbers, string) -> dict[int, str]:

    return {number: f"{string}{number}" for number in numbers}


def _sanitize_names_abbrevs(numbers, values, default) -> dict[int, str]:

    if isinstance(values, str):
        values = _create_dict_of_numbered_string(numbers, values)
    elif values is None:
        values = _create_dict_of_numbered_string(numbers, default)
    else:
        if not len(numbers) == len(values):
            raise ValueError("`numbers` and `values` do not have the same length.")

        values = _maybe_to_dict(numbers, values)

    return values


def _wrapAngle360(lon: ArrayLike) -> np.ndarray:
    """wrap angle to `[0, 360[`."""
    lon = np.array(lon)
    return np.mod(lon, 360)


def _wrapAngle180(lon: ArrayLike) -> np.ndarray:
    """wrap angle to `[-180, 180[`."""
    lon = np.array(lon)
    sel = (lon < -180) | (180 <= lon)
    lon[sel] = _wrapAngle360(lon[sel] + 180) - 180
    return lon


def _wrapAngle(
    lon: float | ArrayLike,
    wrap_lon: None | bool | Literal[180, 360] = True,
    is_unstructured: bool = False,
) -> np.ndarray:
    """wrap the angle to the other base

    If lon is from -180 to 180 wraps them to 0..360
    If lon is from 0 to 360 wraps them to -180..180
    """

    lon_ = [lon] if np.isscalar(lon) else lon

    lon_ = np.array(lon_)

    if wrap_lon is True:
        mn, mx = np.nanmin(lon_), np.nanmax(lon_)
        msg = "Cannot infer the transformation."
        wrap_lon = 360 if _is_180(mn, mx, msg_add=msg) else 180

    if wrap_lon == 180:
        lon_ = _wrapAngle180(lon_)

    if wrap_lon == 360:
        lon_ = _wrapAngle360(lon_)

    # check if they are still unique
    if lon_.ndim == 1 and not is_unstructured:
        if lon_.shape != np.unique(lon_).shape:
            raise ValueError("There are equal longitude coordinates (when wrapped)!")

    return lon_


def _is_180(lon_min: float, lon_max: float, *, msg_add: str = "") -> bool:

    lon_min = np.round(lon_min, 6)
    lon_max = np.round(lon_max, 6)

    if (lon_min < 0) and (lon_max > 180):
        msg = f"lon has data that is larger than 180 and smaller than 0. {msg_add}"
        raise ValueError(msg)

    return lon_max <= 180


def create_lon_lat_dataarray_from_bounds(
    lon_start, lon_stop, lon_step, lat_start, lat_stop, lat_step
) -> xr.Dataset:
    """example xarray Dataset

    Parameters
    ----------
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
    -------
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


def _is_numeric(numbers) -> bool:

    numbers = np.asarray(numbers)
    return np.issubdtype(numbers.dtype, np.number)


def equally_spaced(*args) -> bool:

    args_ = [np.asarray(arg) for arg in args]

    if any(arg.ndim > 1 for arg in args_):
        return False

    if any(arg.size < 2 for arg in args_):
        return False

    d_args = (np.diff(arg) for arg in args_)

    return all(np.allclose(d_arg[0], d_arg) for d_arg in d_args)


def _equally_spaced_on_split_lon(lon) -> bool:

    lon = np.asarray(lon)

    if lon.ndim > 1 or lon.size < 2:
        return False

    d_lon = np.diff(lon)
    d_lon_not_isclose = ~np.isclose(d_lon[0], d_lon)

    # there can only be one breakpoint
    return (d_lon_not_isclose.sum() == 1) and not d_lon_not_isclose[-1]


def _find_splitpoint(lon: ArrayLike) -> int:

    lon = np.asarray(lon)
    d_lon = np.diff(lon)

    d_lon_not_isclose = ~np.isclose(d_lon[0], d_lon)

    split_point = np.argwhere(d_lon_not_isclose)

    if len(split_point) != 1:
        raise ValueError("more or less than one split point found")

    return split_point.item() + 1


def _sample_coords(coord: ArrayLike) -> np.ndarray:
    """Sample coords for percentage overlap."""

    n = 10

    coord = np.asarray(coord)

    d_coord = coord[1] - coord[0]

    n_cells = coord.size

    left = coord[0] - d_coord / 2 + d_coord / (n * 2)
    right = coord[-1] + d_coord / 2 - d_coord / (n * 2)

    return np.linspace(left, right, n_cells * n)


def unpackbits(numbers: np.ndarray, num_bits: int) -> np.ndarray:
    "Unpacks elements of a array into a binary-valued output array."

    # after https://stackoverflow.com/a/51509307/3010700

    if np.issubdtype(numbers.dtype, np.floating):
        raise ValueError("numpy data type needs to be int-like")
    shape = numbers.shape + (num_bits,)

    numbers = numbers.reshape([-1, 1])
    mask = 2 ** np.arange(num_bits, dtype=numbers.dtype).reshape([1, num_bits])

    # avoid casting to float64
    out = np.empty(numbers.shape[0:1] + (num_bits,), dtype=bool)
    return np.bitwise_and(numbers, mask, out=out, casting="unsafe").reshape(shape)


def flatten_3D_mask(mask_3D: xr.DataArray) -> xr.DataArray:
    """flatten 3D masks

    Parameters
    ----------
    mask_3D : xr.DataArray
        3D mask to flatten and plot. Should be the result of
        `Regions.mask_3D(...)`.
    **kwargs : keyword arguments
        Keyword arguments passed to xr.plot.pcolormesh.

    Returns
    -------
    mesh : ``matplotlib.collections.QuadMesh``

    """

    if not isinstance(mask_3D, xr.DataArray):
        raise ValueError("expected a xarray.DataArray")

    if not mask_3D.ndim == 3:
        raise ValueError(f"``mask_3D`` must have 3 dimensions, found {mask_3D.ndim}")

    if "region" not in mask_3D.coords:
        raise ValueError("``mask_3D`` must contain the dimension 'region'")

    if (mask_3D.sum("region") > 1).any():
        warnings.warn(
            "Found overlapping regions which cannot correctly be reduced to a 2D mask",
            RuntimeWarning,
        )

    # flatten the mask
    mask_2D = (mask_3D * mask_3D.region).sum("region")

    # mask all gridpoints not belonging to any region
    return mask_2D.where(mask_3D.any("region"))


def _snap_polygon(polygon, to, atol, xy_col):
    """

    idx: x or y coordinate
    - 0: x-coord
    - 1: y-coord

    """

    arr = shapely.get_coordinates(polygon)

    sel = np.isclose(arr[:, xy_col], to, atol=atol)
    arr[sel, xy_col] = to

    return shapely.set_coordinates(polygon, arr)


def _snap(df, idx, to, atol, xy_col):

    polygons = df.loc[idx].geometry.tolist()

    polygons = [_snap_polygon(poly, to, atol, xy_col) for poly in polygons]
    df.loc[idx, "geometry"] = polygons

    return df


def _snap_to_90S(df, idx, atol):

    return _snap(df, idx, to=-90, atol=atol, xy_col=1)


def _snap_to_180E(df, idx, atol):

    return _snap(df, idx, to=180, atol=atol, xy_col=0)
