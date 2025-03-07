from __future__ import annotations

import copy
import warnings
from collections.abc import Iterable
from typing import Literal, overload

import geopandas as gp
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import MultiPolygon, Polygon

from regionmask.core.formatting import _display
from regionmask.core.mask import (
    _inject_mask_docstring,
    _mask_2D,
    _mask_3D,
    _mask_3D_frac_approx,
)
from regionmask.core.plot import _plot, _plot_regions
from regionmask.core.utils import (
    _is_180,
    _is_numeric,
    _maybe_to_dict,
    _sanitize_names_abbrevs,
    _total_bounds,
)


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
    overlap : bool | None, default: None
        Indicates if (some of) the regions overlap  and determines the behaviour of the
        ``mask`` methods.

        - If True ``Regions.mask_3D`` ensures overlapping regions are correctly assigned
          to grid points, while ``Regions.mask`` raises an Error  (because overlapping
          regions cannot be represented by a 2D mask).
        - If False assumes non-overlapping regions. Grid points are silently assigned to
          the region with the higher number.
        - If None (default) checks if any gridpoint belongs to more than one region.
          If this is the case ``Regions.mask_3D`` correctly assigns them and
          ``Regions.mask`` raises an Error.

    Examples
    --------
    Create your own ``Regions``::

    >>> from regionmask import Regions

    >>> name = 'Example'
    >>> numbers = [0, 1]
    >>> names = ['Unit Square1', 'Unit Square2']
    >>> abbrevs = ['uSq1', 'uSq2']

    >>> outl1 = ((0, 0), (0, 1), (1, 1.), (1, 0))
    >>> outl2 = ((0, 1), (0, 2), (1, 2.), (1, 1))
    >>> outlines = [outl1, outl2]

    >>> r = Regions(outlines, numbers, names, abbrevs, name)
    >>> r
    <regionmask.Regions 'Example'>
    overlap:  None
    <BLANKLINE>
    Regions:
    0 uSq1 Unit Square1
    1 uSq2 Unit Square2
    <BLANKLINE>
    [2 regions]

    It's also possible to pass shapely Poylgons::

    >>> from shapely.geometry import Polygon

    >>> numbers = [1, 2]
    >>> names = {1:'Unit Square1', 2: 'Unit Square2'}
    >>> abbrevs = {1:'uSq1', 2:'uSq2'}
    >>> poly = {1: Polygon(outl1), 2: Polygon(outl2)}

    >>> r = Regions(outlines, numbers, names, abbrevs, name)
    >>> r
    <regionmask.Regions 'Example'>
    overlap:  None
    <BLANKLINE>
    Regions:
    1 uSq1 Unit Square1
    2 uSq2 Unit Square2
    <BLANKLINE>
    [2 regions]

    >>> # arguments are now optional
    >>> r = Regions(outlines)
    >>> r
    <regionmask.Regions 'unnamed'>
    overlap:  None
    <BLANKLINE>
    Regions:
    0 r0 Region0
    1 r1 Region1
    <BLANKLINE>
    [2 regions]
    """

    def __init__(
        self,
        outlines,
        numbers=None,
        names=None,
        abbrevs=None,
        name: str = "unnamed",
        source: str | None = None,
        overlap: bool | None = None,
    ) -> None:

        if isinstance(outlines, np.ndarray | Polygon | MultiPolygon):
            klass = type(outlines).__name__
            raise ValueError(
                f"Cannot pass a single {klass} as region - please pass it as a list."
            )

        if numbers is None:
            numbers = range(len(outlines))

        if not _is_numeric(numbers):
            raise ValueError("'numbers' must be numeric")

        outlines = _maybe_to_dict(numbers, outlines)

        names = _sanitize_names_abbrevs(numbers, names, "Region")
        abbrevs = _sanitize_names_abbrevs(numbers, abbrevs, "r")

        regions = {
            n: _OneRegion(n, names[n], abbrevs[n], outlines[n]) for n in sorted(numbers)
        }

        self.regions: dict[int, _OneRegion] = regions
        self.name: str = name
        self.source: str | None = source
        self.overlap: bool | None = overlap

    @overload
    def __getitem__(self, key: int) -> _OneRegion: ...

    @overload
    def __getitem__(self, key: str) -> _OneRegion: ...

    @overload
    def __getitem__(self, key: Iterable) -> Regions: ...

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
        if np.ndim(key) == 0:
            return self.regions[key]
        else:
            # subsample the regions
            regions = {k: self.regions[k] for k in key}
            new_self = copy.copy(self)  # shallow copy
            new_self.regions = regions
            return new_self

    def __len__(self) -> int:
        return len(self.regions)

    def map_keys(self, key) -> int | list[int]:
        """map from names and abbrevs of the regions to numbers

        Parameters
        ----------
        key : str | list of str
            key can be a single or a list of abbreviation/ name of
            existing regions.

        Returns
        -------
        mapped_key : int or list of int

        Raises
        ------
        KeyError if the key does not exist.

        """

        _region_ids = self._region_ids

        # a single key
        if np.ndim(key) == 0:
            key = _region_ids[key]
        # a list of keys
        else:
            key = [_region_ids[k] for k in key]
            # make sure they are unique
            key = np.unique(key).tolist()

        return key

    def __iter__(self):
        yield from self.regions.values()

    @property
    def region_ids(self):
        """dictionary that maps all names and abbrevs to the region number"""

        warnings.warn(
            "`Regions.region_ids` has been made private in v0.13.0 and will be removed",
            FutureWarning,
            stacklevel=2,
        )

        return self._region_ids

    @property
    def _region_ids(self) -> dict[str | int, int]:
        """dictionary that maps all names and abbrevs to the region number"""

        # collect data
        abbrevs = self.abbrevs
        names = self.names
        numbers = self.numbers
        # combine data and make a mapping
        keys: list[int | str] = abbrevs + names + numbers
        all_comb = zip(keys, numbers * 3)
        region_ids = {key: value for key, value in all_comb}
        return region_ids

    @property
    def abbrevs(self) -> list[str]:
        """list of abbreviations of the regions"""
        return [r.abbrev for r in self.regions.values()]

    @property
    def names(self) -> list[str]:
        """list of names of the regions"""
        return [r.name for r in self.regions.values()]

    @property
    def numbers(self) -> list[int]:
        """list of the numbers of the regions"""
        return [r.number for r in self.regions.values()]

    @property
    def coords(self):
        """list of coordinates of the region vertices as numpy array"""

        warnings.warn(
            "`Regions.coords` has been deprecated in v0.12.0 and will be removed. "
            "Please raise an issue if you have an use case for them.",
            FutureWarning,
            stacklevel=2,
        )

        return [r.coords for r in self.regions.values()]

    @property
    def polygons(self) -> list[Polygon | MultiPolygon]:
        """list of shapely Polygon/ MultiPolygon of the regions"""
        return [r.polygon for r in self.regions.values()]

    @property
    def centroids(self) -> list[np.ndarray]:
        """list of the center of mass of the regions"""
        return [r.centroid for r in self.regions.values()]

    @property
    def bounds(self) -> list[tuple[float, float, float, float]]:
        """list of the bounds of the regions (min_lon, min_lat, max_lon, max_lat)"""
        return [r.bounds for r in self.regions.values()]

    @property
    def bounds_global(self) -> np.ndarray:
        """global bounds over all regions (min_lon, min_lat, max_lon, max_lat)"""

        return _total_bounds(self.polygons)

    @property
    def lon_180(self) -> bool:
        """if the regions extend from -180 to 180"""
        lon_min, __, lon_max, __ = self.bounds_global

        return _is_180(lon_min, lon_max)

    @property
    def lon_360(self) -> bool:
        """if the regions extend from 0 to 360"""
        return not self.lon_180

    def _display(self, max_rows: int = 10, max_width: int | None = None) -> str:
        """Render ``Regions`` object to a console-friendly tabular output.

        Parameters
        ----------
        max_rows : int, optional
            Maximum number of rows to display in the console. Note that this does
            not affect the displayed metadata.
        max_width : int, optional
            Width to wrap a line in characters. If none uses console width.

        Returns
        -------
        str or None
            Returns the result as a string.

        Notes
        -----
        Used as the repr.

        """
        return _display(self, max_rows, max_width)

    def __repr__(self) -> str:  # pragma: no cover
        from regionmask.core.options import OPTIONS

        max_rows = OPTIONS["display_max_rows"]

        return self._display(max_rows=max_rows)

    def mask(
        self,
        lon_or_obj: np.typing.ArrayLike | xr.DataArray | xr.Dataset,
        lat: np.typing.ArrayLike | xr.DataArray | None = None,
        *,
        method=None,
        wrap_lon: None | bool | Literal[180, 360] = None,
        flag: Literal["abbrevs", "names"] | None = "abbrevs",
        use_cf: bool | None = None,
    ) -> xr.DataArray:

        if self.overlap:
            raise ValueError(
                "Creating a 2D mask with overlapping regions yields wrong results. "
                "Please use ``region.mask_3D(...)`` instead. "
                "To create a 2D mask anyway, set ``region.overlap = False``."
            )

        mask_2D = _mask_2D(
            polygons=self.polygons,
            numbers=self.numbers,
            lon_or_obj=lon_or_obj,
            lat=lat,
            method=method,
            wrap_lon=wrap_lon,
            use_cf=use_cf,
            overlap=self.overlap,
        )

        if flag not in [None, "abbrevs", "names"]:
            raise ValueError(
                f"`flag` must be one of `None`, `'abbrevs'` and `'names'`, found {flag}"
            )

        if flag is not None:
            # see http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#flags

            # find detected regions (assign ALL regions?)
            isnan = np.isnan(mask_2D.values)
            numbers = np.unique(mask_2D.values[~isnan])
            numbers = numbers.astype(int)

            flag_meanings = getattr(self[numbers], flag)
            # TODO: check for invalid characters
            flag_meanings = " ".join(flag.replace(" ", "_") for flag in flag_meanings)

            mask_2D.attrs["flag_values"] = numbers
            mask_2D.attrs["flag_meanings"] = flag_meanings

        return mask_2D

    mask.__doc__ = _inject_mask_docstring(which="2D", is_gpd=False)

    def mask_3D(
        self,
        lon_or_obj: np.typing.ArrayLike | xr.DataArray | xr.Dataset,
        lat: np.typing.ArrayLike | xr.DataArray | None = None,
        *,
        drop: bool = True,
        method=None,
        wrap_lon: None | bool | Literal[180, 360] = None,
        use_cf: bool | None = None,
    ) -> xr.DataArray:

        mask_3D = _mask_3D(
            polygons=self.polygons,
            numbers=self.numbers,
            lon_or_obj=lon_or_obj,
            lat=lat,
            drop=drop,
            method=method,
            wrap_lon=wrap_lon,
            overlap=self.overlap,
            use_cf=use_cf,
        )

        numbers = mask_3D.region.values
        abbrevs = self[numbers].abbrevs
        names = self[numbers].names

        mask_3D = mask_3D.assign_coords(
            abbrevs=("region", abbrevs), names=("region", names)
        )

        return mask_3D

    mask_3D.__doc__ = _inject_mask_docstring(which="3D", is_gpd=False)

    def mask_3D_all_touched(
        self,
        lon_or_obj,
        lat=None,
        *,
        drop=True,
        wrap_lon=None,
        use_cf=None,
    ):
        mask_3D = _mask_3D(
            polygons=self.polygons,
            numbers=self.numbers,
            lon_or_obj=lon_or_obj,
            lat=lat,
            drop=drop,
            wrap_lon=wrap_lon,
            overlap=self.overlap,
            use_cf=use_cf,
            all_touched=True,
        )

        numbers = mask_3D.region.values
        abbrevs = self[numbers].abbrevs
        names = self[numbers].names

        mask_3D = mask_3D.assign_coords(
            abbrevs=("region", abbrevs), names=("region", names)
        )

        return mask_3D

    # TODO: docstring
    # mask_3D.__doc__ = _inject_mask_docstring(which="3D", is_gpd=False)

    def mask_3D_frac_approx(
        self,
        lon_or_obj: np.typing.ArrayLike | xr.DataArray | xr.Dataset,
        lat: np.typing.ArrayLike | xr.DataArray | None = None,
        *,
        drop: bool = True,
        wrap_lon: None | bool | Literal[180, 360] = None,
        use_cf: bool | None = None,
    ) -> xr.DataArray:

        mask_3D = _mask_3D_frac_approx(
            polygons=self.polygons,
            numbers=self.numbers,
            lon_or_obj=lon_or_obj,
            lat=lat,
            drop=drop,
            wrap_lon=wrap_lon,
            overlap=self.overlap,  # as_3D is always True
            use_cf=use_cf,
        )

        numbers = mask_3D.region.values
        abbrevs = self[numbers].abbrevs
        names = self[numbers].names

        mask_3D = mask_3D.assign_coords(
            abbrevs=("region", abbrevs), names=("region", names)
        )

        return mask_3D

    mask_3D_frac_approx.__doc__ = _inject_mask_docstring(which="frac", is_gpd=False)

    def to_dataframe(self) -> pd.DataFrame:
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

    def to_geodataframe(self) -> gp.GeoDataFrame:
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

    def to_geoseries(self) -> gp.GeoSeries:
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
    def from_geodataframe(
        cls,
        df: gp.GeoDataFrame,
        *,
        name: str | None = None,
        source: str | None = None,
        overlap: bool | None = None,
    ):
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

        overlap : bool | None, default: None
            Indicates if (some of) the regions overlap and determines the behaviour of the
            ``mask`` methods.

            - If True ``mask_3D`` ensures overlapping regions are correctly assigned
              to grid points, while ``mask`` raises an Error (because overlapping
              regions cannot be represented by a 2 dimensional mask).
            - If False assumes non-overlapping regions. Grid points are silently assigned to the
              region with the higher number.
            - If None (default) checks if any gridpoint belongs to more than one region.
              If this is the case ``mask_3D`` correctly assigns them and ``mask``
              raises an Error.

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
            overlap = df.attrs.get("overlap", None)

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
    plot = _plot
    plot_regions = _plot_regions


# =============================================================================


class _OneRegion:
    """a single Region, used as member of ``Regions``

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
    ``_OneRegion`` can be created with numpy-style outlines:

    >>> outl = ((0, 0), (0, 1), (1, 1.), (1, 0))
    >>> r = _OneRegion(1, 'Unit Square', 'USq', outl)
    >>> r
    <regionmask._OneRegion: Unit Square (USq / 1)>

    or by passing shapely Polygons:

    >>> from shapely.geometry import Polygon
    >>> poly = Polygon(outl)
    >>> r = _OneRegion(1, 'Unit Square', 'USq', poly)
    >>> r
    <regionmask._OneRegion: Unit Square (USq / 1)>
    """

    def __init__(self, number, name, abbrev, outline):

        self.number = number
        self.name = name
        self.abbrev = abbrev
        self._centroid = None
        self._bounds = None

        if isinstance(outline, Polygon | MultiPolygon):
            self.polygon = outline
            self._coords = None
        else:

            outline = np.asarray(outline)

            if outline.ndim != 2:
                raise ValueError(
                    "Outline must be 2D. Did you pass a single region and need to wrap "
                    "it in a list?"
                )

            if outline.shape[1] != 2:
                raise ValueError("Outline must have Nx2 elements")

            self.polygon = Polygon(outline)
            self._coords = outline

    def __repr__(self):

        klass = type(self).__name__
        return f"<regionmask.{klass}: {self.name} ({self.abbrev} / {self.number})>"

    @property
    def centroid(self):

        # the Polygon Centroid is much stabler
        if self._centroid is None:
            poly = self.polygon
            if isinstance(poly, MultiPolygon):
                # find the polygon with the largest area and assign as centroid
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
    def coords(self):
        """numpy array of the region"""

        if self._coords is None:

            if isinstance(self.polygon, Polygon):
                coords_ = np.array(self.polygon.exterior.coords)
            else:
                polys = self.polygon.geoms

                # separate the single polygons with nans
                nan = np.full((1, 2), np.nan)
                coords = [c for poly in polys for c in (poly.exterior.coords, nan)]
                # remove the last nan and stack
                coords_ = np.vstack(coords[:-1])

            self._coords = coords_

        return self._coords

    @property
    def bounds(self):
        """
        bounds of the regions (Multi)Polygon.bounds (min_lon, min_lat, max_lon, max_lat)
        """
        if self._bounds is None:
            self._bounds = self.polygon.bounds
        return self._bounds
