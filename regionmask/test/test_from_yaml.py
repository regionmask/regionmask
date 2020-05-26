import os

import pytest

import regionmask
from regionmask.core.io import longdir_cache
from regionmask.defined_regions import build_region
from regionmask.defined_regions.from_yaml import download_regions_config, keywords_dict


@pytest.mark.slow()
@pytest.mark.parametrize(
    "dataset_key", regionmask.defined_regions.from_yaml.keywords_dict.keys()
)
def test_build_region(dataset_key):
    dataset_key_sanitized = keywords_dict[dataset_key]
    if download_regions_config[dataset_key_sanitized]["download"]["url"] is None:
        if (
            download_regions_config[dataset_key_sanitized]["download"]["manually"]
            is not None
        ):
            # dont test the already manually downloaded
            if not os.path.exists(
                f"{longdir_cache}/{dataset_key_sanitized}/{dataset_key_sanitized}.shp"
            ):
                with pytest.raises(ValueError) as record:
                    build_region(dataset_key)
                # expect manually
                assert "Please follow these instructions" in str(record.value)
        else:
            with pytest.raises(ValueError) as record:
                build_region(dataset_key)
            # expect information from yaml file not enough
            assert "downloaded based on the information from yaml file" in str(
                record.value
            )
    else:
        assert isinstance(build_region(dataset_key), regionmask.core.regions.Regions)


# def test_build_region_unknown_dataset_key()
