Installation
============

Required dependencies
---------------------

- Python 2.6, 2.7, 3.3, 3.4 or 3.5.
- `numpy <http://www.numpy.org/>`__
- `shapely <http://toblerity.org/shapely/>`__

For plotting on geographical maps:

- `matplotlib <http://matplotlib.org/>`__
- `cartopy <http://scitools.org.uk/cartopy/>`__

To open Natural Earth datasets (shapefiles):

- `geopandas <http://geopandas.org/>`__

Optional dependencies
---------------------

To output `xarray` data sets:

- `xarray <http://xarray.pydata.org/>`__

Instructions
------------

regionmask itself is a pure Python package, but its dependencies are not. The
easiest way to get them installed is to use conda_. 

    $ conda install numpy cartopy xarray

If you don't use conda, be sure you have the required dependencies. You can
then install regionmask via pip (it is not (yet) available on PyPi and on
conda):

.. code-block:: bash

   pip install git+https://github.com/mathause/regionmask

To run the test suite after installing xarray, install
`py.test <https://pytest.org>`__ and run ``py.test regionmask``.


.. _conda: http://conda.io/
