.. _time_series_params_example:

Adding a timeseries for a parameter
###################################

Sometimes you may want to define a parameter not as a scalar value but as a time series.
This can for example happen for efficiencies (heat pump COP during the seasons),
energy prices (currently only hourly resolution), or the state of charge
(for example if you want to achieve a certain stage of charge of an FCEV at a certain point of time).

You can define a scalar as a time series in the csv input files (not applicable for `energyConsumption.csv`),
by replacing the scalar value with following dictionary:

    {'file_name': 'your_file_name.csv', 'header': 'your_header', 'unit': 'your_unit'}

The feature was tested for following parameters:

- energy_price

- feedin_tariff

- dispatch_price

- efficiency

You can see an implemented example here, where the heat pump has a time-dependent efficiency:

.. csv-table:: Example for defining a scalar parameter as a time series
   :file: ../files_to_be_displayed/example_scalar_as_timeseries_energyConversion.csv
   :widths: 70, 30, 50
   :header-rows: 1

The feature is tested with benchmark test `test_benchmark_feature_parameters_as_timeseries()`.

Example input files, where at least one parameter is defined as a time series, can be found here:

* `First example <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/AFG_grid_heatpump_heat>`__: Defines the `energy_price` (`file <https://github.com/rl-institut/multi-vector-simulator/blob/dev/tests/benchmark_test_inputs/AFG_grid_heatpump_heat/csv_elements/energyProviders.csv>`__) of an energy provider as a time series

* `Second example <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/Feature_parameters_as_timeseries>`__: Defines the `energy_price` (`file <https://github.com/rl-institut/multi-vector-simulator/blob/dev/tests/benchmark_test_inputs/Feature_parameters_as_timeseries/csv_elements/energyProviders.csv>`__) of an energy provider and the efficiency of a diesel generator (`file <https://github.com/rl-institut/multi-vector-simulator/blob/dev/tests/benchmark_test_inputs/Feature_parameters_as_timeseries/csv_elements/energyConversion.csv>`__) as a time series.
