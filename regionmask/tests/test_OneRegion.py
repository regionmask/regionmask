import numpy as np
import pytest
from shapely.geometry import MultiPolygon, Polygon

from regionmask import _OneRegion


def test_attributes() -> None:

    outl = ((0, 0), (0, 1), (1, 1.0), (1, 0))
    r = _OneRegion(1, "Unit Square", "USq", outl)

    assert r.number == 1
    assert r.name == "Unit Square"
    assert r.abbrev == "USq"

    assert np.allclose(r.coords, outl)
    assert isinstance(r.coords, np.ndarray)

    assert r.polygon.equals(Polygon(outl))
    assert isinstance(r.polygon, Polygon)

    assert np.allclose(r.centroid, (0.5, 0.5))

    assert r.__repr__() == "<regionmask._OneRegion: Unit Square (USq / 1)>"


def test_polygon_input() -> None:

    # polygon closes open paths
    outl = ((0, 0), (0, 1), (1, 1.0), (1, 0), (0, 0))

    outl_poly = Polygon(outl)

    r = _OneRegion(1, "Unit Square", "USq", outl_poly)

    assert np.allclose(r.coords, outl)
    assert r.polygon == outl_poly


def test_multi_polygon_input() -> None:

    # polygon closes open paths
    outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0), (0, 0))
    outl2 = ((1, 1), (1, 2), (2, 2.0), (2, 1), (1, 1))
    nan = np.ones(shape=(1, 2)) * np.nan
    outl = np.vstack((outl1, nan, outl2))

    outl_poly = MultiPolygon([Polygon(outl1), Polygon(outl2)])

    r = _OneRegion(1, "Unit Square", "USq", outl_poly)

    assert np.allclose(r.coords, outl, equal_nan=True)
    assert r.polygon == outl_poly


def test_centroid() -> None:

    outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0))

    # normal
    r = _OneRegion(1, "Unit Square", "USq", outl1)
    assert np.allclose(r.centroid, (0.5, 0.5))

    # superfluous point -> center should still be at (0.5, 0.5)
    outl2 = ((0, 0), (0, 0.5), (0, 1), (1, 1.0), (1, 0))
    r = _OneRegion(1, "Unit Square", "USq", outl2)
    assert np.allclose(r.centroid, (0.5, 0.5))


def test_bounds() -> None:

    outl = ((0, 0), (0, 1), (1, 1.0), (1, 0))

    # normal
    r = _OneRegion(1, "Unit Square", "USq", outl)
    assert np.allclose(r.bounds, (0, 0, 1, 1))

    # a diamond-shape
    outl = ((0, 0), (1, -1), (2, 0), (1, 1))

    # normal
    r = _OneRegion(1, "Unit Square", "USq", outl)
    assert np.allclose(r.bounds, (0, -1, 2, 1))


def test_wrong_region_outlines() -> None:

    outl1 = (((0, 0), (0, 1)), ((1, 1.0), (1, 0)))

    with pytest.raises(ValueError, match="Outline must be 2D"):
        _OneRegion(1, "Unit Square", "USq", outl1)

    outl2 = ((0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 0))

    with pytest.raises(ValueError, match="Outline must have Nx2 elements"):
        _OneRegion(1, "Unit Square", "USq", outl2)
