import pytest
import numpy as np

from regionmask.core.utils import (
    _create_dict_of_numbered_string,
    _maybe_to_dict,
    _sanitize_names_abbrevs,
    _is_180,
    create_lon_lat_dataarray_from_bounds,
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

    for coord in ["lon", "lat", "lon_bnds", "lat_bnds"]:
        assert coord in result.coords

    def _check_coords(vals, name):

        bnds_expected = np.arange(*vals)
        expected = (bnds_expected[:-1] + bnds_expected[1:]) / 2

        assert np.allclose(result[name], expected)
        assert np.allclose(result[name + "_bnds"], bnds_expected)

    _check_coords(lon_vals, "lon")
    _check_coords(lat_vals, "lat")
