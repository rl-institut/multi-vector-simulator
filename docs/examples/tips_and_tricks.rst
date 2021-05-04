.. _tips_and_tricks:

Tips & Tricks
#############



.. _tip_sunk_costs:

Including sunk costs for previous investments into specific assets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to include the previous investment costs into now pre-existing asset capacities in the economic evaluation of a scenario. For this, following trick can be applied to the input data of the asset in question, by setting:
* :code:`optimizeCap` to False
* :code:`installedCap` to the specific existing capacity
* :code:`aged_installed` to the lifetime of the asset
With this, it is possible to optimize a system with a specific or a specific minimal capacity of a certain asset and still account for installation costs of the asset at the beginning of the project (in the idea of a greenfield / brownfield optimization). This can work for energy production assets as well as energy conversion assets.
Usually, the investments into existing capacities are neglected and assumed to be sunk costs of the system. The existing capacity :code:`installedCap` as well as the age of the installed asset:code:`age_installed` are only used to calculate when necessary re-investments take place, and how high the :ref:`replacements costs <Cost_calculations>` are.

