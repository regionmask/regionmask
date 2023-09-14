import contextlib

from packaging.version import Version

try:
    import cartopy.crs as ccrs
except ImportError:  # pragma: no cover
    pass

try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover
    pass

import numpy as np
import pytest
from shapely.geometry import MultiPolygon, Point, Polygon

import regionmask
from regionmask import Regions, plot_3D_mask
from regionmask.core.plot import (
    _check_unused_kws,
    _flatten_polygons,
    _maybe_gca,
    _polygons_coords,
)

from . import assert_no_warnings, requires_cartopy, requires_matplotlib

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

# a region with segments longer than 1, use Polygon to close the coords
r_large = regionmask.Regions([Polygon(c * 10) for c in r1.coords])

# create a polygon with a hole
interior1_closed = ((0.2, 0.2), (0.2, 0.45), (0.45, 0.45), (0.45, 0.2), (0.2, 0.2))
interior2_closed = ((0.55, 0.55), (0.55, 0.8), (0.8, 0.8), (0.8, 0.55), (0.55, 0.55))
poly1_interior1 = Polygon(outl1, [interior1_closed])
poly1_interior2 = Polygon(outl1, [interior1_closed, interior2_closed])

point = Point(1, 2)

# =============================================================================


@contextlib.contextmanager
def figure_context(*args, **kwargs):
    fig = plt.figure(*args, **kwargs)

    try:
        yield fig
    finally:
        plt.close(fig)


@pytest.fixture(scope="module", autouse=True)
def assert_all_figures_closed():
    """meta-test to ensure all figures are closed at the end of a test
    Notes:  Scope is kept to module (only invoke this function once per test
    module) else tests cannot be run in parallel (locally). Disadvantage: only
    catches one open figure per run. May still give a false positive if tests
    are run in parallel.
    """
    yield None

    open_figs = len(plt.get_fignums())
    if open_figs:
        raise RuntimeError(
            f"tests did not close all figures ({open_figs} figures open)"
        )


PLOTFUNCS = [
    "plot_regions",
    pytest.param("plot", marks=requires_cartopy),
]


# =============================================================================


def test_flatten_polygons():
    # TODO: move to test_utils.py

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

    with pytest.raises(ValueError, match="'error' must be one of 'raise' and 'skip'"):
        _flatten_polygons([poly1, point], error="foo")

    with pytest.raises(TypeError, match="Expected 'Polygon' or 'MultiPolygon'"):
        _flatten_polygons([poly1, point])

    result = _flatten_polygons([poly1, point], error="skip")
    assert len(result) == 1
    assert result[0].equals(poly1)


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


@requires_matplotlib
def test_maybe_gca():

    with figure_context():
        ax = _maybe_gca(aspect=1)

        assert isinstance(ax, mpl.axes.Axes)
        assert ax.get_aspect() == 1

    with figure_context():
        ax = _maybe_gca(aspect=1)

        assert isinstance(ax, mpl.axes.Axes)
        assert ax.get_aspect() == 1

    with figure_context():
        existing_axes = plt.axes()
        ax = _maybe_gca(aspect=1)

        # re-uses the existing axes
        assert existing_axes == ax
        # kwargs are ignored when reusing axes
        assert ax.get_aspect() == "auto"


@requires_cartopy
def test_plot_projection():

    # default is PlateCarree
    with figure_context():
        ax = r1.plot(tolerance=None)
        assert isinstance(ax.projection, ccrs.PlateCarree)

    # make sure the proj keyword is respected
    with figure_context():
        ax = r1.plot(tolerance=None, projection=ccrs.Miller())
        assert isinstance(ax.projection, ccrs.Miller)

    # projection given with axes is respected
    with figure_context() as f:
        ax = f.subplots(subplot_kw=dict(projection=ccrs.Mollweide()))
        ax = r1.plot(tolerance=None, ax=ax)
        assert isinstance(ax.projection, ccrs.Mollweide)


