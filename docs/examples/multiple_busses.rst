.. _multiple_busses_example:

Using multiple in- or output busses
###################################

Sometimes, you may also want to have multiple input- our output busses connected to a component.
This is for example the case if you want to implement an electrolyzer with a transformer,
and want to track water consumption at the same time as you want to track electricity consumption.

You can define this, again, in the csv´s.
Here, you would insert a list of your parameters instead of the scalar value of a parameter:

    [0.99, 0.98]

Would be an example of a transformer with two efficiencies.

You can also wrap multiple inputs/outputs with scalars that are defined as efficiencies.
For that, you define one or multiple of the parameters within the list with the above introduced dictionary:

    [0.99, {'value': {'file_name': 'your_file_name.csv', 'header': 'your_header'}, 'unit': 'your_unit'}]

If you define an output- or input flow with with a list,
you also have to define related parameters as a list.
So, for example, if you define the input direction as a list for an energyConsumption asset,
you need to define the efficiencies and dispatch_price costs as a list as well.

You can see an implemented example here, where the heat pump has a time-dependent efficiency:

.. csv-table:: Example for defining a component with multiple inputs/outputs
   :file: ../files_to_be_displayed/example_multiple_inputs_energyConversion.csv
   :widths: 70, 30, 50
   :header-rows: 1

The features were integrated with `Pull Request #63 <https://github.com/rl-institut/multi-vector-simulator/pull/63>`__.
For more information, you might also reference following issues:

- Parameters can now be a list of values, eg. efficiencies for two busses or multiple input/output vectors(`Issue #52 <https://github.com/rl-institut/multi-vector-simulator/issues/52>`__)

- Parameters can now be defined as a list as well as as a timeseries (`Issue #52 <https://github.com/rl-institut/multi-vector-simulator/issues/52>`__, `Issue #82 <https://github.com/rl-institut/multi-vector-simulator/issues/82>`__)
