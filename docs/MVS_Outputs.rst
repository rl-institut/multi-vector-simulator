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

Levelized Cost of Energy of Asset (LCOE ASSET)
##############################################

This KPI measures the cost of generating 1 kWh for each asset in the system.
It can be used to assess and compare the available alternative methods of energy production.
The levelized cost of energy of an asset (LCOE ASSET) is usually obtained
by looking at the lifetime costs of building and operating the asset per unit of total energy throughput of an asset
over the assumed lifetime [currency/kWh].

Since not all assets are production assets, the MVS distinguishes between the type of assets.
For assets in energyConversion and energyProduction the MVS calculates the LCOE ASSET
by dividing the total annuity :math:`a_i` of the asset :math:`i` by the total flow :math:`\sum{t} E_i(t)`.

.. math::
        LCOE~ASSET_i = \frac{a_i}{\sum^{t} E_i(t)}
  
For assets in energyStorage, the MVS sums the annuity for `storage capacity` :math:`a_{i,sc}`, `input power` $a_{i,ip}$ and `output power` :math:`a_{i,op}` and divides it by the `output power` total flow :math:`\sum{t} E_{i,op}(t)`.

.. math::
        LCOE~ASSET_i = \frac{a_{i,sc} + a_{i,ip} + a_{i,op}}{\sum^{t}{E_{i,op}(t)}}

If the total flow is 0 in any of the previous cases, then the LCOE ASSET is set to None.

.. math::
        LCOE~ASSET{i} = None
  
For assets in energyConsumption, the MVS outputs 0 for the LCOE ASSET.

.. math::
        LCOE~ASSET{i} = 0


Technical data
--------------

Energy flows (aggregated) per asset
###################################

Renewable share (RES)
#####################

Describes the share of the MES demand that is supplied from renewable sources.

.. math::
        RES &=\frac{\sum_i {E_{RES,generation} (i) \cdot w_i}}{\sum_j {E_{generation}(j) \cdot w_j}+\sum_k {E_{grid} (k)}}

        \text{with~} &i \epsilon \text{[PV,Geothermal,…]}

        &j \epsilon \text{[generation assets 1,2,…]}

        &k \epsilon \text{[DSO 1,2…]}

** The content of this section was copied from the conference paper handed in to CIRED 2020**

CO2 Emissions
#############

The total C02 emissions of the MES in question can be calculated
with all aggregated energy flows from the generation assets and their subsequent emission factor:

.. math::
        CO2 Emissions &= \sum_i {E_{gen} (i) \cdot CO2_{eq} (i)}

        \text{with~} &i \epsilon \text{[generation assets 1,2,…]}

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
        DSC & =\frac{\sum_{i,j}{E_{conversion} (i,j) \cdot w_i}}{\sum_i {E_{demand} (i) \cdot w_i}}

        \text{with~} & i,j \epsilon \text{[Electricity,H2…]}

** The content of this section was copied from the conference paper handed in to CIRED 2020**

Self consumption (SC)
###############################

The self-consumption describes the fraction of all renewable energy that is consumed by the system itself.

.. math::
        SC &=\frac{\sum_{i,j} {E_{generation} (i,j) \cdot w_i} - E_{gridfeedin}(i,j) \cdot w_i}{\sum_{i,j} {E_{generation} (i,j) \cdot w_i}}

        \text{with~} &i \epsilon \text{[PV,Geothermal,…]}

        &j \epsilon \text{[generation assets 1,2,…]}

[1] https://www.sciencedirect.com/science/article/pii/S0960148119315216
[2] https://www.iip.kit.edu/downloads/McKennaetal_paper_full.pdf

self_sufficiency (SS)
###############################

The self sufficiency describes the fraction of the total demand that can be covered by renewable generated energy see [1] and [2]

.. math::
        SS &=\frac{\sum_{i,j} {E_{generation} (i,j) \cdot w_i} - E_{gridfeedin}(i,j) \cdot w_i}{\sum_i {E_{demand} (i) \cdot w_i}}

        \text{with~} &i \epsilon \text{[PV,Geothermal,…]}

        &j \epsilon \text{[generation assets 1,2,…]}


Electrical Autonomy (EA)
###############################

The degree of electrical autonomy describes the relation of the total renewale generated energy to the total demand of the system. See [2]

.. math::
        EA &=\frac{\sum_{i,j} {E_{generation} (i,j) \cdot w_i}}{\sum_i {E_{demand} (i) \cdot w_i}}

        \text{with~} &i \epsilon \text{[PV,Geothermal,…]}

        &j \epsilon \text{[generation assets 1,2,…]}


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
