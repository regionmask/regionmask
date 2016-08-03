.. regionmask documentation master file, created by
   sphinx-quickstart on Wed Jul 20 14:36:54 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: _static/notebooks/logo.png
   :width: 500 px
   :align: center

|

************************************
create masks of geographical regions
************************************

regionmask is a Python module that:

- contains :doc:`predefined geographical regions</predefined>`:

  - from `Natural Earth <http://www.naturalearthdata.com/>`_ (countries)
  - the Giorgi regions [#]_
  - the SREX regions [#]_

- can plot figures of these regions (:doc:`tutorial</tutorials/plotting>`) with 
  `matplotlib <http://matplotlib.org/>`_ and 
  `cartopy <http://scitools.org.uk/cartopy/>`_

- can be used to create masks of geographical regions for arbitrary longitude and latitude grids

  - passing ``longitude`` and ``latitude``, an array is returned that can
    be used to select gridded data
  - the input (longitude/ latitude grid) and output (mask) can either be a `numpy <http://www.numpy.org/>`_ array (:doc:`tutorial</tutorials/mask_numpy>`) or a `xarray <http://xarray.pydata.org/>`__ object (:doc:`tutorial</tutorials/mask_xarray>`)

- arbitrary regions can be defined easily (:doc:`tutorial<tutorials/create_own_regions>`)



Usage
=====
Please have a look at the tutorials.


Contents
========

.. toctree::
   :maxdepth: 2

   installation

.. toctree::
   :maxdepth: 2
   :caption: Predefined Regions

   predefined


.. toctree::
   :maxdepth: 2
   :caption: Tutorials
   
   tutorials/plotting
   tutorials/mask_numpy
   tutorials/mask_xarray
   tutorials/create_own_regions
   
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

