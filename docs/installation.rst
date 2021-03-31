Installation
============

Required dependencies
---------------------

- Python 3,6, 3.7, or 3.8.
- `numpy <http://www.numpy.org/>`__
- `rasterio <https://rasterio.readthedocs.io/>`__
- `shapely <http://toblerity.org/shapely/>`__
- `xarray <http://xarray.pydata.org/>`__
- `geopandas <http://geopandas.org/>`__


Optional dependencies
---------------------

For plotting
~~~~~~~~~~~~

- `matplotlib <http://matplotlib.org/>`__ is required to create any plots.
- `cartopy <http://scitools.org.uk/cartopy/>`__ for plotting on geographical maps and 
  for downloading natural earth data.

Instructions
------------

regionmask itself is a pure Python package, but its dependencies are not. The
easiest way to get them installed is to use conda_. The package is available
on the conda-forge channel.

.. code-block:: bash

    conda install -c conda-forge regionmask cartopy

If you don't use conda, be sure you have the required dependencies. You can
then install regionmask via pip:

.. code-block:: bash

   pip install regionmask

To run the test suite, install
`py.test <https://pytest.org>`__ and run ``py.test regionmask``.

To install the development version (master), do:

.. code-block:: bash

   pip install git+https://github.com/mathause/regionmask


.. _conda: http://conda.io/
