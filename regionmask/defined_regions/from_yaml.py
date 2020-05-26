import os

import geopandas

from ..core._geopandas import from_geopandas
from ..core.io import (
    download_dataset,
    download_regions_config,
    keywords_dict,
    longdir_cache,
)


def build_region(dataset_key):
    """Build a pre-defined region in downloadable_regions.yaml. Download if necessary.

    Parameters
    ----------
    dataset_key : str
        String of dataset. Keywords from download_regions are also allowed.

    Returns
    -------
    regionmask.core.regions.Regions

    """
    # convert keyword to real dataset key
    if dataset_key not in keywords_dict:
        raise ValueError(
            f"{dataset_key} not found in keywords: "
            f"Please select from {keywords_dict.keys()}."
        )
    dataset_key = keywords_dict[dataset_key]

    shpfilename_long = f"{longdir_cache}/{dataset_key}/{dataset_key}.shp"
    shapefile_args = download_regions_config[dataset_key]["from_geopandas_args"]
    # download shapefile if not in longdir_cache
    if not os.path.exists(shpfilename_long):
        url = download_regions_config[dataset_key]["download"]["url"]
        # if url given
        if url is not None:
            download_dataset(dataset_key=dataset_key)
        # if no downloadable url is present in yaml
        else:
            # give manual download instructions
            if "manually" in download_regions_config[dataset_key]["download"]:
                raise ValueError(
                    f"Dataset {dataset_key} cannot be automatically downloaded. "
                    f"Please follow these instructions: "
                    f"{download_regions_config[dataset_key]['download']['manually']} "
                    f"Then unzip if needed and ensure that "
                    f"~/.regionmask_data/{dataset_key}/{dataset_key}.ext "
                    f"(for ext in ['shp','shx','dbf']) exist."
                )
            else:
                raise ValueError(
                    "Dataset {dataset_key} cannot be automatically "
                    "downloaded based on the information from yaml file."
                )
    # open shapefile
    gdf = geopandas.read_file(shpfilename_long)
    preprocess = (
        download_regions_config[dataset_key]["preprocess"]
        if "preprocess" in download_regions_config[dataset_key]
        else None
    )
    if preprocess is not None:
        gdf = eval(f"{download_regions_config[dataset_key]['preprocess']}")
    # handle not required args
    names = shapefile_args["names"] if "names" in shapefile_args else None
    name = shapefile_args["name"] if "name" in shapefile_args else None
    numbers = shapefile_args["numbers"] if "numbers" in shapefile_args else None
    abbrevs = shapefile_args["abbrevs"] if "abbrevs" in shapefile_args else None
    # create region
    new_region = from_geopandas(
        gdf, names=names, name=name, numbers=numbers, abbrevs=abbrevs,
    )
    return new_region
