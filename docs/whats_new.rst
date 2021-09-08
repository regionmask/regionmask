.. currentmodule:: regionmask

What's New
==========

.. ipython:: python
   :suppress:

    import regionmask

.. _whats-new.0.8.0:

v0.8.0 (08.09.2021)
-------------------

Version 0.8.0 contains an important bugfix, improves the handling of wrapped longitudes,
can create masks for coordinates and regions that do not have a lat/ lon coordinate
reference system and masks for irregular and 2D grids are created faster if the optional
dependency `pygeos <https://pygeos.readthedocs.io/en/stable/>`__ is installed.

Breaking Changes
~~~~~~~~~~~~~~~~

- Points at *exactly* -180°E (or 0°E) and -90°N are no longer special cased if
  ``wrap_lon=False`` when creating a mask - see :doc:`methods<notebooks/method>` for
  details (:issue:`151`).
- Updates to :py:meth:`Regions.plot` and :py:meth:`Regions.plot_regions` (:pull:`246`):

  - Deprecated all positional arguments (keword arguments only).
  - The ``regions`` keyword was deprecated. Subset regions before plotting, i.e.
    use ``r[regions].plot()`` instead of ``r.plot(regions=regions)``. This will allow
    to remove a argument from the methods.
- Updates to :py:meth:`Regions.plot` (:pull:`246`):

  - Added ``lw=0`` to the default ``ocean_kws`` and ``land_kws`` to avoid overlap with
    the coastlines.
  - Renamed the ``proj`` keyword to ``projection`` for consistency with cartopy.
  - Renamed the ``coastlines`` keyword to ``add_coastlines`` for consistency with other
    keywords (e.g. ``add_land``).

Enhancements
~~~~~~~~~~~~

- Creating masks for irregular and 2D grids can be speed up considerably by installing
  `pygeos <https://pygeos.readthedocs.io/en/stable/>`__. pygeos is an optional dependency
  (:issue:`123`).
- Can now create masks for regions with arbitrary coordinates e.g. for coordinate reference
  systems that are not lat/ lon based by setting ``wrap_lon=False`` (:issue:`151`).
- The extent of the longitude coordinates is no longer checked to determine the wrap,
  now only the extent of the mask is considered (:issue:`249`). This should allow to
  infer ``wrap_lon`` correctly for more cases (:issue:`213`).

Bug Fixes
~~~~~~~~~

- Fixed a bug that could silently lead to a wrong mask in certain cases. Three conditions are
  required:

  1. The longitude coordinates are not ordered (note that wrapping the longitudes can
     also lead to unordered coordinates).
  2. Rearranging the coordinates makes them equally spaced.
  3. The split point is not in the middle of the array.

  Thus, the issue would happen for the following example longitude coordinates: ``[3, 4, 5, 1, 2]``
  (but not for ``[3, 4, 1, 2]``). Before the bugfix the mask would incorrectly be rearranged
  in the following order ``[4, 5, 1, 2, 3]`` (:issue:`266`).

- :py:meth:`Regions.mask` (and all other ``mask`` methods and functions) no longer raise
  an error for regions that exceed 360° latitude if ``wrap_lon=False``. This was most
  likely a regression from :pull:`48` (:issue:`151`).
- Raise a ValueError if the input coordinates (lat and lon) have wrong number of dimensions
  or shape (:pull:`245`, :issue:`242`).

Docs
~~~~

- Updated the plotting tutorial (:pull:`246`).
- Install `regionmask` via `ci/requirements/docs.yml` on RTD using pip and update the
  packages: don't require jupyter (but ipykernel, which leads to a smaller environment),
  use new versions of sphinx and sphinx_rtd_theme (:pull:`248`).
- Pin cartopy to version 0.19 and matplotlib to version 3.4 and use a (temorary) fix for
  :issue:`165`. This allows to make use of `conda-forge/cartopy-feedstock#116
  <https://github.com/conda-forge/cartopy-feedstock/pull/116>`__ such that natural_earth
  shapefiles can be donwloaded again. Also added some other minor doc updates
  (:pull:`269`).

Internal Changes
~~~~~~~~~~~~~~~~

