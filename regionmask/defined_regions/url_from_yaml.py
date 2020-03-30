import os

import geopandas

from ..core.io import download_dataset, longdir_cache, keywords_dict, download_regions_config
from .from_geopandas import from_geopandas


def build_region(dataset_key):
    """Build a pre-defined region in download_regions.yaml.

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
        raise ValueError(f"{dataset_key} not found in keywords: "
                         f"Please select from {keywords_dict.keys()}.")
    dataset_key = keywords_dict[dataset_key]

    shapefile_args = download_regions_config[dataset_key]['from_geopandas_args']
    shp_file_str = shapefile_args['shp_file_str']
    shp_file_str_long = f'{longdir_cache}/{shp_file_str}'
    # download shapefile if not in longdir_cache
    if not os.path.exists(shp_file_str_long):
        url = download_regions_config[dataset_key]['download']['url']
        # aim to download from url given in yaml
        if url != 'None':
            download_dataset(dataset_key=dataset_key)
            print(f"Download dataset {dataset_key} from website "
                  f" {download_regions_config[dataset_key]['website']} and url "
                  f" {download_regions_config[dataset_key]['download']['url']}.")
        # if no downloadable url is present in yaml,
        # print message to download manually
        else:
            raise ValueError(
                f"Dataset {dataset_key} cannot be automatically downloaded. "
                f"Please follw these instructions: "
                f"{download_regions_config[dataset_key]['download']['manually']}. "
                f"Then unzip if needed and ensure that ~/.regionmask_data/ "
                f"{shapefile_args['shp_file_str']} exists.")
    # open shapefile
    shp = geopandas.read_file(shp_file_str_long)
    # handle not required args
    abbrevs = shapefile_args['abbrevs'] if 'abbrevs' in shapefile_args else None
    # create region
    new_region = from_geopandas(shp,
                                names=shapefile_args['names'],
                                name=shapefile_args['name'],
                                numbers=shapefile_args['numbers'],
                                abbrevs=abbrevs,
                                )
    return new_region
