import numpy as np

from ..core.regions import Regions
from .natural_earth import _maybe_get_column


def from_geopandas(
    geodataframe,
    numbers=None,
    names=None,
    abbrevs=None,
    name='unnamed',
    source=None,
    # not implemented yet
    on_name_missing="error",
    on_name_duplicates="error",
    on_abbrev_missing="error",
    on_abbrev_duplicates="error"
):
    """
    create Regions from geodataframe data

    manually downloaded or by url from download_regions.yaml

    Parameters
    ----------
    geodataframe : geopandas.geodataframe.GeoDataFrame
        Shapefile to be downloaded. File has extensions .shp.
    number : str (optional)
        Number of the column in shapefile that gives a region its number.
        This column shouldnt have duplicates. If None (default), takes shapefile.index.
    names : str
        Name of the column in shapefile that names a region.
    abbrev_col : str (optional)
        Abbreviation of the column in shapefile that five a region its abbreviation.
        If None (default), a combination of the first letters of region name is taken.
    name : str (optional)
        name of the regionmask.Region instance created
    source : str (optional)
        source of the shapefile

    Returns
    -------
    regionmask.core.regions.Regions

    """

    # get necessary data for Regions

    if numbers is not None:
        # sort, otherwise breaks
        geodataframe = geodataframe.sort_values(numbers)
        # ensure integer
        geodataframe[numbers] = geodataframe[numbers].astype('int')
        numbers = _maybe_get_column(geodataframe, numbers)
    else:
        numbers = geodataframe.index.values
    # make sure numbers is a list
    numbers = np.array(numbers)

    if abbrevs is not None:
        abbrevs = _maybe_get_column(geodataframe, abbrevs)
    else:
        abbrevs = []
        for item in geodataframe.T:
            name_for_abbrev = geodataframe.loc[item][names]
            # catch region with no name
            if name_for_abbrev is None:
                name_for_abbrev = 'UND'  # for undefined
            abbrev = "".join(word[0] for word in name_for_abbrev.split(' '))
            abbrevs.append(abbrev)
    names = _maybe_get_column(geodataframe, names)

    outlines = _maybe_get_column(geodataframe, 'geometry')

    return Regions(outlines,
                   numbers=numbers, names=names,
                   abbrevs=abbrevs, name=name, source=source)