- Updated setup configuration and automated version numbering:

  - Moved contents of setup.py to setup.cfg (:pull:`240`).
  - Use ``pyproject.toml`` to define the installation requirements (:pull:`240`, :pull:`247`).
  - Use setuptools-scm for automatic versioning (:pull:`240`).
  - Allow installing from git archives (:pull:`240`).
- Refactor ``test_defined_region`` and ``test_mask_equal_defined_regions`` - globally
  define a list of all available `defined_regions` (:issue:`256`).
- In the tests: downloading naturalearth regions could run forever. Make sure this does
  not happen and turn the timeout Error into a warning (:pull:`261`).
- Set ``regex=True`` in ``pd.Series.str.replace`` due to an upcoming change in pandas (:pull:`262`).

v0.7.0 (28.07.2021)
-------------------

Version 0.7.0 is mostly a maintenance version. It drops python 2.7 support, accompanies
the move of the repo to the regionmask organisation (`regionmask/regionmask <http://github.com/regionmask/regionmask>`__),
finalizes a number of deprecations, and restores compatibility with xarray 0.19.


Breaking Changes
~~~~~~~~~~~~~~~~

- Removed support for Python 2. This is the first version of regionmask that is Python 3 only!

- The minimum versions of some dependencies were changed (:pull:`220`):

  ============ ===== =====
  Package      Old   New
  ============ ===== =====
  numpy        1.15  1.17
  xarray       0.13  0.15
  ============ ===== =====

- Moved regionmask to its own organisation on github. It can now be found under
  `regionmask/regionmask <http://github.com/regionmask/regionmask>`__ (:issue:`204` and
  :pull:`224`).

- matpoltlib and cartopy are now optional dependencies. Note that cartopy is also
  required to download and access the natural earth shapefiles (:issue:`169`).

Deprecations
~~~~~~~~~~~~

- Removed ``Regions_cls`` and ``Region_cls`` (deprecated in v0.5.0). Use
  :py:class:`Regions` instead (:pull:`182`).
- Removed the ``create_mask_contains`` function (deprecated in v0.5.0). Use
  ``regionmask.Regions(coords).mask(lon, lat)`` instead (:pull:`181`).
- Removed the ``xarray`` keyword to all ``mask`` functions. This was deprecated in
  version 0.5.0. To obtain a numpy mask use ``mask.values`` (:issue:`179`).
- Removed the ``"legacy"``-masking deprecated in v0.5.0 (:issue:`69`, :pull:`183`).

Enhancements
~~~~~~~~~~~~

- :py:attr:`Regions.plot()` and :py:attr:`Regions.plot_regions()` now take the
  ``label_multipolygon`` keyword to add text labels to all Polygons of
  MultiPolygons (:issue:`185`).
- :py:attr:`Regions.plot()` and :py:attr:`Regions.plot_regions()` now warn on unused arguments,
  e.g. ``plot(add_land=False, land_kws=dict(color="g"))`` (:issue:`192`).

New regions
~~~~~~~~~~~
- Added :py:attr:`natural_earth.land_10` and :py:attr:`natural_earth.land_50` regions from
  natural earth (:pull:`195`) by `Martin van Driel <https://github.com/martinvandriel>`_.

Bug Fixes
~~~~~~~~~

- Text labels outside of the map area should now be correctly clipped in most cases
  (:issue:`157`).
- Move ``_flatten_polygons`` to ``utils`` and raise an error when something else than
  a ``Polygon`` or ``MultiPolygon`` is passed (:pull:`211`).
- Fix incompatibility with xarray >=0.19.0 (:pull:`234`). By `Julius Busecke <https://github.com/jbusecke>`_.

Docs
~~~~

- Unified the docstrings of all ``mask`` functions (:issue:`173`).
- Mentioned how to calculate regional medians (:issue:`170`).
- Mentioned how to open regions specified in a yaml file using intake and fsspec
  (:issue:`93`, :pull:`205`). By `Aaron Spring <https://github.com/aaronspring>`_.
- Fixed the docstrings using `velin  <https://github.com/Carreau/velin>`__  (:pull:`231`).

Internal Changes
~~~~~~~~~~~~~~~~

- Moved the CI from azure to github actions (after moving to the regionmask organisation)
  (:pull:`232`).
- Update the CI: use mamba for faster installation, merge code coverage from all runs,
  don't check the coverage of the tests (:pull:`197`).
- Fix doc creation for newest version of ``jupyter nbconvert`` (``template`` is now
  ``template-file``).
