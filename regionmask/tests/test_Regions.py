import geopandas
import geopandas.testing
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import MultiPolygon, Polygon

from regionmask import Regions, _OneRegion

# =============================================================================
# set up the testing regions

name = "Example"

numbers1 = [0, 1]
names = ["Unit Square1", "Unit Square2"]
abbrevs = ["uSq1", "uSq2"]

outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0))
outl2 = ((0, 1), (0, 2), (1, 2.0), (1, 1))

outlines = [outl1, outl2]

test_regions1 = Regions(outlines, numbers1, names, abbrevs, name=name)

numbers2 = [1, 2]
names_dict = {1: "Unit Square1", 2: "Unit Square2"}
abbrevs_dict = {1: "uSq1", 2: "uSq2"}
poly1 = Polygon(outl1)
poly2 = Polygon(outl2)
poly = {1: poly1, 2: poly2}
multipoly = MultiPolygon([poly1, poly2])

test_regions2 = Regions(poly, numbers2, names_dict, abbrevs_dict, name=name)

# numbers as array
numbers3 = [2, 3]
test_regions3 = Regions(outlines, np.array(numbers3), names, abbrevs, name=name)

# float numbers
numbers4 = [0.0, 1.0]
test_regions4 = Regions(outlines, np.array(numbers4), names, abbrevs, name=name)

# =============================================================================

all_test_regions = (test_regions1, test_regions2, test_regions3, test_regions4)

all_numbers = (numbers1, numbers2, numbers3, numbers4)

all_first_numbers = tuple(num[0] for num in all_numbers)

# =============================================================================


def test_regions_single_region() -> None:

    for o in [np.array(outl1), poly1, multipoly]:
        with pytest.raises(ValueError, match="Cannot pass a single"):
            Regions(o)


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_len(test_regions) -> None:
    assert len(test_regions) == 2


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_name(test_regions) -> None:
    assert test_regions.name == name


@pytest.mark.parametrize("test_regions, numbers", zip(all_test_regions, all_numbers))
def test_numbers(test_regions, numbers) -> None:
    assert np.allclose(test_regions.numbers, numbers)


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_names(test_regions) -> None:
    assert test_regions.names == ["Unit Square1", "Unit Square2"]


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_abbrevs(test_regions) -> None:
    assert test_regions.abbrevs == ["uSq1", "uSq2"]


def test_region_ids_deprecated() -> None:

    with pytest.warns(
        FutureWarning, match="`Regions.region_ids` has been made private"
    ):
        test_regions1.region_ids


def test_region_ids() -> None:

    actual = test_regions1._region_ids
    expected = {0: 0, 1: 1, "uSq1": 0, "uSq2": 1, "Unit Square1": 0, "Unit Square2": 1}

    assert actual == expected


def test_coords_deprecated() -> None:

    with pytest.warns(FutureWarning, match="`Regions.coords` has been deprecated"):
        test_regions1.coords


@pytest.mark.filterwarnings("ignore:`Regions.coords` has been deprecated")
def test_coords() -> None:
    # passing numpy coords does not automatically close the coords
    assert np.allclose(test_regions1.coords, [outl1, outl2])

    # the polygon automatically closes the outline
    out1 = np.vstack([outl1, outl1[0]])
    out2 = np.vstack([outl2, outl2[0]])

    assert np.allclose(test_regions2.coords, [out1, out2])


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_bounds(test_regions) -> None:

    expected = [(0, 0, 1, 1), (0, 1, 1, 2)]

    assert np.allclose(test_regions.bounds, expected)


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_bounds_global(test_regions) -> None:

    expected = [0, 0, 1, 2]

    assert np.allclose(test_regions.bounds_global, expected)


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_polygon(test_regions) -> None:
    assert isinstance(test_regions.polygons, list)

    assert len(test_regions.polygons) == 2

    assert test_regions.polygons[0].equals(poly1)
    assert test_regions.polygons[1].equals(poly2)


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_centroid(test_regions) -> None:
    assert np.allclose(test_regions.centroids, [[0.5, 0.5], [0.5, 1.5]])


def test_centroid_multipolygon() -> None:
    multipoly_equal = [MultiPolygon([poly1, poly2])]
    test_regions_multipoly_equal = Regions(multipoly_equal)

    # two equally sized polygons: uses the centroid of the first one
    assert np.allclose(test_regions_multipoly_equal.centroids, [[0.5, 0.5]])

    # two un-equally sized polygons: uses the centroid of the larger one
    outl2_unequal = ((0, 1), (0, 2), (2, 2.0), (2, 1))
    poly2_unequal = Polygon(outl2_unequal)
    multipoly_unequal = [MultiPolygon([poly1, poly2_unequal])]
    test_regions_multipoly_unequal = Regions(multipoly_unequal)

    assert np.allclose(test_regions_multipoly_unequal.centroids, [[1.0, 1.5]])


