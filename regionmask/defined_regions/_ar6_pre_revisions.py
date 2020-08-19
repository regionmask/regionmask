import geopandas as gp
from shapely import geometry

from ..core._geopandas import _enumerate_duplicates, from_geopandas
from ._ressources import read_remote_shapefile

REPR = """
pre-revision version of 'AR6 reference regions - Iturbide et al., 2020'

These are the regions as originally submitted by Iturbide et al., 2020. During
the revisions regions were added and existing regions were adapted. The originally
submitted regions are provided here for completeness. Use the revised regions
i.e. ``regionmask.defined_regions.ar6``.

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
    Original definitions of the regions, no combination of the Pacific
    regions.

Combined Regions
----------------
SPO and SPO*; EPO and EPO*; NPO and NPO*

Note
----
The region numbers for ``all``, ``land``, and ``ocean`` are consistent. The
region numbers for ``separate_pacific`` and all others are not.

"""


def _combine_to_multipolygon(df, column, *names):

    all_poly = [df[df[column] == name].geometry.values[0] for name in names]

    combined_poly = geometry.MultiPolygon(all_poly)

    df.loc[df[column] == names[0], "geometry"] = gp.GeoSeries(combined_poly).values

    for name in names[1:]:
        df = df.loc[df[column] != name]

    return df


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


class ar6_pre_revisions_cls(object):
    """docstring for ar6"""

    def __init__(self):
        super(ar6_pre_revisions_cls, self).__init__()

        self.__df = None
        self.__df_combined = None

        self._all = None
        self._land = None
        self._ocean = None
        self._separate_pacific = None

        self._name = "pre-revision version of 'AR6 reference regions'"
        self._source = "Iturbide et al., 2020 (Earth Syst. Sci. Data)"

    @property
    def _df(self):

        if self.__df is None:
            self.__df = read_remote_shapefile("IPCC-WGI-reference-regions-v1.zip")

        return self.__df

    @property
    def _df_combined(self):

        if self.__df_combined is None:
            _df_combined = self._df.copy()

            _df_combined = _combine_to_multipolygon(_df_combined, "V3", "SPO", "SPO*")
            _df_combined = _combine_to_multipolygon(_df_combined, "V3", "EPO", "EPO*")
            _df_combined = _combine_to_multipolygon(_df_combined, "V3", "NPO", "NPO*")

            # make sure the index goes from 0 to n - 1
            _df_combined = _df_combined.reset_index().drop("index", axis=1)

            self.__df_combined = _df_combined

        return self.__df_combined

    @property
    def all(self):
        if self._all is None:

            self._all = from_geopandas(
                self._df_combined,
                names="V2",
                abbrevs="V3",
                name=self._name,
                source=self._source,
            )

        return self._all

    @property
    def land(self):
        if self._land is None:
            r = self.all[land]
            r.name = self._name + " (land only)"
            self._land = r
        return self._land

    @property
    def ocean(self):
        if self._ocean is None:
            r = self.all[ocean]
            r.name = self._name + " (ocean only)"
            self._ocean = r
        return self._ocean

    @property
    def separate_pacific(self):
        if self._separate_pacific is None:
            # need to fix the duplicates
            df = self._df.copy()
            df["V2"] = _enumerate_duplicates(df["V2"])

            self._separate_pacific = from_geopandas(
                df,
                names="V2",
                abbrevs="V3",
                name=self._name + "(separate Pacific regions)",
                source=self._source,
            )

        return self._separate_pacific

    def __repr__(self):  # pragma: no cover
        return REPR


_ar6_pre_revisions = ar6_pre_revisions_cls()
