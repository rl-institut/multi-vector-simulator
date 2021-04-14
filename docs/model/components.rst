.. _component_models:

Component models
----------------

The component models of the MVS result from the used python-library `oemof-solph` for energy modeling.

It requires component models to be simplified and linearized.
This is the reason that the MVS can provide a pre-feasibility study of a specific system setup,
but not the final sizing and system design.
The types of assets are presented below.

.. _energy_consumption:

Energy consumption
##################

Demands within the MVS are added as energy consumption assets in `energyConsumption.csv`. Most importantly, they are defined by a timeseries, representing the demand profile, and their energy vector. A number of demand profiles can be defined for one energy system, both of the same and different energy vectors.
The main optimization goal for the MVS is to supply the defined demand withouth fail for all of the timesteps in the simulation with the least cost of supply (comp. :ref:`economic_precalculation-label`).


.. _energy_production:

Energy production
#################

Non-dispatchable sources of generation
======================================

`Examples`:

    - PV plants
    - Wind plants
    - Run-of-the-river hydro power plants
    - Solar thermal collectors

Variable renewable energy (VRE) sources, like wind and PV, are non-dispatchable due to their fluctuations in supply. They are added as sources in `energyProduction.csv`.

The fluctuating nature of non-dispatchable sources is represented by generation time series that show the respective production for each time step of the simulated period. In energy system modelling it is common to use hourly time series.
The name of the file containing the time series is added to `energyProduction.csv` with the parameter :ref:`filename-label`. For further requirements concerning the time series see section :ref:`time_series_folder`.

If you cannot provide time series for your VRE assets you can consider to calculate them by using models for generating feed-in time series from weather data. The following is a list of examples, which is not exhaustive:

    - PV: `pvlib <https://github.com/pvlib/pvlib-python/>`_ , `Renewables Ninja <https://www.renewables.ninja/>`_ (download capacity factors)
    - Wind: `windpowerlib <https://github.com/wind-python/windpowerlib>`_, `Renewables Ninja <https://www.renewables.ninja/>`_ (download capacity factors)
    - Hydro power (run-of-the-river): `hydropowerlib <https://github.com/hydro-python/hydropowerlib>`_
    - Solar thermal: `flat plate collectors <https://oemof-thermal.readthedocs.io/en/stable/solar_thermal_collector.html>`_ of `oemof.thermal <https://github.com/oemof/oemof-thermal>`_


.. _dispatchable_sources:

Dispatchable sources of generation
==================================

`Examples`:

    - Fuel sources
    - Deep-ground geothermal plant (ground assumed to allow unlimited extraction of heat, not depending on season)

Fuel sources are added as dispatchable sources, which can have development, investment, operational and dispatch costs.
They are added to `energyProduction.csv`, while setting :ref:`filename-label` to `None`.

Fuel sources are for example needed as source for a diesel generator (diesel), biogas plant (gas) or a condensing power plant (gas, coal, ...), see :ref:`energy_conversion`.

Energy providers, even though also dispatchable sources of generation, should be added via `energyProviders.csv`,
as there are some additional features available then, see :ref:`energy_providers`.

Both energy providers and the additional fuel sources are limited to the options of energy carriers provided in the table of :ref:`table_default_energy_carrier_weights_label`, as the default weighting factors to translate the energy carrier into electricity equivalent need to be defined.


.. _energy_conversion:

Energy conversion
#################

`Examples`:

    - Electric transformers (rectifiers, inverters, transformer stations, charge controllers)
    - HVAC and Heat pumps (as heater and/or chiller)
    - Combined heat and power (CHP) and other condensing power plants
    - Diesel generators
    - Electrolyzers
    - Biogas power plants

Conversion assets are added as transformers and are defined in `energyConversion.csv`.

The parameters `dispatch_price`, `efficiency` and `installedCap` of transformers are assigned to their output flows.
This means that these parameters need to be given for the output of the asset and that the costs of the input, e.g. fuel, if existent, are not included in its `dispatch_price` but in the `dispatch_price` of the fuel source, see :ref:`dispatchable_sources`.

