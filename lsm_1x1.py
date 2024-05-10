import numpy as np
import netCDF4 as nc
import xarray as xr
import xesmf as xe

ocean_topog = 'topog_mio_v3.nc'
ocean_gridfile = 'ocean_hgrid.nc'
lsm_file = 'lsm_1x1.nc'

f = nc.Dataset(ocean_gridfile,'r')
x = f.variables['x'][:]
y = f.variables['y'][:]
f.close()

f = nc.Dataset(ocean_topog,'r')
depth = f.variables['depth'][:]
f.close()

omask = depth == 0
omask = omask.astype('f8')

ocean_grid = xr.Dataset(coords={
    "lat": (("y","x"), y[1::2, 1::2]),
    "lon": (("y","x"), x[1::2, 1::2]),
    "lat_b": (("y_b","x_b"), y[0::2, 0::2]),
    "lon_b": (("y_b","x_b"), x[0::2, 0::2])
    })

trip_grid = xe.util.grid_global(1.0, 1.0, lon1=360)

remap = xe.Regridder(ocean_grid, trip_grid, method="conservative_normed")

lmask = remap(omask.data)
lmask[:12,:] = 1.0 # correction for non-global ocean grid

nlat, nlon = lmask.shape

f = nc.Dataset(lsm_file,'w')
hist = f'lsm_1x1.py on {ocean_topog} \n'
f.setncattr('history', hist)

f.createDimension('lat', nlat)
f.createDimension('lon', nlon)

lat_o = f.createVariable('lat','f8',('lat'))
lat_o.units = 'degrees_north'
lat_o[:] = trip_grid.lat[:,0]

lon_o = f.createVariable('lon','f8',('lon'))
lon_o.units = 'degrees_north'
lon_o[:] = trip_grid.lon[0,:]

lmask_o = f.createVariable('lmask','f8',('lat','lon'))
lmask_o[:] = lmask[:]

f.close()