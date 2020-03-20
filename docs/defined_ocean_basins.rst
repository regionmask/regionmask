################################
Marine Areas/Ocean Basins (NaturalEarth)
################################

The outline of the marine areas are obtained from
`Natural Earth <http://www.naturalearthdata.com/>`_.
They are automatically downloaded on-the-fly (but only once) with cartopy and opened with geopandas.
The following marine regions are defined in regionmask:

* Marine Areas 1:50m


.. ipython:: python
    :suppress:

    # Use defaults so we don't get gridlines in generated docs
    import matplotlib as mpl
    mpl.rcdefaults()
    mpl.use('Agg')

The following imports are necessary for the examples.

.. ipython:: python

    import regionmask
    import matplotlib.pyplot as plt

Ocean Basins
============

.. ipython:: python

    basins = regionmask.defined_regions.natural_earth.ocean_basins_50

    basins.plot(add_label=False);

    @savefig plotting_basins.png width=6in
    plt.tight_layout()

Also create a mask for a 1° grid globally:

.. ipython:: python

    import numpy as np

    # create a grid
    lon = np.arange(0.5, 359.5)
    lat = np.arange(89.5, -89.5, -1)

    mask = states.mask(lon, lat, wrap_lon=True)
    mask_ma = np.ma.masked_invalid(mask)

    basins.plot(add_label=False, add_ocean=False);

    LON_EDGE = np.arange(0, 360)
    LAT_EDGE = np.arange(90, -90, -1)

    plt.pcolormesh(LON_EDGE, LAT_EDGE, mask_ma, cmap='viridis');

    @savefig plotting_basins_mask.png width=6in
    plt.tight_layout()
