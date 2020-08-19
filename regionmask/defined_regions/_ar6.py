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

"""


class ar6_cls(object):
    """docstring for ar6"""

    def __init__(self):
        super(ar6_cls, self).__init__()

        self._df = None

        self._all = None
        self._land = None
        self._ocean = None

        self._name = "AR6 reference regions"
        self._source = "Iturbide et al., 2020 (Earth Syst. Sci. Data)"

    @property
    def df(self):

        if self._df is None:
            self._df = read_remote_shapefile("IPCC-WGI-reference-regions-v4.zip")

        return self._df

    @property
    def all(self):
        if self._all is None:
            self._all = from_geopandas(
                self.df,
                names="Name",
                abbrevs="Acronym",
                name=self._name,
                source=self._source,
            )

        return self._all

    @property
    def land(self):
        if self._land is None:

            land = self.df.Type.str.contains("Land")

            self._land = from_geopandas(
                self.df.loc[land],
                names="Name",
                abbrevs="Acronym",
                name=self._name + " (land only)",
                source=self._source,
            )

        return self._land

    @property
    def ocean(self):
        if self._ocean is None:

            ocean = self.df.Type.str.contains("Ocean")

            self._ocean = from_geopandas(
                self.df.loc[ocean],
                names="Name",
                abbrevs="Acronym",
                name=self._name + " (ocean only)",
                source=self._source,
            )

        return self._ocean

    def __repr__(self):  # pragma: no cover
        return REPR


ar6 = ar6_cls()
