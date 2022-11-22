import pytest

import regionmask


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
