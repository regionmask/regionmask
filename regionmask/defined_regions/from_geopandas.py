import numpy as np
import pandas as pd

from ..core.regions import Regions
from .natural_earth import _maybe_get_column


def from_geopandas(
    geodataframe,
    numbers=None,
    names=None,
    abbrevs=None,
    name='unnamed',
    source=None
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
        Name of the column in shapefile that names a region. Breaks for doublicates.
    abbrev_col : str (optional)
        Abbreviation of the column in shapefile that five a region its abbreviation.
        If 'construct', a combination of the first letters of region name is taken.
        Breaks for doublicates.
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
        if abbrevs == 'construct':
            abbrevs = []
            for item in geodataframe.T:
                name_for_abbrev = geodataframe.loc[item][names]
                # catch region with no name
                if name_for_abbrev is None:
                    name_for_abbrev = 'UND'  # for undefined
                abbrev = "".join(word[0]
                                 for word in name_for_abbrev.split(' '))
                # remove certain chars
                for char_to_remove in ['-', ' ', ')', '(']:
                    abbrev = abbrev.replace(char_to_remove, '')
                # if find doublicates, add counter
                counter = 2
                if abbrev in abbrevs:
                    while (abbrev + str(counter)) in abbrevs:
                        counter += 1
                    abbrev = abbrev + str(counter)
                abbrevs.append(abbrev)
        else:
            abbrevs = _maybe_get_column(geodataframe, abbrevs)
    else:
        raise ValueError('Please provide a string take can be taken from '
                         f' geodataframe.columns for `abbrevs`, found {abbrevs}')
    if names is not None:
        names = _maybe_get_column(geodataframe, names)
    else:
        raise ValueError('Please provide a string take can be taken from '
                         f' geodataframe.columns for `names`, found {names}')

    outlines = _maybe_get_column(geodataframe, 'geometry')

    # check doublicates
    for to_check in [abbrevs, names]:
        if len(set(to_check)) != len(to_check):
            if isinstance(to_check, list):
                doublicates = set(
                    [x for x in to_check if to_check.count(x) > 1])
            elif isinstance(pd.Series):
                doublicates = to_check[to_check.duplicated(keep=False)]
            raise ValueError(
                f"Found doublicates {doublicates}, but should not. {to_check}")

    return Regions(outlines,
                   numbers=numbers, names=names,
                   abbrevs=abbrevs, name=name, source=source)
