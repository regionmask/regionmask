#!/usr/bin/env bash

# forcibly remove packages to avoid artifacts
conda uninstall -y --force \
  cartopy \
  cf_xarray \
  geopandas \
  matplotlib-base \
  numpy \
  pandas \
  packaging \
  pooch \
  pyogrio \
  rasterio \
  xarray
# to limit the runtime of Upstream CI
python -m pip install \
    -i https://pypi.anaconda.org/scientific-python-nightly-wheels/simple \
    --no-deps \
    --pre \
    --upgrade \
    numpy \
    matplotlib \
    pandas
python -m pip install \
    --no-deps \
    --upgrade \
    git+https://github.com/SciTools/cartopy \
    git+https://github.com/xarray-contrib/cf-xarray \
    git+https://github.com/geopandas/geopandas \
    git+https://github.com/pypa/packaging \
    git+https://github.com/fatiando/pooch \
    git+https://github.com/geopandas/pyogrio \
    git+https://github.com/rasterio/rasterio \
    git+https://github.com/pydata/xarray \
