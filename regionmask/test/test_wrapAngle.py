import numpy as np
from pytest import raises

from regionmask.core.utils import _wrapAngle, _wrapAngle180, _wrapAngle360


def test__wrapAngle360():

    assert _wrapAngle360(0) == 0
    assert _wrapAngle360(1) == 1
    assert _wrapAngle360(180) == 180
    assert _wrapAngle360(360) == 0

    assert _wrapAngle360(-1) == 359
    assert _wrapAngle360(-180) == 180

    lon = np.arange(-180, 180)
    result = _wrapAngle360(lon)

    expected = np.concatenate((np.arange(180, 360), np.arange(0, 180)))

    assert np.allclose(result, expected)


def test__wrapAngle180():

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

    assert np.allclose(result, expected)


def test__wrapAngle():
    lon = np.arange(0, 360)
    expected = _wrapAngle180(lon)
    result = _wrapAngle(lon)

    assert np.allclose(result, expected)

    lon = np.arange(-180, 180)
    expected = _wrapAngle360(lon)
    result = _wrapAngle(lon)

    assert np.allclose(result, expected)

    raises(RuntimeError, _wrapAngle, [-1, 181])

    raises(IndexError, _wrapAngle, [0, 0])

    # test explicit argument
    assert _wrapAngle(-1, 180) == -1
    assert _wrapAngle(-1, 360) == 359
    assert _wrapAngle(-1) == 359

    # test explicit argument
    assert _wrapAngle(181, 180) == -179
    assert _wrapAngle(181, 360) == 181
    assert _wrapAngle(181) == -179
