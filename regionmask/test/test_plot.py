import numpy as np

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

import cartopy.crs as ccrs

from regionmask import Regions, _subsample

from shapely.geometry import Polygon

import pytest

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

r1 = Regions(name=name, numbers=numbers, names=names, abbrevs=abbrevs, outlines=outlines)

numbers = [1, 2]
names = {1: "Unit Square1", 2: "Unit Square2"}
abbrevs = {1: "uSq1", 2: "uSq2"}
poly1 = Polygon(outl1)
poly2 = Polygon(outl2)
poly = {1: poly1, 2: poly2}

r2 = Regions(name=name, numbers=numbers, names=names, abbrevs=abbrevs, outlines=poly)

# =============================================================================


def test__subsample():
    lon, lat = _subsample([[0, 1], [1, 0]])
    res = np.concatenate((np.linspace(1, 0), np.linspace(0, 1)))
    assert np.allclose(lon, res)


# =============================================================================


def test_plot_projection():

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
    plt.close("all")


def test_plot_regions_projection():

    # if none is given -> no projection
    ax = r1.plot_regions(subsample=False)
    assert not hasattr(ax, "projection")
    plt.close("all")

    # projection given with axes is respected
    f, ax = plt.subplots(subplot_kw=dict(projection=ccrs.Mollweide()))
    ax = r1.plot_regions(subsample=False, ax=ax)
    assert isinstance(ax.projection, ccrs.Mollweide)
    plt.close("all")


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines(plotfunc):

    func = getattr(r1, plotfunc)

    ax = func(subsample=False)

    lines = ax.lines

    assert len(lines) == 2

    assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)
    assert np.allclose(ax.lines[1].get_xydata(), outl2_closed)

    plt.close("all")


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_selection(plotfunc):

    func = getattr(r1, plotfunc)

    ax = func(subsample=False, regions=[0, 1])
    lines = ax.lines
    assert len(lines) == 2
    assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)
    assert np.allclose(ax.lines[1].get_xydata(), outl2_closed)
    plt.close("all")

    # select a single number
    ax = func(subsample=False, regions=0)
    lines = ax.lines
    assert len(lines) == 1
    assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)
    plt.close("all")

    # select by number
    ax = func(subsample=False, regions=[0])
    lines = ax.lines
    assert len(lines) == 1
    assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)
    plt.close("all")

    # select by long_name
    ax = func(subsample=False, regions=["Unit Square1"])
    lines = ax.lines
    assert len(lines) == 1
    assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)
    plt.close("all")

    # select by abbreviation
    ax = func(subsample=False, regions=["uSq1"])
    lines = ax.lines
    assert len(lines) == 1
    assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)
    plt.close("all")


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_subsample(plotfunc):

    func = getattr(r1, plotfunc)

    ax = func(subsample=True)
    lines = ax.lines

    assert len(lines) == 2
    assert np.allclose(ax.lines[0].get_xydata().shape, (200, 2))

    plt.close("all")


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_from_poly(plotfunc):

    func = getattr(r2, plotfunc)

    # subsample is False if polygon is given
    ax = func()
    lines = ax.lines

    assert len(lines) == 2
    assert np.allclose(ax.lines[0].get_xydata(), r2.coords[0])

    plt.close("all")


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_line_prop(plotfunc):

    func = getattr(r1, plotfunc)
    ax = func(subsample=False, line_kws=dict(lw=2, color="g"))

    lines = ax.lines

    assert lines[0].get_lw() == 2
    assert lines[0].get_color() == "g"

    plt.close("all")


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_label_defaults(plotfunc):

    func = getattr(r1, plotfunc)

    ax = func(subsample=False)
    texts = ax.texts
    assert len(texts) == 2
    plt.close("all")


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_label(plotfunc):

    func = getattr(r1, plotfunc)

    ax = func(subsample=False, add_label=True)
    texts = ax.texts

    # default text is the number
    assert len(texts) == 2
    assert texts[0].get_text() == "0"
    assert texts[1].get_text() == "1"

    # they are at the centroid
    assert np.allclose(texts[0].get_position(), (0.5, 0.5))
    assert np.allclose(texts[1].get_position(), (0.5, 1.5))

    plt.close("all")

    # no label
    ax = func(subsample=False, add_label=False)
    texts = ax.texts
    assert len(texts) == 0

    plt.close("all")

    # label: abbrev
    ax = func(subsample=False, add_label=True, label="abbrev")
    texts = ax.texts

    assert len(texts) == 2
    assert texts[0].get_text() == "uSq1"
    assert texts[1].get_text() == "uSq2"

    plt.close("all")

    # label: name
    ax = func(subsample=False, add_label=True, label="name")
    texts = ax.texts

    assert len(texts) == 2
    assert texts[0].get_text() == "Unit Square1"
    assert texts[1].get_text() == "Unit Square2"

    plt.close("all")


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_text_prop(plotfunc):

    func = getattr(r1, plotfunc)

    ax = func(subsample=False, add_label=True, text_kws=dict(fontsize=15))

    texts = ax.texts

    assert texts[0].get_fontsize() == 15
    assert texts[1].get_fontsize() == 15

    assert texts[0].get_va() == "center"

    bbox = texts[0].get_bbox_patch()
    assert bbox.get_edgecolor() == (0.85, 0.85, 0.85, 1.0)

    plt.close("all")
