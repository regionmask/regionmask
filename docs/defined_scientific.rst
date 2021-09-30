##################
Scientific Regions
##################

The following regions, used in the scientific literature, are already defined:

* Giorgi Regions (from Giorgi and Franciso, 2000)
* SREX Regions (Special Report on Managing the Risks of Extreme Events and Disasters to Advance Climate Change Adaptation (SREX) from Seneviratne et al., 2012)
* AR6 Regions (Iturbide et al., 2020; ESSD)
* PRUDENCE Regions (from European Regional Climate Modelling PRUDENCE Project, Christensen and Christensen, 2007)

.. ipython:: python
    :suppress:

    # Use defaults so we don't get gridlines in generated docs
    import matplotlib as mpl
    mpl.rcdefaults()
    mpl.use('Agg')

    # cut border when saving (for maps)
    mpl.rcParams["savefig.bbox"] = "tight"
    # better quality figures (mostly for PRUDENCE)
    plt.rcParams['savefig.dpi'] = 300


The following imports are necessary for the examples.

.. ipython:: python

    import regionmask

    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt

Giorgi Regions
==============

.. ipython:: python

    regionmask.defined_regions.giorgi.plot(label='abbrev');

    @savefig plotting_giorgi.png width=100%
    plt.tight_layout()

SREX Regions
============

.. ipython:: python

    regionmask.defined_regions.srex.plot();

    @savefig plotting_srex.png width=100%
    plt.tight_layout()
    
AR6 Regions
===========

There are 58 AR6 regions as defined in Iturbide et al. (2020). The regions cover 
the land and ocean (``ar6.all``). In addition the regions are also divided into land 
(``ar6.land``) and ocean (``ar6.ocean``) categories. The numbering is kept consistent
between the categories. Note that some regions are in the land and in the ocean
categories (e.g. the Mediterranean).

.. warning::

  The regions have changed in the review process. Please update your scripts. The
  final region definitions are available at ``regionmask.defined_regions.ar6``.
  For completeness, the submitted region definitions (also referred to as SOD regions)
  are available at ``regionmask.defined_regions._ar6_pre_revisions``.
  

All
~~~

.. ipython:: python

    regionmask.defined_regions.ar6.all


.. ipython:: python
    
    text_kws = dict(color="#67000d", fontsize=7, bbox=dict(pad=0.2, color="w"))
    
    regionmask.defined_regions.ar6.all.plot(
        text_kws=text_kws, label_multipolygon="all"
    );

    @savefig plotting_ar6_all.png width=100%
    plt.tight_layout()

Land
~~~~

.. ipython:: python

    regionmask.defined_regions.ar6.land

.. ipython:: python

    regionmask.defined_regions.ar6.land.plot(text_kws=text_kws, add_ocean=True);

    @savefig plotting_ar6_land.png width=100%
    plt.tight_layout()
        
        
Ocean
~~~~~

.. ipython:: python

    regionmask.defined_regions.ar6.ocean

.. ipython:: python

    regionmask.defined_regions.ar6.ocean.plot(
        text_kws=text_kws, add_land=True, label_multipolygon="all"
    )

    @savefig plotting_ar6_ocean.png width=100%
    plt.tight_layout()


PRUDENCE Regions
================

The PRUDENCE regions were defined in the PRUDENCE project as European sub-areas for regional climate model output and are often used in European climate studies. They contain 8 regions, Alps (AL), British Isles (BI), Eastern Europe (EA), France (FR), Iberian Peninsula (IP), Mediterranean (MD), Mid-Europe (ME), and Scandinavia (SC).

.. warning:: The region FR and ME overlap, hence 2D masks will not be correct. Use ``mask_3D`` to create masks for each region separately and then concatenate, see `#228 <https://github.com/regionmask/regionmask/issues/228>`__.

.. ipython:: python

    # choose a good projection for regional maps
    proj = ccrs.LambertConformal(central_longitude=10)
    regionmask.defined_regions.prudence.plot(projection=proj, resolution="50m");

    @savefig plotting_prudence.png width=100%
    plt.tight_layout()

References
==========
* Giorgi and Franciso, 2000: `<http://onlinelibrary.wiley.com/doi/10.1029/1999GL011016>`_
* Iturbide et al., 2020: `<https://essd.copernicus.org/preprints/essd-2019-258/>`_
* Seneviratne et al., 2012:  `<https://www.ipcc.ch/pdf/special-reports/srex/SREX-Ch3-Supplement_FINAL.pdf>`_
* Christensen and Christensen, 2007: `<https://link.springer.com/article/10.1007/s10584-006-9210-7>`_
