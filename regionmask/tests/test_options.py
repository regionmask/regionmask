import os
from pathlib import Path

import pytest

import regionmask
from regionmask.defined_regions._ressources import _get_cache_dir


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


def test_get_cache_dir():
    import pooch

    default_cache_dir = pooch.os_cache("regionmask")

    assert _get_cache_dir() == default_cache_dir

    with regionmask.set_options(cache_dir="~/.rmask"):
        assert _get_cache_dir() == Path(os.path.expanduser("~/.rmask"))

    with regionmask.set_options(cache_dir="/any/other/location"):
        assert _get_cache_dir() == Path("/any/other/location")

    assert _get_cache_dir() == default_cache_dir
