from functools import cache

from ..core._geopandas import from_geopandas
from ._ressources import read_remote_shapefile

REPR = """
AR6 reference regions - Iturbide et al., 2020

Attributes
----------
all : Regions
    All regions (land + ocean).
land : Regions
    Land regions only
ocean : Regions
    Ocean regions only

Notes
-----
See https://doi.org/10.5194/essd-12-2959-2020

"""


class AR6:
    """docstring for ar6"""

    _name = "AR6 reference regions"
    _source = "Iturbide et al., 2020 (ESSD)"

    @property
    @cache
    def df(self):

        return read_remote_shapefile("IPCC-WGI-reference-regions-v4.zip")

    @property
    @cache
    def all(self):

        return from_geopandas(
            self.df,
            names="Name",
            abbrevs="Acronym",
            name=self._name,
            source=self._source,
            overlap=False,
        )

    @property
    @cache
    def land(self):

        land = self.df.Type.str.contains("Land")

        return from_geopandas(
            self.df.loc[land],
            names="Name",
            abbrevs="Acronym",
            name=self._name + " (land only)",
            source=self._source,
            overlap=False,
        )

    @property
    @cache
    def ocean(self):

        ocean = self.df.Type.str.contains("Ocean")

        return from_geopandas(
            self.df.loc[ocean],
            names="Name",
            abbrevs="Acronym",
            name=self._name + " (ocean only)",
            source=self._source,
            overlap=False,
        )

    def __repr__(self):  # pragma: no cover
        return REPR


ar6 = AR6()
