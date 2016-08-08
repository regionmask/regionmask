

# F. Giorgi R. Francisco

import numpy as np

outline = dict()



outline[1] =  (( 110, -45), ( 155, -45), ( 155, -11), ( 110, -11))
outline[2] =  (( -82, -20), ( -34, -20), ( -34,  12), ( -82,  12))
outline[3] =  (( -76, -56), ( -40, -56), ( -40, -20), ( -76, -20))
outline[4] =  ((-116,  10), ( -83,  10), ( -83,  30), (-116,  30))
outline[5] =  ((-130,  30), (-103,  30), (-103,  60), (-130,  60))
outline[6] =  ((-103,  30), ( -85,  30), ( -85,  50), (-103,  50))
outline[7] =  (( -85,  25), ( -60,  25), ( -60,  50), ( -85,  50))
outline[8] =  ((-170,  60), (-103,  60), (-103,  72), (-170,  72))
outline[9] =  ((-103,  50), ( -10,  50), ( -10,  85), (-103,  85))
outline[10] = (( -10,  30), (  40,  30), (  40,  48), ( -10,  48))
outline[11] = (( -10,  48), (  40,  48), (  40,  75), ( -10,  75))
outline[12] = (( -20, -12), (  22, -12), (  22,  18), ( -20,  18))
outline[13] = ((  22, -12), (  52, -12), (  52,  18), (  22,  18))
outline[14] = (( -10, -35), (  52, -35), (  52, -12), ( -10, -12))
outline[15] = (( -20,  18), (  65,  18), (  65,  30), ( -20,  30))
outline[16] = ((  95, -11), ( 155, -11), ( 155,  20), (  95,  20))
outline[17] = (( 100,  20), ( 145,  20), ( 145,  50), ( 100,  50))
outline[18] = ((  65,   5), ( 100,   5), ( 100,  30), (  65,  30))
outline[19] = ((  40,  30), (  75,  30), (  75,  50), (  40,  50))
outline[20] = ((  75,  30), ( 100,  30), ( 100,  50), (  75,  50))
outline[21] = ((  40,  50), ( 180,  50), ( 180,  70), (  40,  70))


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

name = dict()

name[1] = "Australia"
name[2] = "Amazon Basin"
name[3] = "Southern South America"
name[4] = "Central America"
name[5] = "Western North America"
name[6] = "Central North America"
name[7] = "Eastern North America"
name[8] = "Alaska"
name[9] = "Greenland"
name[10] = "Mediterranean Basin"
name[11] = "Northern Europe"
name[12] = "Western Africa"
name[13] = "Eastern Africa"
name[14] = "Southern Africa"
name[15] = "Sahara"
name[16] = "Southeast Asia"
name[17] = "East Asia"
name[18] = "South Asia"
name[19] = "Central Asia"
name[20] = "Tibet"
name[21] = "North Asia"

# =============================================================================


from ..core.regions import Regions_cls

numbers = range(1, 22)

source = ('Giorgi and Franciso, 2000 '
	      '(http://onlinelibrary.wiley.com/doi/10.1029/1999GL011016)')

giorgi = Regions_cls('Giorgi', numbers, name, abbrevs, outline, 
	                 source=source)
