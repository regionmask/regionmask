=================================================
Plotting and creating weighted masks
=================================================

Introduction:
-------------
The aim of the modifications of the Regionmask module is to include functions to compute weighted masks for different kind of grids.
The different kinds of grids are: regular grids, rotated pole grids and irregular grids.

Methods:
-------------
There are three methods added. All of them are based on the same code-style. A lon/lat-drid is needed as well as a shapefile.
A new grid of polygons is created and intersected with the provided shapefile. Then the areal weights are computed.
1. Method: "weights_default"
With this method one can compute weighted masks for regular grids.
2. Method: "weights_rot_pole"
This method transforms the coordinate system of the shapefile provided into the coordinate system of the rlon/rlat-grid provided.
The information fo the coordinate transformation has to be provided in for example this form:
"regionmask.mask_geopandas(shapefile, rlon, rlat, method="weights_rot_pole",pole_longitude=-162,pole_latitude=39.25,central_rotated_longitude=0, globe='WGS84')"
3. Method: "weights_irregular"
This is a work in progress. The polygonal grid created is not cruvilinear, but rectilinear, the method delivers therefore an approximiation.
