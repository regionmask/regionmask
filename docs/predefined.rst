##################
Predefined Regions
##################

Some regions are already available in ```regionmask```. At the moment that are the:

* Giorgi Regions (from Giorgi and Franciso, 2000)
* SREX Regions (Special Report on Managing the Risks of Extreme Events and Disasters to Advance Climate Change Adaptation (SREX) from Seneviratne et al., 2012)


.. ipython:: python
    :suppress:

    # Use defaults so we don't get gridlines in generated docs
    import matplotlib as mpl
    mpl.rcdefaults()
    mpl.use('Agg')

The following imports are necessary for all of the examples.

.. ipython:: python

    import regionmask
    import matplotlib.pyplot as plt

Giorgi Regions
==============

.. ipython:: python

    @savefig plotting_giorgi.png width=6in height=3in
    regionmask.giorgi.plot(label='abbrev');


SREX Regions
============

.. ipython:: python

    @savefig plotting_srex.png width=6in
    regionmask.srex.plot();

References
----------
* Giorgi and Franciso, 2000: `<http://onlinelibrary.wiley.com/doi/10.1029/1999GL011016>`_
* Seneviratne et al., 2012:  `<https://www.ipcc.ch/pdf/special-reports/srex/SREX-Ch3-Supplement_FINAL.pdf>`_