@pytest.mark.parametrize(
    "test_regions, number", zip(all_test_regions, all_first_numbers)
)
def test_map_keys_one(test_regions, number) -> None:
    pytest.raises(KeyError, test_regions1.__getitem__, "")

    expected = number

    assert test_regions.map_keys(number) == expected
    assert test_regions.map_keys("uSq1") == expected
    assert test_regions.map_keys("Unit Square1") == expected


def test_map_keys_np_integer() -> None:
    key = np.array([2, 2])[0]
    assert test_regions3.map_keys(key) == 2


@pytest.mark.parametrize("test_regions, numbers", zip(all_test_regions, all_numbers))
def test_map_keys_several(test_regions, numbers) -> None:

    assert test_regions.map_keys(numbers) == numbers
    assert test_regions.map_keys(("uSq1", "uSq2")) == numbers
    assert test_regions.map_keys(("Unit Square1", "Unit Square2")) == numbers


def test_map_keys_mixed() -> None:
    assert test_regions1.map_keys([0, "uSq2"]) == [0, 1]


def test_map_keys_unique() -> None:
    assert test_regions1.map_keys([0, 0, 0]) == [0]
    assert test_regions1.map_keys([0, 0, 0, 1]) == [0, 1]


@pytest.mark.parametrize(
    "test_regions, number", zip(all_test_regions, all_first_numbers)
)
def test_subset_to_OneRegion(test_regions, number) -> None:
    s1 = test_regions[number]
    assert isinstance(s1, _OneRegion)
    assert s1.number == number
    assert s1.abbrev == "uSq1"

    s1 = test_regions["uSq1"]
    assert isinstance(s1, _OneRegion)
    assert s1.number == number
    assert s1.abbrev == "uSq1"

    s1 = test_regions["Unit Square1"]
    assert isinstance(s1, _OneRegion)
    assert s1.number == number
    assert s1.abbrev == "uSq1"


@pytest.mark.parametrize("test_region", all_test_regions)
def test_Regions_iter(test_region) -> None:

    for result, expected in zip(test_region, test_region.regions.values()):
        assert result is expected


@pytest.mark.parametrize(
    "test_regions, number", zip(all_test_regions, all_first_numbers)
)
def test_subset_to_Regions(test_regions, number) -> None:
    s1 = test_regions[[number]]
    assert isinstance(s1, Regions)
    assert s1.numbers == [number]
    assert s1.abbrevs == ["uSq1"]


@pytest.mark.parametrize("numbers", [None, [1, 2]])
@pytest.mark.parametrize("names", [None, "names", names])
@pytest.mark.parametrize("abbrevs", [None, "abbrevs", abbrevs])
@pytest.mark.parametrize("name", [None, "name"])
def test_optional_arguments(numbers, names, abbrevs, name) -> None:

    if name is None:
        result = Regions(outlines, numbers, names, abbrevs)
    else:
        result = Regions(outlines, numbers, names, abbrevs, name)

    if numbers is None:
        numbers = [0, 1]

    if names is None:
        names = _create_expected_str_list(numbers, "Region")
    elif isinstance(names, str):
        names = _create_expected_str_list(numbers, names)

    if abbrevs is None:
        abbrevs = _create_expected_str_list(numbers, "r")
    elif isinstance(abbrevs, str):
        abbrevs = _create_expected_str_list(numbers, abbrevs)

    expected_centroids = [[0.5, 0.5], [0.5, 1.5]]

    if name is None:
        name = "unnamed"

    assert result.numbers == numbers

    assert result.names == names

    assert result.abbrevs == abbrevs

    assert np.allclose(result.centroids, expected_centroids)

    assert result.name == name


def _create_expected_str_list(numbers, string):

    return [string + str(number) for number in numbers]


def test_lon_extent() -> None:

    assert test_regions1.lon_180
    assert not test_regions1.lon_360

    outl_ = ((0, 0), (0, 1), (360, 1.0), (360, 0))

    test_regions_ = Regions([outl_])

    assert not test_regions_.lon_180
    assert test_regions_.lon_360

    outl_ = ((-1, 0), (-1, 1), (360, 1.0), (360, 0))
    test_regions_ = Regions([outl_])

    with pytest.raises(ValueError, match="lon has data that is larger than 180 "):
        test_regions_.lon_180

    with pytest.raises(ValueError, match="lon has data that is larger than 180 "):
        test_regions_.lon_360


