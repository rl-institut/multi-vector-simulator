======================
Set of Model Equations
======================

Economic Dispatch
-----------------

Linear programming is a mathematical modelling and optimization technique for a system of a linear objective function subject to linear constraints. The goal of a linear programming problem is to find the optimal value for the objective function, be it a maximum or a minimum. The MVS is based on oemof-solph, which in turn uses Pyomo to create a linear problem. The economic dispatch problem in the MVS has the objective of minimizing the production cost by allocating the total demand among the generating units. The equation is the following:

.. math::
        min Z = \sum_i a_i \cdot CAP_i + \sum_i \sum_t c_{var,i} \cdot E_i(t)
.. math::        
        CAP_i \geq 0
.. math::        
        E_i(t) \geq 0  \qquad  \forall t

i: asset

a~i: asset annuity [currency/kWp/year, currency/kW/year, currency/kWh/year]

CAP~i: assetcapacity [kWp, kW, kWh]

c~{var,i}: variable operational or dispatch cost [currency/kWh, currency/L]

E~i(t): asset dispatch [kWh]

The annual cost function of each asset includes the capital expenditure (investment cost) and residual value, as well as the operating expenses of each asset. It is expressed as follows:

.. math:: 
        a_i = \left( capex_i + \sum_{k=1}^{n} \frac{capex_i}{(1+d)^{k \cdot t_a}} - c_{res,i} \right) \cdot CRF(T) + opex_i
.. math:: 
        CRF(T) = \frac{d \cdot (1+d)^T}{(1+d)^t - 1}

capex~i: specific investment costs [currency/unit]

n: number of replacements of an asset within project lifetime T

t~a: asset lifetime [years]

CRF: capital recovery factor

c~{res,i}: residual value of asset i at the end of project lifetime T [currency/unit]

opex~i: annual operational and management costs [currency/unit/year]

d: discount factor

T: project lifetime [years]
