.. currentmodule:: regionmask

API reference
#############

This page provides an auto-generated summary of regionmask's API.


Top-level functions
===================

.. autosummary::
   :toctree: generated/

   mask_geopandas
   mask_3D_geopandas
   from_geopandas
   flatten_3D_mask
   plot_3D_mask
   set_options
   get_options

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
   Regions.mask_3D

Conversion
----------

.. autosummary::
   :toctree: generated/

   Regions.to_dataframe
   Regions.to_geodataframe
   Regions.to_geoseries
   Regions.from_geodataframe


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
