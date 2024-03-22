#!/usr/bin/env bash

# NOTE: pyogrio is not tested as it is a optional dependency

# forcibly remove packages to avoid artifacts
conda uninstall -y --force \
  cartopy \
  cf_xarray \
  geopandas \
  geopandas-base \
  matplotlib-base \
  numpy \
  packaging \
  pandas \
  pooch \
  pyogrio \
  rasterio \
  shapely \
  xarray
# to limit the runtime of Upstream CI
python -m pip install \
    -i https://pypi.anaconda.org/scientific-python-nightly-wheels/simple \
    --no-deps \
    --pre \
    --upgrade \
    matplotlib \
    numpy \
    pandas \
    xarray
python -m pip install \
    --no-deps \
    --upgrade \
    git+https://github.com/SciTools/cartopy \
    git+https://github.com/xarray-contrib/cf-xarray \
    git+https://github.com/geopandas/geopandas \
    git+https://github.com/pypa/packaging \
    git+https://github.com/fatiando/pooch
python -m pip install cython # to build shapely
python -m pip install \
    --no-deps \
    --no-build-isolation \
    git+https://github.com/rasterio/rasterio \
    git+https://github.com/shapely/shapely
