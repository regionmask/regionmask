# import mpl and change the backend before other mpl imports
import matplotlib as mpl # isort:skip
# Order of imports is important here: using Agg for non-display environments
mpl.use("Agg")

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import pytest
from shapely.geometry import MultiPolygon, Polygon

from regionmask import Regions
from regionmask.core.plot import _subsample

# =============================================================================

# set up the testing regions

name = "Example"
numbers = [0, 1]
names = ["Unit Square1", "Unit Square2"]
abbrevs = ["uSq1", "uSq2"]

outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0))
outl2 = ((0, 1), (0, 2), (1, 2.0), (1, 1))
outlines = [outl1, outl2]

outl1_closed = outl1 + outl1[:1]
outl2_closed = outl2 + outl2[:1]

r1 = Regions(
    name=name, numbers=numbers, names=names, abbrevs=abbrevs, outlines=outlines
)

numbers = [1, 2]
names = {1: "Unit Square1", 2: "Unit Square2"}
abbrevs = {1: "uSq1", 2: "uSq2"}
poly1 = Polygon(outl1)
poly2 = Polygon(outl2)
poly = {1: poly1, 2: poly2}

r2 = Regions(name=name, numbers=numbers, names=names, abbrevs=abbrevs, outlines=poly)

multipoly = [MultiPolygon([poly1, poly2])]
r3 = Regions(multipoly)
# polygons are automatically closed
outl_multipoly = np.concatenate((outl1_closed, [[np.nan, np.nan]], outl2_closed))

# =============================================================================


def test__subsample():
    lon, lat = _subsample([[0, 1], [1, 0]])
    res = np.concatenate((np.linspace(1, 0), np.linspace(0, 1)))
    assert np.allclose(lon, res)


# =============================================================================


@pytest.mark.filterwarnings("ignore:numpy.dtype size changed")
@pytest.mark.filterwarnings("ignore:numpy.ufunc size changed")
def test_plot_projection():

    plt.close("all")
    # default is PlateCarree
    ax = r1.plot(subsample=False)
    assert isinstance(ax.projection, ccrs.PlateCarree)

    plt.close("all")
    # make sure the proj keword is respected
    ax = r1.plot(subsample=False, proj=ccrs.Miller())
    assert isinstance(ax.projection, ccrs.Miller)

    plt.close("all")
    # projection given with axes is respected
    f, ax = plt.subplots(subplot_kw=dict(projection=ccrs.Mollweide()))
    ax = r1.plot(subsample=False, ax=ax)
    assert isinstance(ax.projection, ccrs.Mollweide)


def test_plot_regions_projection():

    plt.close("all")
    # if none is given -> no projection
    ax = r1.plot_regions(subsample=False)
    assert not hasattr(ax, "projection")

    plt.close("all")
    # projection given with axes is respected
    f, ax = plt.subplots(subplot_kw=dict(projection=ccrs.Mollweide()))
    ax = r1.plot_regions(subsample=False, ax=ax)
    assert isinstance(ax.projection, ccrs.Mollweide)


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines(plotfunc):

    func = getattr(r1, plotfunc)

    plt.close("all")
    ax = func(subsample=False)

    lines = ax.lines

    assert len(lines) == 2

    assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)
    assert np.allclose(ax.lines[1].get_xydata(), outl2_closed)


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_multipoly(plotfunc):
    # regression of 47: because multipolygons were concatenated
    # they did not look closed

    func = getattr(r3, plotfunc)

    plt.close("all")
    ax = func(subsample=False)

    lines = ax.lines

    assert len(lines) == 1

    assert np.allclose(ax.lines[0].get_xydata(), outl_multipoly, equal_nan=True)


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_selection(plotfunc):

    func = getattr(r1, plotfunc)

    plt.close("all")
    ax = func(subsample=False, regions=[0, 1])
    lines = ax.lines
    assert len(lines) == 2
    assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)
    assert np.allclose(ax.lines[1].get_xydata(), outl2_closed)

    # select a single number
    plt.close("all")
    ax = func(subsample=False, regions=0)
    lines = ax.lines
    assert len(lines) == 1
    assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)

    # select by number
    plt.close("all")
    ax = func(subsample=False, regions=[0])
    lines = ax.lines
    assert len(lines) == 1
    assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)

    # select by long_name
    plt.close("all")
    ax = func(subsample=False, regions=["Unit Square1"])
    lines = ax.lines
    assert len(lines) == 1
    assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)

    # select by abbreviation
    plt.close("all")
    ax = func(subsample=False, regions=["uSq1"])
    lines = ax.lines
    assert len(lines) == 1
    assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_subsample(plotfunc):

    plt.close("all")
    func = getattr(r1, plotfunc)

    ax = func(subsample=True)
    lines = ax.lines

    assert len(lines) == 2
    assert np.allclose(ax.lines[0].get_xydata().shape, (200, 2))


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_from_poly(plotfunc):

    plt.close("all")
    func = getattr(r2, plotfunc)

    # subsample is False if polygon is given
    ax = func()
    lines = ax.lines

    assert len(lines) == 2
    assert np.allclose(ax.lines[0].get_xydata(), r2.coords[0])


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_line_prop(plotfunc):

    plt.close("all")
    func = getattr(r1, plotfunc)
    ax = func(subsample=False, line_kws=dict(lw=2, color="g"))

    lines = ax.lines

    assert lines[0].get_lw() == 2
    assert lines[0].get_color() == "g"


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_label_defaults(plotfunc):

    func = getattr(r1, plotfunc)

    plt.close("all")
    ax = func(subsample=False)
    texts = ax.texts
    assert len(texts) == 2


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_label(plotfunc):

    func = getattr(r1, plotfunc)

    plt.close("all")
    ax = func(subsample=False, add_label=True)
    texts = ax.texts

    # default text is the number
    assert len(texts) == 2
    assert texts[0].get_text() == "0"
    assert texts[1].get_text() == "1"

    # they are at the centroid
    assert np.allclose(texts[0].get_position(), (0.5, 0.5))
    assert np.allclose(texts[1].get_position(), (0.5, 1.5))

    # no label
    plt.close("all")
    ax = func(subsample=False, add_label=False)
    texts = ax.texts
    assert len(texts) == 0

    # label: abbrev
    plt.close("all")
    ax = func(subsample=False, add_label=True, label="abbrev")
    texts = ax.texts

    assert len(texts) == 2
    assert texts[0].get_text() == "uSq1"
    assert texts[1].get_text() == "uSq2"

    # label: name
    plt.close("all")
    ax = func(subsample=False, add_label=True, label="name")
    texts = ax.texts

    assert len(texts) == 2
    assert texts[0].get_text() == "Unit Square1"
    assert texts[1].get_text() == "Unit Square2"


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_text_prop(plotfunc):

    plt.close("all")
    func = getattr(r1, plotfunc)

    ax = func(subsample=False, add_label=True, text_kws=dict(fontsize=15))

    texts = ax.texts

    assert texts[0].get_fontsize() == 15
    assert texts[1].get_fontsize() == 15

    assert texts[0].get_va() == "center"

    bbox = texts[0].get_bbox_patch()
    assert bbox.get_edgecolor() == (0.85, 0.85, 0.85, 1.0)
