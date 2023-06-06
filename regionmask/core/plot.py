import warnings

import numpy as np

from .utils import _flatten_polygons, flatten_3D_mask


def _polygons_coords(polygons):

    coords = []
    for p in polygons:
        coords += [np.asarray(p.exterior.coords)[:, :2]] + [
            np.asarray(i.coords)[:, :2] for i in p.interiors
        ]

    return coords


def _get_tolerance(coords):

    mx = np.max(np.abs(coords))
    return 1 if mx == 0 else max(10 ** (int(np.log10(mx)) - 2), 1)


def _draw_poly(ax, polygons, tolerance=None, **kwargs):
    """
    draw the outline of the regions

    """

    from matplotlib.collections import LineCollection

    polygons = _flatten_polygons(polygons)
    coords = _polygons_coords(polygons)

    if tolerance == "auto":
        tolerance = _get_tolerance(np.concatenate(coords, 0))

    if tolerance is not None:
        coords = [segmentize(coord, tolerance) for coord in coords]

    color = kwargs.pop("color", "0.1")

    lc = LineCollection(coords, color=color, **kwargs)
    ax.add_collection(lc)
    ax.autoscale_view()

    # from matplotlib.path import Path
    # import matplotlib.patches as patches
    # paths = [Path(coord) for coord in coords]
    # patches = [patches.PathPatch(path, facecolor='none', **kwargs) for path in paths]
    # [ax.add_patch(patch) for patch in patches]
    # ax.autoscale_view()


def segmentize(coords, tolerance):
    """Adds vertices to line segments based on tolerance.

    Additional vertices will be added to every line segment in input coordinates
    so that segments are no greater than tolerance. New vertices will evenly
    subdivide each segment.

    Parameters
    ----------
    coords : ndarray
        2D coordinate array of shape N x 2
    tolerance : float
        Additional vertices will be added so that all line segments are no
        greater than this value. Must be greater than 0.

    See Also
    --------
    pygeos.segmentize
    """

    coords = np.asarray(coords)
    dist = np.sqrt(np.sum((coords[1:] - coords[:-1]) ** 2, axis=1))
    num = np.ceil(dist / tolerance).astype(int)

    if (num == 1).all():
        return coords

    out = list()
    for i in range(len(coords) - 1):
        if num[i] > 1:
            out.append(
                np.linspace(coords[i, :], coords[i + 1, :], num=num[i], endpoint=False)
            )
        else:
            out.append(coords[i : i + 1, :])

    out.append(coords[-1:, :])

    return np.concatenate(out, 0)


def _check_unused_kws(add, kws, feature_name, kws_name):
    if (kws is not None) and (not add):
        warnings.warn(
            f"'{kws_name}' are passed but '{feature_name}' is False.", RuntimeWarning
        )


def _maybe_gca(**kwargs):

    import matplotlib.pyplot as plt

    # can call gcf unconditionally: either it exists or would be created by plt.axes
    f = plt.gcf()

    # only call gca if an active axes exists
    if f.axes:
        # can not pass kwargs to active axes
        return plt.gca()

    return plt.axes(**kwargs)


