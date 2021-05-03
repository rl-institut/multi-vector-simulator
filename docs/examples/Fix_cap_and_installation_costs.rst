.. _costs_examples:

Installation costs with existing capacity of certain assets
###########################################################

This trick can be used if one wants to optimize a system with a fix capacity of certain assets and still count for installation costs. This trick works by setting the optimizeCap to False , the installedCap to the specific capacity and the aged_installed equal to the lifetime of the asset. It is then possible to optimize a system with a specific capacity of certain assets and still account for installation costs of the assets at the first timestep (in the idea of a greenfield / brownfield optimization). This can work for Production assets as well as Conversion assets.