Conversion assets can be defined with multiple inputs or multiple outputs, but one asset currently cannot have both, multiple inputs and multiple outputs. Note that multiple inputs/output have not been tested, yet.

.. _energyconversion_electric_transformers:

Electric transformers
=====================

Electric rectifiers and inverters that are transforming electricity in one direction only, are simply added as transformers.
Bidirectional converters and transformer stations are defined by two transformers that are optimized independently from each other, if optimized.
The same accounts for charge controllers for a :ref:`battery_storage` that are defined by two transformers, one for charging and one for discharging.
The parameters `dispatch_price`, `efficiency` and `installedCap` need to be given for the electrical output power of the electric transformers.

.. note::
    When using two conversion objects to emulate a bidirectional conversion asset, their capacity should be interdependent. This is currently not the case, see `Infeasible bi-directional flow in one timestep <https://multi-vector-simulator.readthedocs.io/en/stable/Model_Assumptions.html#infeasible-bi-directional-flow-in-one-timestep>`_.

.. _energyconversion_hvac:

Heating, Ventilation, and Air Conditioning (HVAC)
=================================================

Like other conversion assets, devices for heating, ventilation and air conditioning (HVAC) are added as transformers. As the parameters `dispatch_price`, `efficiency` and `installedCap` are assigned to the output flows they need to be given for the nominal heat output of the HVAC.

Different types of HVAC can be modelled. Except for an air source device with ambient temperature as heat reservoir, the device could be modelled with two inputs (electricity and heat) in case the user is interested in the heat reservoir. This has not been tested, yet. Also note that currently efficiencies are assigned to the output flows the see `issue #799 <https://github.com/rl-institut/multi-vector-simulator/issues/799>`_.
Theoretically, a HVAC device can be modelled with multiple outputs (heat, cooling, ...); this has not been tested, yet.

The efficiency of HVAC systems is defined by the coefficient of performance (COP), which is strongly dependent on the temperature. In order to take account of this, the efficiency can be defined as time series, see section :ref:`time_series_params_example`.
If you do not provide your own COP time series you can calculate them with `oemof.thermal <https://github.com/oemof/oemof-thermal>`_, see  `documentation on compression heat pumps and chillers <https://oemof-thermal.readthedocs.io/en/stable/compression_heat_pumps_and_chillers.html>`_ and  `documentation on absorption chillers <https://oemof-thermal.readthedocs.io/en/stable/absorption_chillers.html>`_.

.. _energyconversion_electrolyzers:

Electrolyzers
=============

Electrolyzers are added as transformers with a constant or time dependent but in any case pre-defined efficiency. The parameters `dispatch_price`, `efficiency` and `installedCap` need to be given for the output of the electrolyzers (hydrogen).

Currently, electrolyzers are modelled with only one input flow (electricity), not taking into account the costs of water; see `issue #799 <https://github.com/rl-institut/multi-vector-simulator/issues/799>`_.
The minimal operation level and consumption in standby mode are not taken into account, yet, see `issue #50 <https://github.com/rl-institut/multi-vector-simulator/issues/50>`_.

.. _power_plants:

Condensing power plants and Combined heat and power (CHP)
=========================================================

Condensing power plants are added as transformers with one input (fuel) and one output (electricity), while CHP plants are defined with two outputs (electricity and heat).
The parameters `dispatch_price`, `efficiency` and `installedCap` need to be given for the electrical output power (and nominal heat output) of the power plant, while fuel costs need to be included in the `dispatch_price` of the fuel source.

The ratio between the heat and electricity output of a CHP is currently simulated as fix values. This might be changed in the future by using the `ExtractionTurbineCHP <https://oemof-solph.readthedocs.io/en/latest/usage.html#extractionturbinechp-component>`_
or the `GenericCHP <https://oemof-solph.readthedocs.io/en/latest/usage.html#genericchp-component>`_ component of oemof, see `issue #803 <https://github.com/rl-institut/multi-vector-simulator/issues/803>`_

Note that multiple inputs/output have not been tested, yet.

