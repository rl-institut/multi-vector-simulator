======================
Set of Model Equations
======================

Economic Dispatch
-----------------

Linear programming is a mathematical modelling and optimization technique for a system of a linear objective function subject to linear constraints. The goal of a linear programming problem is to find the optimal value for the objective function, be it a maximum or a minimum. The MVS is based on oemof-solph, which in turn uses Pyomo to create a linear problem. The economic dispatch problem in the MVS has the objective of minimizing the production cost by allocating the total demand among the generating units at each time step. The equation is the following:

.. math::
        min Z = \sum_i a_i \cdot CAP_i + \sum_i \sum_t c_{var,i} \cdot E_i(t)
.. math::        
        CAP_i \geq 0
.. math::        
        E_i(t) \geq 0  \qquad  \forall t
        
.. math::
        i \text{: asset}

        a_i \text{: asset annuity [currency/kWp/year, currency/kW/year, currency/kWh/year]}

        CAP_i \text{: asset capacity [kWp, kW, kWh]}

        c_{var,i} \text{: variable operational or dispatch cost [currency/kWh, currency/L]}

        E_i(t) \text{: asset dispatch [kWh]}

The annual cost function of each asset includes the capital expenditure (investment cost) and residual value, as well as the operating expenses of each asset. It is expressed as follows:

.. math:: 
        a_i = \left( capex_i + \sum_{k=1}^{n} \frac{capex_i}{(1+d)^{k \cdot t_a}} - c_{res,i} \right) \cdot CRF(T) + opex_i
.. math:: 
        CRF(T) = \frac{d \cdot (1+d)^T}{(1+d)^t - 1}
        
.. math::
        capex_i \text{: specific investment costs [currency/unit]}

        n \text{: number of replacements of an asset within project lifetime T}

        t_a \text{: asset lifetime [years]}

        CRF \text{: capital recovery factor}

        c_{res,i} \text{: residual value of asset i at the end of project lifetime T [currency/unit]}

        opex_i \text{: annual operational and management costs [currency/unit/year]}

        d \text{: discount factor}

        T \text{: project lifetime [years]}

The CRF is a ratio used to calculate the present value of the the annuity. The discount factor can be replaced by the weighted average cost of capital (WACC), calculated by the user. 

The lifetime of the asset t\ :sub:`a`\  and the lifetime of the project T can be different from each other; hence, the number of replacements n is estimated using the equation below:

.. math::
        n = round \left( \frac{T}{t_a} + 0.5 \right) - 1
        
The residual value is also known as salvage value and it represents an estimate of the monetary value of an asset at the end of the project lifetime T. The MVS considers a linear depreciation over T and accounts for the time value of money by using the following equation:

.. math::
        c_{res,i} = \frac{capex_i}{(1+d)^{n \cdot t_a}} \cdot \frac{1}{T} \cdot \frac{(n+1) \cdot t_a - T}{(1+d)^T}


Energy Balance Equation
-----------------------

One main constraint that the optimization model is subject to is the energy balance equation. The latter maintains equality between the incoming energy into a bus and the outgoing energy from that bus. This balancing equation is applicable to all bus types, be it electrical, thermal, hydrogen or for any other energy carrier.

.. math::
        \sum E_{in,i}(t) - \sum E_{out,j}(t) = 0 \qquad  \forall t

.. math::

        E_{in,i} \text{: energy flowing from asset i to the bus}

        E_{out,j} \text{: energy flowing from the bus to asset j}

It is very important to note that assets i and j can be the same asset (e.g., battery) however, one of the energy flowing values E_{in} or E_{out} should be zero at the same time step t.


Example: Sector Coupled Energy System Scenario
----------------------------------------------

In order to understand the component models, a generic sector coupled example in shown in the next figure. It brings together the electricity and heat sector through Transformer 4 as it connects the two sector buses. 

.. image:: images/23-10-2020_sector_coupled_example.png
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

All grids and dispatchable sources are assumed to be available 100% of the time with no consumption limits. The MVS includes a sink component for excess energy, connected to each bus in the system and denoted by E\ :sub:`ex`\  in the equations. This excess sink accounts for the extra energy in the system that has to be dumped.

Electricity Grid Equation
#########################

.. math::
        E_{grid,c}(t) - E_{grid,f}(t) + E_{ts,f}(t) \cdot \eta_{ts,f} - E_{ts,c}(t) = 0 \qquad  \forall t
        
.. math::
        E_{grid,c} \text{: energy consumption from the electricity grid}
        
        E_{grid,f} \text{: energy feed into the electricity grid}
        
        E_{grid,c} \text{: transformer station feed-in}
        
        \eta_{ts,f} \text{: transformer station efficiency}
        
        E_{grid,c} \text{: transformer station consumption}
 
Non-Dispatchable Source Equations
#################################

.. math::   
        E_{wind}(t) = CAP_{wind} \cdot \alpha_{wind}(t) \qquad  \forall t
        
        E_{pv}(t) = CAP_{pv} \cdot \beta_{pv}(t) \qquad  \forall t

.. math::
        E_{wind} \text{: energy generated from the wind turbine}
        
        CAP_{wind} \text{: wind turbine capacity [kW]}

        \alpha_{wind} \text{: instantaneous wind turbine performance metric [kWh/kW]}
        
        E_{pv} \text{: energy generated from the PV panels}
        
        CAP_{pv} \text{: PV panel capacity [kWp]}

        \beta_{pv} \text{: instantaneous PV specific yield [kWh/kWp]}
        
Battery Storage Model
#####################

.. math::   
        E_{bat}(t) = E_{bat}(t - 1) + E_{bat,in}(t) \cdot \eta_{bat,in} - \frac{E_{bat,out}}{\eta_{bat,out}} - E_{bat}(t - 1) \cdot \epsilon \qquad  \forall t
        
        CAP_{bat} \cdot SOC_{min} \leq E_{bat}(t) \leq CAP_{bat} \cdot SOC_{max} \qquad  \forall t
        
        0 \leq E_{bat}(t) - E_{bat}(t - 1) \leq CAP_{bat} \cdot C_{rate,in} \qquad  \forall t
        
        0 \leq E_{bat}(t - 1) - E_{bat}(t) \leq CAP_{bat} \cdot C_{rate,out} \qquad  \forall t

.. math::
        E_{bat} \text{: energy stored in the battery at time t}
        
        E_{bat,in} \text{: battery charging energy}
        
        \eta_{bat,in} \text{: battery charging efficiency}
        
        E_{bat,out} \text{: battery discharging energy}
        
        \eta_{bat,out} \text{: battery discharging efficiency}
        
        \epsilon \text{: decay per time step}
        
        \CAP_{bat} \text{: battery capacity [kWh]}
        
        SOC_{min} \text{: minimum state of charge}
        
        SOC_{max} \text{: maximum state of charge}
        
        C_{rate,in} \text{: battery charging rate}
        
        C_{rate,in} \text{: battery discharging rate}
 
DC Electricity Bus Equation
###########################

.. math::   
        E_{pv}(t) + E_{bat,out}(t) \cdot \eta_{bat,out} + E_{rec}(t) \cdot \eta_{rec} - E_{inv}(t) - E_{bat,in} - E_{ex}(t) = 0 \qquad  \forall t

.. math::
        E_{rec} \text{: rectifier energy}
        
        \eta_{rec} \text{: rectifier efficiency}
        
        E_{inv} \text{: inverter energy}
        
        \eta_{rec} \text{: inverter efficiency}
