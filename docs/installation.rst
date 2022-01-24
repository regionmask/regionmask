Installation
============

Required dependencies
---------------------

- Python (3.7 or later)
- `geopandas <http://geopandas.org/>`__ (v0.7 or later)
- `numpy <http://www.numpy.org/>`__ (v1.17 or later)
- `pooch <https://www.fatiando.org/pooch/latest/>`__ (v1.2 or later)
- `rasterio <https://rasterio.readthedocs.io/>`__ (v1.1 or later)
- `shapely <http://toblerity.org/shapely/>`__ (v1.7 or later)
- `xarray <http://xarray.pydata.org/>`__ (v0.15 or later)

Optional dependencies
---------------------

For plotting
~~~~~~~~~~~~

- `matplotlib <http://matplotlib.org/>`__ (v3.2 or later) is required to create any plots.
- `cartopy <http://scitools.org.uk/cartopy/>`__ (v0.18 or later) for plotting on
  geographical maps.

For faster masking
~~~~~~~~~~~~~~~~~~

- `pygeos <https://pygeos.readthedocs.io/en/stable/>`__ (v0.9 or later) enables faster mask creations for
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
