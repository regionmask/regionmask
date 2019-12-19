#######################
Landmask (NaturalEarth)
#######################

The outline of the landmask is obtained from
`Natural Earth <http://www.naturalearthdata.com/>`_.
It is automatically downloaded on-the-fly (but only once) with cartopy and opened with geopandas.
The following landmask is currently available:

* Land 1:110m

.. note::
   If available, it is better to use the landmask of the used data set.

.. ipython:: python
    :suppress:

    # Use defaults so we don't get gridlines in generated docs
    import matplotlib as mpl
    mpl.rcdefaults()
    mpl.use('Agg')

The following imports are necessary for the examples.

.. ipython:: python

    import cartopy.crs as ccrs
    import regionmask
    import matplotlib.pyplot as plt

Landmask
========

.. note::
   From v0.5 the Caspian Sea is included in the (land-) mask.

.. ipython:: python

    land = regionmask.defined_regions.natural_earth.land_110

    f, ax = plt.subplots(1, 1, subplot_kw=dict(projection=ccrs.PlateCarree()))

    # use add_geometries because land.plot does not add the polygon interiors
    ax.add_geometries(land.polygons, ccrs.PlateCarree(), fc="none", ec="0.1")

    @savefig plotting_landmask.png width=6in
    plt.tight_layout()

