================================
Moddeling Assumptions of the MVS
================================

Component models
----------------

The component models of the MVS result from the used python-library `oemof-solph` for energy moddeling.
It requires component models to be simplified and linearized.
This is the reason that the MVS can provide a pre-feasibility study of a specific system setup,
but not the final sizing and system design.
The types of assets are presented below.

Non-dispatchable sources of generation
######################################

`Examples`:
    - PV plant
    - Wind plant

Dispatchable sources of generation
##################################

`Examples`:
    - Fuel sources
    - Run-of-the-river hydro power plant
    - Deep-ground geothermal plant (ground assumed to allow unlimited extraction of heat, not depending on season)


Dispatchable conversion assets
##############################
`Examples`:
    - Diesel generator
    - Electric transformers (rectifiers, inverters

Energy excess
#############

Energy excess is allowed to take place on each of the systems energy busses.
This means that there are assumed to be sufficient vents (heat) or transistors (electricity) to dump excess (waste) generation.
Excess generation can only take place when a non-dispatchable source is present or if an asset can supply energy without any fuel or dispatch costs.


Limitations
-----------

Perfect foresight
#################
- Battery charge

Infeasible dispatch of assets
#############################

- Energy consumption and feed-in at the same time
- Bi-directional inverters
