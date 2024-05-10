# TRIP_river_runoff

Scripts to generate TRIP river runoff from a new topography, for use in ACCESS-ESM1.5 Miocene (15 Ma) configuration. The main scripts, in order of running are:
- `atmos_topog_trip.py`
- `lsm_1x1.py`
- `downslope_trip.py`
- `update_rivers_restart.py`

## atmos_topog_trip.py

This interpolates the original 0.5 x 0.5 deg Miocene topography onto the 1x1 deg TRIP grid. 

## lsm_1x1.py

This remaps the land-sea mask from the ocean grid to the 1x1 deg TRIP grid. Since the ocean is the component that controls the definitive land-sea mask, it's better to use this to derive the LSM than the original Miocene input file.

## dowslope_trip.py
This creates an output of:
`river_mio.nc`

In this script, the key outputs are:
- **route** : specifies field1906, the direction variable (integer from 1-9) 
- **trip_steps** : specifies field1905, the number of steps down the river.

## update_rivers_restart.py

This takes an existing restart file (the variable `restartfile` in the script), and updates the two river fields, given by `ITEM_CODE == 151` and `ITEM_CODE == 152`. The new restart file is given by the variable `new_restart`. 

A couple of key points in this script:
- The latitudinal dimension needs to be flipped because the UM coordinates run from North to South (decreasing).
- The missing value has to be set according to the special value contained in `fin.missval_r`. 