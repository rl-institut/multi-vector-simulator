===========
Assumptions
===========

The MVS is based on the programming framework `oemof-solph` and builds an energy system model based up on its nomenclature.
As such, the energy system model can be described with a linear equation system.
Below, the most important aspects are described in a genrealized way, as well as explained based on an example.
This will ease the comparision to other energy system models.

.. _economic_precalculation-label:

Economic Dispatch
-----------------

Linear programming is a mathematical modelling and optimization technique for a system of a linear objective function subject to linear constraints.
The goal of a linear programming problem is to find the optimal value for the objective function, be it a maximum or a minimum.
The MVS is based on `oemof-solph`, which in turn uses `Pyomo` to create a linear problem.
The economic dispatch problem in the MVS has the objective of minimizing the production cost by allocating the total demand among the generating units at each time step.
The equation is the following:

.. math::
        min Z = \sum_i a_i \cdot CAP_i + \sum_i \sum_t c_{var,i} \cdot E_i(t)

.. math::
        CAP_i &\geq 0

        E_i(t) &\geq 0  \qquad  \forall t

        i &\text{: asset}

        a_i &\text{: asset annuity [currency/kWp/year, currency/kW/year, currency/kWh/year]}

        CAP_i &\text{: asset capacity [kWp, kW, kWh]}

        c_{var,i} &\text{: variable operational or dispatch cost [currency/kWh, currency/L]}

        E_i(t) &\text{: asset dispatch [kWh]}

The annual cost function of each asset includes the capital expenditure (investment cost) and residual value, as well as the operating expenses of each asset.
It is expressed as follows:

.. math::
        a_i &= \left( capex_i + \sum_{k=1}^{n} \frac{capex_i}{(1+d)^{k \cdot t_a}} - c_{res,i} \right) \cdot CRF(T) + opex_i

        CRF(T) &= \frac{d \cdot (1+d)^T}{(1+d)^T - 1}

.. math::
        capex_i &\text{: specific investment costs [currency/unit]}

        n &\text{: number of replacements of an asset within project lifetime T}

        t_a &\text{: asset lifetime [years]}

        CRF &\text{: capital recovery factor}

        c_{res,i} &\text{: residual value of asset i at the end of project lifetime T [currency/unit]}

        opex_i &\text{: annual operational and management costs [currency/unit/year]}

        d &\text{: discount factor}

        T &\text{: project lifetime [years]}

The CRF is a ratio used to calculate the present value of the the annuity.
The discount factor can be replaced by the weighted average cost of capital (WACC), calculated by the user.

The lifetime of the asset :math:`t_a` and the lifetime of the project :math:`T` can be different from each other;
hence, the number of replacements n is estimated using the equation below:

.. math::
        n = round \left( \frac{T}{t_a} + 0.5 \right) - 1

The residual value is also known as salvage value and it represents an estimate of the monetary value of an asset at the end of the project lifetime T.
The MVS considers a linear depreciation over T and accounts for the time value of money by using the following equation:

.. math::
        c_{res,i} = \frac{capex_i}{(1+d)^{n \cdot t_a}} \cdot \frac{1}{T} \cdot \frac{(n+1) \cdot t_a - T}{(1+d)^T}

Energy Balance Equation
-----------------------

One main constraint that the optimization model is subject to is the energy balance equation.
The latter maintains equality between the incoming energy into a bus and the outgoing energy from that bus.
This balancing equation is applicable to all bus types, be it electrical, thermal, hydrogen or for any other energy carrier.

.. math::
        \sum E_{in,i}(t) - \sum E_{out,j}(t) = 0 \qquad  \forall t

.. math::
        E_{in,i} &\text{: energy flowing from asset i to the bus}

        E_{out,j} &\text{: energy flowing from the bus to asset j}

It is very important to note that assets i and j can be the same asset (e.g., battery).
`oemof-solph` allows both :math:`E_{in}` or :math:`E_{out}` to be larger zero in same time step t (see :ref:`limitations-real-life-constraint`).


Example: Sector Coupled Energy System
-------------------------------------

In order to understand the component models, a generic sector coupled example is shown in the next figure.
It brings together the electricity and heat sector through Transformer 4 as it connects the two sector buses.

