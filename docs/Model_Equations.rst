======================
Set of Model Equations
======================

Economic Dispatch
-----------------

Linear programming is a mathematical modelling and optimization technique for a system of a linear objective function subject to linear constraints. The goal of a linear programming problem is to find the optimal value for the objective function, be it a maximum or a minimum. The MVS is based on oemof-solph, which in turn uses Pyomo to create a linear problem. The economic dispatch problem in the MVS has the objective of minimizing the production cost by allocating the total demand among the generating units. The equation is the following:

.. math::
        min Z = \sum_i a_i \cdot CAP_i + \sum_i \sum_t c_{var,i} \cdot E_i(t)
        CAP_i \geq 0
        E_i(t) \geq 0    \forall t

        i: asset
        a_i: asset annuity [currency/kWp/year, currency/kW/year, currency/kWh/year]
        CAP_i: assetcapacity [kWp,kW,kWh]
        c_{var,i}: variable operational or dispatch cost [currency/kWh, currency/L]
        E_i(t): asset dispatch [kWh]