@pytest.mark.parametrize("numbers", [["a", "b"], ["a", 2]])
def test_error_on_non_numeric(numbers) -> None:

    with pytest.raises(ValueError, match="'numbers' must be numeric"):
        Regions(poly, numbers)


def test_regions_sorted() -> None:

    numbers = [3, 1, 2]
    outl = [poly1, poly1, poly2]
    names = ["R3", "R1", "R2"]
    abbrevs = ["r3", "r1", "r2"]

    r = Regions(outl, numbers, names, abbrevs)

    assert r.numbers == [1, 2, 3]
    assert r.names == sorted(names)
    assert r.abbrevs == sorted(abbrevs)

    assert r.polygons[0].equals(poly1)
    assert r.polygons[1].equals(poly2)
    assert r.polygons[2].equals(poly1)


@pytest.mark.parametrize("numbers", [[1, 3, 4, 9, 10], [10, 9, 4, 3, 1]])
def test_getitem_sorted(numbers) -> None:

    r = Regions([outl1] * 20)[numbers]

    numbers_expected = sorted(numbers)
    abbrevs_expected = [f"r{n}" for n in numbers_expected]
    names_expected = [f"Region{n}" for n in numbers_expected]

    assert r.numbers == numbers_expected
    assert r.abbrevs == abbrevs_expected
    assert r.names == names_expected


@pytest.mark.parametrize("overlap", [None, True, False])
def test_overlap(overlap) -> None:

    r = Regions([outl1], overlap=overlap)

    assert r.overlap is overlap


@pytest.mark.parametrize("overlap", [None, True, False])
def test_overlap_getitem(overlap) -> None:

    r = Regions(3 * [outl1], overlap=overlap)
    r_select = r[[0, 2]]

    assert r_select.overlap is overlap


def _check_dataframe(df, r):

    assert (df.index == r.numbers).all()
    assert (df.abbrevs == r.abbrevs).all()
    assert (df.names == r.names).all()


def _check_attrs(df, r):

    assert df.attrs["name"] == r.name
    assert df.attrs["source"] == r.source
    assert df.attrs["overlap"] == r.overlap


def _check_polygons(df, r):

    from geopandas import GeoSeries

    geopandas.testing.assert_geoseries_equal(df, GeoSeries(r.polygons, index=r.numbers))


def test_to_geodataframe() -> None:

    r = test_regions1

    df = r.to_geodataframe()

    assert isinstance(df, geopandas.GeoDataFrame)
    _check_dataframe(df, r)
    _check_attrs(df, r)
    _check_polygons(df["geometry"], r)


def test_to_series() -> None:

    r = test_regions1

    df = r.to_geoseries()

    assert isinstance(df, geopandas.GeoSeries)
    _check_attrs(df, r)
    _check_polygons(df, r)


def test_to_dataframe() -> None:

    r = test_regions1

    df = r.to_dataframe()

    assert isinstance(df, pd.DataFrame)
    _check_dataframe(df, r)


def test_from_geodataframe() -> None:

    import geopandas

    data = dict(names=names, abbrevs=abbrevs)

    df = geopandas.GeoDataFrame(data=data, geometry=[poly1, poly2], index=numbers2)
    df.attrs = dict(source="source", name=name, overlap=True)

    r = Regions.from_geodataframe(df)

    _check_dataframe(df, r)
    _check_attrs(df, r)
    _check_polygons(df["geometry"], r)

    r = Regions.from_geodataframe(df, name="test")
    assert r.name == "test"

    r = Regions.from_geodataframe(df, source="test")
    assert r.source == "test"

    r = Regions.from_geodataframe(df, overlap=False)
    assert r.overlap is False

    df.attrs = {}

    r = Regions.from_geodataframe(df)
    assert r.name == "unnamed"
    assert r.source is None
    assert r.overlap is None


@pytest.mark.parametrize("overlap", [True, False, None])
def test_from_geodataframe_roundtrip(overlap) -> None:

    import geopandas

    data = dict(abbrevs=abbrevs, names=names)

    df = geopandas.GeoDataFrame(data=data, geometry=[poly1, poly2], index=numbers2)
    df.index.name = "numbers"
    df.attrs = dict(source="source", name=name, overlap=overlap)

    r = Regions.from_geodataframe(df)

    df_roundtrip = r.to_geodataframe()

    geopandas.testing.assert_geodataframe_equal(df, df_roundtrip)
