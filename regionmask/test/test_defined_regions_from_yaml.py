import pytest
import os

import regionmask
from regionmask.core.io import longdir_cache, download_regions_config


# make list dynamic
# teow is quite large
@pytest.mark.parametrize("dataset_key", ['meow', 'feow'])
def test_build_region_from_downloadable_datasets(dataset_key):
    region = regionmask.build_region(dataset_key)
    assert isinstance(region, regionmask.core.regions.Regions)


@pytest.mark.parametrize("dataset_key", ['Longhurst', 'LME'])
def test_build_region_if_datasets_have_been_downloaded(dataset_key):
    cached_file_path = f"{longdir_cache}/{download_regions_config[dataset_key]['from_geopandas_args']['shp_file_str']}"
    print(cached_file_path)
    if os.path.exists(cached_file_path):
        region = regionmask.build_region(dataset_key)
        assert isinstance(region, regionmask.core.regions.Regions)
