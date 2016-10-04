.. currentmodule:: regionmask

What's New
==========

.. ipython:: python
   :suppress:

    import regionmask

.. _whats-new.0.3.1:

v0.3.1 (unreleased)
--------------------------

Bug Fixes
~~~~~~~~~

- travis was configured wrong - it always tested on python 2.7, thus some
  python3 issues went unnoticed (:issue:`14`).
- natural_earth was not properly imported (:issue:`10`).
- A numpy scalar of dtype integer is not `int` - i.e. `isinstance(np.int32, int)`
  is False (:issue:`11`).
- In python 3 zip is an iterator (and not a list), thus it failed on
  `mask` (:issue:`15`).
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
