#####################
Region from geopandas
#####################

regionmask can also create regions from a ``geopandas.GeoDataFrame``. 
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


When creating a region with ``regionmask.from_geopandas``, you must provide the
arguments ``names`` and ``abbrevs`` as strings of the columns of the ``GeoDataFrame``.
If ``abbrevs`` is not present, you can use ``abbrevs='_from_name'``,
which creates unique abbreviations.

.. ipython:: python

    meow_regions = regionmask.from_geopandas(meow,
                                             names='ECOREGION',
                                             abbrevs='_from_name')

    meow_regions.plot(add_label=False);

    @savefig plotting_meow_regions.png width=6in
    plt.tight_layout()
