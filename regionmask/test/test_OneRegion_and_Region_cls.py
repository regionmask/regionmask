import numpy as np
import pytest
from shapely.geometry import MultiPolygon, Polygon

from regionmask import Region_cls, _OneRegion


@pytest.mark.filterwarnings("ignore:Using 'Region_cls'")
@pytest.mark.parametrize("cls", (Region_cls, _OneRegion))
def test_attributes(cls):

    outl = ((0, 0), (0, 1), (1, 1.0), (1, 0))
    r = cls(1, "Unit Square", "USq", outl)

    assert r.number == 1
    assert r.name == "Unit Square"
    assert r.abbrev == "USq"

    assert np.allclose(r.coords, outl)
    assert isinstance(r.coords, np.ndarray)

    assert r.polygon.equals(Polygon(outl))
    assert isinstance(r.polygon, Polygon)

    assert np.allclose(r.centroid, (0.5, 0.5))


@pytest.mark.filterwarnings("ignore:Using 'Region_cls'")
@pytest.mark.parametrize("cls", (Region_cls, _OneRegion))
def test_polygon_input(cls):

    # polygon closes open paths
    outl = ((0, 0), (0, 1), (1, 1.0), (1, 0), (0, 0))

    outl_poly = Polygon(outl)

    r = cls(1, "Unit Square", "USq", outl_poly)

    assert np.allclose(r.coords, outl)
    assert r.polygon == outl_poly


@pytest.mark.filterwarnings("ignore:Using 'Region_cls'")
@pytest.mark.parametrize("cls", (Region_cls, _OneRegion))
def test_multi_polygon_input(cls):

    # polygon closes open paths
    outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0), (0, 0))
    outl2 = ((1, 1), (1, 2), (2, 2.0), (2, 1), (1, 1))
    nan = np.ones(shape=(1, 2)) * np.nan
    outl = np.vstack((outl1, nan, outl2))

    outl_poly = MultiPolygon([Polygon(outl1), Polygon(outl2)])

    r = cls(1, "Unit Square", "USq", outl_poly)

    assert np.allclose(r.coords, outl, equal_nan=True)
    assert r.polygon == outl_poly


@pytest.mark.filterwarnings("ignore:Using 'Region_cls'")
@pytest.mark.parametrize("cls", (Region_cls, _OneRegion))
def test_centroid(cls):

    outl = ((0, 0), (0, 1), (1, 1.0), (1, 0))

    # normal
    r = cls(1, "Unit Square", "USq", outl)
    assert np.allclose(r.centroid, (0.5, 0.5))

    # user defined centroid
    c = (1, 1)
    r = cls(1, "Unit Square", "USq", outl, centroid=c)
    assert np.allclose(r.centroid, c)

    # superfluous point -> center should still be at (0.5, 0.5)
    outl = ((0, 0), (0, 0.5), (0, 1), (1, 1.0), (1, 0))
    r = cls(1, "Unit Square", "USq", outl)
    assert np.allclose(r.centroid, (0.5, 0.5))


@pytest.mark.filterwarnings("ignore:Using 'Region_cls'")
@pytest.mark.parametrize("cls", (Region_cls, _OneRegion))
def test_bounds(cls):

    outl = ((0, 0), (0, 1), (1, 1.0), (1, 0))

    # normal
    r = cls(1, "Unit Square", "USq", outl)
    assert np.allclose(r.bounds, (0, 0, 1, 1))

    # a diamond-shape
    outl = ((0, 0), (1, -1), (2, 0), (1, 1))

    # normal
    r = cls(1, "Unit Square", "USq", outl)
    assert np.allclose(r.bounds, (0, -1, 2, 1))


def test_Regions_cls_deprection_warning():

    outl = ((0, 0), (0, 1), (1, 1.0), (1, 0))

    with pytest.warns(
        FutureWarning,
        match="Using 'Region_cls' is deprecated, please use '_OneRegion' instead.",
    ):
        Region_cls(1, "Unit Square", "USq", outl)


@pytest.mark.filterwarnings("ignore:Using 'Region_cls'")
@pytest.mark.parametrize("cls", (Region_cls, _OneRegion))
def test_wrong_region_outlines(cls):

    outl = (((0, 0), (0, 1)), ((1, 1.0), (1, 0)))

    with pytest.raises(ValueError, match="Outline must be 2D"):
        cls(1, "Unit Square", "USq", outl)

    outl = ((0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 0))

    with pytest.raises(ValueError, match="Outline must have Nx2 elements"):
        cls(1, "Unit Square", "USq", outl)
