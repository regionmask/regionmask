import os
from pathlib import Path

import pytest

import regionmask
from regionmask.defined_regions._ressources import _get_cache_dir


@pytest.mark.parametrize("invalid_option", [None, "None", "__foo__"])
def test_option_invalid_error(invalid_option):

    with pytest.raises(ValueError, match="not in the set of valid options"):

        regionmask.set_options(invalid_option=invalid_option)


def test_options_display_max_rows_errors():

    default = regionmask.core.options.OPTIONS["display_max_rows"]
    assert default == 10

    with pytest.raises(ValueError, match="'display_max_rows' must be a positive"):
        regionmask.set_options(display_max_rows=0)

    with pytest.raises(ValueError, match="'display_max_rows' must be a positive"):
        regionmask.set_options(display_max_rows=-3)

    with pytest.raises(ValueError, match="'display_max_rows' must be a positive"):
        regionmask.set_options(display_max_rows=3.5)


@pytest.mark.parametrize("n, expected", [(3, 3), (5, 5), (8, 9), (25, 25), (None, 26)])
def test_options_display_max_rows(n, expected):
    # NOTE: pandas has a strange behaviour here

    from regionmask.defined_regions import srex

    with regionmask.set_options(display_max_rows=n):
        result = srex.__repr__()
        result = len(result.split("\n"))

        assert result == expected + 6 + 1


class A:
    pass


@pytest.mark.parametrize("cache_dir", [5, str, A()])
def test_set_cache_dir_error(cache_dir):

    with pytest.raises(
        ValueError, match="cache_dir' must be None, a string or pathlib.Path"
    ):
        regionmask.set_options(cache_dir=cache_dir)


def test_get_cache_dir():
    import pooch

    default_cache_dir = pooch.os_cache("regionmask")

    assert _get_cache_dir() == default_cache_dir

    with regionmask.set_options(cache_dir="~/.rmask"):
        assert _get_cache_dir() == Path(os.path.expanduser("~/.rmask"))

    with regionmask.set_options(cache_dir="/any/other/location"):
        assert _get_cache_dir() == Path("/any/other/location")

    assert _get_cache_dir() == default_cache_dir


def test_get_options():

    options = regionmask.get_options()

    assert isinstance(options, dict)

    assert options == {"display_max_rows": 10, "cache_dir": None}
