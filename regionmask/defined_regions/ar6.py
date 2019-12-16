import os

import geopandas as gp
import pkg_resources
from shapely import geometry

from ..core.regions import Regions

DATA_PATH = pkg_resources.resource_filename("regionmask", "defined_regions")


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

df = gp.read_file(filename)


ar6_separate_pacific = Regions(
    df.geometry, names=df.V2, abbrevs=df.V3, name="IPCC AR6 WGI Reference Regions"
)


df = _combine_to_multipolygon(df, "SPO", "SPO*")
df = _combine_to_multipolygon(df, "EPO", "EPO*")
df = _combine_to_multipolygon(df, "NPO", "NPO*")


ar6 = Regions(
    df.geometry,
    names=df.V2,
    abbrevs=df.V3,
    name="IPCC AR6 WGI Reference Regions (combined Pacific regions)",
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
]


ar6_land = ar6[land]
ar6_land.name = "IPCC AR6 WGI Reference Regions (combined Pacific regions, land only)"

ocean = [
    "WAN",
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

ar6_ocean = ar6[ocean]
ar6_ocean.name = "IPCC AR6 WGI Reference Regions (combined Pacific regions, ocean only)"

# df.drop(49)

# df.loc[48].geometry = geometry.MultiPolygon([df.loc[48].geometry, df.loc[49].geometry])
