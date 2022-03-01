#!/usr/bin/env python

# Author: Mathias Hauser
# Date:

import copy
from collections import OrderedDict

import geopandas as gp
import numpy as np
import pandas as pd
from shapely.geometry import MultiPolygon, Polygon

from .formatting import _display
from .mask import _inject_mask_docstring, _mask_2D, _mask_3D
from .plot import _plot, _plot_regions
from .utils import _is_180, _is_numeric, _maybe_to_dict, _sanitize_names_abbrevs


class Regions:
    """
    class for plotting regions and creating region masks

    Parameters
    ----------
    outlines : iterable or dict of: Nx2 array of vertices, Polygon or MultiPolygon
        List of the coordinates of the vertices (outline) of the region as
        shapely Polygon/ MultiPolygon or list.
    numbers : iterable of int, optional
        List of numerical indices for every region. Default: range(0, len(outlines))
    names : iterable or dict of string, optional
        Long name of each region. Default: ["Region0", .., "RegionN"]
    abbrevs : iterable or dict of string, optional
        Abbreviations of each region. Default: ["r0", ..., "rN"]
    name : string, optional
        Name of the collection of regions. Default: "unnamed"
    source : string, optional
        Source of the region definitions. Default: "".
    overlap : bool, default: False
        Indicates if (some of) the regions overlap. If True ``mask_3D`` will ensure
        overlapping regions are correctly assigned to grid points while ``mask`` will
        error (because overlapping regions cannot be represented by a 2D mask).

        If False (default) assumes non-overlapping regions. Grid points will
        silently be assigned to the region with the higher number (this may change
        in a future version of regionmask).

        There is (currently) no automatic detection of overlapping regions.

    Examples
    --------
    Create your own ``Regions``::

        from regionmask import Regions

        name = 'Example'
        numbers = [0, 1]
        names = ['Unit Square1', 'Unit Square2']
        abbrevs = ['uSq1', 'uSq2']

        outl1 = ((0, 0), (0, 1), (1, 1.), (1, 0))
        outl2 = ((0, 1), (0, 2), (1, 2.), (1, 1))
        outlines = [outl1, outl2]

        r = Regions(outlines, numbers, names, abbrevs, name)

    It's also possible to pass shapely Poylgons::

        from shapely.geometry import Polygon

        numbers = [1, 2]
        names = {1:'Unit Square1', 2: 'Unit Square2'}
        abbrevs = {1:'uSq1', 2:'uSq2'}
        poly = {1: Polygon(outl1), 2: Polygon(outl2)}

        r = Regions(outlines, numbers, names, abbrevs, name)

        # arguments are now optional
        r = Regions(outlines)

    """

    def __init__(
        self,
        outlines,
        numbers=None,
        names=None,
        abbrevs=None,
        name="unnamed",
        source=None,
        overlap=False,
    ):

        if numbers is None:
            numbers = range(len(outlines))

        if not _is_numeric(numbers):
            raise ValueError("'numbers' must be numeric")

        outlines = _maybe_to_dict(numbers, outlines)

        names = _sanitize_names_abbrevs(numbers, names, "Region")
        abbrevs = _sanitize_names_abbrevs(numbers, abbrevs, "r")

        regions = OrderedDict()

        for n in sorted(numbers):
            regions[n] = _OneRegion(n, names[n], abbrevs[n], outlines[n])

        self.regions = regions
        self.name = name
        self.source = source
        self.overlap = overlap

    def __getitem__(self, key):
        """subset of Regions or Region

        Parameters
        ----------
        key : (list of) int or string
            Key can be a mixed (list of) number, abbrev or name of the
            defined regions. If a list is given returns a subset of all
            regions, if a single element is given returns this region.

        Returns
        -------
        selection : Regions or _OneRegion
            If a list is given returns a subset of all
            regions, if a single element is given returns this region.

        """

        key = self.map_keys(key)
        if isinstance(key, (int, np.integer)):
            return self.regions[key]
        else:
            # subsample the regions
            regions = OrderedDict()
            for k in key:
                regions[k] = self.regions[k]
            new_self = copy.copy(self)  # shallow copy
            new_self.regions = regions
            return new_self

    def __len__(self):
        return len(self.numbers)

    def map_keys(self, key):
        """map from names and abbrevs of the regions to numbers

        Parameters
        ----------
        key : str | list of str
            key can be a single or a list of abbreviation/ name of
            existing regions.

        Returns
        -------
        mapped_key : int or list of int
        Raises a KeyError if the key does not exist.

        """

        # a single key
        if isinstance(key, (int, np.integer, str)):
            key = self.region_ids[key]
        # a list of keys
        else:
            key = [self.region_ids[k] for k in key]
            # make sure they are unique
            key = np.unique(key).tolist()

        return key

    def __repr__(self):  # pragma: no cover
        return self._display()

    def __iter__(self):
        for i in self.numbers:
            yield self[i]

    def combiner(self, prop):
        """combines attributes from single regions"""

        return [getattr(r, prop) for r in self.regions.values()]

    @property
    def region_ids(self):
        """dictionary that maps all names and abbrevs to the region number"""

        # collect data
        abbrevs = self.abbrevs
        names = self.names
        numbers = self.numbers
        # combine data and make a mapping
        all_comb = zip(numbers + abbrevs + names, (numbers * 3))
        region_ids = {key: value for key, value in all_comb}
        return region_ids

    @property
    def abbrevs(self):
        """list of abbreviations of the regions"""
        return self.combiner("abbrev")

    @property
    def names(self):
        """list of names of the regions"""
        return self.combiner("name")

    @property
    def numbers(self):
        """list of the numbers of the regions"""
        return self.combiner("number")

    @property
    def coords(self):
        """list of coordinates of the region vertices as numpy array"""
        return self.combiner("coords")

    @property
    def polygons(self):
        """list of shapely Polygon/ MultiPolygon of the regions"""
        return self.combiner("polygon")

    @property
    def centroids(self):
        """list of the center of mass of the regions"""
        return self.combiner("centroid")

    @property
    def bounds(self):
        """list of the bounds of the regions (min_lon, min_lat, max_lon, max_lat)"""
        return self.combiner("bounds")

    @property
    def bounds_global(self):
        """global bounds over all regions (min_lon, min_lat, max_lon, max_lat)"""

        bounds = self.bounds

        xmin = min([p[0] for p in bounds])
        ymin = min([p[1] for p in bounds])
        xmax = max([p[2] for p in bounds])
        ymax = max([p[3] for p in bounds])

        return [xmin, ymin, xmax, ymax]

    @property
    def lon_180(self):
        """if the regions extend from -180 to 180"""
        lon_min = self.bounds_global[0]
        lon_max = self.bounds_global[2]

        return _is_180(lon_min, lon_max)

    @property
    def lon_360(self):
        """if the regions extend from 0 to 360"""
        return not self.lon_180

    def _display(self, max_rows=10, max_width=None, max_colwidth=50):
        """Render ``Regions`` object to a console-friendly tabular output.

        Parameters
        ----------
        max_rows : int, optional
            Maximum number of rows to display in the console. Note that this does
            not affect the displayed metadata.
        max_width : int, optional
            Width to wrap a line in characters. If none uses console width.
        max_colwidth : int, optional
            Max width to truncate each column in characters. Default 50.

        Returns
        -------
        str or None
            Returns the result as a string.

        Notes
        -----
        Used as the repr.

        """
        return _display(self, max_rows, max_width, max_colwidth)

    def mask(
        self,
        lon_or_obj,
        lat=None,
        lon_name="lon",
        lat_name="lat",
        method=None,
        wrap_lon=None,
    ):

        if self.overlap:
            raise ValueError(
                "Creating a 2D mask with overlapping regions yields wrong results. "
                "Set ``region.overlap = False`` to create a 2D mask anyway."
            )

        return _mask_2D(
            outlines=self.polygons,
            lon_bounds=self.bounds_global[::2],
            numbers=self.numbers,
            lon_or_obj=lon_or_obj,
            lat=lat,
            lon_name=lon_name,
            lat_name=lat_name,
            method=method,
            wrap_lon=wrap_lon,
        )

    mask.__doc__ = _inject_mask_docstring(is_3D=False, gp_method=False)

    def mask_3D(
        self,
        lon_or_obj,
        lat=None,
        drop=True,
        lon_name="lon",
        lat_name="lat",
        method=None,
        wrap_lon=None,
    ):

        mask_3D = _mask_3D(
            outlines=self.polygons,
            lon_bounds=self.bounds_global[::2],
            numbers=self.numbers,
            lon_or_obj=lon_or_obj,
            lat=lat,
            drop=drop,
            lon_name=lon_name,
            lat_name=lat_name,
            method=method,
            wrap_lon=wrap_lon,
            as_3D=self.overlap,
        )

        numbers = mask_3D.region.values
        abbrevs = self[numbers].abbrevs
        names = self[numbers].names

        mask_3D = mask_3D.assign_coords(
            abbrevs=("region", abbrevs), names=("region", names)
        )

        return mask_3D

    mask_3D.__doc__ = _inject_mask_docstring(is_3D=True, gp_method=False)

    def to_dataframe(self):
        """Convert this region into a pandas.DataFrame, excluding polygons.

        See Also
        --------
        from_geopandas, Regions.to_geodataframe, Regions.to_geoseries, Regions.from_geodataframe

        """

        data = dict(
            numbers=self.numbers,
            abbrevs=self.abbrevs,
            names=self.names,
        )

        df = pd.DataFrame.from_dict(data).set_index("numbers")
        return df

    def to_geodataframe(self):
        """Convert this region into a geopandas.GeoDataFrame.

        Use ``Regions.from_geodataframe`` to round-trip a geodataframe created with
        this method.

        See Also
        --------
        from_geopandas, Regions.to_dataframe, Regions.to_geoseries, Regions.from_geodataframe

        """

        data = dict(
            numbers=self.numbers,
            abbrevs=self.abbrevs,
            names=self.names,
            geometry=self.polygons,
        )

        df = gp.GeoDataFrame.from_dict(data).set_index("numbers")
        df.attrs["name"] = self.name
        df.attrs["source"] = self.source
        df.attrs["overlap"] = self.overlap

        return df

    def to_geoseries(self):
        """Convert this region into a geopandas.GeoSeries.

        See Also
        --------
        from_geopandas, Regions.to_dataframe, Regions.to_geodataframe, Regions.from_geodataframe

        """

        df = gp.GeoSeries(self.polygons, index=self.numbers)
        df.attrs["name"] = self.name
        df.attrs["source"] = self.source
        df.attrs["overlap"] = self.overlap

        return df

    @classmethod
    def from_geodataframe(cls, df, *, name=None, source=None, overlap=None):
        """
        Convert a  ``geopandas.GeoDataFrame`` created with ``to_geodataframe`` back to
        ``regionmask.Region`` (round trip)

        Parameters
        ----------
        df : geopandas.GeoDataFrame
            GeoDataFrame to be transformed to a Regions class.

        name : str, optional
            name of the Regions. If None uses ``df.attrs.get("name", "unnamed")``.

        source : str, optional
            Source of the shapefile.  If None uses ``df.attrs.get("source")``.

        overlap : bool, default: None
            Indicates if (some of) the regions overlap. If None uses
            ``df.attrs.get("overlap")``. If True ``mask_3D`` will ensure
            overlapping regions are correctly assigned to grid points while ``mask``
            will error (because overlapping regions cannot be represented by a 2D mask).

            If False assumes non-overlapping regions. Grid points will silently be
            assigned to the region with the higher number (this may change in a future
            version).

            There is (currently) no automatic detection of overlapping regions.

        Returns
        -------
        regionmask.core.regions.Regions

        See Also
        --------
        from_geopandas, Regions.to_dataframe, Regions.to_geodataframe, Regions.to_geoseries
        """

        from regionmask.core._geopandas import _from_geopandas

        if name is None:
            name = df.attrs.get("name", "unnamed")

        if source is None:
            source = df.attrs.get("source")

        if overlap is None:
            overlap = df.attrs.get("overlap", False)

        return _from_geopandas(
            df,
            numbers=None,
            names="names",
            abbrevs="abbrevs",
            name=name,
            source=source,
            overlap=overlap,
        )


