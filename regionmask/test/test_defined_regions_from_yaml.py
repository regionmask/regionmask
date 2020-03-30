import pytest

import regionmask


# make list dynamic
# teow is quite large
@pytest.mark.parametrize("dataset_key", ['meow', 'feow'])
def test_build_region_from_downloadable_datasets(dataset_key):
    region = regionmask.build_region(dataset_key)
    assert isinstance(region, regionmask.Region)