Other fuel powered plants
=========================

Fuel powered conversion assets, such as diesel generators and biogas power plants, are added as transformers.
The parameters `dispatch_price`, `efficiency` and `installedCap` need to be given for the electrical output power of the diesel generator or biogas power plant.
As described above, the costs for diesel and gas need to be included in the `dispatch_price` of the fuel source.


.. _energy_providers:

Energy providers
################

The energy providers are the most complex assets in the MVS model. They are composed of a number of sub-assets

    - Energy consumption source, providing the energy required from the system with a certain price
    - Energy peak demand pricing "transformers", which represent the costs induced due to peak demand
    - Bus connecting energy consumption source and energy peak demand pricing transformers
    - Energy feed-in sink, able to take in generation that is provided to the energy provider for revenue
    - Optionally: Transformer Station connecting the energy provider bus to the energy bus of the LES

With all these components, the energy provider can be visualized as follows:

.. image:: ../images/Model_Assumptions_energyProvider_assets.png
 :width: 600

Variable energy consumption prices (time-series)
================================================

Energy consumption prices can be added as values that vary over time. See section :ref:`time_series_folder` or more information.

.. _energy_providers_peak_demand_pricing:

Peak demand pricing
===================

A peak demand pricing scheme is based on an electricity tariff,
that requires the consumer not only to pay for the aggregated energy consumption in a time period (eg. kWh electricity),
but also for the maximum peak demand (load, eg. kW power) towards the grid of the energy provider within a specific pricing period.

In the MVS, this information is gathered for the `energyProviders` with:

    - :const:`multi_vector_simulator.utils.constants_json_strings.PEAK_DEMAND_PRICING_PERIOD` as the period used in peak demand pricing. Possible is 1 (yearly), 2 (half-yearly), 3 (each trimester), 4 (quaterly), 6 (every 2 months) and 12 (each month). If you have a `simulation_duration` < 365 days, the periods will still be set up assuming a year! This means, that if you are simulating 14 days, you will never be able to have more than one peak demand pricing period in place.

    - :const:`multi_vector_simulator.utils.constants_json_strings.PEAK_DEMAND_PRICING` as the costs per peak load unit, eg. kW

To represent the peak demand pricing, the MVS adds a "transformer" that is optimized with specific operation and maintenance costs per year equal to the PEAK_DEMAND_PRICING for each of the pricing periods.
For two peak demand pricing periods, the resulting dispatch could look as following:

.. image:: ../images/Model_Assumptions_Peak_Demand_Pricing_Dispatch_Graph.png
 :width: 600

.. _energy_storage:

Energy storage
##############

Energy storages such as battery storages, thermal storages or H2 storages are modelled with the *GenericStorage* component of *oemof.solph*. They are designed for one input and one output and are defined with files `energyStorage.csv` and `storage_*.csv` and have several parameters, which are listed in the section :ref:`storage_csv`.

The state of charge of a storage at the first and last time step of an optimization are equal.
Charge and discharge of the whole capacity of the energy storage are possible within one time step in case the capacity of the storage is not optimized. In case of
capacity optimization charge and discharge is limited by the :ref:`crate-label`.

.. _battery_storage:

Battery energy storage system (BESS)
====================================

BESS are modelled as *GenericStorage* like described above. The BESS can either be connected directly to the electricity bus of the LES or via a charge controller that manages the BESS.
When choosing the second option, the capacity of the charge controller can be optimized individually, which takes its specific costs and lifetime into consideration.
If you do not want to optimize the charge controller's capacity you can take its costs and efficiency into account when defining the storage's input and output power, see :ref:`storage_csv`.
A charge controller is defined by two transformers, see section :ref:`energy_conversion` above.

Note that capacity reduction over the lifetime of a BESS that may occur due to different effects during aging cannot be taken into consideration in MVS. A possible workaround for this could be to manipulate the lifetime.


Hydrogen storage (H2)
=====================

Hydrogen storages are modelled as all storage types in MVS with as *GenericStorage* like described above.

