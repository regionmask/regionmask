import pytest
import regionmask
import geopandas


@pytest.fixture
def MEOW_geodataframe():
    return geopandas.read_file('http://maps.tnc.org/files/shp/MEOW-TNC.zip')


source = 'http://maps.tnc.org/gis_data.html'
name = 'MEOW'


def test_from_geopandas_is_region(MEOW_geodataframe):
    region = regionmask.from_geopandas(MEOW_geodataframe, numbers=None,
                                       names='ECOREGION',
                                       abbrevs='construct',
                                       name=name,
                                       source=source)
    assert isinstance(region, regionmask.core.regions.Regions)


@pytest.mark.xfail
def test_from_geopandas_fail_no_abbrevs(MEOW_geodataframe):
    region = regionmask.from_geopandas(MEOW_geodataframe, numbers=None,
                                       names='ECOREGION',
                                       abbrevs=None,
                                       name=name,
                                       source=source)


@pytest.mark.xfail
def test_from_geopandas_fail_no_names(MEOW_geodataframe):
    region = regionmask.from_geopandas(MEOW_geodataframe, numbers=None,
                                       names=None,
                                       abbrevs='construct',
                                       name=name,
                                       source=source)
