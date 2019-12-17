import os

import geopandas as gp
import pkg_resources
from shapely import geometry

from ..core.regions import Regions

DATA_PATH = pkg_resources.resource_filename("regionmask", "defined_regions")

REPR = """
Regions defined for the sixt IPCC assessment report

Attributes
----------
all : Regions
    All regions (land + ocean), regions split along the date line
    are combined (see below).
land : Regions
    Land regions only, regions split along the date line
    are combined (see below).
ocean : Regions
    Ocean regions only, regions split along the date line
    are combined (see below).
separate_pacific : Regions
    Original definitions of the regions, no combination of the pacific
    regions.

Combined Regions
----------------
SPO and SPO*; EPO and EPO*; NPO and NPO*

Note
----
The region numbers for all, land, and ocean are consistent. The
region numbers for all and separate_pacific are not.

"""


def _combine_to_multipolygon(df, *names):

    column = "V3"

    all_poly = [df[df[column] == name].geometry.values[0] for name in names]

    combined_poly = geometry.MultiPolygon(all_poly)

    df.loc[df[column] == names[0], "geometry"] = gp.GeoSeries(combined_poly).values

    for name in names[1:]:
        df = df.loc[df[column] != name]

    return df


filename = os.path.join(
    DATA_PATH, "data", "AR6_WGI_referenceRegions", "AR6_WGI_referenceRegions.shp"
)


land = [
    "GIC",
    "NEC",
    "CNA",
    "ENA",
    "NWN",
    "WNA",
    "NCA",
    "SCA",
    "CAR",
    "NWS",
    "SAM",
    "SSA",
    "SWS",
    "SES",
    "NSA",
    "NES",
    "NEU",
    "CEU",
    "EEU",
    "MED",
    "WAF",
    "SAH",
    "NEAF",
    "CEAF",
    "SWAF",
    "SEAF",
    "CAF",
    "RAR",
    "RFE",
    "ESB",
    "WSB",
    "WCA",
    "TIB",
    "EAS",
    "ARP",
    "SAS",
    "SEA",
    "NAU",
    "CAU",
    "SAU",
    "NZ",
    "EAN",
    "WAN",
]


ocean = [
    "ARO",
    "SPO",
    "EPO",
    "NPO",
    "SAO",
    "EAO",
    "NAO",
    "EIO",
    "SIO",
    "ARS",
    "BOB",
    "SOO",
]


class ar6_cls(object):
    """docstring for ar6"""

    def __init__(self):
        super(ar6_cls, self).__init__()

        self.__df = None
        self.__df_combined = None

        self._all = None
        self._land = None
        self._ocean = None
        self._separate_pacific = None

    @property
    def _df(self):

        if self.__df is None:
            self.__df = gp.read_file(filename)

        return self.__df

    @property
    def _df_combined(self):

        if self.__df_combined is None:
            _df_combined = self._df.copy()

            _df_combined = _combine_to_multipolygon(_df_combined, "SPO", "SPO*")
            _df_combined = _combine_to_multipolygon(_df_combined, "EPO", "EPO*")
            _df_combined = _combine_to_multipolygon(_df_combined, "NPO", "NPO*")

            self.__df_combined = _df_combined

        return self.__df_combined

    @property
    def all(self):
        if self._all is None:
            r = Regions(
                self._df_combined.geometry,
                names=self._df_combined.V2,
                abbrevs=self._df_combined.V3,
                name="IPCC AR6 WGI Reference Regions (combined Pacific regions)",
            )
            self._all = r
        return self._all

    @property
    def land(self):
        if self._land is None:
            r = self.all[land]
            r.name = (
                "IPCC AR6 WGI Reference Regions (combined Pacific regions, land only)"
            )
            self._land = r
        return self._land

    @property
    def ocean(self):
        if self._ocean is None:
            r = self.all[ocean]
            r.name = (
                "IPCC AR6 WGI Reference Regions (combined Pacific regions, ocean only)"
            )
            self._ocean = r
        return self._ocean

    @property
    def separate_pacific(self):
        if self._separate_pacific is None:
            r = Regions(
                self._df.geometry,
                names=self._df.V2,
                abbrevs=self._df.V3,
                name="IPCC AR6 WGI Reference Regions",
            )
            self._separate_pacific = r

        return self._separate_pacific

    def __repr__(self):
        return REPR


ar6 = ar6_cls()
