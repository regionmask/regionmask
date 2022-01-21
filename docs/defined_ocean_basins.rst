#########################################
Marine Areas/ Ocean Basins (NaturalEarth)
#########################################

The outline of the marine areas are obtained from
`Natural Earth <http://www.naturalearthdata.com/>`_.
They are automatically downloaded on-the-fly, cached and opened with geopandas.
The following marine regions are defined in regionmask:

* Marine Areas 1:50m


.. warning::
   ``regionmask.defined_regions.natural_earth`` is deprecated. This used cartopy to download
   natural_earth data and it is unclear which version of the regions is available.
   Please use ``regionmask.defined_regions.natural_earth_v4_1_0`` or
   ``regionmask.defined_regions.natural_earth_v5_0_0`` instead.

   Be careful when with the different versions of ``natural_earth`` Regions. Some polygons
   and regions have changed and the numbering of the regions may be different.

.. ipython:: python
    :suppress:

    import matplotlib as mpl

    # cut border when saving (for maps)
    mpl.rcParams["savefig.bbox"] = "tight"

Import regionmask.

.. ipython:: python

    import regionmask
    regionmask.__version__

Ocean Basins
============

.. ipython:: python

    basins = regionmask.defined_regions.natural_earth.ocean_basins_50
    basins

.. ipython:: python

    @savefig plotting_basins.png width=100%
    basins.plot(add_label=False);

Also create a mask for a 1° grid globally:

.. ipython:: python

    import numpy as np

    # create a grid
    lon = np.arange(0.5, 360)
    lat = np.arange(89.5, -90, -1)

    mask = basins.mask(lon, lat)

    basins.plot(add_label=False, add_ocean=False);

    @savefig plotting_basins_mask.png width=100%
    mask.plot(add_colorbar=False);
