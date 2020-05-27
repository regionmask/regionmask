############################
Predefined regions from yaml
############################

Spatial aggregation with `regionmask` works with many shapefiles which are freely available to download.
However, there are some figuration details in `geopandas` that make exploration of availbale `regionmask`-compatible shapefiles tedious.
To help you/users a quick and reproducible access to these ``Regions``, use ``defined_regions.from_yaml.build_region``.
All information to process a URL into a ``Region`` is accessible in a `yaml` file  ``defined_regions.downloadable_regions.yaml``.
The shapefile is automatically downloaded on-the-fly (but only once) with cartopy and opened with geopandas.
The arguments to be passed to `from_geopandas` can be accessed from there, as well as `preprocess` for data cleaning (``gdf=gdf.dropna()``) or re-projection (``gdf=gdf.to_crs('EPSG:4326')``) before calling `from_geopandas`.
For datasets that are downloadable but not automatically (because the link is not static), a manual download instruction is provided. Please contribute to ``defined_regions.downloadable_regions.yaml`` if you find more suitable shapefiles.

The following datasets are currently available:

.. ipython:: python

    from regionmask.defined_regions.from_yaml import download_regions_config
    print('Key:','Longname:','Automatic download:')
    for key in download_regions_config:
        automatic = True if download_regions_config[key]['download']['url'] is not None else False
        print(f'{key}: {download_regions_config[key]["long_name"]}: {automatic}')

.. ipython:: python
    :suppress:

    # Use defaults so we don't get gridlines in generated docs
    import matplotlib as mpl
    mpl.rcdefaults()
    mpl.use('Agg')

    # cut border when saving (for maps)
    mpl.rcParams["savefig.bbox"] = "tight"

How to use:

.. ipython:: python

    import regionmask
    meow = regionmask.defined_regions.build_region('MEOW')
    meow

    meow.plot(add_label=False)
    @savefig plotting_landmask.png width=100%
    plt.tight_layout()