- Update ``ci/min_deps_check.py`` to the newest version on xarray (:pull:`218`).
- Add a test environment for python 3.9 (:issue:`215`).
- Enforce minimum versions in `requirements.txt` and clean up required dependencies
  (:issue:`199` and :pull:`219`).

v0.6.2 (19.01.2021)
-------------------

This is a minor bugfix release that corrects a problem occurring only in python 2.7 which
could lead to wrong coordinates of 3D masks derived with :py:meth:`Regions.mask_3D` and
:py:func:`mask_3D_geopandas`.

Bug Fixes
~~~~~~~~~

- Make sure ``Regions`` is sorted by the number of the individual regions. This was
  previously not always the case. Either when creating regions with unsorted numbers
  in python 3.6 and higher (e.g. ``Regions([poly2, poly1], [2, 1])``) or when indexing
  regions in python 2.7 (e.g. ``regionmask.defined_regions.ar6.land[[30, 31, 32]]`` sorts
  the regions as 32, 30, 31). This can lead to problems for :py:meth:`Regions.mask_3D` and
  :py:func:`mask_3D_geopandas` (:issue:`200`).

v0.6.1 (19.08.2020)
-------------------

There were some last updates to the AR6 regions (``regionmask.defined_regions.ar6``).
If you use the AR6 regions please update the package. There were no functional changes.

v0.6.0 (30.07.2020)
-------------------

.. warning::

  This is the last release of regionmask that will support Python 2.7. Future releases
  will be Python 3 only, but older versions of regionmask will always be available
  for Python 2.7 users. For the more details, see:

  - `Python 3 Statement <http://www.python3statement.org/>`__

Version 0.6.0 offers better support for shapefiles (via `geopandas
<https://geopandas.readthedocs.io>`__) and can directly create 3D boolean masks
which play nicely with xarray's ``weighted.mean(...)`` function. It also includes
a number of optimizations and bug fixes.


Breaking Changes
~~~~~~~~~~~~~~~~

- Points at *exactly* -180°E (or 0°E) and -90°N are now treated separately; such that a global
  mask includes all gridpoints - see :doc:`methods<notebooks/method>` for details (:issue:`159`).
- :py:attr:`Regions.plot()` no longer colors the ocean per default. Use
  :py:attr:`Regions.plot(add_ocean=True)` to restore the previous behavior (:issue:`58`).
- Changed the default style of the coastlines in :py:attr:`Regions.plot()`. To restore
  the previous behavior use :py:attr:`Regions.plot(coastline_kws=dict())` (:pull:`146`).

Enhancements
~~~~~~~~~~~~

- Create 3D boolean masks using :py:meth:`Regions.mask_3D` and :py:func:`mask_3D_geopandas`
  - see the :doc:`tutorial on 3D masks<notebooks/mask_3D>` (:issue:`4`, :issue:`73`).
- Create regions from geopandas/ shapefiles :py:attr:`from_geopandas`
  (:pull:`101` by `Aaron Spring <https://github.com/aaronspring>`_).
- Directly mask geopandas GeoDataFrame and GeoSeries :py:attr:`mask_geopandas` (:pull:`103`).
- Added a convenience function to plot flattened 3D masks: :py:func:`plot_3D_mask` (:issue:`161`).
- :py:attr:`Regions.plot` and :py:attr:`Regions.plot_regions` now also displays region interiors.
  All lines are now added at once using a ``LineCollection`` which is faster than
  a loop and ``plt.plot`` (:issue:`56` and :issue:`107`).
- :py:attr:`Regions.plot` can now fill land areas with ``add_land``. Further, there is more
  control over the appearance over the land and ocean features as well as the coastlines
  using the ``coastline_kws``, ``ocean_kws``, and ``land_kws`` arguments (:issue:`140`).
- Split longitude if this leads to two equally-spaced parts. This can considerably speed up
  creating a mask. See :issue:`127` for details.
- Added test to ensure ``Polygons`` with z-coordinates work correctly (:issue:`36`).
- Better repr for :py:class:`Regions` (:issue:`108`).
- Towards enabling the download of region definitions using `pooch <https://www.fatiando.org/pooch/>`_
  (:pull:`61`).

New regions
~~~~~~~~~~~

