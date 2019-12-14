Installation
============

Required dependencies
---------------------

- Python 2.7, 3,6, or 3.7.
- `numpy <http://www.numpy.org/>`__
- `shapely <http://toblerity.org/shapely/>`__
- `matplotlib <http://matplotlib.org/>`__
- `xarray <http://xarray.pydata.org/>`__

For plotting on geographical maps:

- `cartopy <http://scitools.org.uk/cartopy/>`__

To open Natural Earth datasets (shapefiles):

- `geopandas <http://geopandas.org/>`__

Instructions
------------

regionmask itself is a pure Python package, but its dependencies are not. The
easiest way to get them installed is to use conda_. The package is only
avilable on the conda-forge channel.

.. code-block:: bash

    conda install -c conda-forge regionmask

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
