#####################
Region from geopandas
#####################

regionmask can create regions from a ``geopandas.GeoDataFrame``.
These are often shapefiles, which can be opened in the formats ``.zip``
or ``.shp`` with ``geopandas.read_file(url_or_path)``.

The Marine Ecosystems Of the World (MEOW) shapefile can be accessed from
`The Nature Conservancy <http://maps.tnc.org/gis_data.html>`_.

.. ipython:: python
    :suppress:

    # Use defaults so we don't get gridlines in generated docs
    import matplotlib as mpl
    mpl.rcdefaults()
    mpl.use('Agg')

.. ipython:: python

    import regionmask
    import geopandas
    import matplotlib.pyplot as plt

    meow = geopandas.read_file('http://maps.tnc.org/files/shp/MEOW-TNC.zip')
    display(meow)


Creating a region with ``regionmask.from_geopandas`` only requires a ``GeoDataFrame``:

.. ipython:: python

    meow_regions = regionmask.from_geopandas(meow)
    display(meow_regions)

This creates default names (``"Region0"``, ..., ``"RegionN"``) and
abbreviations (``"r0"``, ..., ``"rN"``).

However, it is often advantageous to use columns of the ``GeoDataFrame``
as ``names`` and ``abbrevs``. If no column with abbreviations is available,
you can use ``abbrevs='_from_name'``, which creates unique abbreviations
using the names column.

.. ipython:: python

    meow_regions = regionmask.from_geopandas(
        meow,
        names="ECOREGION",
        abbrevs="_from_name"
    )
    display(meow_regions)

As usual the newly created ``Regions`` object can be plotted on a world map:

.. ipython:: python

    meow_regions.plot(add_label=False);

    @savefig plotting_meow_regions.png width=6in
    plt.tight_layout()
