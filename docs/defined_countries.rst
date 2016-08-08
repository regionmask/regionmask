################################
Countries/ States (NaturalEarth)
################################

The outline of the countries are obtained from 
`Natural Earth <http://www.naturalearthdata.com/>`_.
They are automatically downloaded on-the-fly (but only once) with cartopy and opened with geopandas.
The following countries and regions are defined in regionmask.

* Countries 1:110m
* Countries 1:50m
* US States 1:50m
* US States 1:10m

.. note::
   A mask obtained with a fine resolution dataset is not necessarily better.
   Always check your mask!

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

Countries
=========

.. ipython:: python

    regionmask.defined_regions.natural_earth.countries_110.plot(add_label=False);

    @savefig plotting_countries.png width=6in height=3in
    plt.tight_layout()

US States
=========

.. ipython:: python

    states = regionmask.defined_regions.natural_earth.us_states_50

    states.plot(add_label=False);

    @savefig plotting_states.png width=6in
    plt.tight_layout()

Also create a mask for a 1° grid over the US:

.. ipython:: python
    
    import numpy as np
    
    # create a grid
    lon = np.arange(200.5, 325)
    lat = np.arange(74.5, 14, -1)

    mask = states.mask(lon, lat, wrap_lon=True)
    mask_ma = np.ma.masked_invalid(mask)

    states.plot(add_label=False);
    
    LON_EDGE = np.arange(200, 326)
    LAT_EDGE = np.arange(75, 13, -1)

    plt.pcolormesh(LON_EDGE, LAT_EDGE, mask_ma, cmap='viridis');

    @savefig plotting_states_mask.png width=6in
    plt.tight_layout()    