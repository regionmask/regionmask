# F. Giorgi R. Francisco
# Uncertainties in regional climate change prediction: a regional analysis
# of ensemble simulations with the HADCM2 coupled AOGCM

outlines = dict()
outlines[1] = ((110, -45), (155, -45), (155, -11), (110, -11))
outlines[2] = ((-82, -20), (-34, -20), (-34, 12), (-82, 12))
outlines[3] = ((-76, -56), (-40, -56), (-40, -20), (-76, -20))
outlines[4] = ((-116, 10), (-83, 10), (-83, 25), (-85, 25), (-85, 30), (-116, 30))
outlines[5] = ((-130, 30), (-103, 30), (-103, 60), (-130, 60))
outlines[6] = ((-103, 30), (-85, 30), (-85, 50), (-103, 50))
outlines[7] = ((-85, 25), (-60, 25), (-60, 50), (-85, 50))
outlines[8] = ((-170, 60), (-103, 60), (-103, 72), (-170, 72))
outlines[9] = ((-103, 50), (-10, 50), (-10, 85), (-103, 85))
outlines[10] = ((-10, 30), (40, 30), (40, 48), (-10, 48))
outlines[11] = ((-10, 48), (40, 48), (40, 75), (-10, 75))
outlines[12] = ((-20, -12), (22, -12), (22, 18), (-20, 18))
outlines[13] = ((22, -12), (52, -12), (52, 18), (22, 18))
outlines[14] = ((-10, -35), (52, -35), (52, -12), (-10, -12))
outlines[15] = ((-20, 18), (65, 18), (65, 30), (-20, 30))
outlines[16] = ((95, -11), (155, -11), (155, 20), (100, 20), (100, 5), (95, 5))
outlines[17] = ((100, 20), (145, 20), (145, 50), (100, 50))
outlines[18] = ((65, 5), (100, 5), (100, 30), (65, 30))
outlines[19] = ((40, 30), (75, 30), (75, 50), (40, 50))
outlines[20] = ((75, 30), (100, 30), (100, 50), (75, 50))
outlines[21] = ((40, 50), (180, 50), (180, 70), (40, 70))

abbrevs = dict()
abbrevs[1] = "AUS"
abbrevs[2] = "AMZ"
abbrevs[3] = "SSA"
abbrevs[4] = "CAM"
abbrevs[5] = "WNA"
abbrevs[6] = "CNA"
abbrevs[7] = "ENA"
abbrevs[8] = "ALA"
abbrevs[9] = "GRL"
abbrevs[10] = "MED"
abbrevs[11] = "NEU"
abbrevs[12] = "WAF"
abbrevs[13] = "EAF"
abbrevs[14] = "SAF"
abbrevs[15] = "SAH"
abbrevs[16] = "SEA"
abbrevs[17] = "EAS"
abbrevs[18] = "SAS"
abbrevs[19] = "CAS"
abbrevs[20] = "TIB"
abbrevs[21] = "NAS"

names = dict()
names[1] = "Australia"
names[2] = "Amazon Basin"
names[3] = "Southern South America"
names[4] = "Central America"
names[5] = "Western North America"
names[6] = "Central North America"
names[7] = "Eastern North America"
names[8] = "Alaska"
names[9] = "Greenland"
names[10] = "Mediterranean Basin"
names[11] = "Northern Europe"
names[12] = "Western Africa"
names[13] = "Eastern Africa"
names[14] = "Southern Africa"
names[15] = "Sahara"
names[16] = "Southeast Asia"
names[17] = "East Asia"
names[18] = "South Asia"
names[19] = "Central Asia"
names[20] = "Tibet"
names[21] = "North Asia"

# =============================================================================

from ..core.regions import Regions

numbers = range(1, 22)

source = (
    "Giorgi and Franciso, 2000 " "(http://link.springer.com/article/10.1007/PL00013733)"
)

giorgi = Regions(
    outlines,
    numbers=numbers,
    names=names,
    abbrevs=abbrevs,
    name="Giorgi",
    source=source,
)