The most common hydrogen storages store H2 as liquid under temperatures lower than -253 °C or under high pressures.
The energy needed to provide these requirements cannot be modelled via the storage component as another energy sector such as cooling or electricity is needed. It could therefore, be modelled as an additional demand of the energy system, see `issue #811 <https://github.com/rl-institut/multi-vector-simulator/issues/811>`_

.. _thermal_storage:

Thermal energy storage
======================

Thermal energy storages of the type sensible heat storage (SHS) are modelled as *GenericStorage* like described above. The implementation of a specific type of SHS, the stratified thermal energy storage, is described in section :ref:`stratified_tes`.
The modelling of latent-heat (or Phase-change) and chemical storages have not been tested with MVS, but might be achieved by precalculations.

.. _stratified_tes:

Stratified thermal energy storage
=================================

Stratified thermal energy storage is defined by the two optional parameters `fixed_losses_relative` and `fixed_losses_absolute`. If they are not included in `storage_*.csv` or are equal to zero, then a normal generic storage is simulated.
These two parameters are used to take into account temperature dependent losses of a thermal storage. To model a thermal energy storage without stratification, the two parameters are not set. The default values of `fixed_losses_relative` and `fixed_losses_absolute` are zero.
Except for these two additional parameters the stratified thermal storage is implemented in the same way as other storage components.

Precalculations of the `installedCap`, `efficiency`, `fixed_losses_relative` and `fixed_losses_absolute` can be done orientating on the stratified thermal storage component of `oemof.thermal  <https://github.com/oemof/oemof-thermal>`__.
The parameters `U-value`, `volume` and `surface` of the storage, which are required to calculate `installedCap`, can be precalculated as well.

The efficiency :math:`\eta` of the storage is calculated as follows:

.. math::
   \eta = 1 - loss{\_}rate

This example shows how to do precalculations using stratified thermal storage specific input data:


.. code-block:: python

        from oemof.thermal.stratified_thermal_storage import (
        calculate_storage_u_value,
        calculate_storage_dimensions,
        calculate_capacities,
        calculate_losses,
        )

        # Precalculation
        u_value = calculate_storage_u_value(
            input_data['s_iso'],
            input_data['lamb_iso'],
            input_data['alpha_inside'],
            input_data['alpha_outside'])

        volume, surface = calculate_storage_dimensions(
            input_data['height'],
            input_data['diameter']
        )

        nominal_storage_capacity = calculate_capacities(
            volume,
            input_data['temp_h'],
            input_data['temp_c'])

        loss_rate, fixed_losses_relative, fixed_losses_absolute = calculate_losses(
            u_value,
            input_data['diameter'],
            input_data['temp_h'],
            input_data['temp_c'],
            input_data['temp_env'])

Please see the `oemof.thermal` `examples <https://github.com/oemof/oemof-thermal/tree/dev/examples/stratified_thermal_storage>`__ and the `documentation  <https://oemof-thermal.readthedocs.io/en/latest/stratified_thermal_storage.html>`__ for further information.

For an investment optimization the height of the storage should be left open in the precalculations and `installedCap` should be set to 0 or NaN.

An implementation of the stratified thermal storage component has been done in `pvcompare <https://github.com/greco-project/pvcompare>`__. You can find the precalculations of the stratified thermal energy storage made in `pvcompare` `here <https://github.com/greco-project/pvcompare/blob/dev/pvcompare/stratified_thermal_storage.py>`__.


Energy excess
#############

.. note::
   Energy excess components are implemented **automatically** by MVS! You do not need to define them yourself.

An energy excess sink is placed on each of the LES energy busses, and therefore energy excess is allowed to take place on each bus of the LES.
This means that there are assumed to be sufficient vents (heat) or transistors (electricity) to dump excess (waste) generation.
Excess generation can only take place when a non-dispatchable source is present or if an asset can supply energy without any fuel or dispatch costs.

In case of excessive excess energy, a warning is given that it seems to be cheaper to have high excess generation than investing into more capacities.
High excess energy can for example result into an optimized inverter capacity that is smaller than the peak generation of installed PV.
This becomes unrealistic when the excess is very high.