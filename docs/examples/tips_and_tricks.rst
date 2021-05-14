.. _tips_and_tricks:

Tips & Tricks
#############



.. _tip_sunk_costs:

Including sunk costs for previous investments into specific assets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Usually, the investments into existing capacities are neglected and assumed to be sunk costs of the system. The existing capacity :code:`installedCap` as well as the age of the installed asset :code:`age_installed` are only used to calculate when necessary re-investments take place, and how high the :ref:`replacements costs <Cost_calculations>` are. But there is no option if one wants to optimize a system with pre-existing capacities of certain assets and still account for the installation costs that happened before the first time step of the simulation.

When optimizing a system with pre-existing capacities of certain assets, it can be usefull for the user to implement the installation costs of these assets in the economic evaluation. This trick triggers the replacement of those assets, thus accounting for investments costs of pre-existing assets in the scenario.

With the trick presented here, it is possible to optimize a system with a specific or a specific minimal capacity of a certain asset and still account for installation costs of the asset at the beginning of the project (in the idea of a greenfield / brownfield optimization). The presented trick works for energy production assets as well as energy conversion assets.

To apply this trick, the following manipulations must be applied to the input parameters of the asset in question:

* :code:`optimizeCap` to False

* :code:`installedCap` to the specific existing capacity

* :code:`aged_installed` to the lifetime of the asset

Previous investment costs into now pre-existing asset capacities are now taken into account in the economic evaluation of a scenario.