@requires_cartopy
def test_plot_gca():

    with figure_context() as f:
        axs = f.subplots(1, 2, subplot_kw=dict(projection=ccrs.Robinson()))

        ax = r1.plot(tolerance=None)
        assert ax is axs[1]

    with figure_context() as f:
        ax = f.subplots()

        match = "current axes .* is not a cartopy GeoAxes"
        with pytest.raises(TypeError, match=match):
            r1.plot(tolerance=None)

    with figure_context() as f:
        ax = f.subplots()

        match = "passed axes .* is not a cartopy GeoAxes"
        with pytest.raises(TypeError, match=match):
            r1.plot(tolerance=None, ax=ax)


@requires_cartopy
def test_plot_regions_gca():

    with figure_context() as f:
        axs = f.subplots(1, 2)

        ax = r1.plot_regions(tolerance=None)
        assert ax is axs[1]


@requires_cartopy
def test_plot_regions_projection():

    # if none is given -> no projection
    with figure_context():
        ax = r1.plot_regions(tolerance=None)
        assert not hasattr(ax, "projection")

    # projection given with axes is respected
    with figure_context() as f:
        ax = f.subplots(subplot_kw=dict(projection=ccrs.Mollweide()))
        ax = r1.plot_regions(tolerance=None, ax=ax)
        assert isinstance(ax.projection, ccrs.Mollweide)