def _plot(
    self,
    *,
    ax=None,
    projection=None,
    add_label=True,
    label="number",
    add_coastlines=True,
    add_ocean=False,
    line_kws=None,
    text_kws=None,
    resolution="110m",
    subsample=None,
    add_land=False,
    coastline_kws=None,
    ocean_kws=None,
    land_kws=None,
    label_multipolygon="largest",
    tolerance="auto",
):
    """
    plot map with with region outlines

    Parameters
    ----------
    ax : axes handle, optional
        If given uses existing axes (needs to be a cartopy GeoAxes). If not given,
        uses the current axes or creates a new axes with the specified projection.

    projection : cartopy projection, default: None
        Defines the projection of the map. If None uses 'PlateCarree'.
        See cartopy home page.

    add_label : bool, default: True
        If true labels the regions.

    label : 'number' | 'name' | 'abbrev', default: 'number'
        If 'number' labels the regions with numbers, if 'name' uses
        the long name of the regions, if 'short_name' uses
        abbreviations of the regions.

    add_coastlines : bool, default: None
        If None or true plots coastlines. See coastline_kws.

    add_ocean : bool,  default: False
        If true adds the ocean feature. See ocean_kws.

    line_kws : dict, default: None
        Arguments passed to plot.

    text_kws : dict, default, None
        Arguments passed to the labels (ax.text).

    resolution : '110m' | '50m' | '10m', default: '110m'
        Specify the resolution of the coastline and the ocean dataset.
        See cartopy for details.

    add_land : bool, default: False
        If true adds the land feature. See land_kws.

    coastline_kws : dict, default: None
        Arguments passed to ``ax.coastlines()``. If None uses ``color="0.4"`` and
        ``lw=0.5``.

    ocean_kws : dict, default: None
        Arguments passed to ``ax.add_feature(OCEAN)``. Per default uses the cartopy
        ocean color and ``zorder=0.9, lw=0``.

    land_kws : dict, default: None
        Arguments passed to ``ax.add_feature(LAND)``. Per default uses the cartopy
        land color and ``zorder=0.9, lw=0``.

    label_multipolygon : 'largest' | 'all', default: 'largest'.
        If 'largest' only adds a text label for the largest Polygon of a
        MultiPolygon. If 'all' adds text labels to all of them.

    tolerance : None | 'auto' | float, default: 'auto'.
        Maximum length of drawn line segments. Can lead to better looking plots on
        certain maps.

        - None: draw original coordinates
        - float > 0: the maximum (euclidean) length of each line segment.
        - 'auto': The tolerance is automatically determined based on the log10 of the
          largest absolute coordinate. Defaults to 1 for lat/ lon coordinates.

    Returns
    -------
    ax : axes handle

    Notes
    -----
    plot internally calls :py:func:`Regions.plot_regions`.

    """

    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from cartopy.mpl import geoaxes

    NEF = cfeature.NaturalEarthFeature

    if label_multipolygon not in ["all", "largest"]:
        raise ValueError("'label_multipolygon' must be one of 'all' and 'largest'")

    _check_unused_kws(add_coastlines, coastline_kws, "add_coastlines", "coastline_kws")
    _check_unused_kws(add_ocean, ocean_kws, "add_ocean", "ocean_kws")
    _check_unused_kws(add_land, land_kws, "add_land", "land_kws")

    if projection is None:
        projection = ccrs.PlateCarree()

    if ax is not None and not isinstance(ax, geoaxes.GeoAxes):
        raise TypeError(
            "The passed axes (``ax``) is not a cartopy GeoAxes. "
            "Either provide a GeoAxes or use ``plot_region``"
        )

    if ax is None:
        ax = _maybe_gca(projection=projection)

    if not isinstance(ax, geoaxes.GeoAxes):
        raise TypeError(
            "The current axes (``plt.gca()``) is not a cartopy GeoAxes. "
            "Either provide a GeoAxes or use ``plot_region``"
        )

    if ocean_kws is None:
        ocean_kws = dict(color=cfeature.COLORS["water"], zorder=0.9, lw=0)

    if land_kws is None:
        land_kws = dict(color=cfeature.COLORS["land"], zorder=0.9, lw=0)

    if coastline_kws is None:
        coastline_kws = dict(color="0.4", lw=0.5)

    if add_ocean:
        OCEAN = NEF("physical", "ocean", resolution)

        ax.add_feature(OCEAN, **ocean_kws)

    if add_land:
        LAND = NEF("physical", "land", resolution)

        ax.add_feature(LAND, **land_kws)

    if add_coastlines:
        ax.coastlines(resolution=resolution, **coastline_kws)

    self.plot_regions(
        ax=ax,
        add_label=add_label,
        label=label,
        line_kws=line_kws,
        text_kws=text_kws,
        subsample=subsample,
        label_multipolygon=label_multipolygon,
        tolerance=tolerance,
    )

    return ax


