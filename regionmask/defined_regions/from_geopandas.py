import numpy as np
import pandas as pd

from ..core.regions import Regions
from .natural_earth import _maybe_get_column


def _check_duplicates(to_check):
    """Checks if `to_check` has duplicates. If so, raises error. If not, return True."""
    if len(set(to_check)) == len(to_check):
        return True
    else:
        if isinstance(to_check, list):
            duplicates = set(
                [x for x in to_check if to_check.count(x) > 1])
        elif isinstance(to_check, pd.core.series.Series):
            duplicates = to_check[to_check.duplicated(keep=False)]
        else:
            raise ValueError(
                "to_check not in [list, pd.Series], found {}".format(type(to_check)))
        if len(duplicates) > 0:
            raise ValueError(
                "Found duplicates {}, but should not. {}".format(duplicates, to_check))
        else:
            return True


def _construct_abbrevs(geodataframe, names):
    """Construct unique abbreviations based on geodataframe.names."""
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
        # if find duplicates, add counter
        counter = 2
        if abbrev in abbrevs:
            while (abbrev + str(counter)) in abbrevs:
                counter += 1
            abbrev = abbrev + str(counter)
        abbrevs.append(abbrev)
    return abbrevs


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
        Name of the column in shapefile that names a region. Breaks for duplicates.
    abbrev_col : str (optional)
        Abbreviation of the column in shapefile that five a region its abbreviation.
        If 'construct', a combination of the first letters of region name is taken.
        Breaks for duplicates.
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
            abbrevs = _construct_abbrevs(geodataframe, names)
        else:
            abbrevs = _maybe_get_column(geodataframe, abbrevs)
    else:
        raise ValueError('Please provide a string take can be taken from '
                         'geodataframe.columns for `abbrevs`, '
                         'found {}'.format(abbrevs))
    if names is not None:
        names = _maybe_get_column(geodataframe, names)
    else:
        raise ValueError('Please provide a string take can be taken from '
                         'geodataframe.columns for `names`, found {}'.format(names))

    outlines = _maybe_get_column(geodataframe, 'geometry')

    # check duplicates
    for to_check in [abbrevs, names]:
        assert _check_duplicates(to_check)

    return Regions(outlines,
                   numbers=numbers, names=names,
                   abbrevs=abbrevs, name=name, source=source)
