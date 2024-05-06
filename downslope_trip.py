import numpy as np 
import netCDF4 as nc 
import matplotlib.pyplot as plt

topofile = 'topog_no_sink.nc'
outfile = 'river_mio.nc'
checkfig = 'counts.png'

landfile = 'lsm_1x1.nc'

f = nc.Dataset(topofile,'r')
lat = f.variables['lat'][:]
lon = f.variables['lon'][:]
topo = f.variables['topo'][:]
f.close()

nlat, nlon = topo.shape

f = nc.Dataset(landfile, 'r')
land_mask = f.variables['lmask'][:]
f.close()

thresh = 0.1
land = land_mask > thresh
topo[~land] = 0

# ------------------------------------------
# DIRECTION KEY
# 1-8 = directions - 1: N, 2: NE, 3: E, 4: SE, 5: S, 6: SW, 7: W, 8: NW
# 9 = outflow point - when river hits this, flux gets passed to ocean
# 10 = inland basin - when river reaches this, flow is passed to soil moisture
# ------------------------------------------
istep = np.array([0, 1, 1, 1, 0,-1,-1,-1])
jstep = np.array([1, 1, 0,-1,-1,-1, 0, 1])
directions = np.arange(1,9)
nstep = istep.shape[0]

maxcount = 200

idest = np.zeros((nlat,nlon), 'i4')
jdest = np.zeros((nlat,nlon), 'i4')
counts = np.zeros((nlat,nlon), 'i4')

route = np.zeros((nlat,nlon), 'i4')
trip_steps = np.ones((nlat,nlon), 'i4')

bottom_row = np.ones((1,nlon)) * 5000.
topo_halo = np.concatenate((bottom_row, topo), axis=0)

for j in range(0,nlat-1):
    print(j)
    for i in range(nlon):
        j1 = j
        i1 = i
        j1_halo = j1 + 1
        count = 0
        count1 = 1
        while land[j1,i1] and (count < maxcount):
            count += 1
            count1 += 1
            level = topo_halo[j1_halo,i1]
            for k in range(nstep):
                ii = i1 + istep[k]
                jj = j1 + jstep[k]
                jj_halo = jj + 1
                if ii==-1:
                    ii = nlon-1
                if ii==nlon:
                    ii = 0
                if topo_halo[jj_halo,ii] < level:
                    level = topo_halo[jj_halo,ii]
                    jnew = jj
                    inew = ii
                    route[j1,i1] = directions[k]
            trip_steps[jnew, inew] = max(count1, trip_steps[jnew, inew])
            j1 = jnew
            j1_halo = j1 + 1
            i1 = inew

        if land[j,i]:
            idest[j,i] = i1
            jdest[j,i] = j1
        counts[j,i] = count

def count_unique(keys):
    uniq_keys = np.unique(keys)
    bins = uniq_keys.searchsorted(keys)
    return uniq_keys, np.bincount(bins)

# Create a 1D indexing system to sort the values...
rdest = jdest * nlon + idest
rdest = np.reshape(rdest, (-1))

# Now count the unique destinations.
keys, nums = count_unique(rdest)
nkeys = keys.shape[0]

# initialize a basin counter
nb = 0

# Define a 1D basin array
basin = np.zeros((nlat*nlon),'i4')
# Take the nums of 0 to be the ocean... to which we leave basin=0
for i in range(nkeys):
    if nums[i] != 0:
        basin[rdest==keys[i]] = nb
        basin[keys[i]] = -nb
        nb += 1

# Reshape it back to a 2D array:
basin = np.reshape(basin, (nlat, nlon))

land_sinks = np.logical_and(basin < 0, land)

route[basin < 0] = 9

lmask = route==0

route = np.ma.masked_array(route, lmask)
trip_steps = np.ma.masked_array(trip_steps, lmask)

plt.figure('Check counts', figsize=(10,8))

plt.subplot(221)

plt.pcolor(route)
plt.colorbar()
plt.title('field1906')

plt.subplot(222)

plt.pcolor(trip_steps)
plt.colorbar()
plt.title('field1905')

plt.subplot(223)
plt.pcolor(counts)
plt.colorbar()
plt.title('counts')

plt.subplot(224)
plt.pcolor(land_sinks)
plt.colorbar()
plt.title('Land sinks')

plt.savefig(checkfig)


f = nc.Dataset(outfile, 'w')
f.createDimension('lat', nlat)
f.createDimension('lon', nlon)

lat_o = f.createVariable('lat', 'f8', ('lat'))
lat_o[:] = lat[:]
lat_o.units = 'degrees_N'

lon_o = f.createVariable('lon', 'f8', ('lon'))
lon_o[:] = lon[:]
lon_o.units = 'degrees_E'

sinks_o = f.createVariable('land_sinks', 'i4', ('lat', 'lon'))
sinks_o.long_name = 'Inland sinks, should be all zeros for final version'
sinks_o[:] = land_sinks[:]

counts_o = f.createVariable('counts', 'i4', ('lat','lon'))
counts_o.long_name = 'Steps required to reach ocean (reverse count of field1905)'
counts_o[:] = counts[:]

basin_o = f.createVariable('basin','i4',('lat','lon'))
basin_o.long_name = 'Basin number for GFDL model, pos. = land basin, neg. = destination'
basin_o[:] = basin[:]

route_o = f.createVariable('route', 'i4', ('lat','lon'), fill_value=-99999)
route_o.long_name = 'Direction of flow (1-9), to set field1906'
route_o[:] = route[:]

trip_steps_o = f.createVariable('trip_steps','i4',('lat','lon'), fill_value=-99999)
trip_steps_o.long_name = 'Number of steps increasing down the river, to set field1905'
trip_steps_o[:] = trip_steps[:]

f.close()

f = open('land_sinks.txt','w')
aa = np.where(land_sinks==1)
for i in range(len(aa[0])):
    f.write('[%d,%d]\n' % (aa[0][i], aa[1][i]))
f.close()