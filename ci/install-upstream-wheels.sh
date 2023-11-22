#!/usr/bin/env bash

# forcibly remove packages to avoid artifacts
conda uninstall -y --force \
  cartopy \
  cf_xarray \
  geopandas \
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
python -m pip install --no-deps --upgrade --pre -i https://pypi.anaconda.org/scientific-python-nightly-wheels/simple \
    matplotlib \
    numpy \
    pandas \
    xarray
# install build dependencies (required due to `--no-build-isolation`)
python -m pip install cython
# may be able to remove --no-build-isolation once numpy 2 is out
python -m pip install --no-deps --upgrade --no-build-isolation \
    --no-binary shapely rasterio cartopy \
    git+https://github.com/SciTools/cartopy \
    git+https://github.com/rasterio/rasterio \
    git+https://github.com/shapely/shapely
python -m pip install --no-deps --upgrade \
    git+https://github.com/pypa/packaging \
    git+https://github.com/xarray-contrib/cf-xarray \
    git+https://github.com/geopandas/geopandas \
    git+https://github.com/fatiando/pooch \
    git+https://github.com/geopandas/pyogrio
