import regionmask


def mask_geopandas(
    geodataframe,
    lon_or_obj,
    lat=None,
    lon_name="lon",
    lat_name="lat",
    method=None,
    xarray=None,
    wrap_lon=None,
):

    from geopandas import GeoDataFrame, GeoSeries

    if not isinstance(geodataframe, (GeoDataFrame, GeoSeries)):
        raise TypeError("input must be a geopandas 'GeoDataFrame' or 'GeoSeries'")

    if method == "legacy":
        raise ValueError("method 'legacy' not supported in 'mask_geopandas'")

    lon_min = geodataframe.bounds["minx"].min()
    lon_max = geodataframe.bounds["maxx"].max()
    is_180 = regionmask.core.utils._is_180(lon_min, lon_max)

    polygons = geodataframe["geometry"].tolist()

    numbers = geodataframe.index.values.tolist()

    # _mask requires 'dot' attributes - create a dummy class for now...
    class dummy(object):
        def __init__(self, polygons, is_180, numbers):
            self.polygons = polygons
            self.lon_180 = is_180
            self.numbers = numbers

    return regionmask.core.mask._mask(
        dummy(polygons, is_180, numbers),
        lon_or_obj,
        lat=lat,
        lon_name=lon_name,
        lat_name=lat_name,
        method=method,
        xarray=xarray,
        wrap_lon=wrap_lon,
    )
