##################
Scientific Regions
##################

The following regions, used in the scientific literature, are available in regionmask:

* `Giorgi Regions`_ (from Giorgi and Franciso, 2000)
* `SREX Regions`_ (Special Report on Managing the Risks of Extreme Events and Disasters to Advance Climate Change Adaptation (SREX) from Seneviratne et al., 2012)
* `AR6 Regions`_ (Iturbide et al., 2020; ESSD)
* `PRUDENCE Regions`_ (from European Regional Climate Modelling PRUDENCE Project, Christensen and Christensen, 2007)

.. ipython:: python
    :suppress:

    import matplotlib as mpl

    # cut border when saving (for maps)
    mpl.rcParams["savefig.bbox"] = "tight"
    # better quality figures (mostly for PRUDENCE)
    plt.rcParams['savefig.dpi'] = 300


The following imports are necessary for the examples.

.. ipython:: python

    import regionmask

    import cartopy.crs as ccrs

Giorgi Regions
==============

The Giorgi reference regions, rectangular regions proposed in Giorgi and
Francisco, 2000 were used in the third and fourth assessment reports of the
Intergovernmental Panel on Climate Change (IPCC).

.. ipython:: python

    regionmask.defined_regions.giorgi

.. ipython:: python

    @savefig plotting_giorgi.png width=100%
    regionmask.defined_regions.giorgi.plot(label='abbrev');

SREX Regions
============

The Giorgi regions were modified using more flexible polygons in the IPCC Special Report
on Managing the Risks of Extreme Events and Disasters to Advance Climate Adaptation
(SREX; Seneviratne et al., 2012). A slightly modified and extended version of the SREX
regions (not included in regionmask) was used for the fifth IPCC assessment report.

.. ipython:: python

    regionmask.defined_regions.srex


.. ipython:: python

    @savefig plotting_srex.png width=100%
    regionmask.defined_regions.srex.plot();

AR6 Regions
===========

The sixth IPCC assessment report (AR6) again updated the SREX regions in Iturbide et al.,
(2020), which defines 58 regions. The regions cover the land and ocean (``ar6.all``).
In addition the regions are also divided into land (``ar6.land``) and ocean
(``ar6.ocean``) categories. The numbering is kept consistent between the categories.
Note that some regions are in the land and in the ocean categories (e.g. the Mediterranean).

All
~~~

.. ipython:: python

    regionmask.defined_regions.ar6.all


.. ipython:: python

    text_kws = dict(color="#67000d", fontsize=7, bbox=dict(pad=0.2, color="w"))

    @savefig plotting_ar6_all.png width=100%
    regionmask.defined_regions.ar6.all.plot(
        text_kws=text_kws, label_multipolygon="all"
    );

Land
~~~~

.. ipython:: python

    regionmask.defined_regions.ar6.land

.. ipython:: python

    @savefig plotting_ar6_land.png width=100%
    regionmask.defined_regions.ar6.land.plot(text_kws=text_kws, add_ocean=True);


Ocean
~~~~~

.. ipython:: python

    regionmask.defined_regions.ar6.ocean

.. ipython:: python

    @savefig plotting_ar6_ocean.png width=100%
    regionmask.defined_regions.ar6.ocean.plot(
        text_kws=text_kws, add_land=True, label_multipolygon="all"
    )


PRUDENCE Regions
================

The PRUDENCE regions were defined in the PRUDENCE project as European sub-areas for regional climate model output and are often used in European climate studies. They contain 8 regions, Alps (AL), British Isles (BI), Eastern Europe (EA), France (FR), Iberian Peninsula (IP), Mediterranean (MD), Mid-Europe (ME), and Scandinavia (SC).

.. warning:: The region FR and ME overlap, hence it is not possible to create 2D masks use ``prudence.mask_3D(lon, lat)``.

.. ipython:: python

    regionmask.defined_regions.prudence

.. ipython:: python

    # choose a good projection for regional maps
    proj = ccrs.LambertConformal(central_longitude=10)

    @savefig plotting_prudence.png width=100%
    regionmask.defined_regions.prudence.plot(projection=proj, resolution="50m");


References
==========
* Christensen and Christensen (`2007 <https://link.springer.com/article/10.1007/s10584-006-9210-7>`_)
* Giorgi and Franciso (`2000 <http://onlinelibrary.wiley.com/doi/10.1029/1999GL011016>`_)
* Iturbide et al., (`2020 <https://essd.copernicus.org/preprints/essd-2019-258/>`_)
* Seneviratne et al., (`2012 <https://www.ipcc.ch/pdf/special-reports/srex/SREX-Ch3-Supplement_FINAL.pdf>`_)
