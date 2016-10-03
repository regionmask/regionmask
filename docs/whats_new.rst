.. currentmodule:: regionmask

What's New
==========

v0.3.1 (unreleased)
--------------------------

Bug Fixes
~~~~~~~~~

- natural_earth was not properly imported (:issue:`10`).
- A numpy scalar of dtype integer is not `int` (i.e. isinstance(np.int32, int)
  is False). (:issue:`11`)

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
first release on pypi
