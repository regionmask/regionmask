import numpy as np
import pytest

from regionmask.core.utils import _wrapAngle, _wrapAngle180, _wrapAngle360


def test_wrapAngle360():

    assert _wrapAngle360(0) == 0
    assert _wrapAngle360(1) == 1
    assert _wrapAngle360(180) == 180
    assert _wrapAngle360(360) == 0

    assert _wrapAngle360(-1) == 359
    assert _wrapAngle360(-180) == 180

    lon = np.arange(-180, 180)
    result = _wrapAngle360(lon)

    expected = np.concatenate((np.arange(180, 360), np.arange(0, 180)))

    np.testing.assert_allclose(result, expected)


def test_wrapAngle180():

    assert _wrapAngle180(0) == 0
    assert _wrapAngle180(1) == 1
    assert _wrapAngle180(180) == -180
    assert _wrapAngle180(181) == -179
    assert _wrapAngle180(200) == -160
    assert _wrapAngle180(360) == 0
    assert _wrapAngle180(-1) == -1
    assert _wrapAngle180(-180) == -180

    lon = np.arange(0, 360)
    result = _wrapAngle180(lon)

    expected = np.concatenate((np.arange(0, 180), np.arange(-180, 0)))

    np.testing.assert_allclose(result, expected)


@pytest.mark.parametrize("lon", (360, 180, [360], np.array(360), np.array([360])))
def test_wrapAngle180_not_inplace(lon):

    result = _wrapAngle180(lon)
    assert lon != result


@pytest.mark.parametrize("lon", (360, -10, [360], np.array(360), np.array([360])))
def test_wrapAngle360_not_inplace(lon):

    result = _wrapAngle360(lon)
    assert lon != result


def test_wrapAngle():
    lon = np.arange(0, 360)
    expected = _wrapAngle180(lon)
    result = _wrapAngle(lon)

    np.testing.assert_equal(result, expected)

    lon = np.arange(-180, 180)
    expected = _wrapAngle360(lon)
    result = _wrapAngle(lon)

    np.testing.assert_equal(result, expected)

    with pytest.raises(ValueError, match="larger than 180 and smaller than 0"):
        _wrapAngle([-1, 181])

    with pytest.raises(ValueError, match="There are equal longitude coordinates"):
        _wrapAngle([0, 0])

    # test explicit argument
    assert _wrapAngle(-1, 180) == -1
    assert _wrapAngle(-1, 360) == 359
    assert _wrapAngle(-1) == 359

    # test explicit argument
    assert _wrapAngle(181, 180) == -179
    assert _wrapAngle(181, 360) == 181
    assert _wrapAngle(181) == -179


@pytest.mark.parametrize("wrap_lon", [True, False, 180, 360])
@pytest.mark.parametrize("lon", ([180.0, 190], [-180, 170]))
def test_wrapAngle_nan(wrap_lon, lon):

    result = _wrapAngle(lon + [np.nan], wrap_lon=wrap_lon)[:-1]
    expected = _wrapAngle(lon, wrap_lon=wrap_lon)

    np.testing.assert_equal(result, expected)
