# =============================================================================

# the outlines is given at https://link.springer.com/article/10.1007/s10584-006-9210-7

outlines = dict()

outlines[1] = ((-10., 59.), (2., 59.), (2., 50.), (-10., 50.))
outlines[2] = ((-10., 44.), (3., 44.), (3., 36.), (-10., 36.))
outlines[3] = ((-5., 50.), (5., 50.), (5., 44.), (-5., 44.))
outlines[4] = ((2., 55.), (16., 55.), (16., 48.), (2., 48.))
outlines[5] = ((5., 70.), (30., 70.), (30., 55.), (5., 55.))
outlines[6] = ((5., 48.), (15., 48.), (15., 44.), (5., 44.))
outlines[7] = ((3., 44.), (25., 44.), (25., 36.), (3., 36.))
outlines[8] = ((16., 55.), (30., 55.), (30., 44.), (16., 44.))


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
    "(https://link.springer.com/article/10.1007/s10584-006-9210-7)"
)

prudence = Regions(
    outlines,
    numbers=numbers,
    names=names,
    abbrevs=short_names,
    name="PRUDENCE",
    source=source,
)
