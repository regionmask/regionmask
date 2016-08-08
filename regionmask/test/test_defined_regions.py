from regionmask import defined_regions, Regions_cls


def _defined_region(regions, n_regions):

    assert isinstance(regions, Regions_cls)
    assert len(regions) == n_regions


def test_giorgi():
    regions = defined_regions.giorgi
    _defined_region(regions, 21)
    


def test_srex():
    regions = defined_regions.srex
    _defined_region(regions, 26)


def test_countries_110():
    regions = defined_regions.natural_earth.countries_110
    _defined_region(regions, 177)

def test_countries_50():
    regions = defined_regions.natural_earth.countries_50
    _defined_region(regions, 241)

def test_us_states_50():
    regions = defined_regions.natural_earth.us_states_50
    _defined_region(regions, 51)

def test_us_states_10():
    regions = defined_regions.natural_earth.us_states_10
    _defined_region(regions, 51)









