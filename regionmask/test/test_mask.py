import numpy as np

from regionmask import _Regions_cls, _Region_cls
from regionmask import create_mask_contains


from shapely.geometry import Polygon, MultiPolygon
from pytest import raises

import xarray as xr

# =============================================================================


name = 'Example'
numbers = [0, 1]
names = ['Unit Square1', 'Unit Square2']
abbrevs = ['uSq1', 'uSq2']

outl1 = ((0, 0), (0, 1), (1, 1.), (1, 0))
outl2 = ((0, 1), (0, 2), (1, 2.), (1, 1))
outlines = [outl1, outl2]

r1 = _Regions_cls(name, numbers, names, abbrevs, outlines) 


lon = [0.5, 1.5]
lat = [0.5, 1.5]

# in this example the result looks:
# a fill
# b fill

def expected_mask(a=0, b=1, fill=np.NaN):
    return np.array([[a, fill], [b, fill]])



def test_create_mask_contains():

    # standard
    result = create_mask_contains(lat, lon, outlines)
    expected = expected_mask()
    assert np.allclose(result, expected, equal_nan=True)

    result = create_mask_contains(lat, lon, outlines, fill=5)
    expected = expected_mask(fill=5)
    assert np.allclose(result, expected, equal_nan=True)

    result = create_mask_contains(lat, lon, outlines, numbers=[5, 6])
    expected = expected_mask(a=5, b=6)
    assert np.allclose(result, expected, equal_nan=True)

    raises(AssertionError, create_mask_contains, lat, lon, outlines, fill=0)

    raises(AssertionError, create_mask_contains, lat, lon, outlines,
           numbers=[5])

def test__mask():

    expected = expected_mask()
    result = r1.mask(lon, lat, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)

def test__mask_xarray():

    expected = expected_mask()
    result = r1.mask(lon, lat, xarray=True)

    assert isinstance(result, xr.DataArray)
    assert np.allclose(result, expected, equal_nan=True)
    assert np.allclose(result.lat, lat)
    assert np.allclose(result.lon, lon)


def test__mask_obj():

    expected = expected_mask()
    
    obj = dict(lon=lon, lat=lat)
    result = r1.mask(obj, xarray=False)
    assert np.allclose(result, expected, equal_nan=True)

    obj = dict(longitude=lon, latitude=lat)
    result = r1.mask(obj, lon_name='longitude', lat_name='latitude', 
                     xarray=False)
    
    assert np.allclose(result, expected, equal_nan=True)
