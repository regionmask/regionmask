Landmask (NaturalEarth)
#######################

The outline of the landmask is obtained from
`Natural Earth <http://www.naturalearthdata.com/>`_.
It is automatically downloaded, cached\ [#]_ and opened with geopandas.
The following landmasks are currently available:

* Land 1:110m
* Land 1:50m
* Land 1:10m

.. warning::
   ``regionmask.defined_regions.natural_earth`` is deprecated.
   Please use ``natural_earth_v4_1_0`` or ``natural_earth_v5_0_0`` instead.

   Be careful when working with the different versions of NaturalEarth regions. Some
   polygons and regions have changed and the numbering of the regions may be different.


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

.. ipython:: python

    land = regionmask.defined_regions.natural_earth_v5_0_0.land_110

    @savefig plotting_landmask.png width=100%
    land.plot(add_label=False)

.. [#] You can change the cache location using ``regionmask.set_options(cache_dir="~/.rmask")``.
