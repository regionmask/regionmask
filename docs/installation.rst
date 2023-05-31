Installation
============

Required dependencies
---------------------

- Python (3.8 or later)
- `geopandas <http://geopandas.org/>`__ (0.10 or later)
- `numpy <http://www.numpy.org/>`__ (1.21 or later)
- `packaging <https://packaging.pypa.io/en/latest/>`__ (21.3 or later)
- `pooch <https://www.fatiando.org/pooch/latest/>`__ (1.4 or later)
- `rasterio <https://rasterio.readthedocs.io/>`__ (1.2 or later)
- `shapely <http://toblerity.org/shapely/>`__ (1.8 or later)
- `xarray <http://xarray.pydata.org/>`__ (0.20 or later)

Optional dependencies
---------------------

For plotting
~~~~~~~~~~~~

- `matplotlib <http://matplotlib.org/>`__ (3.5 or later) is required to create any plots.
- `cartopy <http://scitools.org.uk/cartopy/>`__ (0.20 or later) for plotting on
  geographical maps.

For detecting coords and parsing flag values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `cf_xarray <https://cf-xarray.readthedocs.io/en/latest/>`__ (0.7 or later) allows
  to autodetect coordidate names and rich comparison of abbreviations or names of regions
  for 2D masks via ``mask.cf``.

For faster loading of shapefiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `pyogrio <https://pyogrio.readthedocs.io>`__ (0.3 or later) allows faster reading of
  shapefiles. Currently only used for natural earth data (as the other data is loaded
  reasonanbly fast with fiona).

Instructions
------------

regionmask itself is a pure Python package, but its dependencies are not. The
easiest way to get them installed is to use conda_. The package is available
on the conda-forge channel.

.. code-block:: bash

    conda install -c conda-forge regionmask cartopy

All required dependencies can be installed with pip. You can thus install regionmask
directly:

.. code-block:: bash

   pip install regionmask

Note, however, that the optional dependency cartopy can be very difficult to install with pip.

Testing
-------

To run the test suite after installing regionmask, install `pytest <https://pytest.org>`__
and run ``pytest`` in the root directory of regionmask.

To install the development version (main), do:

.. code-block:: bash

   pip install git+https://github.com/regionmask/regionmask


.. _conda: http://conda.io/
