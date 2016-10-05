#######################
Landmask (NaturalEarth)
#######################

The outline of the landmask is obtained from 
`Natural Earth <http://www.naturalearthdata.com/>`_.
It is automatically downloaded on-the-fly (but only once) with cartopy and opened with geopandas.
The following landmask is currently available:

* Land 1:110m

.. note::
   If available, it is better to use the landmask of the used data set.

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

Landmask
========

.. warning::
   The Caspian Sea is not included in the (land-) mask (see (:issue:`22`))!

.. ipython:: python

    land = regionmask.defined_regions.natural_earth.land_110
    land.plot(add_label=False, add_ocean=False, coastlines=False);

    @savefig plotting_countries.png width=6in height=3in
    plt.tight_layout()
