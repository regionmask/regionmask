# region_mask

plotting and creation of masks of spatial regions

### install

```bash
pip install git+https://github.com/mathause/region_mask
```

### Examples

## Examples without using xarray

```python
import regionmask
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs

# plot the srex regions
regionmask.srex.plot()
plt.show()

# ===============

# define a longitude latitude grid
lon = np.arange(-179.5, 180)
lat = np.arange(-89.5, 90)

# for the plotting
lon_edges = np.arange(-180, 181)
lat_edges = np.arange(-90, 91)


# get the mask
mask = regionmask.srex.mask(lon, lat, xarray=False)


# plot on a global map
ax = plt.subplot(111, projection=ccrs.PlateCarree())
# pcolormesh does not handle NaNs, requires masked array
mask_ma = np.ma.masked_invalid(mask)
ax.pcolormesh(lon_edges, lat_edges, mask_ma, transform=ccrs.PlateCarree())

ax.coastlines()

plt.show()

# ===============


# create random data
data = np.random.randn(*mask.shape)

# only retain data in the srex region
data_ceu = np.ma.masked_where(mask != 12, data)

# plot on a global map
ax = regionmask.srex.plot(regions=[11, 'CEU', 13], add_ocean=False,
                          resolution='50m', label='name')

ax.pcolormesh(lon_edges, lat_edges, data_ceu, transform=ccrs.PlateCarree())

ax.set_extent([-15, 45, 25, 80], crs=ccrs.PlateCarree())

plt.show()
```