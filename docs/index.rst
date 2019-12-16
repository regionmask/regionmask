.. regionmask documentation master file, created by
   sphinx-quickstart on Wed Jul 20 14:36:54 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: logo/logo.png
   :width: 500 px
   :align: center

|

************************************
create masks of geographical regions
************************************

regionmask is a Python module that:

- contains a number of defined regions, including:
  :doc:`countries</defined_countries>` (from
  `Natural Earth <http://www.naturalearthdata.com/>`_), a
  :doc:`landmask</defined_landmask>` and regions used in the
  :doc:`scientific literature</defined_scientific>`
  (the Giorgi regions [#]_ and   the SREX regions [#]_).
- can plot figures of these regions (:doc:`tutorial<notebooks/plotting>`) with
  `matplotlib <http://matplotlib.org/>`_ and
  `cartopy <http://scitools.org.uk/cartopy/>`_
- can be used to create masks of the regions for arbitrary longitude
  and latitude grids with
  `numpy <http://www.numpy.org/>`_ (:doc:`tutorial<notebooks/mask_numpy>`)
  and
  `xarray <http://xarray.pydata.org/>`__ (:doc:`tutorial<notebooks/mask_xarray>`)
- arbitrary regions can be defined easily (:doc:`tutorial<notebooks/create_own_regions>`)

.. note::
   From version 0.5 ``regionmask`` treats points on the region borders differently
   and also considers poygon interiors (holes), e.g. the Caspian Sea in
   ``natural_earth.land_110`` region. The differences are illustrated in a
   `notebook<notebooks/new_behavior>`.


Usage
=====
Please have a look at the tutorials.


Contents
========

.. toctree::
   :maxdepth: 2

   whats_new
   installation
   notebooks/new_behavior

.. toctree::
   :maxdepth: 2
   :caption: Defined Regions

   defined_countries
   defined_landmask
   defined_scientific


.. toctree::
   :maxdepth: 2
   :caption: Tutorials

   notebooks/plotting
   notebooks/mask_numpy
   notebooks/mask_xarray
   notebooks/mask_multidim
   notebooks/create_own_regions

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api


License
=======

regionmask is published under a MIT license.

References
==========

Region Definitions
------------------
.. [#] `Giorgi and Franciso, 2000 <http://onlinelibrary.wiley.com/doi/10.1029/1999GL011016>`__
.. [#] `Seneviratne et al., 2012 <https://www.ipcc.ch/pdf/special-reports/srex/SREX-Ch3-Supplement_FINAL.pdf>`__



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

