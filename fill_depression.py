import numpy as np
import netCDF4 as nc
import richdem as rd

infile = 'topog_mio_1x1.nc'
outfile = 'topog_no_sink.nc'

f = nc.Dataset(infile,'r')
lat = f.variables['lat'][:]
lon = f.variables['lon'][:]
topo = f.variables['topo'][:]
f.close()

topo[0,:] = topo[0,:] + 500

nlat, nlon = topo.shape

nx = 5
nx2 = nx * 2

topo_left = topo[:,-5:]
topo_right = topo[:,:5]

topo_halo = np.concatenate((topo_left, topo, topo_right), axis=1)
new_bottom = np.ones((1,nlon+nx2)) * 5000.
topo_halo = np.concatenate((new_bottom, topo_halo), axis=0)

rtopo = rd.rdarray(topo_halo, no_data=-1.e10)
rtopo_fill = rd.FillDepressions(rtopo, epsilon=True, in_place=False)
rtopo_out = rtopo_fill[1:,nx:-nx]

f = nc.Dataset(outfile,'w')
f.history = f'fill_depression.py on {infile}'

f.createDimension('lat', nlat)
f.createDimension('lon', nlon)

lat_o = f.createVariable('lat', 'f8', ('lat'))
lat_o.units = 'degrees_north'
lat_o[:] = lat[:]

lon_o = f.createVariable('lon', 'f8', ('lon'))
lon_o.units = 'degrees_east'
lon_o[:] = lon[:]

topo_o = f.createVariable('topo', 'f8', ('lat','lon'))
topo_o.units = 'metres'
topo_o[:] = rtopo_out[:]

f.close()