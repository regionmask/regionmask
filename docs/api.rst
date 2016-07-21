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


Regions_cls
===========


Creating Regions
----------------

.. autosummary::
   :toctree: generated/

   Regions_cls

Mapping Number/ Abbreviation/ Name 
----------------------------------

.. autosummary::
   :toctree: generated/

   Regions_cls.map_keys

Selecting 
---------

.. autosummary::
   :toctree: generated/

   Regions_cls.__getitem__


Plotting
--------

.. autosummary::
   :toctree: generated/

   Regions_cls.plot

Creating a Mask
---------------

.. autosummary::
   :toctree: generated/

   Regions_cls.mask


Attributes
----------

.. autosummary::
   :toctree: generated/

   Regions_cls.abbrevs
   Regions_cls.names
   Regions_cls.numbers
   Regions_cls.region_ids
   Regions_cls.coords
   Regions_cls.polygons
   Regions_cls.centroids
   Regions_cls._is_polygon


Region_cls
===========


Creating one Region
-------------------

.. autosummary::
   :toctree: generated/

   Region_cls

Attributes
----------

.. autosummary::
   :toctree: generated/

   Region_cls.coords
   Region_cls.polygon

Private Functions
=================

.. autosummary::
   :toctree: generated/

   _wrapAngle360
   _wrapAngle180
   _wrapAngle
