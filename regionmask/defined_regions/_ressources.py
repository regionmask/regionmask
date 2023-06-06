from pathlib import Path

import geopandas as gp
import pooch

import regionmask
from regionmask.core.options import OPTIONS


def _get_cache_dir():
    cache_dir = OPTIONS.get("cache_dir") or pooch.os_cache("regionmask")

    return Path(cache_dir).expanduser()


def fetch_remote_shapefile(name):
    """
    uses pooch to cache files
    """

    REMOTE_RESSOURCE = pooch.create(
        # Use the default cache folder for the OS
        path=_get_cache_dir(),
        # The remote data is on Github
        base_url="https://github.com/regionmask/regionmask/raw/{version}/data/",
        registry={
            "IPCC-WGI-reference-regions-v4.zip": "c83881a18e74912385ad578282de721cc8e866b62cbbc75446e52e7041c81cff",
            "IPCC-WGI-reference-regions-v1.zip": "8507cef52057785117cabc83d6e03414b5994745bf7f297c179eb50507f7ee89",
        },
        version=f"v{regionmask.__version__}",
        version_dev="main",
    )

    # the file will be downloaded automatically the first time this is run.
    return REMOTE_RESSOURCE.fetch(name)


def read_remote_shapefile(name):

    fname = fetch_remote_shapefile(name)

    return gp.read_file("zip://" + fname)