.. image:: ../images/26-10-2020_sector_coupled_example.png
 :width: 600

For the sake of simplicity, the following table gives an example for each asset type with an abbreviation to be used in the energy balance and component equations.

 .. list-table:: Asset Types and Examples
   :widths: 50 25 25 25
   :header-rows: 1

   * - Asset Type
     - Asset Example
     - Abbreviation
     - Unit
   * - Non-dispatchable source 1
     - Wind turbine
     - wind
     - kW
   * - Non-dispatchable source 2
     - Photovoltaic panels
     - pv
     - kWp
   * - Storage 1
     - Battery energy storage
     - bat
     - kWh
   * - Transformer 1
     - Rectifier
     - rec
     - kW
   * - Transformer 2
     - Solar inverter
     - inv
     - kW
   * - Non-dispatchable source 3
     - Solar thermal collector
     - stc
     - kWth
   * - Storage 2
     - Thermal energy storage
     - tes
     - kWth
   * - Dispatchable source
     - Heat source (e.g., biogas)
     - heat
     - L
   * - Transformer 3
     - Turbine
     - turb
     - kWth
   * - Transformer 4
     - Heat pump
     - hp
     - kWth

All grids and dispatchable sources are assumed to be available 100% of the time with no consumption limits.
The MVS includes a sink component for excess energy, connected to each bus in the system and denoted by :math:`E_{ex}` in the equations.
This excess sink accounts for the extra energy in the system that has to be dumped.

Electricity Grid Equation
#########################

The electricity grid is modeled though a feed-in and a consumption node.
Transformers limit the peak flow into or from the local electricity line.
Electricity sold to the grid experiences losses in the transformer :math:`(ts,f)`.

.. math::
        E_{grid,c}(t) - E_{grid,f}(t) + E_{ts,f}(t) \cdot \eta_{ts,f} - E_{ts,c}(t) = 0 \qquad  \forall t

.. math::
        E_{grid,c} &\text{: energy consumed from the electricity grid}

        E_{grid,f} &\text{: energy fed into the electricity grid}

        E_{grid,c} &\text{: transformer station feed-in}

        \eta_{ts,f} &\text{: transformer station efficiency}

        E_{grid,c} &\text{: transformer station consumption}

Non-Dispatchable Source Equations
#################################

Non-dispatchable sources in our example are wind, pv and solar thermal plant.
Their generation is determined by the provided timeseries of instantaneous generation, providing :math:`\alpha`, :math:`\beta`, :math:`\gamma` respectively.

.. math::
        E_{wind}(t) &= CAP_{wind} \cdot \alpha_{wind}(t) \qquad  \forall t

        E_{pv}(t) &= CAP_{pv} \cdot \beta_{pv}(t) \qquad  \forall t

        E_{stc}(t) &= CAP_{stc} \cdot \gamma_{stc}(t) \qquad  \forall t

