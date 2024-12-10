import numpy as np
import pytest

from regionmask.core.plot import _get_tolerance, segmentize


def test_get_tolerance() -> None:

    assert _get_tolerance(0) == 1
    assert _get_tolerance(-1) == 1
    assert _get_tolerance(360) == 1
    assert _get_tolerance([-1, 20]) == 1
    assert _get_tolerance(999) == 1
    assert _get_tolerance(1000) == 10
    assert _get_tolerance([-1000, 10]) == 10
    assert _get_tolerance(10000) == 100
    assert _get_tolerance(10**8) == 10**6


def test_segmentize() -> None:

    zeros = np.zeros(51)

    result = segmentize([[0, 0], [1, 0]], tolerance=1 / 50)
    expected = np.vstack((np.arange(0, 1.01, 0.02), zeros)).T
    assert np.allclose(expected, result)

    result = segmentize([[0, 1], [0, 0]], tolerance=1 / 50)
    expected = np.vstack((zeros, np.arange(1, -0.01, -0.02))).T
    assert np.allclose(expected, result)

    outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0))

    # polygons are automatically closed
    outl1_closed = outl1 + outl1[:1]

    result = segmentize(outl1_closed, tolerance=0.5)

    expected = np.array(
        [
            [0, 0],
            [0, 0.5],
            [0, 1],
            [0.5, 1],
            [1, 1.0],
            [1, 0.5],
            [1, 0],
            [0.5, 0],
            [0, 0],
        ]
    )

    assert np.allclose(expected, result)


def test_segmentize_mixed_length() -> None:
    # only one of the segments needs to be split

    outl = ((0, 0), (0, 1), (0, 5))
    result = segmentize(outl, tolerance=1)
    expected = ((0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5))

    assert np.allclose(expected, result)


@pytest.mark.parametrize("number", [1, 2, 5, 20, 100])
def test_segmentize_n_segments(number) -> None:

    zeros = np.zeros(number + 1)

    result = segmentize([[0, 0], [1, 0]], tolerance=1 / number)
    expected = np.vstack((np.arange(0, 1.0001, 1 / number), zeros)).T
    assert np.allclose(expected, result)


def test_segmentize_smaller() -> None:

    result = segmentize([[0, 0], [0, 1]], tolerance=0.3)
    expected = [
        [0, 0.0],
        [0, 0.25],
        [0, 0.50],
        [0, 0.75],
        [0, 1.0],
    ]

    np.testing.assert_allclose(expected, result)


COORDS = (
    ([[0, 0], [0, 1]]),
    ([[0, 0], [20, 8]]),
    ([[0, 0], [-20.5698, 8.3]]),
    ([[-10, -5], [8, 8.3]]),
)


@pytest.mark.parametrize("coords", COORDS)
@pytest.mark.parametrize("tolerance", [0.3, 1.0, 2.7852])
def test_segmentize_shapely(coords, tolerance) -> None:

    import shapely
    import shapely.testing

    expected = shapely.segmentize(shapely.linestrings(coords), tolerance)
    result = segmentize(coords, tolerance)
    result = shapely.linestrings(result)

    shapely.testing.assert_geometries_equal(result, expected)