# -----------------------------------------------------------------------------


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_lines(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
        ax = func(tolerance=None)

        lines = ax.collections[0].get_segments()

        assert len(lines) == 2
        assert np.allclose(lines[0], outl1_closed)
        assert np.allclose(lines[1], outl2_closed)


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_lines_multipoly(plotfunc):
    """regression of 47: because multipolygons were concatenated
    they did not look closed"""

    func = getattr(r3, plotfunc)

    with figure_context():
        ax = func(tolerance=None)

        lines = ax.collections[0].get_segments()
        assert len(lines) == 2
        assert np.allclose(lines[0], outl1_closed)
        assert np.allclose(lines[1], outl2_closed)


# -----------------------------------------------------------------------------


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_lines_selection(plotfunc):

    with figure_context():
        func = getattr(r1[0, 1], plotfunc)

        ax = func(tolerance=None)
        lines = ax.collections[0].get_segments()
        assert len(lines) == 2
        assert np.allclose(lines[0], outl1_closed)
        assert np.allclose(lines[1], outl2_closed)


@requires_matplotlib
@requires_cartopy
def test_error_extra_kwarg():
    # manual TypeError for extra kwargs
    # remove test after coastlines and proj keywords are removed

    with pytest.raises(TypeError, match="got an unexpected keyword argument 'bar'"):
        with figure_context():
            r1.plot(bar=5)


# -----------------------------------------------------------------------------


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_lines_tolerance(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
        ax = func(tolerance=1 / 50)
        lines = ax.collections[0].get_paths()

        assert len(lines) == 2
        assert np.allclose(lines[0].vertices.shape, (201, 2))


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_lines_tolerance_None(plotfunc):

    func = getattr(r_large, plotfunc)

    with figure_context():
        ax = func(tolerance=None)
        lines = ax.collections[0].get_paths()

        np.testing.assert_allclose(lines[0].vertices, r_large.coords[0])
        np.testing.assert_allclose(lines[1].vertices, r_large.coords[1])


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
@pytest.mark.parametrize("kwargs", ({}, {"tolerance": "auto"}))
def test_plot_lines_tolerance_auto(plotfunc, kwargs):

    func = getattr(r_large, plotfunc)

    expected = (41, 2) if plotfunc == "plot" else (5, 2)

    with figure_context():
        ax = func(**kwargs)

        lines = ax.collections[0].get_paths()
        np.testing.assert_allclose(lines[0].vertices.shape, expected)
        np.testing.assert_allclose(lines[1].vertices.shape, expected)


@requires_cartopy
def test_plot_regions_lines_tolerance_cartopy_axes():

    expected = (41, 2)

    # when passing GeoAxes -> auto segmentizes lines
    with figure_context():
        ax = r_large.plot_regions(ax=plt.axes(projection=ccrs.PlateCarree()))

        lines = ax.collections[0].get_paths()
        np.testing.assert_allclose(lines[0].vertices.shape, expected)
        np.testing.assert_allclose(lines[1].vertices.shape, expected)


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
@pytest.mark.parametrize("subsample", [True, False])
def test_plot_lines_subsample_deprecated(plotfunc, subsample):

    func = getattr(r1, plotfunc)

    with pytest.warns(
        FutureWarning, match="The 'subsample' keyword has been deprecated."
    ):
        with figure_context():
            func(subsample=subsample)


# -----------------------------------------------------------------------------


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_lines_from_poly(plotfunc):

    func = getattr(r2, plotfunc)

    # subsample is False if polygon is given
    with figure_context():
        ax = func()
        lines = ax.collections[0].get_segments()

        assert len(lines) == 2
        assert np.allclose(lines[0], r2.coords[0])


# -----------------------------------------------------------------------------


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_line_prop(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
        ax = func(tolerance=None, line_kws=dict(lw=2, color="g"))

        collection = ax.collections[0]

        assert collection.get_linewidth() == 2
        np.testing.assert_equal(collection.get_color(), mpl.colors.to_rgba_array("g"))


# -----------------------------------------------------------------------------


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_label_defaults(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
        ax = func(tolerance=None)
        texts = ax.texts
        assert len(texts) == 2


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_label(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
        ax = func(tolerance=None, add_label=True)
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
        ax = func(tolerance=None, add_label=False)
        texts = ax.texts
        assert len(texts) == 0

    # label: abbrev
    with figure_context():
        ax = func(tolerance=None, add_label=True, label="abbrev")
        texts = ax.texts

        assert len(texts) == 2
        assert texts[0].get_text() == "uSq1"
        assert texts[1].get_text() == "uSq2"

    # label: name
    with figure_context():
        ax = func(tolerance=None, add_label=True, label="name")
        texts = ax.texts

        assert len(texts) == 2
        assert texts[0].get_text() == "Unit Square1"
        assert texts[1].get_text() == "Unit Square2"


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_label_multipolygon(plotfunc):

    func = getattr(r3, plotfunc)

    with pytest.raises(
        ValueError, match="'label_multipolygon' must be one of 'all' and 'largest'"
    ):
        func(label_multipolygon=None)

    with figure_context():
        ax = func(tolerance=None, add_label=True, label_multipolygon="all")
        texts = ax.texts

        assert len(texts) == 2
        assert texts[0].get_text() == "0"
        assert texts[1].get_text() == "0"

    with figure_context():
        ax = func(tolerance=None, add_label=True, label_multipolygon="largest")
        texts = ax.texts

        assert len(texts) == 1
        assert texts[0].get_text() == "0"


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_text_prop(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():

        ax = func(tolerance=None, add_label=True, text_kws=dict(fontsize=15))

        texts = ax.texts

        assert texts[0].get_fontsize() == 15
        assert texts[1].get_fontsize() == 15

        assert texts[0].get_va() == "center"

        bbox = texts[0].get_bbox_patch()
        assert bbox.get_edgecolor() == (0.85, 0.85, 0.85, 1.0)


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_text_clip(plotfunc):
    """test fix for #157"""

    func = getattr(r1, plotfunc)

    with figure_context():

        ax = func(tolerance=None, add_label=True)

        texts = ax.texts

        for text in texts:
            assert text.get_clip_on() is True
            assert text.get_clip_box() == ax.bbox

    with figure_context():

        ax = func(tolerance=None, add_label=True, text_kws=dict(clip_on=False))

        texts = ax.texts

        for text in texts:
            assert text.get_clip_on() is False


@requires_matplotlib
@requires_cartopy
def test_plot_ocean():

    kwargs = dict(tolerance=None, add_label=False, add_coastlines=False)

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
        # note testing private attribute
        assert art._kwargs["lw"] == 0

    # user settings
    with figure_context():
        ax = r1.plot(add_ocean=True, ocean_kws=dict(zorder=1), **kwargs)
        assert len(ax.artists) == 1

        art = ax.artists[0]
        assert art.get_zorder() == 1


@requires_matplotlib
@requires_cartopy
def test_plot_land():

    kwargs = dict(tolerance=None, add_label=False, add_coastlines=False)

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
        # note testing private attribute
        assert art._kwargs["lw"] == 0

    # user settings
    with figure_context():
        ax = r1.plot(add_land=True, land_kws=dict(zorder=1), **kwargs)
        assert len(ax.artists) == 1
        art = ax.artists[0]
        assert art.get_zorder() == 1


@requires_matplotlib
@requires_cartopy
def test_plot_add_coastlines():

    kwargs = dict(tolerance=None, add_label=False)

    # coastlines are added per default
    with figure_context():
        ax = r1.plot(**kwargs)
        assert len(ax.artists) == 1

    with figure_context():
        ax = r1.plot(add_coastlines=False, **kwargs)
        assert len(ax.artists) == 0

    with figure_context():
        ax = r1.plot(add_coastlines=True, **kwargs)
        assert len(ax.artists) == 1
        art = ax.artists[0]
        assert art._kwargs == {"lw": 0.5, "edgecolor": "0.4", "facecolor": "none"}

    with figure_context():
        ax = r1.plot(add_coastlines=True, coastline_kws=dict(), **kwargs)
        assert len(ax.artists) == 1
        art = ax.artists[0]
        assert art._kwargs == {"edgecolor": "black", "facecolor": "none"}


@requires_matplotlib
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

    expected = np.ma.masked_invalid(mask_2D.values)

    if Version(mpl.__version__) < Version("3.7.99"):
        expected = expected.ravel()

    with figure_context():
        h = plot_3D_mask(mask_3D, zorder=3)

        assert np.ma.allequal(expected, h.get_array())

        # ensure kwargs are passed through
        assert h.get_zorder() == 3


@requires_matplotlib
def test_plot_3D_mask_overlap():

    lon = np.arange(-180, 180, 2)
    lat = np.arange(90, -91, -2)

    outline_GLOB = np.array(
        [[-180.0, 90.0], [-180.0, -90.0], [180.0, -90.0], [180.0, 90.0]]
    )
    region = regionmask.Regions([outline_GLOB, outline_GLOB], overlap=True)

    mask_3D = region.mask_3D(lon, lat)

    with figure_context():
        with pytest.warns(RuntimeWarning, match="overlapping regions"):
            plot_3D_mask(mask_3D)


@requires_matplotlib
@requires_cartopy
def test_check_unused_kws():

    # ensure no warning is raised
    with assert_no_warnings():
        _check_unused_kws(True, None, "feature_name", "kws_name")

    with assert_no_warnings():
        _check_unused_kws(True, {}, "feature_name", "kws_name")

    with assert_no_warnings():
        _check_unused_kws(False, None, "feature_name", "kws_name")

    with pytest.warns(
        RuntimeWarning, match="'kws_name' are passed but 'feature_name' is False"
    ):
        _check_unused_kws(False, {}, "feature_name", "kws_name")


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_no_warning_default(plotfunc):
    # ensure no warning is raised on default

    func = getattr(r1, plotfunc)

    with figure_context():
        with assert_no_warnings():
            func()


@requires_matplotlib
@pytest.mark.parametrize("plotfunc", PLOTFUNCS)
def test_plot_unused_text_kws(plotfunc):

    func = getattr(r1, plotfunc)

    with figure_context():
        with pytest.warns(
            RuntimeWarning, match="'text_kws' are passed but 'add_label' is False"
        ):
            func(add_label=False, text_kws={})


@requires_matplotlib
@requires_cartopy
@pytest.mark.parametrize(
    "feature_name, kws_name",
    [
        ["add_coastlines", "coastline_kws"],
        ["add_ocean", "ocean_kws"],
        ["add_land", "land_kws"],
    ],
)
def test_plot_unused_kws(feature_name, kws_name):

    with figure_context():
        with pytest.warns(
            RuntimeWarning,
            match=f"'{kws_name}' are passed but '{feature_name}' is False",
        ):
            r1.plot(**{feature_name: False, kws_name: {}})
