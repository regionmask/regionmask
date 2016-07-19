


from shapely.geometry import Polygon, MultiPolygon


import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

import matplotlib.pyplot as plt
import numpy as np



# from regions import outline, midpoint, short_name, number, name



# =============================================================================



def _draw_poly(ax, outl, subsample=False, **kwargs):
    """
    draw the outline of the regions

    """
    if subsample:
        lons, lats = _subsample(outl)
    else:
        lons, lats = outl[:, 0], outl[:, 1]
     
    trans = ccrs.PlateCarree()

    color = kwargs.pop('color', '0.05')

    ax.plot(lons, lats, color=color, transform=trans, **kwargs)


def _subsample(outl):
    lons = np.array([])
    lats = np.array([])
    for i in range(len(outl)):
        # make sure we get a nice plot for projections with "bent" lines 
        lons = np.hstack((lons, np.linspace(outl[i - 1][0], outl[i][0])))
        lats = np.hstack((lats, np.linspace(outl[i - 1][1], outl[i][1])))

    return lons, lats




def _plot(self, ax=None, proj=ccrs.PlateCarree(), regions='all',
              add_label=True, label='number', coastlines=True,
              add_ocean=True, line_kws=dict(), text_kws=dict(),
              resolution='110m', subsample=None):
    """
    plot map with with srex regions

    Parameters
    ----------
    ax : axis handle, optinal
        Uses existing axis: needs to be a cartopy axis. If not 
        given, creates a new axis with the specified projection.
    proj : cartopy projection, optional
        Defines the projection of the map. See cartopy home page.
    regions : list | 'all', optinal
        List the regions (as number, abbrev or name, can be mixed)
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
        Arguments passed to text.
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

    if ax is None:
        ax = plt.axes(projection=proj)

    if regions == 'all':
        regions = self.numbers
    else:
        regions = self.map_keys(regions)

    if np.isscalar(regions):
        regions = [regions]

    if subsample is None:
        subsample = not self._is_polygon

    if add_ocean:
        NEF = cfeature.NaturalEarthFeature
        OCEAN = NEF('physical', 'ocean', resolution, edgecolor='face',
                    facecolor=cfeature.COLORS['water'])

        ax.add_feature(OCEAN)
    
    if coastlines:
        ax.coastlines(resolution=resolution)
    
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)

    ax.tick_params(which='major', axis='y', pad=3)
    ax.tick_params(which='major', labelsize=8)    

    for i in regions:
        coords = self[i].coords
        _draw_poly(ax, coords, subsample, **line_kws)

    if add_label:
        
        trans = ccrs.PlateCarree()
        va = text_kws.pop('va', 'center')
        ha = text_kws.pop('ha', 'center')
        col = text_kws.pop('backgroundcolor', '0.85')

        for i in regions:
            r = self[i]
            txt = str(getattr(r, label))
            ax.text(r.centroid[0], r.centroid[1],
                    txt, transform=trans, va=va,
                    ha=ha, backgroundcolor=col, **text_kws)

    return ax








