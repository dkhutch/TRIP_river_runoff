# TRIP_river_runoff

Scripts to generate TRIP river runoff from a new topography, for use in ACCESS-ESM1.5 Miocene (15 Ma) configuration. The main script is:
`downslope_trip.py`

which creates an output of:
`river_save.nc`

In this file, the key outputs are:
- **route** : specifies field1906, the direction variable (integer from 1-9) 
- **trip_steps** : specifies field1905, the number of steps down the river.