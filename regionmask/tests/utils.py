import numpy as np

from regionmask import Regions

outl1 = ((1, 1), (1, 2), (2, 2.0), (2, 1)) #((0, 0), (0, 1), (1, 1.0), (1, 0))
outl2 = ((1, 2), (1, 3), (2, 3.0), (2, 2)) #((0, 1), (0, 2), (1, 2.0), (1, 1))
# no gridpoint in outl3
outl3 = ((1, 3), (1, 4), (2, 4.0), (2, 3)) #((0, 2), (0, 3), (1, 3.0), (1, 2))

dummy_outlines = [outl1, outl2, outl3]
dummy_region = Regions(dummy_outlines)
dummy_outlines_poly = dummy_region.polygons

dummy_lon = [0.,1.,2.,3.,4.,5.]#[0.5, 1.5]
dummy_lat = [0.,1.,2.,3.,4.,5.]#[0.5, 1.5]
dummy_ll_dict = dict(lon=dummy_lon, lat=dummy_lat)


#outl1_3D = ((0, 0), (0, 1), (1, 1.0), (1, 0))
#outl2_3D = ((0, 1), (0, 2), (1, 2.0), (1, 1))
# no gridpoint in outl3
#outl3_3D = ((0, 2), (0, 3), (1, 3.0), (1, 2))

#dummy_outlines_3D = [outl1_3D, outl2_3D, outl3_3D]
#dummy_region_3D = Regions(dummy_outlines_3D)
#dummy_outlines_poly_3D = dummy_region_3D.polygons

#dummy_lon_3D = [0.5, 1.5]
#dummy_lat_3D = [0.5, 1.5]
#dummy_ll_dict_3D = dict(lon=dummy_lon_3D, lat=dummy_lat_3D)


# in this example the result looks:
# | a fill |
# | b fill |


#def expected_mask_2D(a=0, b=1, fill=np.NaN):
#    return np.array([[a, fill], [b, fill]])

def expected_mask_2D(a=0, b=1,c=2, fill=np.NaN):
    #return np.array([[a, fill], [b, fill]])
    return np.array([[fill, fill, fill, fill, fill, fill],
       [fill, fill, fill, fill, fill, fill],
       [fill, fill,  a, fill, fill, fill],
       [fill, fill,  b, fill, fill, fill],
       [fill, fill,  c, fill, fill, fill],
       [fill, fill, fill, fill, fill, fill]])

#def expected_mask_3D(drop):

#    a = [[True, False], [False, False]]
#    b = [[False, False], [True, False]]
#    c = [[False, False], [False, False]]

#    if drop:
#        return np.array([a, b])
#    return np.array([a, b, c])

def expected_mask_3D(drop):

    a = [[False, False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False,  True, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False]]
    b = [[False, False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False,  True, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False]]
    c = [[False, False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False,  True, False, False, False],
        [False, False, False, False, False, False]]

    if drop:
        return np.array([a, b,c])
    return np.array([a, b, c])
