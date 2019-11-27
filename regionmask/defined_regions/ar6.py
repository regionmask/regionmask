import pkg_resources
import os
from shapely import geometry

import geopandas as gp

from ..core.regions import Regions

DATA_PATH = pkg_resources.resource_filename('regionmask', 'defined_regions')

def _combine_to_multipolygon(df, *names):

    column = "V3"

    all_poly = [df[df[column] == name].geometry.values[0] for name in names]

    combined_poly = geometry.MultiPolygon(all_poly)

    df.loc[df[column] == names[0], "geometry"] = [combined_poly]

    for name in names[1:]:
        df = df.loc[df[column] != name]

    return df


filename = os.path.join(DATA_PATH, "data", "AR6_WGI_referenceRegions", "AR6_WGI_referenceRegions.shp")

df = gp.read_file(filename)

df = _combine_to_multipolygon(df, "SPO", "SPO*")
df = _combine_to_multipolygon(df, "EPO", "EPO*")
df = _combine_to_multipolygon(df, "NPO", "NPO*")

r = Regions(df.geometry, names=df.V2, abbrevs=df.V3, name="IPCC AR6 WGI Reference Regions")






# df.drop(49)

# df.loc[48].geometry = geometry.MultiPolygon([df.loc[48].geometry, df.loc[49].geometry])
