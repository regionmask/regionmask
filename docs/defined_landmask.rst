Landmask (NaturalEarth)
#######################

The outline of the landmask is obtained from
`Natural Earth <http://www.naturalearthdata.com/>`_.
It is automatically downloaded, cached\ [#]_ and opened with geopandas.
The following landmasks are currently available:

* Land 1:110m
* Land 1:50m
* Land 1:10m

.. note::
   If available, it is better to use the landmask of the used data set.

.. ipython:: python
    :suppress:

    import matplotlib as mpl

    # cut border when saving (for maps)
    mpl.rcParams["savefig.bbox"] = "tight"

Import regionmask:

.. ipython:: python

    import regionmask

Landmask
========

.. warning::
   ``natural_earth_v4_1_0.land_50`` and ``natural_earth_v5_0_0.land_50``
   do not extend all the way to 90°S (see `#487 <https://github.com/regionmask/regionmask/issues/487>`_).
   If Antarctica is of interest, please use ``natural_earth_v5_1_2.land_50`` instead.

   Be careful, however, as the regions may have changed between the natural_earth versions.

   Note that ``land_10`` and ``land_110`` do not exhibit this problem.


.. ipython:: python

    land = regionmask.defined_regions.natural_earth_v5_0_0.land_110

    @savefig plotting_landmask.png width=100%
    land.plot(add_label=False)

.. [#] You can change the cache location using ``regionmask.set_options(cache_dir="~/.rmask")``.
