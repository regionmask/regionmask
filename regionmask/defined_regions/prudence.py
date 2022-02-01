# the outlines are given at https://link.springer.com/article/10.1007/s10584-006-9210-7

outlines = dict()

outlines[1] = ((-10.0, 59.0), (2.0, 59.0), (2.0, 50.0), (-10.0, 50.0))
outlines[2] = ((-10.0, 44.0), (3.0, 44.0), (3.0, 36.0), (-10.0, 36.0))
outlines[3] = ((-5.0, 50.0), (5.0, 50.0), (5.0, 44.0), (-5.0, 44.0))
outlines[4] = ((2.0, 55.0), (16.0, 55.0), (16.0, 48.0), (2.0, 48.0))
outlines[5] = ((5.0, 70.0), (30.0, 70.0), (30.0, 55.0), (5.0, 55.0))
outlines[6] = ((5.0, 48.0), (15.0, 48.0), (15.0, 44.0), (5.0, 44.0))
outlines[7] = ((3.0, 44.0), (25.0, 44.0), (25.0, 36.0), (3.0, 36.0))
outlines[8] = ((16.0, 55.0), (30.0, 55.0), (30.0, 44.0), (16.0, 44.0))


# -----------------------------------------------------------------------------

short_names = {
    1: "BI",
    2: "IP",
    3: "FR",
    4: "ME",
    5: "SC",
    6: "AL",
    7: "MD",
    8: "EA",
}

# -----------------------------------------------------------------------------

names = {
    1: "British Isles",
    2: "Iberian Peninsula",
    3: "France",
    4: "Mid-Europe",
    5: "Scandinavia",
    6: "Alps",
    7: "Mediterranean",
    8: "Eastern Europe",
}

# =============================================================================

from ..core.regions import Regions

numbers = range(1, 9)
source = (
    "Christensen and Christensen, 2007, Climatic Change 81:7-30"
    " (https://link.springer.com/article/10.1007/s10584-006-9210-7)"
)

prudence = Regions(
    outlines,
    numbers=numbers,
    names=names,
    abbrevs=short_names,
    name="PRUDENCE",
    source=source,
    overlap=True,
)
