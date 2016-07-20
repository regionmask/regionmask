import numpy as np

from region_mask import _Regions_cls, _Region_cls

from shapely.geometry import Polygon, MultiPolygon

from pytest import raises

# =============================================================================

# set up the testing regions

name = 'Example'
numbers = [0, 1]
names = ['Unit Square1', 'Unit Square2']
abbrevs = ['uSq1', 'uSq2']

outl1 = ((0, 0), (0, 1), (1, 1.), (1, 0))
outl2 = ((0, 1), (0, 2), (1, 2.), (1, 1))
outlines = [outl1, outl2]

r1 = _Regions_cls(name, numbers, names, abbrevs, outlines)

numbers = [1, 2]
names = {1:'Unit Square1', 2: 'Unit Square2'}
abbrevs = {1:'uSq1', 2:'uSq2'}
poly1 = Polygon(outl1)
poly2 = Polygon(outl2)
poly = {1: poly1, 2: poly2}

r2 = _Regions_cls(name, numbers, names, abbrevs, poly)    

# =============================================================================

def test_name():
    assert r1.name == name

def test_numbers():
    assert np.allclose(r1.numbers, [0, 1])
    assert np.allclose(r2.numbers, [1, 2])

def test_names():
    assert r1.names == ['Unit Square1', 'Unit Square2']

def test_abbrevs():
    assert r1.abbrevs == ['uSq1', 'uSq2']

def test_coords():
    assert np.allclose(r1.coords, [outl1, outl2])

    out1 = np.vstack([outl1, outl1[0]])
    out2 = np.vstack([outl2, outl2[0]])

    assert np.allclose(r2.coords, [out1, out2])

def test_polygon():
    assert r1.polygons == [poly1, poly2]
    assert r2.polygons == [poly1, poly2]


def test_centroid():
    assert np.allclose(r1.centroids, [[0.5, 0.5], [0.5, 1.5]])

def test_map_keys_one():
    raises(KeyError, r1.__getitem__, '')
    assert r1.map_keys(0) == 0
    assert r1.map_keys('uSq1') == 0
    assert r1.map_keys('Unit Square1') == 0

    assert r2.map_keys(1) == 1
    assert r2.map_keys('uSq1') == 1
    assert r2.map_keys('Unit Square1') == 1


def test_map_keys_several():

    assert r1.map_keys([0, 1]) == [0, 1]
    assert r1.map_keys(('uSq1', 'uSq2')) == [0, 1]
    assert r1.map_keys(('Unit Square1', 'Unit Square2')) == [0, 1]

    assert r2.map_keys([1, 2]) == [1, 2]
    assert r2.map_keys(('uSq1', 'uSq2')) == [1, 2]
    assert r2.map_keys(('Unit Square1', 'Unit Square2')) == [1, 2]

def test_map_keys_mixed():
    assert r1.map_keys([0, 'uSq2']) == [0, 1]


def test_map_keys_unique():
    assert r1.map_keys([0, 0, 0]) == [0]
    assert r1.map_keys([0, 0, 0, 1]) == [0, 1]


def test_subset_to_Region():

    s1 = r1[0]
    assert isinstance(s1, _Region_cls)
    assert s1.number == 0
    assert s1.abbrev == 'uSq1'

    s1 = r1['uSq1']
    assert isinstance(s1, _Region_cls)
    assert s1.number == 0
    assert s1.abbrev == 'uSq1'

    s1 = r1['Unit Square1']
    assert isinstance(s1, _Region_cls)
    assert s1.number == 0
    assert s1.abbrev == 'uSq1'


def test_subset_to_Regions():

    s1 = r1[[0]]
    assert isinstance(s1, _Regions_cls)
    assert s1.numbers == [0]
    assert s1.abbrevs == ['uSq1']
