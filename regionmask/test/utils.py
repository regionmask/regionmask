import numpy as np

from regionmask import Regions

outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0))
outl2 = ((0, 1), (0, 2), (1, 2.0), (1, 1))
outl3 = ((0, 1), (0, 2), (1, 3.0), (1, 1))

dummy_outlines = [outl1, outl2]
dummy_region = Regions(dummy_outlines)
dummy_outlines_poly = dummy_region.polygons

# no gridpoint in outl3
dummy_outlines3 = [outl1, outl2, outl3]
dummy_region3 = Regions(dummy_outlines)
dummy_outlines_poly3 = dummy_region3.polygons

dummy_lon = [0.5, 1.5]
dummy_lat = [0.5, 1.5]
dummy_lon_lat_dict = dict(lon=dummy_lon, lat=dummy_lat)

# in this example the result looks:
# | a fill |
# | b fill |


def expected_mask_2D(a=0, b=1, fill=np.NaN):
    return np.array([[a, fill], [b, fill]])


def expected_mask_3D(drop):
    return np.array([[[True, False], [False, False]], [[False, False], [True, False]]])


def expected_mask(a=0, b=1, fill=np.NaN, mask_3D=False, drop=False):

    if mask_3D:
        return expected_mask_3D()
    return expected_mask_2D(a, b, fill)
