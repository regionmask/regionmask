import numpy as np


def test_a():

    assert False, "a long\nmultiline\reason"


def test_b():
    raise ValueError("another\nmultiline\thingy")

def test_c():

    np.testing.assert_allclose(1, 2)
