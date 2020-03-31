#####################
Region from geopandas
#####################

regionmask can also create regions from a geopandas.GeoDataFrame. 
These are often shapefiles, which can be opened in the formats .zip
and .shp with geopandas.read_file(url_or_path). When creating a region
with regionmask.from_geopandas you must provide the arguments names and
abbrevs as strings of the columns of the GeoDataFrame. If abbrevs is not 
present, you can use abbrevs='construct' which creates unique abbreviations.


The following marine regions are defined in regionmask:

* Marine Areas 1:50m

.. ipython:: python
    :suppress:

    # Use defaults so we don't get gridlines in generated docs
    import matplotlib as mpl
    mpl.rcdefaults()
    mpl.use('Agg')

The following imports are necessary for the examples.

.. ipython:: python

    import regionmask
    import geopandas
    import matplotlib.pyplot as plt


.. ipython:: python
    meow = geopandas.read_file('http://maps.tnc.org/files/shp/MEOW-TNC.zip')
    meow_regions = regionmask.from_geopandas(meow,
                                             names='ECOREGION',
                                             abbrevs='construct')

    meow_regions.plot(add_label=False);

    @savefig plotting_meow_regions.png width=6in
    plt.tight_layout()
