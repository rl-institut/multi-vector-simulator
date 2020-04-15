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


Technical data
--------------

Energy flows (aggregated) per asset
###################################

Renewable share (RES)
#####################

Describes the share of the MES demand that is supplied from renewable sources.

.. math::
  RES ={\sum_i {E_{RES,generation} (i)⋅w_i}}/{\sum_j {E_{generation}(j)⋅w_j}+\sum_k {E_{grid} (k)}}

** The content of this section was copied from the conference paper handed in to CIRED 2020**

CO2 Emissions
#############

The total C02 emissions of the MES in question can be calculated
with all aggregated energy flows from the generation assets and their subsequent emission factor:

** The content of this section was copied from the conference paper handed in to CIRED 2020**

Degree of autonomy (DA)
#######################

The DA represents the level of autonomy that the MES has from potential supply from a distribution system operators (DSO).
DA close to zero shows high dependence on the DSO,
while a DA of 1 represents an autonomous or net-energy system
and a DA higher 1 a plus-energy system.
As above, we apply a weighting based on Electricity Equivalent.

** The content of this section was copied from the conference paper handed in to CIRED 2020**


Degree of sector-coupling
#########################

While a MES includes multiple energy carriers,
this fact does not define how strongly interconnected its sectors are.
To measure this, we propose to compare the energy flows in between the sectors to the energy demand supplied:


** The content of this section was copied from the conference paper handed in to CIRED 2020**

Onsite energy fraction
######################

Onsite energy matching
######################
