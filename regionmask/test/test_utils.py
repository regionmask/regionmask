import numpy as np
import pytest

from regionmask.core.utils import (
    _create_dict_of_numbered_string,
    _equally_spaced_on_split_lon,
    _find_splitpoint,
    _is_180,
    _is_numeric,
    _maybe_to_dict,
    _sanitize_names_abbrevs,
    create_lon_lat_dataarray_from_bounds,
    equally_spaced,
)


@pytest.mark.parametrize(
    "numbers, string, expected",
    [
        [[0, 1], "str", {0: "str0", 1: "str1"}],
        [[1, 2], "str", {1: "str1", 2: "str2"}],
        [[1, 2], "Region", {1: "Region1", 2: "Region2"}],
        [[0, 1, 2], "r", {0: "r0", 1: "r1", 2: "r2"}],
    ],
)
def test_create_dict_of_numbered_string(numbers, string, expected):

    result = _create_dict_of_numbered_string(numbers, string)

    assert isinstance(result, dict)
    assert result == expected


@pytest.mark.parametrize(
    "keys, values, expected",
    [
        [[0, 1], ["a", "b"], {0: "a", 1: "b"}],
        [[1, 2], ["a", "b"], {1: "a", 2: "b"}],
        [[0, 1], {0: "a", 1: "b"}, {0: "a", 1: "b"}],
        [[1, 2], {0: "a", 1: "b"}, {0: "a", 1: "b"}],
    ],
)
def test_maybe_to_dict(keys, values, expected):

    result = _maybe_to_dict(keys, values)

    assert isinstance(result, dict)
    assert result == expected


@pytest.mark.parametrize(
    "numbers, values, default, expected",
    [
        [[0, 1], ["a", "b"], "r", {0: "a", 1: "b"}],
        [[0, 1], {1: "a", 2: "b"}, "r", {1: "a", 2: "b"}],
        [[0, 1], None, "r", {0: "r0", 1: "r1"}],
        [[0, 1], None, "Region", {0: "Region0", 1: "Region1"}],
        [[0, 1], "Region", "r", {0: "Region0", 1: "Region1"}],
    ],
)
def test_sanitize_names_abbrevs(numbers, values, default, expected):

    result = _sanitize_names_abbrevs(numbers, values, default)

    assert isinstance(result, dict)

    assert result == expected


def test_sanitize_names_abbrevs_unequal_length():

    with pytest.raises(ValueError, match="not have the same length"):
        _sanitize_names_abbrevs([0, 1], ["A"], "default")


def test_is_180():

    assert _is_180(-180, 180)
    assert not _is_180(0, 180.1)
    assert not _is_180(0, 180.01)

    # allow for small rounding errors
    assert _is_180(-180.0000002, 180.0000002)

    with pytest.raises(ValueError, match="lon has both data that is larger than 180"):
        _is_180(-1, 181)


@pytest.mark.parametrize("lon_vals", [(-161, -29, 2), (-180, 181, 2)])
@pytest.mark.parametrize("lat_vals", [(75, 13, -2), (90, -91, -2)])
def test_create_lon_lat_dataarray_from_bounds(lon_vals, lat_vals):

    # use "+" because x(*a, *b) is not valid in python 2.7
    result = create_lon_lat_dataarray_from_bounds(*lon_vals + lat_vals)

    for coord in ["lon", "lat", "lon_bnds", "lat_bnds", "LON", "LAT"]:
        assert coord in result.coords

    def _check_coords(vals, name):

        bnds_expected = np.arange(*vals)
        expected = (bnds_expected[:-1] + bnds_expected[1:]) / 2

        assert np.allclose(result[name], expected)
        assert np.allclose(result[name + "_bnds"], bnds_expected)

        return expected

    lon = _check_coords(lon_vals, "lon")
    lat = _check_coords(lat_vals, "lat")

    LON_EXPECTED, LAT_EXPECTED = np.meshgrid(lon, lat)
    np.allclose(result["LON"], LON_EXPECTED)
    np.allclose(result["LAT"], LAT_EXPECTED)


def test_is_numeric():

    assert _is_numeric([1, 2, 3])
    assert not _is_numeric(["a"])


def test_equally_spaced():

    np.random.seed(0)

    equal = np.arange(10)

    grid_2D = np.arange(10).reshape(2, 5)

    un_equal = [0, 1, 2, 4, 5, 6]
    assert equally_spaced(equal)
    assert not equally_spaced(grid_2D)
    assert not equally_spaced(un_equal)
    assert not equally_spaced(1)

    assert equally_spaced(equal, equal)
    assert not equally_spaced(grid_2D, equal)
    assert not equally_spaced(equal, grid_2D)
    assert not equally_spaced(grid_2D, grid_2D)

    assert not equally_spaced(un_equal, equal)
    assert not equally_spaced(equal, un_equal)
    assert not equally_spaced(un_equal, un_equal)

    assert not equally_spaced(1, equal)
    assert not equally_spaced(equal, 1)
    assert not equally_spaced(1, 1)

    close_to_equal = equal + np.random.randn(*equal.shape) * 10 ** -6

    assert equally_spaced(close_to_equal, close_to_equal)


def test__equally_spaced_on_split_lon():
    np.random.seed(0)

    equal = np.arange(10)

    grid_2D = np.arange(10).reshape(2, 5)

    un_equal = [0, 1, 2, 4, 5, 6.1]

    equal_split = np.asarray([5, 6, 7, 8, 9, 10, 1, 2, 3, 4])

    assert _equally_spaced_on_split_lon(equal_split)

    assert not _equally_spaced_on_split_lon([10, 1, 2, 3])
    assert not _equally_spaced_on_split_lon([1, 2, 3, 10])

    assert not _equally_spaced_on_split_lon(equal)
    assert not _equally_spaced_on_split_lon(grid_2D)

    assert not _equally_spaced_on_split_lon(un_equal)

    assert not _equally_spaced_on_split_lon(1)

    close_to_equal = equal + np.random.randn(*equal.shape) * 10 ** -6
    close_to_equal_split = equal_split + np.random.randn(*equal_split.shape) * 10 ** -6

    assert not _equally_spaced_on_split_lon(close_to_equal)
    assert _equally_spaced_on_split_lon(close_to_equal_split)


def test_find_splitpoint():

    np.random.seed(0)
    equal_split = np.asarray([5, 6, 7, 8, 9, 10, 1, 2, 3, 4])
    close_to_equal_split = equal_split + np.random.randn(*equal_split.shape) * 10 ** -6

    assert _find_splitpoint(equal_split) == 6
    assert _find_splitpoint(close_to_equal_split) == 6

    with pytest.raises(ValueError, match="more or less than one split point found"):
        _find_splitpoint([0, 1, 2, 3])

    with pytest.raises(ValueError, match="more or less than one split point found"):
        _find_splitpoint([0, 1, 3, 4, 6, 7])
