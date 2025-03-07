import numpy as np
import pytest
import shapely
import xarray as xr

import regionmask

from . import has_gdal_3_8_2, requires_gdal_3_8_2
from .test_mask import _expected_rectangle
from .utils import dummy_ds, dummy_region


@pytest.mark.skipif(has_gdal_3_8_2, reason="only errors if gdal<3.8.2")
def test_mask_all_touched_requires_gdal_3_7_3():
    with pytest.raises(
        NotImplementedError,
        match="Using ``all_touched`` requires gdal v3.8.2 or higher.",
    ):
        dummy_region.mask_3D_all_touched(dummy_ds)


@requires_gdal_3_8_2
# @pytest.mark.parametrize("xmin", (2.0001, 2.5, 3))
# @pytest.mark.parametrize("ymin", (2.0001, 2.5, 3))
# @pytest.mark.parametrize("xmax", (10.0001, 10.5, 11))
# @pytest.mark.parametrize("ymax", (10.0001, 10.5, 11))
@pytest.mark.parametrize("xmin", (2.5, 3))
@pytest.mark.parametrize("ymin", (2.5, 3))
@pytest.mark.parametrize("xmax", (10.5, 11))
@pytest.mark.parametrize("ymax", (10.5, 11))
def test_mask_all_touched_edge(xmin, ymin, xmax, ymax):

    ds = regionmask.core.utils.create_lon_lat_dataarray_from_bounds(
        0, 18, 1, 15, -1, -1
    )

    p = shapely.geometry.box(xmin, ymin, xmax, ymax, ccw=True)
    r = regionmask.Regions([p])

    result = r.mask_3D_all_touched(ds)

    expected = _expected_rectangle(
        ds, lon_min=2, lon_max=11, lat_min=2, lat_max=11, is_360=False
    )
    expected = expected.assign_coords(region=0)
    expected = expected.expand_dims("region")
    expected = expected.assign_coords(
        names=("region", ["Region0"]), abbrevs=("region", ["r0"])
    )
    expected = expected.drop_vars(["LON", "LAT"])

    print(result.sum())
    print(expected.sum())
    r = result.sum()
    e = expected.sum()
    assert r == e

    # xr.testing.assert_equal(result, expected)

    # p = shapely.geometry.box(xmin, ymin, xmax, ymax, ccw=False)
    # r = regionmask.Regions([p])
    # result = r.mask_3D_all_touched(ds)

    # xr.testing.assert_equal(result, expected)


import matplotlib.pyplot as plt
import shapely

import regionmask

f, axs = plt.subplots(3, 2)

ds = regionmask.core.utils.create_lon_lat_dataarray_from_bounds(15, -1, -1, 15, -1, -1)

for i, xmin in enumerate((2, 2.5, 3)):
    p = shapely.geometry.box(xmin, 2.5, 9.5, 9.5, ccw=False)
    r = regionmask.Regions([p])

    result = r.mask_3D_all_touched(ds)

    ax = axs[i, 0]

    r.plot_regions(ax=ax, line_kws={"color": "r"})
    result.plot(ax=ax, lw=0.5, ec="0.5", add_colorbar=False)


for i, xmax in enumerate((9, 9 - 1e-5, 9 + 5e-5)):
    p = shapely.geometry.box(2.5, 0.5, xmax, 9.5, ccw=False)
    r = regionmask.Regions([p])

    result = r.mask_3D_all_touched(ds)

    ax = axs[i, 1]

    r.plot_regions(ax=ax, line_kws={"color": "r"})
    result.plot(ax=ax, lw=0.5, ec="0.5", add_colorbar=False)


f, axs = plt.subplots(3, 2)

ds = regionmask.core.utils.create_lon_lat_dataarray_from_bounds(0, 18, 1, 15, -1, -1)

for i, ymin in enumerate((2, 2.5, 3)):
    p = shapely.geometry.box(2.5, ymin, 9.5, 9.5, ccw=False)
    r = regionmask.Regions([p])

    result = r.mask_3D_all_touched(ds)

    ax = axs[i, 0]

    r.plot_regions(ax=ax, line_kws={"color": "r"})
    result.plot(ax=ax, lw=0.5, ec="0.5", add_colorbar=False)
    ax.set_title(f"{ymin=}")


for i, ymax in enumerate((9, 9 - 1e-5, 9 + 5e-5)):
    p = shapely.geometry.box(2.5, 0.5, 9.5, ymax, ccw=False)
    r = regionmask.Regions([p])

    result = r.mask_3D_all_touched(ds)

    ax = axs[i, 1]

    r.plot_regions(ax=ax, line_kws={"color": "r"})
    result.plot(ax=ax, lw=0.5, ec="0.5", add_colorbar=False)
    ax.set_title(f"{ymax=}")


regionmask.core.mask._mask_rasterize_no_offset(
    ds.lon, ds.lat, [p], [1], fill=0, dtype=int, all_touched=True
)


import shapely
from affine import Affine
from rasterio import features

transform = Affine(1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
poly = shapely.box(xmin=2.5, ymin=2.5, xmax=7.5, ymax=8)
raster = features.rasterize(
    ((poly, 1),),
    out_shape=(10, 10),
    fill=0,
    all_touched=True,
    transform=transform,
)
print(raster.sum())
raster


import shapely
from affine import Affine
from rasterio import features

transform = Affine(1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
poly = shapely.geometry.box(1 - 1e-5, 1.5, 8.5, 9.0 + 1e-5, ccw=False)

raster = features.rasterize(
    ((poly, 1),),
    out_shape=(10, 10),
    fill=0,
    all_touched=True,
    transform=transform,
)
print(raster.sum())
raster

import shapely
from affine import Affine
from rasterio import features

transform = Affine(1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
poly = shapely.geometry.box(1, 1.5, 9.0 + 1e-5, 9.0, ccw=False)

raster = features.rasterize(
    ((poly, 1),),
    out_shape=(10, 10),
    fill=0,
    all_touched=True,
    transform=transform,
)
print(raster.sum())
raster


import shapely
from affine import Affine
from rasterio import features

transform = Affine(-1.0, 0.0, 10.0 - 1e-8, 0.0, -1.0, 10.0 - 1e-10)
transform = Affine(-1.0, 0.0, 10.0, 0.0, -1.0, 10.0)

poly = shapely.geometry.box(1, 1, 9 - 1e-4, 9, ccw=False)

raster = features.rasterize(
    ((poly, 1),),
    out_shape=(10, 10),
    fill=0,
    all_touched=True,
    transform=transform,
)
print(raster.sum())
raster
