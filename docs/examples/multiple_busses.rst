.. _multiple_busses_example:

Using multiple in- or output busses
###################################

Sometimes, you may also want to have multiple input or output busses connected to a component.
This is for example the case if you want to model an electrolyzer with a transformer,
and want to track water consumption at the same time as you want to track electricity consumption.

You can define this, again, in the csv´s.
First you should provide the input, or output, busses as a list for the :ref:`conversion` parameter of :ref:`inflowdirection-label` or :ref:`outflowdirec-label` resp.:

    "[h2o_bus, electricity_bus]"


Then you need to provide the :ref:`efficiencies <efficiency-label>` and :ref:`dispatch prices <dispatchprice-label>` respective to each bus,
for example:

    "[0.99, 0.98]"

You can also provide a timeseries for one or both values. To do so, you can simply use the notation introduced in :ref:`time_series_params_example`:

    "[0.99, {'value': {'file_name': 'your_file_name.csv', 'header': 'your_header'}, 'unit': 'your_unit'}]"


You can see an example here, with an electrolyzer :

.. csv-table:: Example for defining a component with multiple inputs/outputs
   :escape: '
   :file: ../files_to_be_displayed/example_multiple_inputs_energyConversion.csv
   :widths: 70, 30, 50
   :header-rows: 1

The features were integrated with `Pull Request #63 <https://github.com/rl-institut/multi-vector-simulator/pull/63>`__ and `Pull Request #949 <https://github.com/rl-institut/multi-vector-simulator/pull/949>`__.

For more information, you might also reference following issues:

- Parameters can now be a list of values, eg. efficiencies for two busses or multiple input/output vectors(`Issue #52 <https://github.com/rl-institut/multi-vector-simulator/issues/52>`__)

- Parameters can now be defined as a list as well as as a timeseries (`Issue #52 <https://github.com/rl-institut/multi-vector-simulator/issues/52>`__, `Issue #82 <https://github.com/rl-institut/multi-vector-simulator/issues/82>`__)
