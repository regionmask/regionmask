import os
import shutil

import pytest
from cartopy.io import DownloadWarning

from regionmask.core.io import (
    download_dataset,
    downloader,
    keywords_dict,
    longdir_cache,
)

# turns all warnings into errors for this module
pytestmark = pytest.mark.filterwarnings("error")


@pytest.mark.parametrize(
    ("name", "url", "shpfilename"),
    [
        ("MEOW", "http://maps.tnc.org/files/shp/MEOW-TNC.zip", "meow_ecos"),
        (
            "Andorra",
            "https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_AND_shp.zip",
            "gadm36_AND_1",
        ),
    ],
)
@pytest.mark.parametrize("file_available", [False, True])
def test_downloader_only_if_not_on_disk(name, url, shpfilename, file_available):
    """Test `downloader` downloads only if file not on disk."""
    folder = f"{longdir_cache}/{name}"
    if file_available:
        assert os.path.exists(folder)
    else:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        assert not os.path.exists(folder)

    if not file_available:
        with pytest.warns(DownloadWarning) as record:
            zipfilestr = downloader(url, name, shpfilename)
            for s in ["Downloading", url]:
                assert s in record[0].message.args[0]
            assert zipfilestr == f"{longdir_cache}/{name}/{name}.zip"
    else:
        # should trigger download and should not raise warning
        zipfilestr = downloader(url, name, shpfilename)
        assert zipfilestr == f"{longdir_cache}/{name}/{name}.shp"


@pytest.mark.parametrize("dataset_key", ["MEOW", "meow"])
def test_download_dataset(dataset_key):
    """Test whether `download_dataset` downloads the correct file."""
    assert download_dataset(dataset_key)
    dataset_key = keywords_dict[dataset_key]
    assert os.path.exists(f"{longdir_cache}/{dataset_key}/{dataset_key}.shp")
