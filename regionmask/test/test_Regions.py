import numpy as np
import pytest
import six
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

test_regions2 = Regions(poly, numbers2, names_dict, abbrevs_dict, name=name)

# numbers as array
numbers3 = [2, 3]
test_regions3 = Regions(outlines, np.array(numbers3), names, abbrevs, name=name)


# =============================================================================

all_test_regions = (test_regions1, test_regions2, test_regions3)

all_numbers = (numbers1, numbers2, numbers3)

all_first_numbers = (0, 1, 2)

# =============================================================================


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_len(test_regions):
    assert len(test_regions) == 2


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_name(test_regions):
    assert test_regions.name == name


@pytest.mark.parametrize("test_regions, numbers", zip(all_test_regions, all_numbers))
def test_numbers(test_regions, numbers):
    assert np.allclose(test_regions.numbers, numbers)


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_names(test_regions):
    assert test_regions.names == ["Unit Square1", "Unit Square2"]


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_abbrevs(test_regions):
    assert test_regions.abbrevs == ["uSq1", "uSq2"]


def test_coords():
    # passing numpy coords does not automatically close the coords
    assert np.allclose(test_regions1.coords, [outl1, outl2])

    # the polygon automatically closes the outline
    out1 = np.vstack([outl1, outl1[0]])
    out2 = np.vstack([outl2, outl2[0]])

    assert np.allclose(test_regions2.coords, [out1, out2])


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_bounds(test_regions):

    expected = [(0, 0, 1, 1), (0, 1, 1, 2)]

    assert np.allclose(test_regions.bounds, expected)


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_bounds_global(test_regions):

    expected = [0, 0, 1, 2]

    assert np.allclose(test_regions.bounds_global, expected)


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_polygon(test_regions):
    assert isinstance(test_regions.polygons, list)

    assert len(test_regions.polygons) == 2

    assert test_regions.polygons[0].equals(poly1)
    assert test_regions.polygons[1].equals(poly2)


@pytest.mark.parametrize("test_regions", all_test_regions)
def test_centroid(test_regions):
    assert np.allclose(test_regions.centroids, [[0.5, 0.5], [0.5, 1.5]])


def test_centroid_multipolygon():
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
def test_map_keys_one(test_regions, number):
    pytest.raises(KeyError, test_regions1.__getitem__, "")

    expected = number

    assert test_regions.map_keys(number) == expected
    assert test_regions.map_keys("uSq1") == expected
    assert test_regions.map_keys("Unit Square1") == expected


def test_map_keys_np_integer():
    key = np.array([2, 2])[0]
    assert test_regions3.map_keys(key) == 2


@pytest.mark.parametrize("test_regions, numbers", zip(all_test_regions, all_numbers))
def test_map_keys_several(test_regions, numbers):

    assert test_regions.map_keys(numbers) == numbers
    assert test_regions.map_keys(("uSq1", "uSq2")) == numbers
    assert test_regions.map_keys(("Unit Square1", "Unit Square2")) == numbers


def test_map_keys_mixed():
    assert test_regions1.map_keys([0, "uSq2"]) == [0, 1]


def test_map_keys_unique():
    assert test_regions1.map_keys([0, 0, 0]) == [0]
    assert test_regions1.map_keys([0, 0, 0, 1]) == [0, 1]


@pytest.mark.parametrize(
    "test_regions, number", zip(all_test_regions, all_first_numbers)
)
def test_subset_to_Region(test_regions, number):
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


@pytest.mark.parametrize(
    "test_regions, number", zip(all_test_regions, all_first_numbers)
)
def test_subset_to_Regions(test_regions, number):
    s1 = test_regions[[number]]
    assert isinstance(s1, Regions)
    assert s1.numbers == [number]
    assert s1.abbrevs == ["uSq1"]


@pytest.mark.parametrize("numbers", [None, [1, 2]])
@pytest.mark.parametrize("names", [None, "names", names])
@pytest.mark.parametrize("abbrevs", [None, "abbrevs", abbrevs])
@pytest.mark.parametrize("name", [None, "name"])
def test_optional_arguments(numbers, names, abbrevs, name):

    if name is None:
        result = Regions(outlines, numbers, names, abbrevs)
    else:
        result = Regions(outlines, numbers, names, abbrevs, name)

    if numbers is None:
        numbers = [0, 1]

    if names is None:
        names = _create_expected_str_list(numbers, "Region")
    elif isinstance(names, six.string_types):
        names = _create_expected_str_list(numbers, names)

    if abbrevs is None:
        abbrevs = _create_expected_str_list(numbers, "r")
    elif isinstance(abbrevs, six.string_types):
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


def test_lon_extent():

    assert test_regions1.lon_180
    assert not test_regions1.lon_360

    outl_ = ((0, 0), (0, 1), (360, 1.0), (360, 0))

    test_regions_ = Regions([outl_])

    assert not test_regions_.lon_180
    assert test_regions_.lon_360

    outl_ = ((-1, 0), (-1, 1), (360, 1.0), (360, 0))
    test_regions_ = Regions([outl_])

    with pytest.raises(ValueError, match="lon has both data that is larger than 180 "):
        test_regions_.lon_180

    with pytest.raises(ValueError, match="lon has both data that is larger than 180 "):
        test_regions_.lon_360


@pytest.mark.parametrize("numbers", [["a", "b"], ["a", 2]])
def test_error_on_non_numeric(numbers):

    with pytest.raises(ValueError, match="'numbers' must be numeric"):
        Regions(poly, numbers)
