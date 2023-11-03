import geopandas as gpd
import geopandas.testing
import shapely
import shapely.geometry

from regionmask.core.utils import _snap, _snap_to_90S, _snap_to_180E


def test_snap_to_180E():

    poly = shapely.geometry.box(0, 0, 179, 10)
    poly_180 = shapely.geometry.box(0, 0, 180, 10)

    df = gpd.GeoDataFrame(geometry=[poly, poly])
    expected = gpd.GeoDataFrame(geometry=[poly_180, poly])

    result = _snap_to_180E(df, [0], atol=1)

    geopandas.testing.assert_geodataframe_equal(result, expected)


def test_snap_to_90S():

    poly = shapely.geometry.box(0, -89.9, 180, 10)
    poly_90 = shapely.geometry.box(0, -90, 180, 10)

    df = gpd.GeoDataFrame(geometry=[poly, poly])
    expected = gpd.GeoDataFrame(geometry=[poly, poly_90])

    result = _snap_to_90S(df, [1], atol=0.1)

    geopandas.testing.assert_geodataframe_equal(result, expected)


def test_snap_coords_along():

    poly = shapely.geometry.Polygon(
        [
            (179.0, 0.0),
            (179.0, 2.0),
            (179.0, 9.0),
            (179.0, 10.0),
            (0.0, 10.0),
            (0.0, 0.0),
        ]
    )

    poly_180 = shapely.geometry.Polygon(
        [
            (180.0, 0.0),
            (180.0, 2.0),
            (180.0, 9.0),
            (180.0, 10.0),
            (0.0, 10.0),
            (0.0, 0.0),
        ]
    )

    df = gpd.GeoDataFrame(geometry=[poly])
    expected = gpd.GeoDataFrame(geometry=[poly_180])

    result = _snap(df, [0], to=180, atol=1, xy_col=0)

    geopandas.testing.assert_geodataframe_equal(result, expected)


def test_snap_multipolygon():

    p1 = shapely.geometry.box(0, 0, 9, 10)
    p2 = shapely.geometry.box(0, 10, 9, 20)
    p3 = shapely.geometry.box(-5, 0, 0, 10)

    mp = shapely.geometry.MultiPolygon([p1, p2, p3])

    p1_adj = shapely.geometry.box(0, 0, 10, 10)
    p2_adj = shapely.geometry.box(0, 10, 10, 20)

    mp_adj = shapely.geometry.MultiPolygon([p1_adj, p2_adj, p3])

    df = gpd.GeoDataFrame(geometry=[mp])
    expected = gpd.GeoDataFrame(geometry=[mp_adj])

    result = _snap(df, [0], to=10, atol=1, xy_col=0)

    geopandas.testing.assert_geodataframe_equal(result, expected)


def test_snap_polygon_internal():

    ext = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    hole = [(0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5)]

    ext_snapped = [(0, 0), (0, 2.5), (2, 2.5), (2, 0), (0, 0)]

    polygon = shapely.geometry.Polygon(ext, [hole])
    polygon_snapped = shapely.geometry.Polygon(ext_snapped, [hole])

    df = gpd.GeoDataFrame(geometry=[polygon])
    expected = gpd.GeoDataFrame(geometry=[polygon_snapped])

    result = _snap(df, [0], to=2.5, atol=0.5, xy_col=1)

    geopandas.testing.assert_geodataframe_equal(result, expected)
