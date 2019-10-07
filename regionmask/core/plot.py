import numpy as np

# =============================================================================


def _draw_poly(ax, outl, trans, subsample=False, **kwargs):
    """
    draw the outline of the regions

    """
    if subsample:
        lons, lats = _subsample(outl)
    else:
        lons, lats = outl[:, 0], outl[:, 1]

    color = kwargs.pop("color", "0.05")

    ax.plot(lons, lats, color=color, transform=trans, **kwargs)


def _subsample(outl):
    lons = np.array([])
    lats = np.array([])
    for i in range(len(outl)):
        # make sure we get a nice plot for projections with "bent" lines
        lons = np.hstack((lons, np.linspace(outl[i - 1][0], outl[i][0])))
        lats = np.hstack((lats, np.linspace(outl[i - 1][1], outl[i][1])))

    return lons, lats


def _plot(
    self,
    ax=None,
    proj=None,
    regions="all",
    add_label=True,
    label="number",
    coastlines=True,
    add_ocean=True,
    line_kws=dict(),
    text_kws=dict(),
    resolution="110m",
    subsample=None,
):
    """
    plot map with with region outlines

    Parameters
    ----------
    ax : axes handle, optional
        If given uses existing axes (needs to be a cartopy axes). If not 
        given, creates a new axes with the specified projection.
    proj : cartopy projection or None, optional
        Defines the projection of the map. If None uses 'PlateCarree'.
        See cartopy home page. Default None.
    regions : list of int or str | 'all', optional
        Select the regions (by number, abbrev or name, can be mixed)
        that should be outlined.
    add_label : bool
        If true labels the regions. Optional, default True.
    label : 'number' | 'name' | 'abbrev', optional
        If 'number' labels the regions with numbers, if 'name' uses 
        the long name of the regions, if 'short_name' uses 
        abbreviations of the regions. Default 'number'.
    add_ocean : bool, optional
        If true colors the ocean blue. Default: True.
    line_kws : dict
        Arguments passed to plot.
    text_kws : dict
        Arguments passed to the labels (ax.text).
    resolution : '110m' | '50m' | '10m'
        Specify the resolution of the coastline and the ocean dataset.
        See cartopy for details.
    subsample : None or bool, optional
        If True subsamples the outline of the coords to make better 
        looking plots on certain maps. If False does not subsample.
        If None, infers the subsampling -> if the input is given as 
        array subsamples if it is given as (Multi)Polygons does not
        subsample.

    Note
    ----
    plot internally calls plot_regions.

    """
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    if proj is None:
        proj = ccrs.PlateCarree()

    if ax is None:
        ax = plt.axes(projection=proj)

    if add_ocean:
        NEF = cfeature.NaturalEarthFeature
        OCEAN = NEF(
            "physical",
            "ocean",
            resolution,
            edgecolor="face",
            facecolor=cfeature.COLORS["water"],
        )

        ax.add_feature(OCEAN)

    if coastlines:
        ax.coastlines(resolution=resolution)

    self.plot_regions(
        ax=ax,
        regions=regions,
        add_label=add_label,
        label=label,
        line_kws=line_kws,
        text_kws=text_kws,
        subsample=subsample,
    )

    return ax


def _plot_regions(
    self,
    ax=None,
    regions="all",
    add_label=True,
    label="number",
    line_kws=dict(),
    text_kws=dict(),
    subsample=None,
):
    """
    plot map with with srex regions

    Parameters
    ----------
    ax : axes handle, optional
        If given, uses existing axes. If not given, creates a new axes.
        Note: in contrast to plot this does not create a cartopy axes.
    regions : list of int or str | 'all', optional
        Select the regions (by number, abbrev or name, can be mixed)
        that should be outlined.
    add_label : bool
        If true labels the regions. Optional, default True.
    label : 'number' | 'name' | 'abbrev', optional
        If 'number' labels the regions with numbers, if 'name' uses 
        the long name of the regions, if 'short_name' uses 
        abbreviations of the regions. Default 'number'.
    add_ocean : bool, optional
        If true colors the ocean blue. Default: True.
    line_kws : dict
        Arguments passed to plot.
    text_kws : dict
        Arguments passed to the labels (ax.text).
    resolution : '110m' | '50m' | '10m'
        Specify the resolution of the coastline and the ocean dataset.
        See cartopy for details.
    subsample : None or bool, optional
        If True subsamples the outline of the coords to make better 
        looking plots on certain maps. If False does not subsample.
        If None, infers the subsampling -> if the input is given as 
        array subsamples if it is given as (Multi)Polygons does not
        subsample.
    """

    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    from cartopy.mpl import geoaxes

    if ax is None:
        ax = plt.gca()

    if isinstance(ax, geoaxes.GeoAxes):
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

    # draw the outlines
    for i in regions:
        coords = self[i].coords
        _draw_poly(ax, coords, trans, subsample, **line_kws)

    if add_label:

        va = text_kws.pop("va", "center")
        ha = text_kws.pop("ha", "center")
        col = text_kws.pop("backgroundcolor", "0.85")

        for i in regions:
            r = self[i]
            txt = str(getattr(r, label))

            ax.text(
                r.centroid[0],
                r.centroid[1],
                txt,
                transform=trans,
                va=va,
                ha=ha,
                backgroundcolor=col,
                **text_kws
            )

    return ax
