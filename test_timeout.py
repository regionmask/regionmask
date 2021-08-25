import pytest
import warnings

@pytest.mark.flaky(max_runs=2)
def test_flaky():
    assert False

@pytest.mark.timeout(2)
def test_tt():
    import time
    time.sleep(5)


@pytest.mark.timeout(1)
@pytest.mark.flaky(max_runs=2)
def test_t1():
    import time
    time.sleep(5)
    warnings.warn("t1")

@pytest.mark.flaky(max_runs=2)
@pytest.mark.timeout(1)
def test_t2():
    import time
    time.sleep(5)
    warnings.warn("t2")
