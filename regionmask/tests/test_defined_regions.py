import os
from operator import attrgetter

import numpy as np
import pytest

from regionmask import Regions, defined_regions
from regionmask.defined_regions._natural_earth import _maybe_get_column

from . import has_cartopy, requires_cartopy
from .utils import (
    REGIONS_ALL,
    REGIONS_DEPRECATED,
    REGIONS_REQUIRING_CARTOPY,
    download_naturalearth_region_or_skip,
)


def _test_region(defined_region):

    region = attrgetter(defined_region.region_name)(defined_regions)

    assert isinstance(region, Regions)
    assert len(region) == defined_region.n_regions

    assert region.overlap is defined_region.overlap

    # currently all regions are -180..180
    assert region.lon_180

    if defined_region.bounds is not None:
        np.testing.assert_allclose(defined_region.bounds, region.bounds_global)


@pytest.mark.parametrize("defined_region", REGIONS_ALL, ids=str)
def test_defined_region(defined_region):

    _test_region(defined_region)


@pytest.mark.parametrize("defined_region", REGIONS_DEPRECATED, ids=str)
def test_defined_region_deprecated(defined_region):

    match = "The ``_ar6_pre_revisions`` regions have been deprecated in v0.9.0"
    with pytest.warns(FutureWarning, match=match):
        _test_region(defined_region)


@requires_cartopy
@pytest.mark.filterwarnings("ignore:Downloading")
@pytest.mark.parametrize("defined_region", REGIONS_REQUIRING_CARTOPY, ids=str)
def test_defined_regions_natural_earth(monkeypatch, defined_region):
    # TODO: remove this test once defined_regions.natural_earth is removed

    import cartopy

    from regionmask.defined_regions import _natural_earth

    match = "``regionmask.defined_regions.natural_earth`` is deprecated"

    # get regionmask.defined_regions._natural_earth._land_10 dataclass
    region = defined_region.region_name.split(".")[1]
    natural_earth_feature = attrgetter(f"_{region}")(_natural_earth)

    # get the filename of cartopy-downloaded shapefiles
    resolution = natural_earth_feature.resolution
    category = natural_earth_feature.category
    name = natural_earth_feature.name

    _cartopy_data_dir = cartopy.config["data_dir"]

    # check if cartopy has already downloaded the file
    cartopy_file = os.path.join(
        _cartopy_data_dir,
        "shapefiles",
        "natural_earth",
        f"{category}",
        f"ne_{resolution}_{name}.shp",
    )

    # only raise an error if the file is not downloaded
    if not os.path.isfile(cartopy_file):
        with pytest.raises(ValueError, match=match):
            attrgetter(defined_region.region_name)(defined_regions)

    # download data using cartopy
    download_naturalearth_region_or_skip(monkeypatch, natural_earth_feature)

    # get region and ensure deprcation warning is raised
    with pytest.warns(FutureWarning, match=match):
        _test_region(defined_region)


def test_fix_ocean_basins_50():

    region = defined_regions.natural_earth_v4_1_0.ocean_basins_50
    assert "Mediterranean Sea Eastern Basin" in region.names
    assert "Ross Sea Eastern Basin" in region.names

    region = defined_regions.natural_earth_v5_0_0.ocean_basins_50
    assert "Mediterranean Sea" in region.names
    assert "Ross Sea" in region.names


@requires_cartopy
def test_natural_earth_loaded_as_utf8():
    # GH 95

    region = defined_regions.natural_earth_v5_0_0.ocean_basins_50

    assert "Río de la Plata" in region.names


def test_maybe_get_column():
    class lowercase:
        @property
        def name(self):
            return 1

    class uppercase:
        @property
        def NAME(self):
            return 2

    assert _maybe_get_column(lowercase(), "name") == 1
    assert _maybe_get_column(uppercase(), "name") == 2
    assert _maybe_get_column(uppercase(), "NAME") == 2

    with pytest.raises(KeyError, match="not on the geopandas dataframe"):
        _maybe_get_column(lowercase, "not_a_column")


@pytest.mark.skipif(has_cartopy, reason="should run if cartopy is _not_ installed")
def test_natural_earth_raises_without_cartopy():

    with pytest.raises(ImportError, match="requires cartopy"):
        defined_regions.natural_earth.countries_110
