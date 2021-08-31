import importlib

import pytest


def _importorskip(modname):
    try:
        importlib.import_module(modname)
        has = True
    except ImportError:  # pragma: no cover
        has = False
    func = pytest.mark.skipif(not has, reason=f"requires {modname}")
    return has, func


has_cartopy, requires_cartopy = _importorskip("cartopy")
has_matplotlib, requires_matplotlib = _importorskip("matplotlib")
has_pygeos, requires_pygeos = _importorskip("pygeos")
