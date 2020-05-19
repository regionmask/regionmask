#########################################
Marine Areas/ Ocean Basins (NaturalEarth)
#########################################

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

    # cut border when saving (for maps)
    mpl.rcParams["savefig.bbox"] = "tight"

The following imports are necessary for the examples.

.. ipython:: python

    import regionmask
    import matplotlib.pyplot as plt

Ocean Basins
============

.. ipython:: python

    basins = regionmask.defined_regions.natural_earth.ocean_basins_50

    basins.plot(add_label=False);

    @savefig plotting_basins.png width=100%
    plt.tight_layout()

Also create a mask for a 1° grid globally:

.. ipython:: python

    import numpy as np

    # create a grid
    lon = np.arange(0.5, 360)
    lat = np.arange(89.5, -90, -1)

    mask = basins.mask(lon, lat)

    basins.plot(add_label=False, add_ocean=False);

     # plot using xarray
     mask.plot(add_colorbar=False);

    @savefig plotting_basins_mask.png width=100%
    plt.tight_layout()

