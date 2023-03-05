Countries/ States (NaturalEarth)
################################

The outline of the countries are obtained from
`Natural Earth <http://www.naturalearthdata.com/>`_.
They are automatically downloaded, cached\ [#]_ and opened with geopandas.
The following countries and regions are defined in regionmask.

* Countries 1:110m
* Countries 1:50m
* Countries 1:10m
* US States 1:50m
* US States 1:10m

.. warning::
   ``regionmask.defined_regions.natural_earth`` is deprecated.
   Please use ``natural_earth_v4_1_0`` or ``natural_earth_v5_0_0`` instead.

   Be careful when working with the different versions of NaturalEarth regions. Some
   polygons and regions have changed and the numbering of the regions may be different.

.. note::
   A mask obtained with a fine resolution dataset is not necessarily better.
   Always check your mask!

.. ipython:: python
    :suppress:

    import matplotlib as mpl

    # cut border when saving (for maps)
    mpl.rcParams["savefig.bbox"] = "tight"

Import regionmask:

.. ipython:: python

    import regionmask

Countries
=========

.. ipython:: python

    @savefig plotting_countries.png width=100%
    regionmask.defined_regions.natural_earth_v5_0_0.countries_110.plot(add_label=False);

US States
=========

.. ipython:: python

    states = regionmask.defined_regions.natural_earth_v5_0_0.us_states_50

    @savefig plotting_states.png width=100%
    states.plot(add_label=False);


Also create a mask for a 1° grid over the US:

.. ipython:: python

    import numpy as np

    # create a grid
    lon = np.arange(200.5, 325)
    lat = np.arange(74.5, 14, -1)

    mask = states.mask(lon, lat)

    states.plot(add_label=False);
    @savefig plotting_states_mask.png width=100%
    mask.plot(add_colorbar=False)


.. [#] You can change the cache location using ``regionmask.set_options(cache_dir="~/.rmask")``.
