import numpy as np
import netCDF4 as nc
import xarray as xr
import xesmf as xe

miofile = 'miocene_topo_pollard_antscape_dolan_0.5x0.5.nc'
atmostopo = 'topog_mio_1x1.nc'

f = nc.Dataset(miofile,'r')
topo = f.variables['topo'][:]
f.close()

topo = topo.astype('f8')

grid_mio = xe.util.grid_global(0.5, 0.5, lon1=359.75)
grid_mio["topo"] = (("y","x"), topo)

trip_grid = xe.util.grid_global(1.0, 1.0, lon1=360)

regridder = xe.Regridder(grid_mio, trip_grid, method="conservative_normed")
topo_at = regridder(grid_mio['topo'])
topo_at = topo_at.data
topo_at[topo_at < 0] = 0.

lat_at = trip_grid.lat[:,0]
lon_at = trip_grid.lon[0,:]

nlat, nlon = topo_at.shape

f = nc.Dataset(atmostopo,'w')
f.history = f'atmos_topog_trip.py on {miofile} \n'
f.title = atmostopo

f.createDimension('lat', nlat)
f.createDimension('lon', nlon)

lat_o = f.createVariable('lat', 'f8', ('lat'))
lat_o.units = 'degrees_north'
lat_o[:] = lat_at[:]

lon_o = f.createVariable('lon', 'f8', ('lon'))
lon_o.units = 'degrees_east'
lon_o[:] = lon_at[:]

topo_o = f.createVariable('topo', 'f8', ('lat','lon'))
topo_o.units = 'metres a.s.l.'
topo_o[:] = topo_at[:]

f.close()

