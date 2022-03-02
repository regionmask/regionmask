############################
Using regionmask with intake
############################

Regions from geopandas shapefiles can be pre-defined in a yaml file, which can be
easily shared. This relies on ``intake_geopandas`` and accepts ``regionmask_kwargs``,
which are passed to ``regionmask.from_geopandas``.
If you set ``use_fsspec=True`` and use ``simplecache::`` in the url, the shapefile is
cached locally.

.. ipython:: python
    :suppress:

    # Use defaults so we don't get gridlines in generated docs
    import matplotlib as mpl
    mpl.rcdefaults()
    mpl.use('Agg')

    # cut border when saving (for maps)
    mpl.rcParams["savefig.bbox"] = "tight"

You need to install intake_geopandas, which combines geopandas and intake, see
https://intake.readthedocs.io/en/latest/.

.. ipython:: python

    import intake_geopandas
    import intake
    # open a pre-defined remote or local catalog yaml file
    url = 'https://raw.githubusercontent.com/regionmask/regionmask/main/data/regions_remote_catalog.yaml'
    cat = intake.open_catalog(url)
    # access data from remote source
    meow_regions = cat.MEOW.read()
    print(meow_regions)

    @savefig plotting_MEOW.png width=100%
    meow_regions.plot(add_label=False)


Find more such pre-defined regions in `remote_climate_data <https://github.com/aaronspring/remote_climate_data/blob/master/catalogs/regionmask.yaml>`_.

Build your own catalog
======================

To create a catalog we use the syntax described in
`intake <https://intake.readthedocs.io/en/latest/catalog.html#yaml-format>`_.
Let's explore the Marine Ecoregions Of the World (MEOW) data set, which is a
biogeographic classification of the world's coasts and shelves.

.. ipython:: python

    with open('regions_my_local_catalog.yml', 'w') as f:
        f.write("""
    plugins:
      source:
        - module: intake_geopandas
    sources:
      MEOW:
        description: MEOW for regionmask and cache
        driver: intake_geopandas.regionmask.RegionmaskSource
        args:
          urlpath: simplecache::http://maps.tnc.org/files/shp/MEOW-TNC.zip
          use_fsspec: true  # optional for caching
          storage_options:  # optional for caching
            simplecache:
              same_names: true
              cache_storage: cache
          regionmask_kwargs:
            names: ECOREGION
            abbrevs: _from_name
            source: http://maps.tnc.org
            numbers: ECO_CODE_X
            name: MEOW
    """)

.. ipython:: python

    cat = intake.open_catalog('regions_my_local_catalog.yml')
    meow_regions = cat.MEOW.read()
    print(meow_regions)


Because ``simplecache::`` was added to the urlpath and ``use_fsspec=True``, the zip file was
downloaded to the folder specified in cache_storage. The file access is now local.

.. ipython:: python

    import os
    assert os.path.exists('cache/MEOW-TNC.zip')
