.. currentmodule:: regionmask

#############
API reference
#############

This page provides an auto-generated summary of regionmask's API.


Top-level functions
===================

.. autosummary::
   :toctree: generated/

   create_mask_contains


Regions
=======


Creating Regions
----------------

.. autosummary::
   :toctree: generated/

   Regions

Mapping Number/ Abbreviation/ Name
----------------------------------

.. autosummary::
   :toctree: generated/

   Regions.map_keys

Selecting
---------

.. autosummary::
   :toctree: generated/

   Regions.__getitem__


Plotting
--------

.. autosummary::
   :toctree: generated/

   Regions.plot
   Regions.plot_regions

Creating a Mask
---------------

.. autosummary::
   :toctree: generated/

   Regions.mask


Attributes
----------

.. autosummary::
   :toctree: generated/

   Regions.abbrevs
   Regions.names
   Regions.numbers
   Regions.region_ids
   Regions.coords
   Regions.polygons
   Regions.centroids
   Regions.bounds
   Regions.bounds_global
   Regions.lon_180
   Regions.lon_360
   Regions._is_polygon


_OneRegion
==========


Creating one Region
-------------------

.. autosummary::
   :toctree: generated/

   _OneRegion

Attributes
----------

.. autosummary::
   :toctree: generated/

   _OneRegion.coords
   _OneRegion.polygon
   _OneRegion.bounds


Private Functions
=================

.. autosummary::
   :toctree: generated/

   core.utils._wrapAngle360
   core.utils._wrapAngle180
   core.utils._wrapAngle
   core.utils._is_180