- Added the AR6 reference regions described in `Iturbide et al., (2000)
  <https://essd.copernicus.org/preprints/essd-2019-258/>`_ (:pull:`61`).
- New marine regions from natural earth added as :py:attr:`natural_earth.ocean_basins_50`
  (:pull:`63` by `Julius Busecke <https://github.com/jbusecke>`_).

Bug Fixes
~~~~~~~~~

- The natural earth shapefiles are now loaded with ``encoding="utf8"`` (:issue:`95`).
- Explicitly check that the numbers are numeric and raise an informative error (:issue:`130`).
- Do not subset coords with more than 10 vertices when plotting regions as this
  can be slow (:issue:`153`).

Internal Changes
~~~~~~~~~~~~~~~~

- Decouple ``_maybe_get_column`` from its usage for naturalearth - so it can be
  used to read columns from geodataframes (:issue:`117`).
- Switch to azure pipelines for testing (:pull:`110`).
- Enable codecov on azure (:pull:`115`).
- Install ``matplotlib-base`` for testing instead of ``matplotlib`` for tests,
  seems a bit faster (:issue:`112`).
- Replaced all ``assertion`` with ``if ...: ValueError`` outside of tests (:issue:`142`).
- Raise consistent warnings on empty mask (:issue:`141`).
- Use a context manager for the plotting tests (:issue:`145`).

Docs
~~~~

- Combine the masking tutorials (xarray, numpy, and multidimensional coordinates)
  into one (:issue:`120`).
- Use ``sphinx.ext.napoleon`` which fixes the look of the API docs. Also some
  small adjustments to the docs (:pull:`125`).
- Set ``mpl.rcParams["savefig.bbox"] = "tight"`` in ``docs/defined_*.rst`` to avoid
  spurious borders in the map plots (:issue:`112`).

v0.5.0 (19.12.2019)
-------------------

Version 0.5.0 offers a better performance, a consistent point-on-border behavior,
and also unmasks region interiors (holes). It also introduces a number of
deprecations. Please check the notebook on :doc:`methods<notebooks/method>` and
the details below.


Breaking Changes
~~~~~~~~~~~~~~~~

 - :doc:`New behavior<notebooks/method>` for 'point-on-border' and region interiors:

   - New 'edge behaviour': points that fall on the border of a region are now
     treated consistently (:pull:`63`). Previously the edge behaviour was
     not well defined and depended on the orientation of the outline (clockwise
     vs. counter clockwise; :issue:`69` and `matplotlib/matplotlib#9704 <https://github.com/matplotlib/matplotlib/issues/9704>`_).

   - Holes in regions are now excluded from the mask; previously they were included.
     For the :code:`defined_regions`, this is relevant for the Caspian Sea in the
     :py:attr:`naturalearth.land110` region and also for some countries in
     :py:attr:`naturalearth.countries_50` (closes :issue:`22`).

 - Renamed :py:class:`Regions_cls` to :py:class:`Regions` and changed its call
   signature. This allows to make all arguments except :code:`outlines` optional.
 - Renamed :py:class:`Region_cls` to :py:class:`_OneRegion` for clarity.
 - Deprecated the :code:`centroids` keyword for :py:class:`Regions` (:issue:`51`).
 - `xarray <http://xarray.pydata.org>`_ is now a hard dependency (:issue:`64`).
 - The function :py:func:`regionmask.create_mask_contains` is deprecated and will be
   removed in a future version. Use ``regionmask.Regions(coords).mask(lon, lat)``
   instead.

