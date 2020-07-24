# import mpl and change the backend before other mpl imports
import matplotlib as mpl  # isort:skip

# Order of imports is important here: using Agg for non-display environments
mpl.use("Agg")

import contextlib
from distutils.version import LooseVersion

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import pytest
from shapely.geometry import MultiPolygon, Polygon

import regionmask
from regionmask import Regions, plot_3D_mask
from regionmask.core.plot import _flatten_polygons, _polygons_coords, _subsample

# =============================================================================

# set up the testing regions

name = "Example"
numbers = [0, 1]
names = ["Unit Square1", "Unit Square2"]
abbrevs = ["uSq1", "uSq2"]

outl1 = ((0, 0), (0, 1), (1, 1.0), (1, 0))
outl2 = ((0, 1), (0, 2), (1, 2.0), (1, 1))
outlines = [outl1, outl2]

# polygons are automatically closed
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

multipoly = MultiPolygon([poly1, poly2])
r3 = Regions([multipoly])

# create a polygon with a hole
interior1_closed = ((0.2, 0.2), (0.2, 0.45), (0.45, 0.45), (0.45, 0.2), (0.2, 0.2))
interior2_closed = ((0.55, 0.55), (0.55, 0.8), (0.8, 0.8), (0.8, 0.55), (0.55, 0.55))
poly1_interior1 = Polygon(outl1, [interior1_closed])
poly1_interior2 = Polygon(outl1, [interior1_closed, interior2_closed])

# =============================================================================


@contextlib.contextmanager
def figure_context(*args, **kwargs):
    fig = plt.figure(*args, **kwargs)

    try:
        yield fig
    finally:
        plt.close(fig)


# =============================================================================


