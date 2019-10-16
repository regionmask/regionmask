.. currentmodule:: regionmask

What's New
==========

.. ipython:: python
   :suppress:

    import regionmask

.. _whats-new.0.5.0:

v0.5.0 (unreleased)
-------------------

Breaking Changes
~~~~~~~~~~~~~~~~
 - Renamed :code:`Regions_cls` to :code:`Regions` and changed its call 
   signature. This allows to make all arguments except :code:`outlines` optional.
 - Renamed :code:`Region_cls` to :code:`_OneRegion` for clarity. 


Enhancements
~~~~~~~~~~~~
 - Make all arguments to :code:`Regions` optional (except :code:`outlines`)
   this should make it easier to create your on region definitions (closes :issue:`37`).
 - Allow to pass arbitrary iterables to :code:`Regions` - previously these had to be of
   type :code:`dict` (closes :issue:`43`).
 - Added a :code:`plot_regions` method that only plots the region borders and not a map,
   as :code:`plot`. The :code:`plot_region` function can be used to plots the regions on a
   existing cartopy map or a regular axes (closes :issue:`31`).
 - Added code coverage with pytest-cov and codecov.

Bug Fixes
~~~~~~~~~

 - Conda channel mixing breaks travis tests. Only use conda-forge, add strict
   channel priority (:issue:`27`).
 - Fix documentation compilation on readthedocs (aborted, did not display
   figures.
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
- In python 3 zip is an iterator (and not a list), thus it failed on
  :code:`mask` (:issue:`15`).
- Removed unnecessary files (ne_downloader.py and naturalearth.py).
- Resolved conflicting region outlines in the Giorgi regions (:issue:`17`).


v0.3.0 (20 September 2016)
--------------------------

- Allow passing 2 dimensional latitude and longitude grids (:issue:`8`).


v0.2.0 (5 September 2016)
-------------------------

- Add name for xarray mask (:issue:`3`). By `Mathias Hauser <https://github.com/mathause>`_.
- overhaul of the documentation
- move rtd / matplotlib handling to background

v0.1.0 (15 August 2016)
-----------------------

- first release on pypi
