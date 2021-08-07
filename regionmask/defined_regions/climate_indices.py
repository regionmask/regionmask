outlines = dict()
outlines[1] = ((-120, -5), (-170, -5), (-170, 5), (-120, 5))
outlines[2] = ((-150, -5), (-90, -5), (-90, 5), (-150, 5))
outlines[3] = ((210, -5), (160, -5), (160, 5), (210, 5))
outlines[4] = ((-90, -10), (-80, -10), (-80, 0), (-90, 0))
outlines[5] = ((180, 20), (-180, 20), (-180, 90), (180, 90))
outlines[6] = ((180, 20), (-180, 20), (-180, 90), (180, 90))
outlines[7] = ((180, -20), (-180, -20), (-180, -90), (180, -90))
outlines[8] = ((180, 20), (-180, 20), (-180, 90), (180, 90))
outlines[9] = ((180, -15), (-180, -15), (-180, 15), (180, 15))

abbrevs = dict()
abbrevs[1] = "N34"
abbrevs[2] = "N03"
abbrevs[3] = "N04"
abbrevs[4] = "N12"
abbrevs[5] = "NAO"
abbrevs[6] = "AO"
abbrevs[7] = "AAO"
abbrevs[8] = "PNA"
abbrevs[9] = "MJO"

names = dict()
names[1] = "Niño 3.4"
names[2] = "Niño 3"
names[3] = "Niño 4"
names[4] = "Niño 1.2"
names[5] = "North Atlantic Oscillation"
names[6] = "Arctic Oscillation"
names[7] = "Antarctic Oscillation"
names[8] = "Pacific / North American Pattern"
names[9] = "Madden Julian Oscillation"

# =============================================================================

from ..core.regions import Regions

numbers = sorted(outlines.keys())

source = (
    "Climate Prediction Center" "(https://www.cpc.ncep.noaa.gov/products/precip/CWlink/)"
)

climate_indices = Regions(
    outlines,
    numbers=numbers,
    names=names,
    abbrevs=abbrevs,
    name="Climate Indices",
    source=source,
)
