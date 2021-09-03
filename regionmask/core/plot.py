import warnings

import numpy as np

from .utils import _deprecate_positional, _flatten_polygons


def _polygons_coords(polygons):

    coords = []
    for p in polygons:
        coords += [np.asarray(p.exterior)[:, :2]] + [
            np.asarray(i)[:, :2] for i in p.interiors
        ]

    return coords


def _draw_poly(ax, polygons, subsample=False, **kwargs):
    """
    draw the outline of the regions

    """

    from matplotlib.collections import LineCollection

    polygons = _flatten_polygons(polygons)
    coords = _polygons_coords(polygons)

    if subsample:
        coords = [_subsample(coord) if len(coord) < 10 else coord for coord in coords]

    color = kwargs.pop("color", "0.1")

    lc = LineCollection(coords, color=color, **kwargs)
    ax.add_collection(lc)
    ax.autoscale_view()

    # from matplotlib.path import Path
    # import matplotlib.patches as patches
    # paths = [Path(coord) for coord in coords]
    # patchs = [patches.PathPatch(path, facecolor='none', **kwargs) for path in paths]
    # [ax.add_patch(patch) for patch in patchs]
    # ax.autoscale_view()


def _subsample(outl, num=50):
    # assumes outl is closed - i.e outl[:-1] == outl[0]
    out = np.linspace(outl[:-1], outl[1:], num=num, endpoint=False, axis=1)
    out = out.reshape(-1, 2)
    return np.vstack([out, outl[-1]])


def _check_unused_kws(add, kws, feature_name, kws_name):
    if (kws is not None) and (not add):
        warnings.warn(
            f"'{kws_name}' are passed but '{feature_name}' is False.", RuntimeWarning
        )


@_deprecate_positional
def _plot(
    self,
    ax=None,
    projection=None,
    regions=None,
    add_label=True,
    label="number",
    add_coastlines=None,
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
    **kwargs,
):
    """
    plot map with with region outlines

    Parameters
    ----------
    ax : axes handle, optional
        If given uses existing axes (needs to be a cartopy axes). If not
        given, creates a new axes with the specified projection.
    projection : cartopy projection, default: None
        Defines the projection of the map. If None uses 'PlateCarree'.
        See cartopy home page.
    regions : list of int or str | 'all', default: 'all'
        Deprecated - subset regions before plotting, i.e. use `r[regions].plot()`
        instead of `r.plot(regions=regions)`.
        Select the regions (by number, abbrev or name, can be mixed)
        that should be drawn.
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
    subsample : None or bool, default: None
        If True subsamples the outline of the coords to make better
        looking plots on certain maps. If False does not subsample.
        If None, infers the subsampling -> if the input is given as
        array subsamples if it is given as (Multi)Polygons does not
        subsample.
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

    Returns
    -------
    ax : axes handle

    Notes
    -----
    plot internally calls :py:func:`Regions.plot_regions`.

    """

    proj = kwargs.pop("proj", None)
    if proj is not None:
        if projection is not None:
            raise TypeError("Cannot set 'proj' and 'projection'.")
        projection = proj
        warnings.warn("'proj' has been renamed to 'projection'", FutureWarning)

    coastlines = kwargs.pop("coastlines", None)
    if coastlines is not None:
        if add_coastlines is not None:
            raise TypeError("Cannot set 'coastlines' and 'add_coastlines'.")
        add_coastlines = coastlines
        warnings.warn(
            "'coastlines' has been renamed to 'add_coastlines'", FutureWarning
        )

    # part of the deprecation
    if kwargs:
        key = list(kwargs.keys())[0]
        raise TypeError(f"_plot() got an unexpected keyword argument '{key}'")

    # set add_coastlines=True in the fcn signature after the deprecation period
    if add_coastlines is None:
        add_coastlines = True

    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import matplotlib.pyplot as plt

    NEF = cfeature.NaturalEarthFeature

    if label_multipolygon not in ["all", "largest"]:
        raise ValueError("'label_multipolygon' must be one of 'all' and 'largest'")

    _check_unused_kws(add_coastlines, coastline_kws, "add_coastlines", "coastline_kws")
    _check_unused_kws(add_ocean, ocean_kws, "add_ocean", "ocean_kws")
    _check_unused_kws(add_land, land_kws, "add_land", "land_kws")

    if projection is None:
        projection = ccrs.PlateCarree()

    if ax is None:
        ax = plt.axes(projection=projection)

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
        regions=regions,
        add_label=add_label,
        label=label,
        line_kws=line_kws,
        text_kws=text_kws,
        subsample=subsample,
        label_multipolygon=label_multipolygon,
    )

    return ax


