import numpy as np
import netCDF4 as nc
import umfile
from um_fileheaders import *
import os

restartfile = 'restart.subset.259'
new_restart = 'restart.mio.rivers'
riverfile = 'river_mio.nc'

f = nc.Dataset(riverfile,'r')
route = f.variables['route'][:]
trip_steps = f.variables['trip_steps'][:]
f.close()

# Need to flip vertical dimension because UM goes from top to bottom
route_flip = route[::-1,:]
trip_flip = trip_steps[::-1,:]

# Convert to double
route_flip = route_flip.astype('f8')
trip_flip = trip_flip.astype('f8')

os.system('cp {} {}'.format(restartfile, new_restart))

fin = umfile.UMFile(restartfile, 'r')
f = umfile.UMFile(new_restart, 'r+')
nvars = f.fixhd[FH_LookupSize2]

# Fix missing:
mask_save = route_flip.mask

route_flip = route_flip.data
route_flip[mask_save] = fin.missval_r

trip_flip = trip_flip.data
trip_flip[mask_save] = fin.missval_r

for k in range(nvars):
    ilookup = fin.ilookup[k]
    lbegin = ilookup[LBEGIN] 
    if lbegin == -99:
        break
    a = fin.readfld(k)

    if ilookup[ITEM_CODE] == 151:
        a[:] = trip_flip[:]
    if ilookup[ITEM_CODE] == 152:
        a[:] = route_flip[:]

    f.writefld(a[:], k)
f.close()
