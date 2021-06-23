.. _multiple_busses_example:

Using multiple in- or output busses
###################################

Sometimes, you may want to have multiple input- our output busses connected to an energy conversion asset.
This is for example the case if you want to implement an electrolyzer with a transformer,
and want to track water consumption at the same time as you want to track electricity consumption.

You can define this, again, in the csv´s.
Here, you would insert a list of your parameters instead of the scalar value of a parameter:

    "[0.99, 0.98]"

The apostrophes are necessary to also input in your csv, as otherwise the comma might be interpreted as a cell seperator and destroy your csv formatting.
This could be an example of a transformer with two efficiencies.

You can also wrap multiple inputs/outputs with scalars that are defined as efficiencies.
For that, you define one or multiple of the parameters within the list with the above introduced dictionary:

    "[0.99, {'value': {'file_name': 'your_file_name.csv', 'header': 'your_header'}, 'unit': 'your_unit'}]"

.. warning::
    If you define an output- or input flow with with a list, you also have to define related parameters as a list.

If you are defining the :ref:`inflow_direction <inflowdirection-label>` as a list, you must also define

- The :ref:`efficiency <efficiency-label>`: The efficiency then defines the ratio of the two input flows to generate the output flow.

If you are defining the :ref:`outflow_direction <outflowdirection-label>` as a list, you must also define

- The :ref:`efficiency <efficiency-label>`: The efficiency then defines the ratio of the input flow and the specific produced output flow.

- The :ref:`dispatch_price <dispatchprice-label>` relative to the subsequent output flows

- The :ref:`energyVector <energyvector-label>` according to the energyVector of the subsequent output flows.

.. warning::

    You can not have multiple inflow and outflow directions at the same time!

.. note::
    The appropriateness of inputs is tested with :func:`C1.check_if_that_no_parameters_are_defined_as_lists_for_assets_where_it_is_not_allowed() <multi_vector_simulator.C1_verification.check_if_that_no_parameters_are_defined_as_lists_for_assets_where_it_is_not_allowed>` and :func:`C1.check_if_all_parameters_for_multiple_inflow_outflow_directions_are_provided() <multi_vector_simulator.C1_verification.check_if_all_parameters_for_multiple_inflow_outflow_directions_are_provided>`.

You can see an implemented example here, where the heat pump has a time-dependent efficiency:

.. csv-table:: Example for defining a component with multiple inputs/outputs
   :file: ../files_to_be_displayed/example_multiple_inputs_energyConversion.csv
   :widths: 70, 30, 50
   :header-rows: 1

The features were integrated with `Pull Request #63 <https://github.com/rl-institut/multi-vector-simulator/pull/63>`__.
For more information, you might also reference following issues:

- Parameters can now be a list of values, eg. efficiencies for two busses or multiple input/output vectors(`Issue #52 <https://github.com/rl-institut/multi-vector-simulator/issues/52>`__)

- Parameters can now be defined as a list as well as as a timeseries (`Issue #52 <https://github.com/rl-institut/multi-vector-simulator/issues/52>`__, `Issue #82 <https://github.com/rl-institut/multi-vector-simulator/issues/82>`__)