.. math::
        E_{wind} &\text{: energy generated from the wind turbine}

        CAP_{wind} &\text{: wind turbine capacity [kW]}

        \alpha_{wind} &\text{: instantaneous wind turbine performance metric [kWh/kW]}

        E_{pv} &\text{: energy generated from the PV panels}

        CAP_{pv} &\text{: PV panel capacity [kWp]}

        \beta_{pv} &\text{: instantaneous PV specific yield [kWh/kWp]}

        E_{stc} &\text{: energy generated from the solar thermal collector}

        CAP_{stc} &\text{: Solar thermal collector capacity [kWth]}

        \gamma_{stc} &\text{: instantaneous collector's production [kWh/kWth]}

Storage Model
#############

There are two storages in our system: An electrical energy storage (Storage 1, :math:`bat`) and a thermal energy storage (Storage 2, :math:`tes`).
Below, the equations for the Storage 1 are provided, but Storage 2 follows analogous equations for charge, discharge and bounds.

.. math::
        E_{bat}(t) = E_{bat}(t - 1) + E_{bat,in}(t) \cdot \eta_{bat,in} - \frac{E_{bat,out}}{\eta_{bat,out}} - E_{bat}(t - 1) \cdot \epsilon \qquad  \forall t

.. math::
        CAP_{bat} \cdot SOC_{min} \leq E_{bat}(t) \leq CAP_{bat} \cdot SOC_{max} \qquad  \forall t

        0 \leq E_{bat}(t) - E_{bat}(t - 1) \leq CAP_{bat} \cdot C_{rate,in} \qquad  \forall t

        0 \leq E_{bat}(t - 1) - E_{bat}(t) \leq CAP_{bat} \cdot C_{rate,out} \qquad  \forall t

.. math::
        E_{bat} &\text{: energy stored in the battery at time t}

        E_{bat,in} &\text{: battery charging energy}

        \eta_{bat,in} &\text{: battery charging efficiency}

        E_{bat,out} &\text{: battery discharging energy}

        \eta_{bat,out} &\text{: battery discharging efficiency}

        \epsilon &\text{: decay per time step}

        CAP_{bat} &\text{: battery capacity [kWh]}

        SOC_{min} &\text{: minimum state of charge}

        SOC_{max} &\text{: maximum state of charge}

        C_{rate,in} &\text{: battery charging rate}

        C_{rate,in} &\text{: battery discharging rate}

DC Electricity Bus Equation
###########################

This is an example of a DC bus with a battery, PV and a bi-directional inverter.

.. math::
        E_{pv}(t) + E_{bat,out}(t) \cdot \eta_{bat,out} + E_{rec}(t) \cdot \eta_{rec} - E_{inv}(t) - E_{bat,in} - E_{ex}(t) = 0 \qquad  \forall t

.. math::
        E_{rec} &\text{: rectifier energy}

        \eta_{rec} &\text{: rectifier efficiency}

        E_{inv} &\text{: inverter energy}

AC Electricity Bus Equation
###########################

This describes the local electricity grid and all connected assets:

.. math::
        E_{ts,c}(t) \cdot \eta_{ts,c} + E_{wind}(t) + E_{inv}(t) \cdot \eta_{inv} - E_{ts,c}(t) - E_{rec}(t) - E_{hp}(t) - E_{el}(t) - E_{ex}(t) = 0 \qquad  \forall t

.. math::
        \eta_{ts,c} &\text{: transformer station efficiency}

        \eta_{inv} &\text{: inverter efficiency}

        E_{hp} &\text{: heat pump electrical consumption}

        E_{el} &\text{: electrical load}

Heat Bus Equation
#################

This describes the heat bus and all connected assets:

.. math::
        E_{tes}(t) \cdot \eta_{tes} + E_{turb}(t) \cdot \eta_{turb} + E_{hp}(t) \cdot COP - E_{th}(t) - E_{ex}(t) = 0

.. math::
        \eta_{tes} &\text{: thermal storage efficiency}

        \eta_{turb} &\text{: turbine efficiency}

        COP &\text{: heat pump coefficient of performance}

        E_{th} &\text{: heat load}

NDS3 Bus Equation
#################

The NDS3 Bus is an example of a bus, which does not serve both as in- and output of a storage system.
Instead, the thermal storage is charged from the NDS3 bus, but discharges into the heat bus.

.. math::
        E_{stc}(t) - E_{tes}(t) - E_{ex}(t) = 0

.. math::
        E_{tes} \text{: thermal energy storage}

DS Bus Equation
###############

The DS Bus shows an example of a fuel source providing an energy carrier (biogas) to a transformer (turbine).

.. math::
        E_{heat}(t) - E_{turb}(t) - E_{ex}(t) = 0

.. math::
        E_{heat} &\text{: thermal energy (biogas) production}

        E_{turb} &\text{: turbine (biogas turbine) energy}



Cost calculations
-----------------

The optimization in the MVS is mainly a cost optimization. There are some additional constraints that can be introduced, mainly by adding bounds eg. by limiting the maximum capacity that can be installed (comp. :ref:`maxcap-label`) or adding constraints for certain key performance indicators (see :ref:`constraints-label`). To optimize the energy systems properly, the economic data provided with the input data has to be pre-processed (also see :ref:`economic_precalculation-label`) and then also post-processed when evaluating the results. Following assumptions are important:

* :ref:`Project lifetime <projectduration-label>`: The simulation has a defined project lifetime, for which continuous operation is assumed - which means that the first year of operation is exactly like the last year of operation. Existing and optimized assets have to be replaced to make this possible.
* :ref:`Simulation duration <evaluatedperiod-label>`: It is advisable to simulate whole year to find the most suitable combination of energy assets for your system. Sometimes however you might want to look at specific seasons to see their effect - this is possible in the MVS by choosing a specific start date and simulation duration.
* :ref:`Asset costs <economic_precalculation-label>`: Each asset can have development costs, specific investment costs, specific operation and management costs as well as dispatch costs.
    * *Replacement costs* are calculated based on the lifetime of the assets, and residual values are paid at the end of the project.
    * *Development costs* are costs that will occurr regardless of the installed capacity of an asset - even if it is not installed at all. It stands for system planning and licensing costs. If you have optimized your energy system and see that an asset might not be favourable (zero optimized capacities), you might want to run the simulation again and remove the asset, or remove the development costs of the asset.
    * *Specific investment costs* and *specific operation and maintenance costs* are used to calculate the annual expenditures that an asset has per year, in the process also adding the replacement costs.
    * *Dispatch price* can often be set to zero, but are supposed to cover instances where utilization of an asset requires increased operation and maintenance or leads to wear.
* :ref:`Pre-existing capacities <installedcap-label>`: It is possible to add assets that already exist in your energy system with their capacity and age.
    * *Replacements* - To ensure that the energy system operates continously, the existing assets are replaced with the same capacities when they reached their end of life within the project lifetime.
    * *Replacement costs* are calculated based on the lifetime of the asset in general and the age of the pre-existing capacities
* `Fix project costs <https://github.com/rl-institut/multi-vector-simulator/blob/dev/input_template/csv_elements/fixcost.csv>`__: It is possible to define fix costs of the project - this is important if you want to compare different project locations with each other. You can define...
    * *Development costs*, which could for example stand for the cost of licenses of the whole energy system
    * *(Specific) investment costs*, which could be an investment into land or buildings at the project site. When you define a lifetime for the investment, the MVS will also consider replacements and reimbursements.
    * *(Specific) operation and management costs*, which can cover eg. the salaries of at the project site







Weighting of energy carriers
----------------------------

To be able to calculate sector-wide key performance indicators, it is necessary to assign weights to the energy carriers based on their usable potential. In the conference paper handed in to the CIRED workshop, we have proposed a methodology comparable to Gasoline Gallon Equivalents.

After thorough consideration, it has been decided to base the equivalence in tonnes of oil equivalent (TOE). Electricity has been chosen as a baseline energy carrier, as our pilot sites mainly revolve around it and also because we believe that this energy carrier will play a larger role in the future. For converting the results into a more conventional unit, we choose crude oil as a secondary baseline energy carrier. This also enables comparisons with crude oil price developments in the market. For most KPIs, the baseline energy carrier used is of no relevance as the result is not dependent on it. This is the case for KPIs such as the share of renewables at the project location or its self-sufficiency. The choice of the baseline energy carrier is relevant only for the levelized cost of energy (LCOE), as it will either provide a system-wide supply cost in Euro per kWh electrical or per kg crude oil.

First, the conversion factors to kg crude oil equivalent [`1  <https://www.bp.com/content/dam/bp/business-sites/en/global/corporate/pdfs/energy-economics/statistical-review/bp-stats-review-2019-approximate-conversion-factors.pdf>`__] were determined (see :ref:`table_kgoe_conversion_factors` below). These are equivalent to the energy carrier weighting factors with baseline energy carrier crude oil.

Following conversion factors and energy carriers are defined:

.. _table_kgoe_conversion_factors:

.. list-table:: Conversion factors: kg crude oil equivalent (kgoe) per unit of a fuel
   :widths: 50 25 25
   :header-rows: 1

   * - Energy carrier
     - Unit
     - Value
   * - H2 [`3  <https://www.bp.com/content/dam/bp/business-sites/en/global/corporate/pdfs/energy-economics/statistical-review/bp-stats-review-2020-full-report.pdf>`__]
     - kgoe/kgH2
     - 2.87804
   * - LNG
     - kgoe/kg
     - 1.0913364
   * - Crude oil
     - kgoe/kg
     - 1
   * - Gas oil/diesel
     - kgoe/litre
     - 0.81513008
   * - Kerosene
     - kgoe/litre
     - 0.0859814
   * - Gasoline
     - kgoe/litre
     - 0.75111238
   * - LPG
     - kgoe/litre
     - 0.55654228
   * - Ethane
     - kgoe/litre
     - 0.44278427
   * - Electricity
     - kgoe/kWh(el)
     - 0.0859814
   * - Biodiesel
     - kgoe/litre
     - 0.00540881
   * - Ethanol
     - kgoe/litre
     - 0.0036478
   * - Natural gas
     - kgoe/litre
     - 0.00080244
   * - Heat
     - kgoe/kWh(therm)
     - 0.086
   * - Heat
     - kgoe/kcal
     - 0.0001
   * - Heat
     - kgoe/BTU
     - 0.000025

The values of ethanol and biodiesel seem comparably low in [`1  <https://www.bp.com/content/dam/bp/business-sites/en/global/corporate/pdfs/energy-economics/statistical-review/bp-stats-review-2019-approximate-conversion-factors.pdf>`__] and [`2  <https://www.bp.com/content/dam/bp/business-sites/en/global/corporate/pdfs/energy-economics/statistical-review/bp-stats-review-2020-full-report.pdf>`__] and do not seem to be representative of the net heating value (or lower heating value) that was expected to be used here.

From this, the energy weighting factors using the baseline energy carrier electricity are calculated (see :ref:`table_default_energy_carrier_weights_label`).

.. _table_default_energy_carrier_weights_label:

.. list-table:: Electricity equivalent conversion per unit of a fuel
   :widths: 50 25 25
   :header-rows: 1

   * - Product
     - Unit
     - Value
   * - LNG
     - kWh(eleq)/kg
     - 33.4728198
   * - Crude oil
     - kWh(eleq)/kg
     - 12.6927029
   * - Gas oil/diesel
     - kWh(eleq)/litre
     - 11.630422
   * - Kerosene
     - kWh(eleq)/litre
     - 9.48030688
   * - Gasoline
     - kWh(eleq)/litre
     - 8.90807395
   * - LPG
     - kWh(eleq)/litre
     - 8.73575397
   * - Ethane
     - kWh(eleq)/litre
     - 6.47282161
   * - H2
     - kWh(eleq)/kgH2
     - 5.14976795
   * - Electricity
     - kWh(eleq)/kWh(el)
     - 1
   * - Biodiesel
     - kWh(eleq)/litre
     - 0.06290669
   * - Ethanol
     - kWh(eleq)/litre
     - 0.04242544
   * - Natural gas
     - kWh(eleq)/litre
     - 0.00933273
   * - Heat
     - kWh(eleq)/kWh(therm)
     - 1.0002163
   * - Heat
     - kWh(eleq)/kcal
     - 0.00116304
   * - Heat
     - kWh(eleq)/BTU
     - 0.00029076

With this, the equivalent potential of an energy carrier *E*:sub:`{eleq,i}`, compared to electricity, can be calculated with its conversion factor *w*:sub:`i` as:

.. math::
        E_{eleq,i} = E_{i} \cdot w_{i}

As it can be noticed, the conversion factor between heat (kWh(therm)) and electricity (kWh(el)) is almost 1. The deviation stems from the data available in source [`1  <https://www.bp.com/content/dam/bp/business-sites/en/global/corporate/pdfs/energy-economics/statistical-review/bp-stats-review-2019-approximate-conversion-factors.pdf>`__] and [`2  <https://www.bp.com/content/dam/bp/business-sites/en/global/corporate/pdfs/energy-economics/statistical-review/bp-stats-review-2020-full-report.pdf>`__]. The equivalency of heat and electricity can be a source of discussion, as from an exergy point of view these energy carriers can not be considered equivalent. When combined, say with a heat pump, the equivalency can also result in ripple effects in combination with the minimal renewable factor or the minimal degree of autonomy, which need to be evaluated during the pilot simulations.

:Code:

Currently, the energy carrier conversion factors are defined in `constants.py` with `DEFAULT_WEIGHTS_ENERGY_CARRIERS`. New energy carriers should be added to its list when needed. Unknown carriers raise an `UnknownEnergyVectorError` error.

:Comment:

Please note that the energy carrier weighting factor is not applied dependent on the LABEL of the energy asset, but based on its energy vector. Let us consider an example:

In our system, we have a dispatchable `diesel fuel source`, with dispatch carrying the unit `l Diesel`.
The energy vector needs to be defined as `Diesel` for the energy carrier weighting to be applied, ie. the energy vector of `diesel fuel source` needs to be `Diesel`. This will also have implications for the KPI:
For example, the `degree of sector coupling` will reach its maximum, when the system only has heat demand and all of it is provided by processing diesel fuel. If you want to portrait diesel as something inherent to heat supply, you will need to make the diesel source a heat source, and set its `dispatch costs` to currency/kWh, ie. divide the diesel costs by the heating value of the fuel.

:Comment:

In the MVS, there is no distinction between energy carriers and energy vector. For `Electricity` of the `Electricity` vector this may be self-explanatory. However, the energy carriers of the `Heat` vector can have different technical characteristics: A fluid on different temperature levels. As the MVS measures the energy content of a flow in kWh(thermal) however, this distinction is only relevant for the end user to be aware of, as two assets that have different energy carriers as an output should not be connected to one and the same bus if a detailed analysis is expected. An example of this would be, that a system where the output of the diesel boiler as well as the output of a solar thermal panel are connected to the same bus, eventhough they can not both supply the same kind of heat demands (radiator vs. floor heating).  This, however, is something that the end-user has to be aware of themselves, eg. by defining self-explanatory labels.

Emission factors
----------------

In order to optimise the energy system with minimum emissions, it is important to calculate emission per unit of fuel consumption.

In table :ref:`table_emissions_energyCarriers` the emission factors for energy carriers are defined. These values are based on direct emissions during stationary consumption of the mentioned fuels.

.. _table_emissions_energyCarriers:

.. list-table:: Emission factors: Kg of CO2 equivalent per unit of fuel consumption
   :widths: 50 25 25 25
   :header-rows: 1

   * - Energy carrier
     - Unit
     - Value
     - Source
   * - Diesel
     - kgCO2eq/litre
     - 2.7
     - [`4  <https://www.eib.org/attachments/strategies/eib_project_carbon_footprint_methodologies_en.pdf>`__] Page No. 26
   * - Gasoline
     - kgCO2eq/litre
     - 2.3
     - [`4  <https://www.eib.org/attachments/strategies/eib_project_carbon_footprint_methodologies_en.pdf>`__] Page No. 26
   * - Kerosene
     - kgCO2eq/litre
     - 2.5
     - [`4  <https://www.eib.org/attachments/strategies/eib_project_carbon_footprint_methodologies_en.pdf>`__] Page No. 26
   * - Natural gas
     - kgCO2eq/m3
     - 1.9
     - [`4  <https://www.eib.org/attachments/strategies/eib_project_carbon_footprint_methodologies_en.pdf>`__] Page No. 26
   * - LPG
     - kgCO2eq/litre
     - 1.6
     - [`4  <https://www.eib.org/attachments/strategies/eib_project_carbon_footprint_methodologies_en.pdf>`__] Page No. 26
   * - Biodiesel
     - kgCO2eq/litre
     - 0.000125
     - [`5  <https://www.mfe.govt.nz/sites/default/files/media/Climate%20Change/2019-emission-factors-summary.pdf>`__] Page No. 6
   * - Bioethanol
     - kgCO2eq/litre
     - 0.0000807
     - [`5  <https://www.mfe.govt.nz/sites/default/files/media/Climate%20Change/2019-emission-factors-summary.pdf>`__] Page No. 6
   * - Biogas
     - kgCO2eq/m3
     - 0.12
     - [`6 <https://www.winnipeg.ca/finance/findata/matmgt/documents/2012/682-2012/682-2012_Appendix_H-WSTP_South_End_Plant_Process_Selection_Report/Appendix%207.pdf>`__] Page No. 1

In table :ref:`table_CO2_emissions_countries` the CO2 emissions for Germany and the four pilot sites (Norway, Spain, Romania, India) are defined:

.. _table_CO2_emissions_countries:

.. list-table:: CO2 Emission factors: grams of CO2 equivalent per kWh of electricity consumption
   :widths: 50 25 25 25
   :header-rows: 1

   * - Country
     - Unit
     - Value
     - Source
   * - Germany
     - gCO2eq/kWh
     - 338
     - [`7 <https://www.eea.europa.eu/data-and-maps/indicators/overview-of-the-electricity-production-3/assessment>`__] Fig. 2
   * - Norway
     - gCO2eq/kWh
     - 19
     - [`7 <https://www.eea.europa.eu/data-and-maps/indicators/overview-of-the-electricity-production-3/assessment>`__] Fig. 2
   * - Spain
     - gCO2eq/kWh
     - 207
     - [`7 <https://www.eea.europa.eu/data-and-maps/indicators/overview-of-the-electricity-production-3/assessment>`__] Fig. 2
   * - Romania
     - gCO2eq/kWh
     - 293
     - [`7 <https://www.eea.europa.eu/data-and-maps/indicators/overview-of-the-electricity-production-3/assessment>`__] Fig. 2
   * - India
     - gCO2eq/kWh
     - 708
     - [`8 <https://www.climate-transparency.org/wp-content/uploads/2019/11/B2G_2019_India.pdf>`__] Page No. 7

The values mentioned in the table above account for emissions during the complete life cycle. This includes emissions during energy production, energy conversion, energy storage and energy transmission.


.. _verification_of_inputs:

Input verification
------------------

The inputs for a simulation with the MVS are subjected to a couple of verification tests to make sure that the inputs result in valid oemof simulations. This should ensure:

- Uniqueness of labels (`C1.check_for_label_duplicates`): This function checks if any LABEL provided for the energy system model in dict_values is a duplicate. This is not allowed, as oemof can not build a model with identical labels.

- No levelized costs of generation lower than feed-in tariff of same energy vector in case of investment optimization (`optimizeCap` is True) (`C1.check_feedin_tariff_vs_levelized_cost_of_generation_of_providers`):  Raises error if feed-in tariff > levelized costs of generation if `maximumCap` is None for energy asset in ENERGY_PRODUCTION. This is not allowed, as oemof otherwise may be subjected to an unbound problem, ie. a business case in which an asset should be installed with infinite capacities to maximize revenue. If maximumCap is not None a logging.warning is shown as the maximum capacity of the asset will be installed.

- No feed-in tariff higher then energy price from an energy provider (`C1.check_feedin_tariff_vs_energy_price`): Raises error if feed-in tariff > energy price of any asset in 'energyProvider.csv'. This is not allowed, as oemof otherwise is subjected to an unbound and unrealistic problem, eg. one where the owner should consume electricity to feed it directly back into the grid for its revenue.

- Assets have well-defined energy vectors and belong to an existing bus (`C1.check_if_energy_vector_of_all_assets_is_valid`):     Validates for all assets, whether 'energyVector' is defined within DEFAULT_WEIGHTS_ENERGY_CARRIERS and within the energyBusses.

- Energy carriers used in the simulation have defined factors for the electricity equivalency weighting (`C1.check_if_energy_vector_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS`): Raises an error message if an energy vector is unknown. It then needs to be added to the DEFAULT_WEIGHTS_ENERGY_CARRIERS in constants.py

- An energy bus is always connected to one inflow and one outflow (`C1.check_for_sufficient_assets_on_busses`): Validating model regarding busses - each bus has to have 2+ assets connected to it, exluding energy excess sinks

- Time series of energyProduction assets that are to be optimized have specific generation profiles (`C1.check_non_dispatchable_source_time_series`, `C1.check_time_series_values_between_0_and_1`): Raises error if time series of non-dispatchable sources are not between [0, 1].

- Provided timeseries are checked for `NaN` values, which are replaced by zeroes (`C0.replace_nans_in_timeseries_with_0`).

- Asset capacities connected to each bus are sized sufficiently to fulfill the maximum demand (`C1.check_energy_system_can_fulfill_max_demand`): Logs a logging.warning message if the aggregated installed capacity and maximum capacity (if applicable) of all conversion, generation and storage assets connected to one bus is smaller than the maximum demand. The check is applied to each bus of the energy system. Check passes when the potential peak supply is larger then or equal to the peak demand on the bus, or if the maximum capacity of an asset is set to None when optimizing.
