############################
Using regionmask with intake
############################

Regions from geopandas shapefiles can be pre-defined in a yaml file, which can be
easily shared. This relies on ``intake_geopandas`` and accepts ``regionmask_kwargs``,
which are passed to ``regionmask.from_geopandas``.

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

Let's explore the Marine Ecoregions Of the World (MEOW) data set, which is a
biogeographic classification of the world's coasts and shelves.

.. ipython:: python

    import importlib

    import intake
    import intake_geopandas

    # open a pre-defined remote or local catalog yaml file, containing the MEOW regions
    path = importlib.resources.files("regionmask").parent / "data"
    filename = path / "regions_remote_catalog.yaml"

    cat = intake.open_catalog(filename)

    # access data from remote source
    meow_regions = cat.MEOW.read()
    print(meow_regions)

    @savefig plotting_MEOW.png width=100%
    meow_regions.plot(add_label=False)

Remote catalogs can also be used:

.. code-block:: python

    url = 'https://raw.githubusercontent.com/regionmask/regionmask/main/data/regions_remote_catalog.yaml'
    cat = intake.open_catalog(path)

Because the catalog sets ``use_fsspec=True`` and uses ``simplecache::`` in the url, the shapefile is
cached locally:

.. ipython:: python

    import os
    import zipfile

    file = ".cache/MEOW-TNC/data"

    assert os.path.exists(file)
    assert zipfile.is_zipfile(file)


Find more such pre-defined regions in `remote_climate_data <https://github.com/aaronspring/remote_climate_data/blob/master/catalogs/regionmask.yaml>`_.

Build your own catalog
======================

To create a catalog we use the syntax described in `intake <https://intake.readthedocs.io/en/latest/catalog.html#yaml-format>`_.
Below we show the catalog used above, which contains two example datasets (the second is the MEOW regions):

.. literalinclude:: ../../data/regions_remote_catalog.yaml
   :language: yaml

