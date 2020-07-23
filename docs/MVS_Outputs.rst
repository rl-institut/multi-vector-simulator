=============================
Outputs of the MVS simulation
=============================

System schematic
----------------

- plot_networkx_graph

Optimized dispatch
------------------

Dispatch of all assets (timeseries)
###################################

Energy flows on each bus (graphic)
##################################

Optimal capacities
------------------


Cost data
---------

Net present cost
################

The Net present cost (NPC) is the present value of all the costs associated with installation, operation,
maintenance and replacement of energy technologies comprising the sector-coupled system over the project lifetime,
minus the present value of all the revenues that it earns over the project lifetime.
The capital recovery factor (CRF) is used to calculate the present value of the cash flows.

** The content of this section was copied from the conference paper handed in to CIRED 2020**

Levelized costs of energy (LCOE)
################################

As a sector-coupled system connects energy vectors,
not the costs associated to each individual energy carrier but the overall energy costs should be minimized.
Therefore, we propose a new KPI:
The levelized costs of energy (LCOEnergy) aggregates the costs for energy supply
and distributes them over the total energy demand supplied,
which is calculated by weighting the energy carriers by their energy content.
To determine the weighting factors of the different energy carriers,
we reference the method of gasoline gallon equivalent (GGE) [12],
which enables the comparison of alternative fuels.
Instead of comparing the energy carriers of an MES to gasoline,
we rebase the factors introduced in [12] onto the energy carrier electricity,
thus proposing a unit Electricity Equivalent (ElEq).
The necessary weights are summarized in Table 1.
With this, we propose to calculate LCOEnergy based on the annual energy demand and the systems annuity,
calculated with the CRF, as follows:


Specific electricity supply costs, eg. levelized costs of electricity (LCOElectricity) are a common KPI
that can be compared to local prices or generation costs.
As in a sector-coupled system the investments cannot be clearly distinguished into sectors,
we propose to calculate the levelized costs of energy carriers by distributing the costs relative to supplied demand.
The LCOElectricity are then calculated with:


** The content of this section was copied from the conference paper handed in to CIRED 2020**

Levelized Cost of Energy of Asset (LCOE_ASSET)
################################

This KPI measures the cost of generating 1 kWh for each asset in the system. It can be used to assess and compare the available alternative methods of energy production. The levelized cost of energy of an asset (LCOE_ASSET) is usually obtained by looking at the lifetime costs of building and operating the asset per unit of total energy throughput of an asset over the assumed lifetime [currency/kWh].  

Since not all assets are production assets, the MVS distinguishes between the type of assets. For assets in energyConversion and energyProduction the MVS calculates the LCOE_ASSET by dividing the total annuity $a_i$ of the asset $i$ by the total flow $\sum{t} E_i(t)$.

.. math::
  LCOE\_ASSET{i} = \frac{a_i}{\sum^{t} E_i(t)} 
  
For assets in energyStorage, the MVS sums the annuity for "storage capacity" $a_i_sc$, "input power" $a_i_ip$ and "output power" $a_i_op$ and divides it by the "output power" total flow $\sum{t} E_i_op(t)$.

.. math::
  LCOE\_ASSET{i} = \frac{a_i_sc + a_i_ip + a_i_op}{\sum^{t} E_i_op(t)} 

If the total flow is 0 in any of the previous cases, then the LCOE_ASSET is set to None.

.. math::
  LCOE\_ASSET{i} = None
  
For assets in energyConsumption, the MVS outputs 0 for the LCOE_ASSET.

.. math::
  LCOE\_ASSET{i} = 0


Technical data
--------------

Energy flows (aggregated) per asset
###################################

Renewable share (RES)
#####################

Describes the share of the MES demand that is supplied from renewable sources.

.. math::
  RES =\frac{\sum_i {E_{RES,generation} (i)⋅w_i}}{\sum_j {E_{generation}(j)⋅w_j}+\sum_k {E_{grid} (k)}}
  with i \epsilon [PV,Geothermal,…]
  and j \epsilon [generation assets 1,2,…]
  and  k \epsilon [DSO 1,2…]

** The content of this section was copied from the conference paper handed in to CIRED 2020**

CO2 Emissions
#############

The total C02 emissions of the MES in question can be calculated
with all aggregated energy flows from the generation assets and their subsequent emission factor:

.. math::
  CO2 Emissions= \sum_i {E_{gen} (i)⋅CO2_{eq} (i)}
  with i \epsilon [generation assets 1,2,…]

** The content of this section was copied from the conference paper handed in to CIRED 2020**

Degree of autonomy (DA)
#######################

The DA represents the level of autonomy that the MES has from potential supply from a distribution system operators (DSO).
DA close to zero shows high dependence on the DSO,
while a DA of 1 represents an autonomous or net-energy system
and a DA higher 1 a plus-energy system.
As above, we apply a weighting based on Electricity Equivalent.

** The content of this section was copied from the conference paper handed in to CIRED 2020**


Degree of sector-coupling (DSC)
###############################

While a MES includes multiple energy carriers,
this fact does not define how strongly interconnected its sectors are.
To measure this, we propose to compare the energy flows in between the sectors to the energy demand supplied:

.. math::
   DSC=\frac{\sum_{i,j}{E_{conversion} (i,j)⋅w_i}}{\sum_i {E_{demand} (i)⋅w_i}}
   with i,j \epsilon [Electricity,H2…]

** The content of this section was copied from the conference paper handed in to CIRED 2020**

Onsite energy fraction
######################

Onsite energy matching
######################

Automatic Report
-----------------
MVS has a feature to automatically generate a PDF report that contains the main elements from the input data as well as the simulation results' data.
The report can also be viewed as a web app on the browser, which provides some interactivity.

MVS version number, the branch ID and the simulation date are provided as well in the report, under the MVS logo.
A commit hash number is provided at the end of the report in order to prevent the erraneous comparing results from simulations using different versions.

It includes several tables with project data, simulation settings, the various demands supplied by the user, the various components of the system and the optimization results such as the energy flows and the costs.
The report also provides several plots which help to visualize the flows and costs. The PDF report can be generated by running the command (details in the READTHEDOCS `here <https://github.com/rl-institut/mvs_eland/blob/dev/README.md#generate-report>`_)::

    python mvs_report.py