Enhancements
~~~~~~~~~~~~

 - New faster and consistent methods to rasterize regions:

   - New algorithm to rasterize regions for equally-spaced longitude/ latitude grids.
     Uses ``rasterio.features.rasterize``: this offers a 50x to 100x speedup compared
     to the old method, and also has consistent edge behavior (closes :issue:`22` and
     :issue:`24`).
   - New algorithm to rasterize regions for grids that are not equally-spaced.
     Uses ``shapely.vectorized.contains``: this offers a 2x to 50x speedup compared
     to the old method. To achieve the same edge-behavior a tiny (10 ** -9) offset
     is subtracted from lon and lat (closes :issue:`22` and :issue:`62`).
   - Added a :doc:`methods page<notebooks/method>` to the documentation, illustrating
     the algorithms, the edge behavior and treatment of holes (closes :issue:`16`).
   - Added a test to ensure that the two new algorithms ("rasterize", "shapely")
     yield the same result. Currently for 1° and 2° grid spacing (:issue:`74`).

 - Automatically detect whether the longitude of the grid needs to be wrapped,
   depending on the extent of the grid and the regions (closes :issue:`34`).
 - Make all arguments to :py:class:`Regions` optional (except :code:`outlines`)
   this should make it easier to create your own region definitions (closes :issue:`37`).
 - Allow to pass arbitrary iterables to :py:class:`Regions` - previously these had to be of
   type :code:`dict` (closes :issue:`43`).
 - Added a :py:meth:`Regions.plot_regions` method that only plots the region borders
   and not a map, as :py:meth:`Regions.plot`. The :py:meth:`Regions.plot_regions`
   method can be used to plot the regions on a existing :code:`cartopy` map or a
   regular axes (closes :issue:`31`).
 - Added :py:attr:`Regions.bounds` and :py:attr:`Regions.bounds_global`
   indicating the minimum bounding region of each and all regions, respectively.
   Added :py:attr:`_OneRegion.bounds` (closes :issue:`33`).
 - Add possibility to create an example dataset containing lon, lat and their
   bounds (closes :issue:`66`).
 - Added code coverage with pytest-cov and codecov.

Bug Fixes
~~~~~~~~~

 - Regions were missing a line when the coords were not closed and
   :code:`subsample=False`  (:issue:`46`).
 - Fix a regression introduced by :pull:`47`: when plotting regions containing
   multipolygons :code:`_draw_poly` closed the region again and introduced a spurious
   line (closes :issue:`54`).
 - For a region defined via :code:`MultiPolygon`: use the centroid of the largest
   :code:`Polygon` to add the label on a map. Previously the label could be placed
   outside of the region (closes :issue:`59`).
 - Fix regression: the offset was subtracted in ``mask.lon`` and ``mask.lat``;
   test ``np.all(np.equal(mask.lon, lon))``, instead of ``np.allclose`` (closes
   :issue:`78`).
 - Rasterizing with ``"rasterize"`` and ``"shapely"`` was not equal when gridpoints
   exactly fall on a 45° border outline (:issue:`80`).
 - Conda channel mixing breaks travis tests. Only use conda-forge, add strict
   channel priority (:issue:`27`).
 - Fix documentation compilation on readthedocs (aborted, did not display
   figures).
 - Fix wrong figure in docs: countries showed landmask (:issue:`39`).

v0.4.0 (02.03.2018)
-------------------

Enhancements
~~~~~~~~~~~~

- Add landmask/ land 110m from `Natural Earth <http://www.naturalearthdata.com/downloads/110m-physical-vectors/>`_ (:issue:`21`).
- Moved some imports to functions, so :code:`import regionmask` is faster.
- Adapted docs for python 3.6.

Bug Fixes
~~~~~~~~~

- Columns of geodataframes can be in lower ('name') or upper case ('NAME') (:issue:`25`).
- Links to github issues not working, due to missing sphinx.ext.extlinks (:issue:`26`).
- Docs: mask_xarray.ipynb: mask no longer needs a name (as of :pull:`5`).

v0.3.1 (4 October 2016)
-----------------------

This is a bugfix/ cleanup release.

Bug Fixes
~~~~~~~~~

- travis was configured wrong - it always tested on python 2.7, thus some
  python3 issues went unnoticed (:issue:`14`).
- natural_earth was not properly imported (:issue:`10`).
- A numpy scalar of dtype integer is not :code:`int` - i.e. :code:`isinstance(np.int32, int)`
  is False (:issue:`11`).
- In python 3 :code:`zip` is an iterator (and not a :code:`list`), thus it failed on
  :code:`mask` (:issue:`15`).
- Removed unnecessary files (ne_downloader.py and naturalearth.py).
- Resolved conflicting region outlines in the Giorgi regions (:issue:`17`).


v0.3.0 (20 September 2016)
--------------------------

- Allow passing 2 dimensional latitude and longitude grids (:issue:`8`).


v0.2.0 (5 September 2016)
-------------------------

- Add name for xarray mask (:issue:`3`).
- overhaul of the documentation
- move rtd / matplotlib handling to background

v0.1.0 (15 August 2016)
-----------------------

- first release on pypi
