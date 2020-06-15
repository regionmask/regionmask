# import mpl and change the backend before other mpl imports
import matplotlib as mpl  # isort:skip

# Order of imports is important here: using Agg for non-display environments
mpl.use("Agg")

import contextlib

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

@contextlib.contextmanager
def figure_context(*args, **kwargs):
    fig = plt.figure(*args, **kwargs)

    try:
        yield fig
    finally:
        plt.close(fig)


# =============================================================================


def test__subsample():
    lon, lat = _subsample([[0, 1], [1, 0]])
    res = np.concatenate((np.linspace(1, 0), np.linspace(0, 1)))
    assert np.allclose(lon, res)


# =============================================================================


@pytest.mark.filterwarnings("ignore:numpy.dtype size changed")
@pytest.mark.filterwarnings("ignore:numpy.ufunc size changed")
def test_plot_projection():

    # default is PlateCarree
    with figure_context():
        ax = r1.plot(subsample=False)
        assert isinstance(ax.projection, ccrs.PlateCarree)

    # make sure the proj keword is respected
    with figure_context():
        ax = r1.plot(subsample=False, proj=ccrs.Miller())
        assert isinstance(ax.projection, ccrs.Miller)

    # projection given with axes is respected
    with figure_context() as f:
        ax = f.subplots(subplot_kw=dict(projection=ccrs.Mollweide()))
        ax = r1.plot(subsample=False, ax=ax)
        assert isinstance(ax.projection, ccrs.Mollweide)


def test_plot_regions_projection():

    # if none is given -> no projection
    with figure_context():
        ax = r1.plot_regions(subsample=False)
        assert not hasattr(ax, "projection")

    # projection given with axes is respected
    with figure_context() as f:
        ax = f.subplots(subplot_kw=dict(projection=ccrs.Mollweide()))
        ax = r1.plot_regions(subsample=False, ax=ax)
        assert isinstance(ax.projection, ccrs.Mollweide)


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
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

    with figure_context():
        ax = func(subsample=False)

        lines = ax.lines

        assert len(lines) == 1

        assert np.allclose(ax.lines[0].get_xydata(), outl_multipoly, equal_nan=True)


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_selection(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
        ax = func(subsample=False, regions=[0, 1])
        lines = ax.lines
        assert len(lines) == 2
        assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)
        assert np.allclose(ax.lines[1].get_xydata(), outl2_closed)

    # select a single number
    with figure_context():
        ax = func(subsample=False, regions=0)
        lines = ax.lines
        assert len(lines) == 1
        assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)

    # select by number
    with figure_context():
        ax = func(subsample=False, regions=[0])
        lines = ax.lines
        assert len(lines) == 1
        assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)

    # select by long_name
    with figure_context():
        ax = func(subsample=False, regions=["Unit Square1"])
        lines = ax.lines
        assert len(lines) == 1
        assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)

    # select by abbreviation
    with figure_context():
        ax = func(subsample=False, regions=["uSq1"])
        lines = ax.lines
        assert len(lines) == 1
        assert np.allclose(ax.lines[0].get_xydata(), outl1_closed)


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_subsample(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
        ax = func(subsample=True)
        lines = ax.lines

        assert len(lines) == 2
        assert np.allclose(ax.lines[0].get_xydata().shape, (200, 2))


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_from_poly(plotfunc):

    func = getattr(r2, plotfunc)

    # subsample is False if polygon is given
    with figure_context():
        ax = func()
        lines = ax.lines

        assert len(lines) == 2
        assert np.allclose(ax.lines[0].get_xydata(), r2.coords[0])


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_line_prop(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
        ax = func(subsample=False, line_kws=dict(lw=2, color="g"))

        lines = ax.lines

        assert lines[0].get_lw() == 2
        assert lines[0].get_color() == "g"


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_label_defaults(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
        ax = func(subsample=False)
        texts = ax.texts
        assert len(texts) == 2


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_label(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
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
    with figure_context():
        ax = func(subsample=False, add_label=False)
        texts = ax.texts
        assert len(texts) == 0

    # label: abbrev
    with figure_context():
        ax = func(subsample=False, add_label=True, label="abbrev")
        texts = ax.texts

        assert len(texts) == 2
        assert texts[0].get_text() == "uSq1"
        assert texts[1].get_text() == "uSq2"

    # label: name
    with figure_context():
        ax = func(subsample=False, add_label=True, label="name")
        texts = ax.texts

        assert len(texts) == 2
        assert texts[0].get_text() == "Unit Square1"
        assert texts[1].get_text() == "Unit Square2"


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_text_prop(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():

        ax = func(subsample=False, add_label=True, text_kws=dict(fontsize=15))

        texts = ax.texts

        assert texts[0].get_fontsize() == 15
        assert texts[1].get_fontsize() == 15

        assert texts[0].get_va() == "center"

        bbox = texts[0].get_bbox_patch()
        assert bbox.get_edgecolor() == (0.85, 0.85, 0.85, 1.0)


def test_plot_ocean():

    kwargs = dict(subsample=False, add_label=False, coastlines=False)

    # no ocean per default
    with figure_context():
        ax = r1.plot(**kwargs)
        assert len(ax.artists) == 0

    with figure_context():
        ax = r1.plot(add_ocean=False, **kwargs)
        assert len(ax.artists) == 0

    # default settings
    with figure_context():
        ax = r1.plot(add_ocean=True, **kwargs)
        assert len(ax.artists) == 1

        art = ax.artists[0]
        assert art.get_zorder() == 0.9

    # user settings
    with figure_context():
        ax = r1.plot(add_ocean=True, ocean_kws=dict(zorder=1), **kwargs)
        assert len(ax.artists) == 1

        art = ax.artists[0]
        assert art.get_zorder() == 1


def test_plot_land():

    kwargs = dict(subsample=False, add_label=False, coastlines=False)

    # no land per default
    with figure_context():
        ax = r1.plot(**kwargs)
        assert len(ax.artists) == 0

    with figure_context():
        ax = r1.plot(add_land=False, **kwargs)
        assert len(ax.artists) == 0

    # default settings
    with figure_context():
        ax = r1.plot(add_land=True, **kwargs)
        assert len(ax.artists) == 1
        art = ax.artists[0]
        assert art.get_zorder() == 0.9

    # user settings
    with figure_context():
        ax = r1.plot(add_land=True, land_kws=dict(zorder=1), **kwargs)
        assert len(ax.artists) == 1
        art = ax.artists[0]
        assert art.get_zorder() == 1


def test_plot_coastlines():

    kwargs = dict(subsample=False, add_label=False)

    # coastlines are added per default
    with figure_context():
        ax = r1.plot(**kwargs)
        assert len(ax.artists) == 1

    with figure_context():
        ax = r1.plot(coastlines=False, **kwargs)
        assert len(ax.artists) == 0

    with figure_context():
        ax = r1.plot(coastlines=True, **kwargs)
        assert len(ax.artists) == 1
        art = ax.artists[0]
        assert art._kwargs == {"lw": 0.5, "edgecolor": "0.4", "facecolor": "none"}

    with figure_context():
        ax = r1.plot(coastlines=True, coastline_kws=dict(), **kwargs)
        assert len(ax.artists) == 1
        art = ax.artists[0]
        assert art._kwargs == {"edgecolor": "black", "facecolor": "none"}