def _plot_regions(
    self,
    *,
    ax=None,
    add_label=True,
    label="number",
    line_kws=None,
    text_kws=None,
    subsample=None,
    label_multipolygon="largest",
    tolerance="auto",
):
    """
    plot map with with srex regions

    Parameters
    ----------
    ax : axes handle, optional
        If given, uses existing axes. If not given, uses the current axes or creates new
        axes. In contrast to plot this does not create a cartopy axes.

    add_label : bool
        If true labels the regions. Optional, default True.

    label : 'number' | 'name' | 'abbrev', optional
        If 'number' labels the regions with numbers, if 'name' uses
        the long name of the regions, if 'short_name' uses
        abbreviations of the regions. Default 'number'.

    line_kws : dict, optional
        Arguments passed to plot.

    text_kws : dict, optional
        Arguments passed to the labels (ax.text).

    label_multipolygon : 'largest' | 'all', optional
        If 'largest' only adds a text label for the largest Polygon of a
        MultiPolygon. If 'all' adds text labels to all of them. Default:
        'largest'.

    tolerance : None | 'auto' | float, default: 'auto'.
        Maximum length of drawn line segments. Can lead to better looking plots on
        certain maps.

        - None: draw original coordinates
        - float > 0: the maximum (euclidean) length of each line segment.
        - 'auto': None if a matplotlib axes is passed. If a cartopy GeoAxes is passed
          the tolerance is automatically determined based on the log10 of the
          largest absolute coordinate. Defaults to 1 for lat/ lon coordinates.

    Returns
    -------
    ax : axes handle

    """

    if subsample is not None:
        warnings.warn(
            "The 'subsample' keyword has been deprecated in v0.9.0. Use "
            "``tolerance`` instead.",
            FutureWarning,
        )

    import matplotlib.pyplot as plt

    is_geoaxes = False
    try:
        import cartopy.crs as ccrs
        from cartopy.mpl import geoaxes

        is_geoaxes = isinstance(ax, geoaxes.GeoAxes)
    except ImportError:
        pass

    if label_multipolygon not in ["all", "largest"]:
        raise ValueError("'label_multipolygon' must be one of 'all' and 'largest'")

    _check_unused_kws(add_label, text_kws, "add_label", "text_kws")

    if ax is None:
        ax = plt.gca()

    if is_geoaxes:
        trans = ccrs.PlateCarree()
    else:
        trans = ax.transData

    if line_kws is None:
        line_kws = dict()

    if text_kws is None:
        text_kws = dict()

    if tolerance == "auto" and not is_geoaxes:
        tolerance = None

    # draw the outlines
    polygons = [self[i].polygon for i in self.numbers]
    _draw_poly(ax, polygons, tolerance=tolerance, transform=trans, **line_kws)

    if add_label:

        va = text_kws.pop("va", "center")
        ha = text_kws.pop("ha", "center")
        col = text_kws.pop("backgroundcolor", "0.85")
        clip_on = text_kws.pop("clip_on", True)

        for i in self.numbers:
            r = self[i]
            txt = str(getattr(r, label))

            if label_multipolygon == "all":
                polys = _flatten_polygons([r.polygon])
                xy = [p.centroid.coords[0] for p in polys]
            elif label_multipolygon == "largest":
                xy = [r.centroid]

            for x, y in xy:
                t = ax.text(
                    x,
                    y,
                    txt,
                    transform=trans,
                    va=va,
                    ha=ha,
                    backgroundcolor=col,
                    clip_on=clip_on,
                    **text_kws,
                )

                t.clipbox = ax.bbox

    return ax


def plot_3D_mask(mask_3D, **kwargs):
    """flatten and plot 3D masks

    Parameters
    ----------
    mask_3D : xr.DataArray
        3D mask to flatten and plot. Should be the result of
        `Regions.mask_3D(...)`.
    **kwargs : keyword arguments
        Keyword arguments passed to xr.plot.pcolormesh.

    Returns
    -------
    mesh : ``matplotlib.collections.QuadMesh``

    """

    mask_2D = flatten_3D_mask(mask_3D)

    return mask_2D.plot.pcolormesh(**kwargs)
