#######################
Landmask (NaturalEarth)
#######################

The outline of the landmask is obtained from
`Natural Earth <http://www.naturalearthdata.com/>`_.
It is automatically downloaded on-the-fly (but only once) with cartopy and opened with geopandas.
The following landmasks are currently available:

* Land 1:110m
* Land 1:50m
* Land 1:10m

.. note::
   If available, it is better to use the landmask of the used data set.

.. ipython:: python
    :suppress:

    # Use defaults so we don't get gridlines in generated docs
    import matplotlib as mpl
    mpl.rcdefaults()
    mpl.use('Agg')

    # cut border when saving (for maps)
    mpl.rcParams["savefig.bbox"] = "tight"

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

    land.plot()

    @savefig plotting_landmask.png width=100%
    plt.tight_layout()