def test_subsample():

    result = _subsample([[0, 1], [1, 0]])
    expected = np.vstack((np.arange(0, 1.01, 0.02), np.arange(1, -0.01, -0.02))).T

    assert np.allclose(expected, result)

    result = _subsample(outl1_closed, num=2)

    expected = [
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

    assert np.allclose(expected, result)


def test_flatten_polygons():

    result = _flatten_polygons([poly1])
    assert len(result) == 1
    assert result[0].equals(poly1)

    result = _flatten_polygons([poly1, poly2])
    assert len(result) == 2
    assert result[0].equals(poly1)
    assert result[1].equals(poly2)

    result = _flatten_polygons([multipoly])
    assert len(result) == 2
    assert result[0].equals(poly1)
    assert result[1].equals(poly2)

    result = _flatten_polygons([poly1, multipoly, poly2])
    assert len(result) == 4
    assert result[0].equals(poly1)
    assert result[1].equals(poly1)
    assert result[2].equals(poly2)
    assert result[3].equals(poly2)


def test_polygons_coords():

    result = _polygons_coords([poly1, poly2])
    assert len(result) == 2
    assert np.allclose(outl1_closed, result[0])
    assert np.allclose(outl2_closed, result[1])

    result = _polygons_coords([poly1_interior1])
    assert len(result) == 2
    assert np.allclose(outl1_closed, result[0])
    assert np.allclose(interior1_closed, result[1])

    result = _polygons_coords([poly1_interior2])
    assert len(result) == 3
    assert np.allclose(outl1_closed, result[0])
    assert np.allclose(interior1_closed, result[1])
    assert np.allclose(interior2_closed, result[2])


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

        lines = ax.collections[0].get_segments()

        assert len(lines) == 2
        assert np.allclose(lines[0], outl1_closed)
        assert np.allclose(lines[1], outl2_closed)


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_multipoly(plotfunc):
    # regression of 47: because multipolygons were concatenated
    # they did not look closed

    func = getattr(r3, plotfunc)

    with figure_context():
        ax = func(subsample=False)

        lines = ax.collections[0].get_segments()
        assert len(lines) == 2
        assert np.allclose(lines[0], outl1_closed)
        assert np.allclose(lines[1], outl2_closed)


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_selection(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
        ax = func(subsample=False, regions=[0, 1])
        lines = ax.collections[0].get_segments()
        assert len(lines) == 2
        assert np.allclose(lines[0], outl1_closed)
        assert np.allclose(lines[1], outl2_closed)

    # select a single number
    with figure_context():
        ax = func(subsample=False, regions=0)
        lines = ax.collections[0].get_segments()
        assert len(lines) == 1
        assert np.allclose(lines[0], outl1_closed)

    # select by number
    with figure_context():
        ax = func(subsample=False, regions=[0])
        lines = ax.collections[0].get_segments()
        assert len(lines) == 1
        assert np.allclose(lines[0], outl1_closed)

    # select by long_name
    with figure_context():
        ax = func(subsample=False, regions=["Unit Square1"])
        lines = ax.collections[0].get_segments()
        assert len(lines) == 1
        assert np.allclose(lines[0], outl1_closed)

    # select by abbreviation
    with figure_context():
        ax = func(subsample=False, regions=["uSq1"])
        lines = ax.collections[0].get_segments()
        assert len(lines) == 1
        assert np.allclose(lines[0], outl1_closed)


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_subsample(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
        ax = func(subsample=True)
        lines = ax.collections[0].get_paths()

        assert len(lines) == 2
        assert np.allclose(lines[0].vertices.shape, (201, 2))


@pytest.mark.skipif(
    LooseVersion(np.__version__) < "1.16", reason="requires numpy 1.16 or higher"
)
@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
@pytest.mark.parametrize("n, expected", [(9, (9 - 1) * 50 + 1), (10, 10)])
def test_plot_lines_maybe_subsample(plotfunc, n, expected):
    #  only subset non-polygons if they have less than 10 elements GH153
    # should potentially be superseeded by GH109

    # create closed coordinates with n points
    coords = np.linspace(interior1_closed[0], interior1_closed[1], num=n - 4)
    coords = np.vstack((coords, interior1_closed[1:]))
    r = Regions([coords])

    func = getattr(r, plotfunc)
    with figure_context():
        ax = func(subsample=True)
        lines = ax.collections[0].get_paths()

        assert len(lines) == 1
        assert np.allclose(lines[0].vertices.shape, (expected, 2))


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_lines_from_poly(plotfunc):

    func = getattr(r2, plotfunc)

    # subsample is False if polygon is given
    with figure_context():
        ax = func()
        lines = ax.collections[0].get_segments()

        assert len(lines) == 2
        assert np.allclose(lines[0], r2.coords[0])


# -----------------------------------------------------------------------------


@pytest.mark.parametrize("plotfunc", ["plot", "plot_regions"])
def test_plot_line_prop(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
        ax = func(subsample=False, line_kws=dict(lw=2, color="g"))

        collection = ax.collections[0]

        assert collection.get_linewidth() == 2
        np.testing.assert_equal(collection.get_color(), mpl.colors.to_rgba_array("g"))


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


def test_plot_3D_mask_wrong_input():

    lon = np.arange(-180, 180, 2)
    lat = np.arange(90, -91, -2)
    srex = regionmask.defined_regions.srex

    mask_2D = srex.mask(lon, lat)
    mask_3D = srex.mask_3D(lon, lat)

    with pytest.raises(ValueError, match="expected a xarray.DataArray"):
        plot_3D_mask(None)

    with pytest.raises(ValueError, match="``mask_3D`` must have 3 dimensions"):
        plot_3D_mask(mask_2D)

    with pytest.raises(ValueError, match="must contain the dimension 'region'"):
        plot_3D_mask(mask_2D.expand_dims("foo"))

    expected = np.ma.masked_invalid(mask_2D.values).flatten()
    with figure_context():
        h = plot_3D_mask(mask_3D, zorder=3)

        assert np.ma.allequal(expected, h.get_array())

        # ensure kwargs are passed through
        assert h.get_zorder() == 3