@_deprecate_positional
def _plot_regions(
    self,
    ax=None,
    regions=None,
    add_label=True,
    label="number",
    line_kws=None,
    text_kws=None,
    subsample=None,
    label_multipolygon="largest",
):
    """
    plot map with with srex regions

    Parameters
    ----------
    ax : axes handle, optional
        If given, uses existing axes. If not given, creates a new axes.
        Note: in contrast to plot this does not create a cartopy axes.
    regions : list of int or str | 'all', default: "all"
        Deprecated - subset regions before plotting, i.e. use `r[regions].plot()`
        instead of `r.plot(regions=regions)`.
        Select the regions (by number, abbrev or name, can be mixed)
        that should be drawn.
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
    subsample : None or bool, optional
        If True subsamples the outline of the coords to make better
        looking plots on certain maps. If False does not subsample.
        If None, infers the subsampling -> if the input is given as
        array subsamples if it is given as (Multi)Polygons does not
        subsample.
    label_multipolygon : 'largest' | 'all', optional
        If 'largest' only adds a text label for the largest Polygon of a
        MultiPolygon. If 'all' adds text labels to all of them. Default:
        'largest'.

    Returns
    -------
    ax : axes handle

    """

    if regions is not None:
        warnings.warn(
            "The 'regions' keyword has been deprecated. Subset regions before plotting,"
            " i.e. use `r[regions].plot()` instead of `r.plot(regions=regions)`.",
            FutureWarning,
        )
    else:
        regions = "all"

    import matplotlib.pyplot as plt

    try:
        import cartopy.crs as ccrs
        from cartopy.mpl import geoaxes

        has_cartopy = True
    except ImportError:
        has_cartopy = False

    if label_multipolygon not in ["all", "largest"]:
        raise ValueError("'label_multipolygon' must be one of 'all' and 'largest'")

    _check_unused_kws(add_label, text_kws, "add_label", "text_kws")

    if ax is None:
        ax = plt.gca()

    if has_cartopy and isinstance(ax, geoaxes.GeoAxes):
        trans = ccrs.PlateCarree()
    else:
        trans = ax.transData

    if regions == "all":
        regions = self.numbers
    else:
        regions = self.map_keys(regions)

    if np.isscalar(regions):
        regions = [regions]

    if subsample is None:
        subsample = not self._is_polygon

    if line_kws is None:
        line_kws = dict()

    if text_kws is None:
        text_kws = dict()

    # draw the outlines
    polygons = [self[i].polygon for i in regions]
    _draw_poly(ax, polygons, subsample=subsample, transform=trans, **line_kws)

    if add_label:

        va = text_kws.pop("va", "center")
        ha = text_kws.pop("ha", "center")
        col = text_kws.pop("backgroundcolor", "0.85")
        clip_on = text_kws.pop("clip_on", True)

        for i in regions:
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

    import xarray as xr

    if not isinstance(mask_3D, xr.DataArray):
        raise ValueError("expected a xarray.DataArray")

    if not mask_3D.ndim == 3:
        raise ValueError(f"``mask_3D`` must have 3 dimensions, found {mask_3D.ndim}")

    if "region" not in mask_3D.coords:
        raise ValueError("``mask_3D`` must contain the dimension 'region'")

    # flatten the mask
    mask_2D = (mask_3D * mask_3D.region).sum("region")

    # mask all gridpoints not belonging to any region
    mask_2D = mask_2D.where(mask_3D.any("region"))

    return mask_2D.plot.pcolormesh(**kwargs)
