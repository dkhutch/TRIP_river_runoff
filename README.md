# TRIP_river_runoff

Scripts to generate TRIP river runoff from a new topography, for use in ACCESS-ESM1.5 Miocene (15 Ma) configuration. The main scripts are:
- `downslope_trip.py`
- `update_rivers_restart.py`

## dowslope_trip.py
This creates an output of:
`river_mio.nc`

In this file, the key outputs are:
- **route** : specifies field1906, the direction variable (integer from 1-9) 
- **trip_steps** : specifies field1905, the number of steps down the river.

## update_rivers_restart.py

This takes an existing restart file (the variable `restartfile` in the script), and updates the two river fields, given by `ITEM_CODE == 151` and `ITEM_CODE == 152`. The new restart file is given by the variable `new_restart`. 

A couple of key points in this script:
- The latitudinal dimension needs to be flipped because the UM coordinates run from North to South (decreasing).
- The missing value has to be set according to the special value contained in `fin.missval_r`. 