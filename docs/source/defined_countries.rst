Countries/ States (NaturalEarth)
################################

The outline of the countries are obtained from
`Natural Earth <https://www.naturalearthdata.com/>`_.
They are automatically downloaded, cached\ [#]_ and opened with geopandas.
The following countries and regions are defined in regionmask.

* Countries 1:110m
* Countries 1:50m
* Countries 1:10m
* US States 1:50m
* US States 1:10m

.. note::
   A mask obtained with a fine resolution dataset is not necessarily better.
   Always check your mask!

.. ipython:: python
    :suppress:

    import matplotlib as mpl

    mpl.rcParams["figure.dpi"] = 200
    mpl.rcParams["savefig.bbox"] = "tight"

Import regionmask:

.. ipython:: python

    import regionmask

Countries
=========

.. warning::
   ``natural_earth_v4_1_0.countries_50`` and ``natural_earth_v5_0_0.countries_50``
   do not extend all the way to 90°S (see `#487 <https://github.com/regionmask/regionmask/issues/487>`_).
   If Antarctica is of interest, please use ``natural_earth_v5_1_2.countries_50`` instead.

   Be careful, however, as the regions may have changed between the natural_earth versions.

   Note that ``countries_10`` and ``countries_110`` do not exhibit this problem.


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
