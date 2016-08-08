
from cartopy.io import shapereader
import numpy as np
import geopandas

from ..core.regions import Regions_cls

#from ne_downloader import _maybe_download


def _obtain_ne(resolution, category, name, title, names='name',
               abbrevs='postal' , coords='geometry', query=None):

    shpfilename = shapereader.natural_earth(resolution, category, name)

    gp = geopandas.read_file(shpfilename)

    # SUBSET THE WHOLE DATASET IF NECESSARY
    if query is not None:
        gp = gp.query(query).reset_index(drop=True)

    # GET NECESSARY DATA FOR Regions_cls
    numbers = np.array(gp.index)
    names = gp[names]
    abbrevs = gp[abbrevs]
    coords = gp[coords]

    return Regions_cls(title, numbers, names, abbrevs, coords)







class natural_earth_cls(object):
    """docstring for natural_earth"""
    def __init__(self):
        super(natural_earth_cls, self).__init__()

        self._countries_110 = None      
        self._countries_50 = None

        self._us_states_50 = None    
        self._us_states_10 = None    


    def __repr__(self):
        return "Combines Region Definitions from 'http://www.naturalearthdata.com'."

    @property
    def countries_110(self):
        if self._countries_110 is None:
            
            opt = dict(resolution='110m',
                       category='cultural',
                       name='admin_0_countries',
                       title='Natural Earth Countries: 110m')

            self._countries_110 = _obtain_ne(**opt)
        return self._countries_110
    
    @property
    def countries_50(self):
        if self._countries_50 is None:
            
            opt = dict(resolution='50m',
                       category='cultural',
                       name='admin_0_countries',
                       title='Natural Earth Countries: 50m')

            self._countries_50 = _obtain_ne(**opt)
        return self._countries_50

    @property
    def us_states_50(self):
        if self._us_states_50 is None:
            
            opt = dict(resolution='50m',
                       category='cultural',
                       name='admin_1_states_provinces_lakes',
                       title='Natural Earth: US States 50m',
                       query="admin == 'United States of America'")

            self._us_states_50 = _obtain_ne(**opt)
        return self._us_states_50


    @property
    def us_states_10(self):
        if self._us_states_10 is None:
            
            opt = dict(resolution='10m',
                       category='cultural',
                       name='admin_1_states_provinces_lakes',
                       title='Natural Earth: US States 10m',
                       query="admin == 'United States of America'")

            self._us_states_10 = _obtain_ne(**opt)
        return self._us_states_10


    """  @property
    def us_states_10(self):
        if self._us_states_10 is None:


            shpfilename = shapereader.natural_earth(resolution='10m',
                                      category='cultural',
                                      name='admin_1_states_provinces_lakes')

            states = geopandas.read_file(shpfilename)
            us_states = states.query("admin == 'United States of America'").reset_index(drop=True)
        
            numbers = np.array(us_states.index)
            names = us_states['name']
            abbrevs = us_states['postal']
            coords = us_states['geometry']

            us_states_10 = Regions_cls('Natural Earth: US States 10m', numbers, names, abbrevs, coords)

            self._us_states_10 = us_states_10
        return self._us_states_10
    
"""






natural_earth = natural_earth_cls()


