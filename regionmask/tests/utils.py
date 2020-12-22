import numpy as np

from regionmask import Regions

outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0))
outl2 = ((0, 1), (0, 2), (1, 2.0), (1, 1))
# no gridpoint in outl3
outl3 = ((0, 2), (0, 3), (1, 3.0), (1, 2))

dummy_outlines = [outl1, outl2, outl3]
dummy_region = Regions(dummy_outlines)
dummy_outlines_poly = dummy_region.polygons

dummy_lon = [0.5, 1.5]
dummy_lat = [0.5, 1.5]
dummy_ll_dict = dict(lon=dummy_lon, lat=dummy_lat)

# in this example the result looks:
# | a fill |
# | b fill |


def expected_mask_2D(a=0, b=1, fill=np.NaN):
    return np.array([[a, fill], [b, fill]])


def expected_mask_3D(drop):

    a = [[True, False], [False, False]]
    b = [[False, False], [True, False]]
    c = [[False, False], [False, False]]

    if drop:
        return np.array([a, b])
    return np.array([a, b, c])
