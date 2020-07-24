import geopandas as gp
import pooch

REMOTE_RESSOURCE = pooch.create(
    # Use the default cache folder for the OS
    path=pooch.os_cache("regionmask"),
    # The remote data is on Github
    base_url="https://github.com/mathause/regionmask/raw/master/data/",
    registry={
        "CMIP6_referenceRegions.zip": "258eabc4f2167631b80049050de554c83fc1785872ed12b563ce49a2b035cb6c",
        "CMIP6_referenceRegions_pre_revisions.zip": "8507cef52057785117cabc83d6e03414b5994745bf7f297c179eb50507f7ee89",
    },
)


def fetch_remote_shapefile(name):
    """
    uses pooch to cache files
    """

    # the file will be downloaded automatically the first time this is run.
    return REMOTE_RESSOURCE.fetch(name)


def read_remote_shapefile(name):

    fname = fetch_remote_shapefile(name)

    return gp.read_file("zip://" + fname)
