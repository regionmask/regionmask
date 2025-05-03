Marine Areas/ Ocean Basins (NaturalEarth)
#########################################

The outline of the marine areas are obtained from
`Natural Earth <https://www.naturalearthdata.com/>`_.
They are automatically downloaded, cached\ [#]_ and opened with geopandas.
The following marine regions are defined in regionmask:

* Ocean basins 1:50m


.. ipython:: python
    :suppress:

    import matplotlib as mpl

    # cut border when saving (for maps)
    mpl.rcParams["savefig.bbox"] = "tight"

Import regionmask:

.. ipython:: python

    import regionmask

Ocean Basins
============

.. warning::
   ``natural_earth_v4_1_0.ocean_basins_50`` and ``natural_earth_v5_0_0.ocean_basins_50``
   do not extend all the way to 180°E (see `#410 <https://github.com/regionmask/regionmask/issues/410>`_).
   Please use ``natural_earth_v5_1_2.ocean_basins_50``

   Be careful, however, as the regions changed between the natural_earth versions.


.. ipython:: python

    basins = regionmask.defined_regions.natural_earth_v5_1_2.ocean_basins_50
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

    basins.plot(add_label=False);

    @savefig plotting_basins_mask.png width=100%
    mask.plot(add_colorbar=False);

.. [#] You can change the cache location using ``regionmask.set_options(cache_dir="~/.rmask")``.
