.. _constraints-label:

Constraints
-----------

Constraints are controlled with the file `constraints.csv`.

.. _constraint_min_re_factor:

Minimal renewable factor constraint
###################################

The minimal renewable factor constraint requires the capacity and dispatch optimization of the MVS to reach at least the minimal renewable factor defined within the constraint. The renewable share of the optimized energy system may also be higher than the minimal renewable factor.

The minimal renewable factor is applied to the minimal renewable factor of the whole, sector-coupled energy system, but not to specific sectors. As such, energy carrier weighting plays a role and may lead to unexpected results. The constraint reads as follows:

.. math::
        minimal renewable factor <= \frac{\sum renewable generation \cdot weighting factor}{\sum renewable generation \cdot weighting factor + \sum non-renewable generation \cdot weighting factor}

Please be aware that the minimal renewable factor constraint defines bounds for the :ref:`renewable_factor` of the system, ie. taking into account both local generation as well as renewable supply from the energy providers. The constraint explicitly does not aim to reach a certain :ref:`renewable_share_of_local_generation` on-site.

:Deactivating the constraint:

The minimal renewable factor constraint is deactivated by inserting the following row in `constraints.csv` as follows:

```minimal_renewable_factor,factor,0```

:Activating the constraint:

The constraint is enabled when the value of the minimal renewable factor factor is above 0 in `constraints.csv`:

```minimal_renewable_factor,factor,0.3```


Depending on the energy system, especially when working with assets which are not to be capacity-optimized, it is possible that the minimal renewable factor criterion cannot be met. The simulation terminates in that case. If you are not sure if your energy system can meet the constraint, set all `optimize_Cap` parameters to `True`, and then investigate further.
Also, if you are aiming at very high minimal renewable factors, the simulation time can increase drastically. If you do not get a result after a maximum of 20 Minutes, you should consider terminating the simulation and trying with a lower minimum renewable share.

The minimum renewable share is introduced to the energy system by `D2.constraint_minimal_renewable_share()` and a validation test is performed with `E4.minimal_renewable_share_test()`.

.. _constraint_minimal_degree_of_autonomy:

Minimal degree of autonomy constraint
######################################

The minimal degree of autonomy constraint requires the capacity and dispatch optimization of the MVS to reach at least the minimal degree of autonomy defined within the constraint. The degree of autonomy of the optimized energy system may also be higher than the minimal degree of autonomy. Please find the definition of here: :ref:`degree_of_autonomy`

The minimal degree of autonomy is applied to the whole, sector-coupled energy system, but not to specific sectors. As such, energy carrier weighting plays a role and may lead to unexpected results. The constraint reads as follows:

.. math::
        minimal~degree~of~autonomy <= DA = \frac{\sum E_{demand,i} \cdot w_i - \sum E_{consumption,provider,j} \cdot w_j}{\sum E_{demand,i} \cdot w_i}

:Deactivating the constraint:

The minimal degree of autonomy constraint is deactivated by inserting the following row in `constraints.csv` as follows:

```minimal_degree_of_autonomy,factor,0```

:Activating the constraint:

The constraint is enabled when the value of the minimal degree of autonomy is above 0 in `constraints.csv`:

```minimal_degree_of_autonomy,factor,0.3```


Depending on the energy system, especially when working with assets which are not to be capacity-optimized, it is possible that the minimal degree of autonomy criterion cannot be met. The simulation terminates in that case. If you are not sure if your energy system can meet the constraint, set all `optimizeCap` parameters to `True`, and then investigate further.

The minimum degree of autonomy is introduced to the energy system by `D2.constraint_minimal_degree_of_autonomy()` and a validation test is performed with `E4.minimal_degree_of_autonomy()`.

.. _constraint_maximum_emissions:

Maximum emission constraint
###########################

The maximum emission constraint limits the maximum amount of total emissions per year of the energy system. It allows the capacity and dispatch optimization of the MVS to result into a maximum amount of emissions defined by the maximum emission constraint. The yearly emissions of the optimized energy system may also be lower than the maximum emission constraint.

Please note that the maximum emissions constraint currently does not take into consideration life cycle emissions, also see :ref:`total_emissions` section for an explanation.

:Activating the constraint:

The maximum emissions constraint is enabled by inserting the following row in `constraints.csv` as follows:

```maximum_emissions,kgCO2eq/a,800000```

:Deactivating the constraint:

The constraint is deactivated by setting the value in `constraints.csv` to None:

```maximum_emissions,kgCO2eq/a,None```

The unit of the constraint is `kgCO2eq/a`. To select a useful value for this constraint you can e.g.:

- Firstly, optimize your system without the constraint to get an idea about the scale of the emissions and then, secondly, set the constraint and lower the emissions step by step until you receive an unbound problem (which then represents the non-archievable minimum of emissions for your energy system)
- Check the emissions targets of your region/country and disaggregate the number

The maximum emissions constraint is introduced to the energy system by `D2.constraint_maximum_emissions()` and a validation test is performed with `E4.maximum_emissions_test()`.

.. _constraint_net_zero_energy:

Net zero energy (NZE) constraint
################################

The net zero energy (NZE) constraint requires the capacity and dispatch optimization of the MVS to result into a net zero system, but can also result in a plus energy system.
The degree of NZE of the optimized energy system may be higher than 1, in case of a plus energy system. Please find the definition of net zero energy (NZE) and the KPI here: :ref:`degree_of_nze`.

Some definitions of NZE systems in literature allow the energy system's demand solely be provided by locally generated renewable energy. In MVS this is not the case - all locally generated energy is taken into consideration. To enlarge the share of renewables in the energy system you can use the :ref:`constraint_min_re_factor`.

The NZE constraint is applied to the whole, sector-coupled energy system, but not to specific sectors. As such, energy carrier weighting plays a role and may lead to unexpected results. The constraint reads as follows:

.. math::
        \sum_{i} {E_{feedin, DSO} (i) \cdot w_i - E_{consumption, DSO} (i) \cdot w_i} >= 0

:Deactivating the constraint:

The NZE constraint is deactivated by inserting the following row in `constraints.csv` as follows:

```net_zero_energy,bool,False```

:Activating the constraint:

The constraint is enabled when the value of the NZE constraint is set to `True` in `constraints.csv`:

```net_zero_energy,bool,True```


Depending on the energy system, especially when working with assets which are not to be capacity-optimized, it is possible that the NZE criterion cannot be met. The simulation terminates in that case. If you are not sure if your energy system can meet the constraint, set all `optimizeCap` parameters to `True`, and then investigate further.

The net zero energy constraint is introduced to the energy system by `D2.constraint_net_zero_energy()` and a validation test is performed with `E4.net_zero_energy_test()`.
