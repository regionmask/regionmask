Installation
============

Required dependencies
---------------------

- Python (3.6 or later)
- `geopandas <http://geopandas.org/>`__ (0.6 or later)
- `numpy <http://www.numpy.org/>`__ (1.17 or later)
- `pooch <https://www.fatiando.org/pooch/latest/>`__ (1.0 or later)
- `rasterio <https://rasterio.readthedocs.io/>`__ (1.0 or later)
- `shapely <http://toblerity.org/shapely/>`__ (1.6 or later)
- `xarray <http://xarray.pydata.org/>`__ (0.15 or later)

Optional dependencies
---------------------

For plotting
~~~~~~~~~~~~

- `matplotlib <http://matplotlib.org/>`__ is required to create any plots.
- `cartopy <http://scitools.org.uk/cartopy/>`__ for plotting on geographical maps and
  for downloading natural earth data.

For faster masking
~~~~~~~~~~~~~~~~~~

- `pygeos <https://pygeos.readthedocs.io/en/stable/>`__ enables faster mask creations for
  irregular and 2D grids.

Instructions
------------

regionmask itself is a pure Python package, but its dependencies are not. The
easiest way to get them installed is to use conda_. The package is available
on the conda-forge channel.

.. code-block:: bash

    conda install -c conda-forge regionmask cartopy pygeos

All required dependencies can be installed with pip. You can thus install regionmask
directly:

.. code-block:: bash

   pip install regionmask

Note, however, that the optional dependency cartopy can be very difficult to install with pip.

Testing
-------

To run the test suite after installing regionmask, install `pytest <https://pytest.org>`__
and run ``pytest`` in the root directory of regionmask.

To install the development version (master), do:

.. code-block:: bash

   pip install git+https://github.com/regionmask/regionmask


.. _conda: http://conda.io/
