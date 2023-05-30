import importlib
import warnings
from contextlib import contextmanager

import pytest
from packaging.version import Version


def _importorskip(modname, minversion=None):
    try:
        mod = importlib.import_module(modname)
        has = True
        if minversion is not None:
            if Version(mod.__version__) < Version(minversion):
                raise ImportError("Minimum version not satisfied")
    except ImportError:  # pragma: no cover
        has = False
    func = pytest.mark.skipif(not has, reason=f"requires {modname}")
    return has, func


@contextmanager
def assert_no_warnings():

    with warnings.catch_warnings(record=True) as record:
        yield
        assert len(record) == 0, "got unexpected warning(s)"


has_cartopy, requires_cartopy = _importorskip("cartopy")
has_cf_xarray, requires_cf_xarray = _importorskip("cf_xarray")
has_matplotlib, requires_matplotlib = _importorskip("matplotlib")
has_pygeos, requires_pygeos = _importorskip("pygeos")
has_shapely_2, requires_shapely_2 = _importorskip("shapely", minversion="2.0b1")


has_geos_3_10 = False
if has_pygeos:
    import pygeos

    has_geos_3_10 = Version(pygeos.geos_version_string) >= Version("3.10")

requires_geos_3_10 = pytest.mark.skipif(
    not has_geos_3_10, reason="requires geos > 3.10.0"
)