# add the plotting methods
Regions.plot = _plot
Regions.plot_regions = _plot_regions


# =============================================================================


class _OneRegion:
    """a single Region, used as member of 'Regions'"""

    def __init__(self, number, name, abbrev, outline):
        """
        Parameters
        ----------
        number : int
            Number of this region.
        name : string
            Long name of this region.
        abbrev : string
            Abbreviation of this region.
        outline : Nx2 array of vertices, Polygon or MultiPolygon
            Coordinates/ outline of the region as shapely Polygon/
            MultiPolygon or list.

        Examples
        --------
        ``_OneRegion`` can be created with numpy-style outlines::

            outl = ((0, 0), (0, 1), (1, 1.), (1, 0))
            r = _OneRegion(1, 'Unit Square', 'USq', outl)

        or by passing shapely Polygons::

            from shapely.geometry import Polygon

            poly = Polygon(outl)
            r = _OneRegion(1, 'Unit Square', 'USq', poly)
        """

        self.number = number
        self.name = name
        self.abbrev = abbrev
        self._centroid = None
        self._bounds = None

        if isinstance(outline, (Polygon, MultiPolygon)):
            self._polygon = outline
            self._coords = None
        else:
            self._polygon = None
            outline = np.asarray(outline)

            if outline.ndim != 2:
                raise ValueError("Outline must be 2D")

            if outline.shape[1] != 2:
                raise ValueError("Outline must have Nx2 elements")

            self._coords = np.array(outline)

    def __repr__(self):

        klass = type(self).__name__
        return f"<regionmask.{klass}: {self.name} ({self.abbrev} / {self.number})>"

    @property
    def centroid(self):

        # the Polygon Centroid is much stabler
        if self._centroid is None:
            poly = self.polygon
            if isinstance(poly, MultiPolygon):
                # find the polygon with the largest area and assig as centroid
                area = 0
                for p in poly.geoms:
                    if p.area > area:
                        centroid = np.array(p.centroid.coords).squeeze()
                        area = p.area

                # another possibility; errors on self-intersecting polygon
                # centroid = np.array(poly.representative_point().coords).squeeze()
            else:
                centroid = np.array(poly.centroid.coords).squeeze()

            self._centroid = centroid

        return self._centroid

    @property
    def polygon(self):
        """shapely Polygon or MultiPolygon of the region"""

        if self._polygon is None:
            self._polygon = Polygon(self.coords)
        return self._polygon

    @property
    def coords(self):
        """numpy array of the region"""

        if self._coords is None:

            # make an array of polygons
            if isinstance(self._polygon, Polygon):
                polys = [self._polygon]
            else:
                polys = list(self._polygon.geoms)

            # separate the single polygons with NaNs
            nan = np.full((1, 2), np.nan)
            lst = [np.vstack((np.array(poly.exterior.coords), nan)) for poly in polys]

            # remove the very last NaN
            self._coords = np.vstack(lst)[:-1, :]

        return self._coords

    @property
    def bounds(self):
        """bounds of the regions ((Multi)Polygon.bounds (min_lon, min_lat, max_lon, max_lat)"""
        if self._bounds is None:
            self._bounds = self.polygon.bounds
        return self._bounds
