# Changelog
All notable changes to this project will be documented in this file.

The format is inspired from [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and the versioning aim to respect [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

Here is a template for new release sections

```
## [_._._] - 20XX-MM-DD

### Added
-
### Changed
-
### Removed
-
### Fixed
-
```

## [Unreleased]

### Added
- Benchmark test (`tests/benchmark_test_inputs/objective_value_exception_equal_annuity`) for in `F0_output.parse_simulation_log` and data stored to `SIMULATION_RESULTS` as well as `OBJECTIVE_VALUE` (#901)
- Constants `BENCHMARK_TEST_INPUT_FOLDER` and `BENCHMARK_TEST_OUTPUT_FOLDER` in `tests/_constants.py` (#901)
- Tests `E3.test_add_total_consumption_from_provider_electricity_equivalent_two_providers_one_energy_carrier` and `E3.test_add_total_feedin_electricity_equivalent_two_providers_one_energy_carrier`(#932)
- Add the argument `return_les` to the function `D0.run_oemof` to return the energy system if set to `True` (#923)
- Save the content of the lp file into a string in the `dict_values` under `SIMULATION_SETTINGS->OUTPUT_LP_FILE` in server mode (#923)
- Set `OUTPUT_LP_FILE` value to be by default `False` when coming from EPA in server mode (#923)
- Function `server.run_sensitivity_analysis_step` to perform one step of a sensitivity analysis (#936)
- Function `utils.nested_dict_crawler` to return mapping of path within a nested dict to the keys at the lowest nested level (#936)
- Test `test_utils.TestAccessKPIs` to test the nested dict utils functions (#936)
- `sankey` method to the `ESGraphRenderer` class to return a sankey diagram (#935)
- `plot_sankey_diagramm` function in `D0_modelling_and_optimization.py` to add the dict of the sankey diagram (#935)
- `ready_sankey_diagram` in `F2_autoreport.py` to add sankey diagram to output and report (#935)
- "maximum_add_cap" to the keys returned to EPA after simulating got production assets (#939)

### Changed
- `F0_output.parse_simulation_log`, so that `SIMULATION_RESULTS` are not overwritten anymore (#901)
- `input_template/csv_elements`: Added missing parameters and generalized units (#904)
- `CONTRIBUTING.md` according to last lessons learnt (#904)
- Set numpy version to lower or equal than `1.19.4` (#924)
- `F2.create_app()` to specify tab name of Dash report to `scenario_name` (`scenario_id`) instead of `Dash` (#934)
- Bugfix in functions `test_add_total_consumption_from_provider_electricity_equivalent` and `E3.test_add_total_feedin_electricity_equivalent` (#932)
- `version.py`: Version number increased to 1.0.2dev, so simulations run before and after this fix can easily be identified (in the autoreport) (#932)
- Enable capacity optimization for storage assets in the epa (#936)
- Make the `utils` function `get_nested_value`and `set_nested_value` raise a Key error with a traceback indicating where in the nested dict this key was missing to help debugging (#936)
- When the user ask for images to be produced (`-pdf` or `-png` options) a sankey diagram is added to the report and to the `dict_values` under `[PATH_TO_PLOTS][PLOT_SANKEY]` (#935)
- Update requirements for numpy (v 1.21.0 or greater) and for dash (v 2.3.1 or greater) (#938)
- `OPTIMIZED_ADD_CAP` replaced by "optimized_add_cap" in the assets keys returned to EPA after simulating (#939)
- The if statement for adapting `MAXIMUM_CAP` for non-dispatchable production assets is now based on the value of `DISPATCHABILITY` and not on the existence of the key `FILENAME` in the `asset_dict` (#939)
- The default values for the constraints are now located in `src/constants.py` under the variable `DEFAULT_CONSTRAINT_VALUES` (#953)

### Removed
- Input timeseries is now not returned to epa in `utils.data_parser.py` (#936)

### Fixed
- `OBJECTIVE_VALUE`, `SIMULTATION_TIME`, `MODELLING_TIME` now included in the `json_with_results.json` (#901)
- Missing parameters in `input_template/csv_elements` (#904)
- Confusing Dash report tab names (#933)
- Calculation of `total_feedin` and `total_consumption_from_providers`, where multiple providers of one energy carrier were not aggregated correctly (#931)
- Used `pandas.concat` instead of `DataFrame.append` to add rows to a `pandas.DataFrame` instance to suppress UserWarning (#937)
- Add missing file for test `test_F0_output.TestLogCreation.test_parse_simulation_log` (#937)
- Transformers can have multiple input or output busses (tested in `tests/test_D1_model_components` by `test_transformer_optimize_cap_multiple_output_busses_multiple_inst_cap`, `test_transformer_optimize_cap_multiple_output_busses_multiple_max_add_cap`, `test_transformer_fix_cap_multiple_output_busses_multiple_inst_cap` and in `tests/test_benchmark_special_features` by `test_benchmark_feature_parameters_as_timeseries_multiple_inputs`)(#949)
- The constraints are not all set to default values if only one constraint is missing, only the missing constraint is set to default value (#953)

## [1.0.0] - 2021-05-31

### Added
- Check for correct `installedcap` processing to `AB_grid_pv` benchmark test (#831)
- Check to `AB_grid_pv` benchmark test: total pv generation is used to cover demand (#831)
- Section on energy consumption assets in `Model_Assumptions.rst` and `MVS_Outputs.rst` (#817)
- Constant variables: `MODELLING_TIME`, `LP_FILE` (#839), `MAXIMUM_ADD_CAP` (#848), `TIMESERIES_SOC`, `AVERAGE_SOC` (#859), `INSTALLED_CAP_NORMALIZED` (#835)
- Requirement of plotly in `requirements/default.txt` (#840)
- Pytests for `C1.check_for_sufficient_assets_on_busses()` (#837)
- Lookup table for parameters in RTD (#842)
- Column `category` in the file `docs/MVS_parameters_categories.csv` to know in which csv file(s) the parameter is used (#842)
- Define `OEMOF_SOLPH_OBJECT_ASSET`, `WEIGHTING_FACTOR_ENERGY_CARRIER`, `RENEWABLE_SHARE_ASSET_FLOW`, `OEMOF_SOLPH_OBJECT_BUS` as constants in `D2` module (#834)
- Import and use constants from `D2` module in `test_D2_model_constraints.py` (#834)
- Check for the capability of asset capacities in an energy system to fulfill the maximum demand in `C1.check_energy_system_can_fulfill_max_demand()` (#824)
- Tests for `C1.check_energy_system_can_fulfill_max_demand()`, including pseudo-benchmark test in `test_C1` (#824, #896)
- Zenodo badge on README (#850)
- `VERSION_NUM` to simulation settings, added with `C0.add_version_number_used()` (#855)
- Generation of pdf version of the readthedocs (#853)
- `sphinxcontrib-svg2pdfconverter` in `docs/conf.py` for `svg` images into `pdf` (also added in `requirements/docs.txt`(#853)
- Function `generate_kpi_description` in `docs/conf.py` module to generate documentation of kpi parameters listed in `docs/MVS_kpis_list.csv`(#863)
- Badges for pypi, black linter and license in `docs/index.rst` and `README.rst` (#865)
- `--version` option for the command line `mvs_tool` (#866)
- `sphinx.ext.imgconverter` in `docs/conf.py` for svg images into pdf (#853)
- Parameter `maximumAddCap` where `maximumAddCap=maximumCap-installedCap` in `C0.process_maximum_cap_constraint()`, ie. make the coupling of the two parameters `installedCap` with `maximumCap` explicit (#848)
- Check that storage file name defined with ending `.csv` with new `A1.check_storage_file_is_csv()` in `A1.create_json_from_csv()` (#859)
- Class in `exceptions.py`: `MissingCsvEndingError` (#859)
- Constant variables in `E1` for accessing oemof-solph results: `OEMOF_FLOW`, `OEMOF_SEQUENCES`, `OEMOF_INVEST`, `OEMOF_SCALARS` (#859)
- Constant variables in `E1`: `THRESHOLD` for central definition of precision limit (#859)
- `docs/MVS_kpi_categories.csv` and `conf.generate_kpi_categories()` to list KPI under in the RTD (#869)
- Descriptions of all output files to RTD (#874)
- Benchmark test for `maximumCap` constraint in `test_benchmark_constraints.py` (#835)
- Functions `C0.process_normalized_installed_cap()` to process the normalized installed capacity value as well as its pytests (#835)
- Test for `C0.process_normalized_installed_cap()` (#835)
- Tips and Tricks in the RTD (#876)
- Logging option for server (#895)

### Changed
- Release protocol in `CONTRIBUTING.md` (#821)
- Status messages of requirements in `E-Land_Requirements.rst` (#817)
- `Model_Assumptions.rst` and `MVS_Outputs.rst`, mainly adding labels (#817)
- Pytests for `D0` to let them pass on Windows (#839)
- Dependencies of pyomo and pandas (#840, #896)
- Validate of peak demand pricing bus in `C1.check_for_sufficient_assets_on_busses()` (#837)
- Refactored `EXCESS` to `EXCESS_SINK` as this is more intuitive (#837)
- Order of `maximumCap` check and adaption in `C0.process_maximum_cap_constraint()` (#833)
- Adapt parameters in `test/inputs` to make simulation run without errors after correcting processing of `maximumCap`: set constraints `minimal_renewable_factor` and `minimal_degree_of_autonomy` to `0.01`, `maximumCap` of pv plant to `10000` and `feedin_tariff` to `0.05` (#833)
- Generate the parameters categories in RTD lookup table automatically from `docs/MVS_parameters_categories.csv` (#842)
- `DISPATCHABILITY` of energyConsumption assets now set to `FALSE` by default (#824)
- Function `C0.define_sink()` now defines `DISPATCHABILITY=TRUE` for the created sink (#824)
- Only implement the constraints defined by the user explicitly: move accessing the constraint key in `dict_value` in the respective constraint preparation functions (#845)
- Restructure chapters of Readthedocs (#853, #860)
- Turn Readthedocs build warnings into errors in CI (#863)
- Pytest triggers the kpi benchmark tests (which was not the case before) (#864)
- Deactivate optimization when `maximumCap<=installedCap and maximumCap!=0` in `C0.process_maximum_cap_constraint()` (#848)
- Replace usage of `maximumCap` in `D1` with `maximumAddCap` calculated in `C0` (#848)
- Adjust `tests/test_benchmark_feedin.test_benchmark_feedin_tariff_optimize_positive_value()` and `tests/benchmark_test_inputs/Feedin_optimize/csv_elements/energyProduction.csv` to fit new `maximumCap` and `maximumAddCap` definitions (#848)
- Include new parameter `maximumAddCap` in `tests/test_data/inputs_for_D0/mvs_config.json` and `tests/test_data/inputs_for_D1/mvs_config.json` (#848)
- Explicitely include badges only for the html version of the RTD and not the pdf (#870)
- Change `E1.get_timeseries_per_bus()` and `E1.get_flows` and utilize `E1.cut_below_micro` to apply precision limit (#859)
- Separate calculation of SOC into own function: `E1.get_state_of_charge_info` (#859)
- Change `E1.add_info_flows()` so that storage peculiarities for the information is considered (#859)
- Benchmark tests for `AE-Grid-Battery`: Input files and pytests (#859)
- `E1.lcoe_assets` to calculate LCOE of storage capacity throughput based on input flow. Required change of `test_benchmark_KPI` (storage not used, `LCOE=0`) (#589)
- Modified github action workflow so that it is not triggered when one modifies the README, CHANGELOG or the docs (#872)
- Proofread RTD for the release of the ELAND report (#871, #878, #884, #885, #886, #887, #897)
- Prepared `docs/MVS_kpis_list.csv` summarizing all simulation outputs (#869)
- Decapitalizing and removing spaces of all variable values in `constants_json_strings.py` (#869)
- Reformatting code snippets in RTD to `:code:` (#880)
- `E3.add_levelized_cost_of_energy_carriers` to fix wrong variable definition, extend pytest (#890)
- `E2.convert_components_to_dataframe()` to correctly display when an asset is optimized, add pytests (#875)
- If the `TIMESERIES` key is in the `dict_values` and the file under `FILENAME` key cannot be found, the timeseries is loaded from `TIMESERIES` (#881)
- updated the SOC defintions in RTD (#876)
- Corrected faulty weighting factors (`DEFAULT_WEIGHTS_ENERGY_CARRIERS` in `utils/constants.py`, `docs/model/assumptions.rst`) (#894)
- MVS-EPA parser to work with current EPA as of 2021-05-28, commit 5e7c4c39b2564c569c31907cbcb3cb07b92ebd2f: `utils.data_parser.convert_epa_params_to_mvs()` (#895)

### Removed
- `AUTO_SOURCE` and `AUTO_SINK` as this overcomplicated the labelling process (#837)
- `AUTO_SINK` suffix in `utils.data_parser.convert_mvs_params_to_epa()` (#837)
- `EXCESS_SINK_POSTFIX` and only use `EXCESS` (#837)
- Quotes for command line instruction in `README.rst` (#850)
- Superfluous `docs/readthedocs.yml` file (#853)
- Broken links in readthedocs (#861)
- Calculation of `LCOE_Asset` for energy storage capacity are not calculated anymore in `E2.lcoe_assets` (#589)
 
### Fixed
- Skip `test_benchmark_KPI` as it was seen to be consuming the whole test time leading to timeout on github action (#826)
- Reduce `simulation_settings.evaluated_period` to one day for the tests where simulation results are not important (for `E0` and `D2` test modules setup) (#826)
- Fix formula of degree of NZE in RTD and in docstring of `E3.equation_degree_of_net_zero_energy()`  (#832)
- Tests failing on windows with `FileExistsError` (#839, #854)
- No excess error message regarding the auto-generated peak demand pricing bus (#837)
- `C0.prepare_demand_assets()` did not explicitly exclude feedin sinks (#837)
- Hotfix: `C0.define_sinks()` now works for scalar feed-in prices, but not for lists of timeseries (#837)
- Address issue #825 by changing order of `maximumCap` check and adaption in `C0.process_maximum_cap_constraint()` (#833)
- Bugfix in `C0.process_maximum_cap_constraint()`: Always set `maximumCap` to `None` in case its value is 0 (#833)
- Solved ReadTheDocs warnings (#863)
- Re-enable the coverage tests on github actions (#864)
- Adjust definition for `maximumCap` in `docs/MVS_parameters_list.csv`: Total maximum installable capacity (#848)
- Negative values within the precision limit in `timeseries.xlsx` (#859)
- Introduce new standard for cites (#885)
- Faulty calculation of attributed costs (#890)
- Show actual setting of `OPTIMIZE_CAP` in autoreport for storages and energy production fuel sources (#875)
- Faulty weighting factors, now energy carrier weights mostly in the range of lower heating value (#894)

## [0.5.5] - 2021-03-04

### Added
- Verification of the SoC values after simulation for any physically infeasible values with `E4.verify_state_of_charge` and added tests for this function (#739)
- Explanation in `MVS_parameters_list.csv` on how to deactivate the RES constraint (#752)
- Add the new parameter `scenario_description` to input files and docs and a section in autoreport describing the scenario being simulated (#722)
- Add a new sub-section in RTD describing the suite of post-simulation tests carried out through functions in `E4_verification.py` (#753)
- Add KPI individual sectors as an own table to the report (#757)
- Add pytests for the minimal renewable share constraint of function `D2.add_constraints()` (#742)
- Throw an explanatory warning in `A1` module when csv file cannot be parsed (#675)
- Add `-d` option to `mvs_report` command to use hotreload of dash app for devs (#770)
- Add `utils.analysis` module for overall analysis functions (#679)
- Added pre-processing step with `C0.replace_nans_in_timeseries_with_0` to set NaNs occurring in provided timeseries to zero (#746)
- KPI processing function `E3.add_total_consumption_from_provider_electricity_equivalent()` incl. pytest (#726)
- Subsection `Minimal degree of autonomy constraint` for RTD, added parameter in `MVS_parameters_list.csv` (#730, #726)
- Minimal degree of autonomy constraint including pytest and benchmark test (#726)
- Add benchmark test for json benchmark file (`tests/benchmark_test_inputs/epa_benchmark.json`) from EPA (EPA-MVS compatibility) (#781)
- Add a try-except code block to catch fatal errors in `DO.simulating()` that cause simulation to terminate unsuccessfully (#754)
- It is now possible to model a stratified thermal energy storage. In this context, the two optional parameters `fixed_losses_relative` and `fixed_losses_absolute` were added and can be set in the `storage_*.csv` file. The usage of this new component was tested in `test_A1_csv_to_json.py`, `test_D1_model_components.py` and `test_benchmark_stratified_thermal_storage.py`. A documentation was added in the chapter `Model_Assumptions.rst` (#718)
- Allow to run workflow manually from the GitHub Actions tab by adding `workflow_dispatch` to `main.yml` (#793)
- Added a note in energy excess section in RTD (component models, `Model_Assumptions.rst`) saying that excess sinks are added automatically (#792)
- Added net zero energy KPI `degree of NZE` with `E3.equation_degree_of_net_zero_energy()` and `E3.add_degree_of_net_zero_energy()` (#776)
- Added tests for `E3.equation_degree_of_net_zero_energy()` and `E3.add_degree_of_net_zero_energy()` (#776)
- Added information about degree of NZE to RTD (`Model_Assumptions.rst`) (#776)
- Function `E1.cut_below_micro` to round decision variables (capacities, flows) below threshold of plus/minus 10^-6 (1e-6) to 0, add warnings if negative value larger then threshold (invalid result). Includes pytests (#791)
- Update `component models` (`Model_Assumptions.rst`) section in RTD with information on energy storages, heat pumps and HVAC (#794)
- Section `Cost Assumptions` to `Model_Assumptions.rst` (#795)
- Pre- and post-processing of `fixcost.csv` entries, so that they also appear in economic evaluation, including pytests (#795)
- Update `component models` section in RTD with information on H2 storage, dispatchable and non-dispatchable sources, electrolyzers, CHP, other fuel powered plants and electric transformers. (#804)
- Added net zero energy (NZE) constraint with `D2.constraint_net_zero_energy()` and `D2.prepare_energy_provider_feedin_sinks()` (#796)
- Added test for `D2.prepare_energy_provider_feedin_sinks()` (#796)
- Added benchmark test for NZE constraint (#796)
- Added information about NZE constraint to RTD (#796)
- Added `net_zero_energy` parameter to all `constraints.csv` files and all json files (#796)
- Added `net_zero_energy` parameter to `MVS_parameters.rst` and `MVS_parameters_list.csv` (#796)
- Added verification of NZE constraint in `E4.net_zero_energy_constraint_test()`, added tests for this function (#796)
- Added test for `D2.add_constraints()` with activated NZE constraint (#796)

### Changed
- Fix xlrd to xlrd==1.2.0 in `requirements/default.txt` (#716)
- Format `KPI_UNCOUPLED_DICT` to a `pd.DataFrame` (#757)
- Rename variable `EXTRA_CSV_PARAMETERS` to `KNOWN_CSV_PARAMETERS` (#761)
- If a required parameter is missing but is in the `KNOWN_EXTRA_PARAMETERS` dict in `constants.py`: do not flag it as missing and set its default value (#761)
- Gather all missing MVS parameters and raise a single error listing all of them (`src/multi_vector_simulator/utils/__init__.py`) (#761)
- Add `set_default_values` argument to the `B0.load_json` function to set default values of missing parameter which is listed in `KNOWN_EXTRA_PARAMETERS`(#761)
- Add `flag_missing_values` argument to the `B0_load_json` function to allow switching between `MissingParameterWarning` and `MissingParameterError`(#761)
- Write lp file only when executing `cli.py` (#675)
- Change `C0.change_sign_of_feedin_tariff()` - `logging.info` message if `feedin==0` (#675)
- Update RTD instruction for instructions for the `mvs_tool` command (#770)
- Change `test_benchmark_special_features.py` (#746)
- Update "Input verification" section in `Model_Assmptions.rst` for NaNs (#746)
- (!) Major change: Definition of Degree of Autonomy (DA) updated in the RTD, also changed calculation of that KPI (#730, #726)
- Updated all input files to also include `minimal_degree_of_autonomy`, including `input_template`, `tests/inputs`, `tests/benchmark_test_inputs` (#726, #783)
- `E4.minimal_renewable_share_test()` into generic `E4.minimal_constraint_test()` so that it can be applied both to minimal renewable share and minimal degree of autonomy (#726)
- `C1.check_non_dispatchable_source_time_series()`, now verification not only applied to renewable assets, but all non-dispatchable assets (#726)
- Add `MINIMAL_DEGREE_OF_AUTONOMY` to EPA-MVS parser (`utils.data_parser.convert_epa_params_to_mvs()`)(#726)
- Provide the modeler with helpful messages enabling simpler identification and rectification of problems in their input files (`D0.simulating()`) (#754)
- In `test_A1_csv_to_json.py` tests were added that check whether default values of `0` are set for `fixed_losses_relative` and `fixed_losses_absolute` in case the user does not pass these two parameters (#718)
- In `test_D1_model_components.py` tests were added that check whether the `GenericStorage` parameter `investment.minimum` is set to `0` in case `fixed_losses_relative` and `fixed_losses_absolute` are not passed and to `1` in case they are passed as times series or floats. At this time it is not possible to do an investment optimization of a stratified thermal energy storage without a non-zero `investment.minimum` (see this [issue](https://github.com/oemof/oemof-thermal/issues/174)) (#718)
- The two optional parameters `fixed_losses_relative` and `fixed_losses_absolute` were added in `tests/inputs/mvs_config.json` (#718)
- Adapted structure of component models in RTD (`Model_Assumptions.rst`) to mirror EPA and MVS input data (#792)
- Refactor module imports in `cli.py` and `server.py` (#783)
- Limit index of availability timeseries to simulation timeindex (`C0.define_availability_of_peak_demand_pricing_assets`) (#783)
- Call `E1.cut_below_micro` in `E1.get_flows`, `E1.get_optimal_cap` and `E1.get_storage_results` (#791) 
- Split preprocessing function `D2.prepare_constraint_minimal_degree_of_autonomy()` into two functions that can be used by multiple constraints: `D2.prepare_demand_assets()` and `D2.prepare_energy_provider_consumption_sources()`, also adapted tests (#796)
- Edited epa parser so that net zero energy constraint is added in `utils.data_parser.convert_epa_params_to_mvs()` (#796)
- Update definition of degree of net zero energy in `docs/MVS_Outputs.rst`, `src/multi_vector_simulator/E3_indicator_calculation.py ` and `tests/test_E3_indicator_calculation.py` (#797)
- Changed `utis.data_parser.convert_epa_params_to_mvs()` to fix EPA-MVS parsing bugs, now also prints extra parameters, improved comments (#810)
- Edited error message when a parameter is missing to make it easier to track (`A1.conversion()`) (#795)
- Improved warning message when a unknown parameter is added (`A1.create_json_from_csv`) (#795)
- Changed `REQUIRED_CSV_PARAMETERS` of `FIX_COSTS`: Removed `LABEL` and `DISPATCH_PRICE` and removed those parameters from all `fixcost.csv` (#795)
- Added exception to `E0.store_result_matrix` for `fixcost.csv` entries (#795)
- Moved parts of `E0.evaluate_dict` into a subfunction `E0.initialize_kpi` (#795)
- Exchanged all demand profiles in `tests` with standardized ones (#818)

### Removed
- Remove `MissingParameterWarning` and use `logging.warning` instead (#761)
- Remove redundant function `A1.check_for_official_extra_parameters` as `utils.compare_input_parameters_with_reference` works for both csv and json and will therefore be preferred (#761)
- Remove `STORE_OEMOF_RESULTS` variable (#675)
- Remove `F0.select_essential_results()` (#675)
- Removed `DSM` and `TYPE_ASSET` from `input_template/energyConsumption.csv`, also in `constants.py` (#726)
- Removed warning message about excess energy calculation that is outdated as #559 is solved (777)
- Remove `test_C1_verification.get_json()` as now not used (#783)
- Removed instances of `WrongParameterWarning` and replaced it with `logging.warning` in `A1` (#795)

### Fixed
- Minor typos in D0, E4 and test_E4 files (#739)
- `utils.data_parser.convert_epa_params_to_mvs()` and `utils.data_parser.convert_mvs_params_to_epa()` now parse succesfully input files generated from EPA (#675)
- Fix issue (#763): Avoid displaying an energy sector demand table in report if it is empty (#770)
- Fix issue (#769): Fix argument parsing and error messages of `mvs_report` command (#770)
- Fix issue (#756): Avoid crashing report generation when internet not available (#770)
- Fixed display of math equations in RTD (#730)
- Fix `numpy.int32` error in `B0` (#778)
- `mvs_config.json` is generated again, now from `cli.py` (#783)
- Fix pytest `C1.test_check_non_dispatchable_source_time_series_passes` and `C1.test_check_non_dispatchable_source_time_series_results_in_error_msg` (#783)
- Fix typo in `utils.data_parser` `logging.INFO` was used instead of `logging.info` (#809)
- Fix: Asset groups that are empty are not provided by EPA, adapted parser (#810)
- Fix: `ENERGY_PROVIDER` assets are missing parameter `DISPATCHABILITY` when parsed from EPA to MVS (#810)
- Fix: No `DISPATCHABILITY` parameter for `ENERGY_PRODUCTION` assets in EPA (#810)
- Fix: Default value of `MAXIMUM_EMISSIONS` when parsing from EPA (#810)
- Move `process_fixcost` from `E1` to `E0` to avoid circular imports (#820)

## [0.5.4] - 2020-12-18

### Added
- Updated release protocol with info on credentials for test.pypi.org (step 9) and added "Fixed" to unreleased section of changelog.md in release protocol (#695)
- Added information about the API to the docs (#701)
- Added CO2 emission factors in the section `Model_Assumption.rst` (#697, #735)
- Added `energyBusses.csv` in RTD (#678)
- Add and link `rewableAsset` as parameter in RTD, specifically `MVS_parameters.rst` and `MVS_parameters_list.csv` (#710)
- Parameter `emission_factor` to `energyProduction` and `energyProviders` and to rtd (`MVS_parameters.rst` and `MVS_parameters_list.csv`) (#706)
- Parameter `total_emissions` in kgCO2eq/a to `constraints.csv` (#706)
- Constant variables `TOTAL_EMISSIONS` and `SPECIFIC_EMISSIONS_ELEQ` for emission KPIs, `MAXIMUM_EMISSIONS` for emission constraint and `UNIT_EMISSIONS` and `UNIT_SPECIFIC_EMISSIONS` for unit definitions (#706)
- Calculation of total emissions per production asset in `E3.calculate_emissions_from_flow()`, which are added to `KPI_SCALARS_DICT` (#706)
- KPI "Total emissions" in kgCO2eq/a per production asset (`E3.add_total_emissions()`) and KPI "Specific emissions per electricity equivalent" in kgCO2eq/kWheleq (`E3.add_specific_emissions_per_electricity_equivalent()`) (#706)
- Tests for functions `E3.calculate_emissions_from_flow()`, `E3.add_specific_emissions_per_electricity_equivalent()`) and `E3.add_total_emissions()` (#706)
- Added `emisson_factor` of providers to automatic source for providers in `C0.define_source()` and adapted tests (#706)
- Added information on calculation of total emissions in RTD in Simulation Outputs section (#706)
- Parameter `maximum_emissions` (`MAXIMUM_EMISSIONS`) to `constraints.csv`, unit: kgCO2eq/a (#706)
- Maximum emission constraint by `D2.constraint_maximum_emissions()` to `D2.add_constraints()` using `oemof.solph.constraints.emission_limit()`, also added tests (#714, #706)
- Benchmark test for maximum emission constraint in `test_benchmark_constraints.py` (#714, #706)
- Information on maximum emissions constraint to RTD, including help for the end-user to define the value for this constraint (#714, #706)
- A logging.warning (`C1.check_feasibility_of_maximum_emissions_constraint()`) if `maximum_emissions` constraint is used but no asset with zero emissions is optimized without maximum capacity constraint, also added tests (#714, #706)
- A logging.warning (`C1.check_emission_factor_of_providers()`) in case any of the providers has a renewable share of 100 % but an emission factor > 0, also added tests (#714, #706)
- Info on maximum emissions constraint benchmark test to RTD (#714, #706)
- Verification for maximum emissions contraint in `E4.maximum_emissions_test()`, also added tests (#714, #706)
- Added pytests for the function 'C0.compute_timeseries_properties()' (#705)

### Changed 
- Benchmark test for investment model (`Test_Economic_KPI.test_benchmark_Economic_KPI_C2_E2`): Expand test to LCOE as well as all all other system-wide economic parameters, transpose `test_data_economic_expected_values.csv`, change `test_data_economic_expected_values.xls` (#613)
- Adapt pre-processing for investment benchmark tests into a seperate function (#613)
- `COST_REPLACEMENT` is now a parameter that is included in output cost matrix (#613)
- Improved `Code.rst` for RTD code documentation (#704)
- All `.py` files to add a module description for RTD on top (#704)
- Converted `README` from `.md` to` .rst` format and updated `Installation.rst` file (#646)
- Updated `setup.py` to use the rst formatted README file
- Changed `C0.energyStorage()` for timeseries in storage parameters (hotfix) (#720)
- Input files and benchmark test `test_benchmark_special_features.Test_Parameter_Parsing()`: Now also including timeseries in a storage component (#723)
- Adapted `E0` tests to new parameter `emission_factor` (#706)
- Adapted all test inputs and json files and the input template, adding `emission_factor` (`energyProduction`, `energyProviders`) and `maximum_emissions` (`constraints.csv`) (#706)

### Removed
- Removed `README.md` in favour of `README.rst` (#646)

### Fixed
- Decreased warnings of RTD compilation drastically (#693)
- Use current version number as defined in `version.py` for RTD (#693)
- Added storage to the table in autoreport listing the energy system components (#686)
- Add assertion `sum(attributed_costs)==cost_total` (for single-vector system) (#613)
- Benchmark test for renewable share (`TestTechnicalKPI.test_renewable_factor_and_renewable_share_of_local_generation()`) (#613)
- Github actions workflow: update apt-get before installing pre-dependencies (#729)
- Got rid of logging messages of imported libraries in the log file (#725)
- Fix RTD for emissions (#735)
- Hot fix: Parameters to be defined as timeseries in `storage_*.csv` (#720)
- Tests for `E4.minimal_renewable_share_test` (#714, #706)

## [0.5.3] - 2020-12-08

### Added
- Warning for missing parameter when parsing inputs from epa to mvs (#656)
- New module `exceptions.py` in `multi_vector_simulator.utils` to gather custom MVS exceptions (#656)
- New argument for functions `E1.convert_demand_to_dataframe`, `F1.plot_timeseries`, `F2.ready_timeseries_plots` (#665)
- File .github/workflow/main.yml for github actions (#668)
- `energyBusses` now have to be defined by the user via `energyBusses.csv` (#649)
- Input validation test `C1.check_for_label_duplicates` (#649)
- Constant variables: `JSON_PROCESSED`, `JSON_WITH_RESULTS`, `JSON_FILE_EXTENSION` (#649)
- Comment in the RTD concerning the logical equivalence of `energyCarrier` and `energyVector` in the MVS (#649)
- Comment how fuels can either be attributed to the fuel energy vactor or another vector (#649)
- Labels for tables in `Model_assumptions.rst` (#649)
- New in `utils`: `helpers.py` with `find_valvue_by_key()`: Finds value of a key in a nested dictionary (#649)
- New exception `DuplicateLabels` (#649)
- Plot showing state of charge (SOC) of storages of each bus separately, as it is provided in %, also added to automatic report (#666)
- "SOC" as string representative in `utils/constants.py`, used in `F1` and `E0` (#666)
- SOC plot of storages is added to the autoreport (#666)
- Test for correct storage labelling in `A1.add_storage_components()` (#666)
- Test for getting two time series with `E1.get_timeseries_per_bus()` for storage (input and output power) if storage is directly connected to bus (#666)
- Function `C1.check_efficiency_of_storage_capacity` that raises error message if the `efficiency` of `storage capacity` of any storage is 0 and a logging.warning if the efficiency is < 0.2, to help users to spot major change when using old files (#676)
- Function `C0.change_sign_of_feedin_tariff()` for changing the sign of the `feedin_tariff`, added tests as well (#685)
- Benchmark tests in `test_benchmark_feedin.py` to check the feed-in behaviour and feed-in revenues in dispatch and invest optimization (#685)
- Pytests for `C0.add_a_transformer_for_each_peak_demand_pricing_period()`, `C0.define_dso_sinks_and_sources`/`C0.define_auxiliary_assets_of_energy_providers`, `C0.define_source` (#685)
- Basic structure for pytest of `C0.define_sink` (#685)
- Add verification test `C1.check_feedin_tariff_vs_levelized_cost_of_generation_of_production()` (#685)

### Changed
- Function `utils.compare_input_parameters_with_reference` accepts parameters as dict for json comparison (#656)
- Move A1 and C0 custom exceptions into `multi_vector_simulator.utils.exceptions.py` (#656)
- Adapt `E1.convert_demand_to_dataframe` for multiple sectors (#656)
- Improve the demands section of the autoreport: Divide the demand tables and plots sector-wise (#665)
- All tests and benchmark tests are adapted to `energyBusses` being defined manually (#649)
- Input for for `tests\test_F1_plotting.py` changed from `tests/test_data/inputs_F1_plot_es_graph` to default input folder `tests/inputs` (#649)
- `tests/inputs`, `input_template` and the inputs of the benchmark as well as pytests adapted to `energyBusses` defined via `csv` (#649)
- Refactored and changed `C0.update_bus()` to `C0.add_asset_to_dict_of_bus` (#649) 
- Refactored and changed `C0.define_busses()` as it now only defines the energy assets connected to the defined busses (#649)
- Changed `C0.define_sink()` and `C0.define_source()` so that it fits with externally defined `ENERGY_BUSSES` (#649)
- Adapt pytests of `D1` and `D0` (#649)
- Changed `C1.identify_energy_vectors` to be a test `C1.check_if_energy_vector_of_an_asset_is_valid` (#649)
- Input folder for the `F1` tests now `tests/inputs` (#649)
- Refactored parameters: `DSO_PEAK_DEMAND_BUS_NAME` to `DSO_PEAK_DEMAND_SUFFIX`, `SECTORS` to `LES_ENERGY_VECTORS` (#649)
- Update `MVS_parameter_list.csv`: Added information to `energyVector` (#649)
- Modify `E1.get_timeseries_per_bus()` to add `INPUT_POWER` and respectively `OUTPUT_POWER` to a storage component directly connected to the a bus to fix #444 and add logging.debug(#666)
- Changed label of storage in `timeseries_all_busses.xlsx` to be defined by `installedCap` + `optimizedAddCap` to prevent confusion (#666)
- Make use of constant variables (#684)
- `tests/inputs` adapted so that storage is used (#684)
- Significant change(!): `loss_rate` of storages in `D1` defined as `1-efficiency` instead of as `efficiency` of the storage capacity (see `storage_*.csv` files) (#676)
- `efficiency` of `storage capacity` in `storage_*.csv` now actually displays the storages' efficiency/ability to hold charge over time (#676)
- Adapted `efficiency` of `storage capacity` in all provided benchmark tests and inputs (#676)
- Documented the change of `efficiency` of `storage capacity` as actual efficiency/ability to hold charge over time in RTD (#676)
- Significant change(!): `feedin_tariff` in `energyProviders.csv` should now be provided as positive value to earn money with feed-in and to a negative value to pay for feed-in (#685)
- Simplified `C0.define_source()` (#685)
- Refactored `C0.define_dso_sinks_and_sources` to `C0.define_auxiliary_assets_of_energy_providers` (#685)
- Refactored `C0.check_feedin_tariff()` to `C0.check_feedin_tariff_vs_energy_price()` to specify test (#685)
- Changed `tests/inputs` so that feed-in tariff checks pass (#685)
- Adapted check in `C0.check_feedin_tariff_vs_levelized_cost_of_generation_of_production()`: if `maximumCap` is not None only a warning is logged as this wouldn't result in an unbound problem. In case of an investment optimization of the asset a logging.debug is shown. (#690)

### Removed
- File .travis.yml (#668)
- Folder `tests/test_data/inputs_F1_plot_es_graph`, now using default input folder `tests/inputs` as input for `tests\test_F1_plotting.py` (#649)
- Mention of `LABEL` in the RTD description of the `csv` files (#649)
- `C0.bus_suffix()`, `C0.remove_bus_suffix()` and `C0.get_name_or_names_of_in_or_output_bus()`, as this overcomplicated the issue and the end user now can define their own bus labels (#649)
- Parameters `INPUT_BUS_NAME` and `INPUT_BUS_NAME`, as they are now equivalent to `INFLOW_DIRECTION` and `OUTFLOW_DIRECTION` (#649)
- Removed SOC from storages from busses' plots (in `F1.plot_instant_power()`) but not from `OPTIMZIED_FLOWS` so that it is still printed into `timeseries.xlsx` (#666)

### Fixed
- Storage label definition (remove filename) and use `LABEL` instead (#666)
- Make deep copy of data frame in `F1.plot_optimized_capacities()` to prevent errors (#666)
- Benchmark test for minimal renewable share constraint (#685)

## [0.5.2] - 2020-11-11

### Added
- Create function `utils.copy_inputs_template` to copy input_template from package data_files (#608)
- Create `MANIFEST.in` file (#608)
- Add entrypoint for `mvs_create_input_template` in `setup.py` (#608)
- Create script `prepare_package.py` to add data to package and build dist folder (#608)
- Five new KPI's added to E3: Onsite energy fraction, Onsite energy matching, Degree of autonomy, total_feedin_electricity_equivalent and internal generation (#624)
- Add definition of `renewable share of local generation` in RTD, `E3.add_renewable_share_of_local_generation` and pytests (#637)
- Add calculation of electricity equivalents in `E3.weighting_for_sector_coupled_kpi()` (#637)
- Add benchmark test for  the calculation of: `TOTAL_NON_RENEWABLE_GENERATION_IN_LES`, `TOTAL_RENEWABLE_GENERATION_IN_LES`, `TOTAL_NON_RENEWABLE_ENERGY_USE`, `TOTAL_RENEWABLE_ENERGY_USE`, `RENEWABLE_FACTOR`, `RENEWABLE_SHARE_OF_LOCAL_GENERATION` for one sector (#637)
- New constant variable: `DATA="data"` (#651)

### Changed
- Moved `get_nested_value`, `set_nested_value`, `split_nested_path` from `tests/test_sensitivity.py` to `src/multi_vector_simulator/utils/__init__.py` (#650)
- Rename PACKAGE_PATH to PACKAGE_DATA_PATH (#608)
- Update release protocol within `Contributing.md` (#608)
- Definition of renewable share (RES), now renewable factor (#637)
- Refactoring of `RENEWABLE_SHARE` into `RENEWABLE_FACTOR` and some functions in E3 (now `E3.add_total_renewable_and_non_renewable_energy_origin` and `E3.add_renewable_factor`) (#637)
- Rename: `Minimal renewable share constraint` to `Minimal renewable factor constraint` in all files (python, messages, RTD, json, tests, csv), so that this is in line with the definition and does not cause any confusion, explained in RTD (#637)
- Modify `B0_data_input_json.py` to read "input_timeseries" into `pandas.Series` from epa formated input json (#651)
- Modify `convert_mvs_params_to_epa` in `utils.data_parser` to convert `pandas.Series` back to "input_timeseries" (#651)

### Removed
- Variable `TEMPLATE_INPUT_PATH` (#608)
- Field `data_files` from `setup.py` (#608)

### Fixed
- Calculation of the renewable share relative taking into account energy carrier weighting (#637)

## [0.5.1 - 2020-11-10]

### Added
- `E-Land_Requirements.rst`: Official E-Land requirement list as well as progress on functional and non-functional requirements (#590)
- Add pytests for `E4.detect_excessive_excess_generation_in_bus()` (#591)
- Add pypi release to release protocol and update/simplify protocol (#601)
- Remove REPORT_PATH constant (#607)
- Add report assets and example simulation to package_data in `setup.py` (#607)
- Add a util function `copy_report_assets` to copy report asset to simulation output folder when user generates the report (#607)
- Add entrypoints for `mvs_tool` and `mvs_report` in `setup.py` (this can be simply typed directly in terminal) (#607)
- Updated readthedocs: Validation plan - Implemented tests and possible future ones (#593)
- Updated readthedocs: Gather the MVS parameters in a csv file and parse it to a sphinx RTD file (#620)
- Added more energy carriers and their weights to the list of already available energy carriers in constants.py (#621)
- Three new KPI's added to MVS_output.rst read the docs page: Onsite energy fraction, Onsite energy matching, Degree of autonomy (#609)
- New constant variables: `LOGS = "logs"`, `WARNINGS = "warnings"`, `ERRORS = "errors"` (#623)
- Tests for `D1.transformer()` (#596)
- Add economic model equations in readthedocs (#581)
- Add component model equations and energy balance adapted to sector coupled example (#581)
- Create function `F0.select_essential_results` to select main results out of `dict_values` (#625)
- Create mapping between EPA and MVS parameter names (#625)
- Create parameter parser from EPA to MVS (#625)
- Create parameter parser from MVS to EPA (#625)

### Changed
- Order of readthedocs content (#590)
- Make sure report can be generated even if figures are missing from simulation outputs (#607)
- Move the code located in `mvs_report.py` into `multi_vector_simulator.cli:report` (#607)
- Update installation steps in README and in RTD (#607)
- If default folder does not exist when code is executed, example simulation's inputs are used from package_data (#607)
- Rename `PATH_SIM_OUTPUT` to `ARG_PATH_SIM_OUTPUT` (#607)
- Rename function `A0.create_parser` to `A0.mvs_arg_parser` (#607)
- Update validation plan description in RTD (#593)
- Column headers of csv input files need to be unique amongst all files, info added to documentation (#602)
- Change mvs_eland to multi_vector_simulator in `docs/Code.rst` (#620)
- Change mvs_eland to multi-vector-simulator in `docs/*.rst` `urls (#620)
- Improved the description of assigning weightage to energy carriers in readthedocs (#619)
- Replaced the DSO sub-system image in Modelling Assumptions chapter of readthedocs (#622)
- Fixed several typos in readthedocs (#622)
- Move the function parse_log_messages to F0 and modify it to print log messages in results JSON file (#623)
- Move the function `parse_log_messages` from F1 to F0 and modify it to print log messages in results JSON file (#623)
- If `assets` folder is not found in package look in current folder for `report/assets` folder (#632)
- `D1.transformer_constant_efficiency_fix()` and `D1.transformer_constant_efficiency_optimize()`, as well as their tests to reassign attributes (#596)
- Move `retrieve_date_time_info` from C0 to B0 (#625)
- Conversion from dict to json drop the timeindexes from pandas.Series (#625)
- Conversion from json to dict allow to load a timeindex for pandas.Series (#625)
- Replace `==` by `is` in expression with `True`, `False` or `None` (#625)
- Remove unused `dict_values` argument of function `receive_timeseries_from_csv` (#625)
- Move the end of the function `receive_timeseries_from_csv` into `C0.compute_timeseries_properties()` (#625)
- Fix rendering issues with the PDF report and web app: Tables, ES graph sizing (#643)
- Improve the description of demands in the autoreport: Adapted section so that it applies to all vectors (#647)

### Removed
- Parameter label from input csv files; label is now set by filenames (for `project_data`, `economic_data`, `simulation_settings`) and column headers (for `energyConsumption`, `energyConversion`, `energyProduction`, `energyProviders`), special for storage: `filename` + `column header` (#602)
- Remove reference to git branch ID in the report (#607)

### Fixed
- RTD entry for defining parameters as timeseries (#597)
- Math equations of RTD in files `Model_Assumptions.rst` and `MVS_Output.rst` (#604)
- Repaired the broken links to input CSV files (#618)
- Outdated RTD info and mistakenly deleted sentence (#629)
- All `variable_costs`, `efficiency` and `nominal_value` of transformers on output flows. Before they were inconsistently assigned to input or output flows. (#596)
- Calculation of the renewable share relative taking into account energy carrier weighting (#637)

## [0.5.0] - 2020-10-05

### Added
- Instruction to install graphviz on windows in `docs/troubleshooting.rst` (#572)
- Benchmark test `test_benchmark_feature_parameters_as_timeseries` to ensure that parameters can always also be defined as a timeseries. Applied to `efficiency` of an energyConversion asset and `electricity_price` of an energyProduction asset (#542)
- Input files for benchmark tests `test_benchmark_feature_input_flows_as_list` (`Feature_input_flows_as_list`) and `test_benchmark_feature_output_flows_as_list` (`Feature_output_flows_as_list`), but not the benchmark assertions (#542)
- Error message if time series of non-dispatchable sources do not meet requirement: values betw. 0 and 1. (#498)
- Requirement for time series of non-dispatchable sources in readthedocs (#498)
- Provide a warning in case of excessive excess generation (#498)
- Pytests for `C0.add_maximum_cap()`, renamed function into `C0.process_maximum_cap_constraint()` (#498)
- Description of the inherited MVS limitations as well as the ones that can be addressed (#580)

### Changed
- Modify `setup.py` to upload the code as package on pypi.org (#570)
- Improve message when the `tests/test_input_folder_parameters.py` fails (#578)
- Modify PR template to precise to add assert message and link to example docstring 
- Update CONTRIBUTING to add a "Write test for your code" section before the "Run tests locally" one (#579)
- Modified readthedocs page describing the parameters of MVS (#479)
- Changed `E2.calculate_dispatch_expenditures()` so that it can process parameters defined as lists (#542)
- Rename `E4` to `E4_verification.py` (#498)
- Rename package name `mvs_eland` to `multi-vector-simulator` in `setup.py` (#587)
- Rename `src/mvs_eland` to `src/multi_vector_simulator` (#587)
- Rename repository from `mvs_eland` to `multi-vector-simulator` (#587)
- Refactor modules calls (`mvs_eland.` is replaced by `multi_vector_simulator.`) (#587)
- Update `README.md` and `CONTRIBUTING.md` replacing `mvs_eland` or `mvs-eland` by `multi-vector-simulator` (#587)

### Removed
- Remove unused function `mvs_eland.utils.get_version_info` (#587)

### Fixed
- Update the release protocol in `CONTRIBUTING.md` file (#576)
- Fix reading timeseries for parameters in `C0` (#542)
- Constraint for `optimizedAddCap` of non-dispatchable sources: multiply `maximumCap` by `max(timeseries(kWh/kWp))` to fix issue #446 (#562, #498)
-`timeseries_normalized` are calculated for all `timeseries` of non-dispatchable sources now (before only if `optimizeCap==True`) (#562, #498)
- Input files of benchmark test `Test_Constraints.test_benchmark_minimal_renewable_share_constraint()` (#498)

## [0.4.1] - 2020-09-21

### Added
- Evaluation of excess energy for each of the energy carriers and for the whole system. The excess per sector and their energy equivalent may currently be faulty (comp. issue #559) (#555)
- Debug messages for pytests: `C0`, `D2` (#555, #560)
- Labels on capacity barplot bars (#567)

### Changed
- `C1.total_demand_each_sector()` to `C1.total_demand_and_excess_each_sector()`, now also evaluating the excess energy flows (#555)
- `energyBusses` now is defined by: `LABEL, ASSET_LIST, ENERGY_VECTOR`, all functions using `energyBusses` now follow this nomenclature (#555)
- Energy excess sinks now also have parameter `ENERGY_VECTOR` (#555)
- `C0.define_sink` now always defines a sink that is capacity-optimized (#555)
- `D1.sink_dispatchable()`, renamed to `D1.sink_dispatchable_optimize()` now adds a capacity-optimized, dispatchable sink. (#555) 
- Simulation data `tests/inputs`: Oemof-solph results are not stored (#555)
- Change logging level of some messages from `logging.info` to `logging.debug` (#555)
- Move and rename json input files for D0 and D1 tests (`test_data_for_D0.json` to `tests/test_data/inputs_for_D0/mvs_config.json`, `test_data_for_D1.json` to `tests/test_data/inputs_for_D1/mvs_config.json`), add required parameters (#555) 
- Change requirements/test.txt: `black==19.10b0`, as otherwise there are incompatabilities (#555)
- `D2.prepare_constraint_minimal_renewable_share`, including logging messages and pytest (#560)
- Change the import path of the modules for automatic docstrings import in `docs/Code.rst` (#564)
- Fix the docstrings with math expressions (need to add `r` before the `"""` of the docstring
) (#564)
- Rename the function in F1 module `plot_flows` to `plot_instant_power` (#567)
- Change flow to power in the instanteous power figures (#567)
- `F1.plot_piecharts_of_costs()` now cites costs with currect currency and avoids decimal numbers (#561)

### Fixed
- `C1.check_feedin_tariff()` now also accepts `isinstance(diff, int)` (#552)
- Feed-in sinks of the DSOs now are capacity-optimized and can actually be used (#555)
- Incorrectly applied minimal renewable share criterion (#560)
- Pdf report generation (#566)
- Update fresh install instructions for developers (#565)
- Graphs of the report now use appropriate currency (#561)

## [0.4.0] - 2020-09-01

### Added
- Docstrings for E2 (#520)
- New constant variable: `SIMULATION_RESULTS="simulation_results"` (#520)
- Explicit calculation of replacement costs (`C2.get_replacement_costs()`), so that they can be used in `E2` for installed capacities and optimal additional capacities (#520)
- New constant variable: JSON_WITH_RESULTS="json_with_results.json" (#520)
- Benchmark test "Economic_KPI_C2_E2" to test economic evaluations in C2 and E2 (#520)
- Possibility to add an upper bound  on the number of days to display in a timeseries' plot (#526)
- Graph of the energy system model to the report (#528)
- Function to encode images into dash app's layout (#528)
- System KPI now printed in automatic report (section "Energy system key performance indicators"), draft (#525)
- Added units to system-wide cost KPI in excel and in report. Some of these changes might need to be reworked when elaborating on units for the report (#525)
- `References.rst` to the readthedocs, which should gather all the references of the MVS (#525)
- New system-wide KPI:
    - Demand per energy carrier, in original unit and electricity equivalent with `E3.total_demand_each_sector()` (#525)
    - Attributed cost per energy carrier, related to the its share in the total demand equivalent  with `E3.total_demand_each_sector()` (#525)
    - LCOE per energy carrier `E3.add_levelized_cost_of_energy_carriers()` (#525)
- Default values for energy carrier "Heat" for `DEFAULT_WEIGHTS_ENERGY_CARRIERS` with `{UNIT: "KWh_eleq/kWh_therm", VALUE: 1}`. This is still TBD, as there is no source for this ratio yet (#525)
- Default unit for energy carriers defined in `DEFAULT_WEIGHTS_ENERGY_CARRIERS`: ENERGY_CARRIER_UNIT. Might be used to define the units of flows and LCOE. (#525)
- New constant variables: TIMESERIES_TOTAL, TIMESERIES_AVERAGE, LOGFILE, RENEWABLE_SHARE, TOTAL_DEMAND, SUFFIX_ELECTRICITY_EQUIVALENT, ATTRIBUTED_COSTS, LCOeleq, DEGREE_OF_SECTOR_COUPLING (#525)
- New constant variable: OEMOF_BUSSES, MINIMAL_RENEWABLE_SHARE, CONSTRAINTS (#538)
- New required input csv: `constraints.csv` including possible constraints for the energy system. Added to all input folders. (#538)
- Added error message: New energy carriers always have to be added to `DEFAULT_WEIGHTS_ENERGY_CARRIERS` (`C0.check_if_energy_carrier_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS()`, applied to `ENERGY_VECTOR` and to fuel sources) (#538)
- Added minimal renewable share contraint though  `D2.constraint_minimal_renewable_share()` and added description of the constraint in `Model_Assumptions.rst` (#538)
- Benchmark test for minimal renewable share constraint (#538)
- Benchmark test `test_benchmark_AFG_grid_heatpump_heat` for a sector-coupled energy system, including electricity and heat, with a heat pump and an energy price as time series (#524)
- Benchmark test descriptions for `test_benchmark_simple_scenarios.py` (#524)
- Create `src/mvs_eland/utils` subpackage (contains `constants.py`, `constants_json_string.py
`, `constants_output.py` (#501)

### Changed
- Changed structure for `E2.get_cost()` and complete disaggregation of the formulas used in it (#520)
- Added pytest for many `E2` functions (#520)
- Changed and added pytests in for `C2` (#520)
- All energyProviders that have key `FILENAME` (and, therefore, a timeseries), are now of `DISPATCHABILITY = False`(#520)
- Changed structure of `E2.lcoe_assets()` so that each asset has a defined LCOE_ASSET. If `sum(FLOW)==0` of an asset, the LCOE_ASSET (utilization LCOE) is defined to be 0 (#520)
- Color lists for plots are provided by user and are not hard coded anymore (#527)
- Replace function `F1.draw_graph` by the class `F1.ESGraphRenderer` and use `graphviz` instead of
 `networkx` to draw the graph of the energy system model (#528) 
- Rename variable `PLOTS_NX` to `PLOTS_ES` (#528)
- Changed `requirements.txt` (removing and updating dependencies) (#528)
- A png of the energy system model graph is only saved if either `-png` or `-pdf` options are chosen (#530)
- Accepting string "TRUE"/"FALSE" now for boolean parameters (#534)
- Order of pages in the readthedocs.io (#525)
- Reactivated KPI: Renewable share. Updated pytests (#525)
- Extended `DEFAULT_WEIGHTS_ENERGY_CARRIERS` by `Diesel` and `Gas`, added explaination in `Model_Assumptions.rs` (#538)
- Create `dict_model` with constant variables in `D0` and update in `D1` (#538)
- Separate the installation of the packages needed for the report generation from the mvs
 simulation (#501)
- Move all source files in `src/mvs_eland` (#501)
- Move the content of the previous `src/utils.py` module to  `src/mvs_eland/utils/__init__.py` (#501)
- Rename `tests/constants.py` --> `tests/_constants.py` (#501)
- Refactor modules calls (mostly `src.` is replaced by `mvs_eland.`) (#501)
- Move `mvs_eland_tool` folder's content in `src/mvs_eland` (#501)
- Gather all requirements files in a `requirements` folder and read the requirement from there for `setup.py` (#501)
- Update `install_requires` and `extra_requires` in `setup.py` (#501)

### Removed
- `E2.add_costs_and_total`() (#520)
- Calculation of energy expenditures using `price` (#520)
- Function `F1.plot_input_timeseries` which is based on `matplotlib` (#527)
- Dependency to `matplotlib` (#528)
- Remove `STORE_NX_GRAPH` and `DISPLAY_NX_GRAPH` variables (#530)
- Remove `tests/__init__.py` (#501)
- Delete `mvs_eland_tool` folder (#501)

### Fixed
- Calculation of `cost_upfront` required a multiplication (#520)
- Fixed `E2.convert_components_to_dataframe()`, Key error (#520)
- Fixed `F1.extract_plot_data_and_title()`, Key error (#520)
- Fixed hard-coded energy vector of ENERGY_PRODUCTION units in E1.convert_components_to_dataframe(#520)
- Generating report for multiple sectors (#534)
- Fixed hard-coded energy vector of `ENERGY_PRODUCTION` units in `E1.convert_components_to_dataframe` (#520)
- Fixed parsing issue in `A1.conversion()`, incl. pytest (#538)
- Quick fix to read a timeseries for `"price"` in `C0.define_source()` (#524)
- Fix `C1.check_feedin_tariff()`: Now also applyable to timeseries of feed-in tariff or electricity prices (#524)
- Add a warning message if the timeseries of demands or resources are empty (#543)
- Fix failing KPI test (due to newer pandas version) (#501)

## [0.3.3] - 2020-08-19

### Added
- Also components that have no investment costs now have a value (of 0) for COST_INVESTMENT and COST_UPFRONT (#493)
- Display error message when feed-in tariff > electricity price of any  asset in 'energyProvider.csv'. (#497)
- Added pie plots created using Plotly library to the auto-report (#482) 
- Added functions to `F2_autoreport.py` that save the images of plots generated using Plotly to `MVS_outputs` folder as `.png` (#499)
- Inserted docstrings in the definitions of all the functions in `F2_autoreport.py` (#505)
- Functions in F1 to create plotly static `.png` files (#512)
- New argument for MVS execution: `-png` to store plotly graphs to file (#512)
- Benchmark test for peak demand pricing for grid and battery case (#510)
- Logging error message if a cell is left empty for a parameter in the csvs (see `A1`) (#492)
- Logging error message if a bus connects less then three assets including the excess sink, as in that case the energy system model is likely to be incomplete (`C1.check_for_sufficient_assets_on_busses()`) (#492)

### Changed
- Move and rename json converter and parser to B0 module (#464)
- Modified json converter to avoid stringifying special types such as pandas.Dataframes (#464)
- Changed the font family used in the plots in F2_autoreport.py and changed the wording of some comments (#496)
- Changed styling of plots, mainly how legends appear in the PDF report (#482) 
- Move and rename json converter and parser to B0 module (#464)
- Modified json converter to avoid stringifying special types such as pandas.Dataframes (#464)
- Changed the font family used in the plots in F2_autoreport.py and changed the wording of some comments (#496)
- Replaced parameter strings by variables (#500)
- Changed the font family used in the plots in F2_autoreport.py and changed the wording of some comments (#496)
- Moved function `C0.determine_lifetime_price_dispatch()` to C2 with all its sub-functions.  (#495)
- Changed calculation of `LIFETIME_PRICE_DISPATCH` for lists and pd.Series (see dosctrings of `C2.get_lifetime_price_dispatch_list`, `C2.get_lifetime_price_dispatch_timeseries`) (#495)
- Changed dostring format in `C2` to numpy (#495)
- Deactivated function `C2.fuel_price_present_value` as it is not used and TBD (#495)
- Modified the doc-strings in the definitions of some functions to abide by the formatting rules of numpy doc-strings (#505)
- Suppressed the log messages of the Flask server (for report webapp) (#509) 
- Move bulk data preparation code for report from F2 into E1 and F1 modules and into functions (#511, #512)
- F2 now calls functions from F1 to prepare the figures of the report (#512)
- Dispatchable (fuel) sources can now be defined by adding a column to the `energyProduction.csv` and setting `file_name==None` (#492)
- Updated `Model_Assumptions.rst`: Minimal description of dispatchable fuel sources (#492)
- `tests/inputs` energyAssets are updated (#492)
- Fixed test_benchmark_AD_grid_diesel() - now this one tests fuel source and diesel at once (#492)

### Removed
- Functions to generate plots with matplotlib in F1 (#512)
- Many tests that checked if matplot lib plots were stored to file, not replaced by new tests for storing plotly graphs to file (#512)

### Fixed
- Image path for readthedocs (Model_Assumpation.rst) (#492)

## [0.3.2] 2020-08-04

### Added
- `Model_Assumptions` added, including outline for component models, bulletpoints on limitations, energyProviders and peak demand pricing model. (#454)

### Changed
- Definition of busses from assets: Now all INFLOW_DIRECTION / OUTFLOW_DIRECTION are translated into ENERGY_BUSSES (#454, #387)
- An excess sink is created for each and every bus (#454)
- Splitting functions in `C0` and adding tests for them: `C0.define_sink()`, `C0.define_source()` and `C0.define_dso_sinks_and_sources()` (#454)
- Instead of defining multiple DSO sources for modelling peak demand pricing, now a single source is defined and another level added with transformers that, with an availability limited to a peak demand pricing period, only represent the costs of peak demand pricing in the specific period. (#454)
- Moved function `C0.plot_input_timeseries()` to `F1.plot_input_timeseries()` (#454)
- Add required parameter "unit" to energyProviders.csv. Used for defining the units of the peak demand pricing transformer. (#454)
- Updated `F2` for new DSO/excess sink structure: DSO feedin and excess sink removal from demands now universal (#454)
- Replace `logging.warning` for dispatch price of sources in case of DSOs - this is now only an `logging.info`
- Added global variables for KPI connected to renewable energy use (TOTAL_RENEWABLE_GENERATION_IN_LES = "Total internal renewable generation", TOTAL_NON_RENEWABLE_GENERATION_IN_LES = "Total internal non-renewable generation", TOTAL_RENEWABLE_ENERGY_USE = "Total renewable energy use", TOTAL_NON_RENEWABLE_ENERGY_USE = "Total non-renewable energy use") (#454)
- Updated to disagregated `oemof-solph==0.4.1`, which required changing the `requirements.txt` as well as the usage of `oemof` within the MVS (#405)

### Removed
-

### Fixed
- Peak demand pricing feature (#454)


## [0.3.1] - 2020-07-30

### Added
- Release protocol in `CONTRIBUTING.md` file (#353)
- Custom heat demand profile generation (#371)
- Add custom solar thermal collector generation profile (#370)
- Input template folder for easy generation of new simulations (#374), later also for tests of the input folder
- Tests for ABE usecase (grid, PV, battery) (#385)
- Test to verify that input folders have all required parameters (#398)
- New `dict` `REQUIRED_MVS_PARAMETERS` to gather the required parameters from the csv or json
 input type (#398)
- `utils.py` module in `src` to gather the functions `find_input_folders` and `compare_input_parameters_with_reference` which can be used to find and validate input folders (#398)
- Code and test for checking for new parameters in csv and raising warning message if not defined (`A1.check_for_newly_added_parameters`). This then also adds a default value to the new parameter  (#384)
- Exception if an energyVector does not have internal generation or consumption from a DSO, and is only supplied by energy conversion from another sector: renewable share = 0. (#384)
- Tests for source components in D1 (#391)
- Option `-i` for `python mvs_report.py`, `python mvs_report.py -h` for help (#407)
- Pyppeteer package for OS X users in troubleshooting (#414)
- Add an enhancement to the auto-report by printing the log messages such as warnings and errors (#417)
- New `dict` `REQUIRED_JSON_PARAMETERS` to gather the required parameters from the json input files (#432)
- `.readthedocs.yml` configuration file (#435, #436)
- Calculation of levelized cost of energy (`LCOE_ASSET`) of each asset in E2 (#438)
- Tests for LCOE function in `test_E2_economics` (#438)
- Output of `scalars.xlsx`now also includes `INSTALLED_CAP` and `LCOE_ASSET`(#438)
- File `constants_output.py` to contain all keys included in `scalars.xlsx` (#453)
- Installation help for `pygraphviz` on Win10/64bit systems in `troubleshooting.rst` (#379)
- Add Plotly-based blots (line diagrams for energy flows and bar charts) to `F2_autoreport.py` (#439)
- LCOE_ASSET (Levelized Cost of Energy of Asset) explaination in KPI documentation (#458)
- Heat demand profiles with option of using monitored weather data (ambient temperature) at the use case UVtgV. note: file not provided so far (#474)
- Solar generation profiles with option of using monitored weather data (ambient temp, ghi, dhi) at the use case uvtgv. note: file not provided so far (#475)
- Benchmark test for simple case grid and diesel without test for fuel consumption (#386)
- Example docstring to readthedocs (#489)

### Changed
- Use selenium to print the automatic project report, `python mvs_report.py -h` for help (#356)
- Sort parameters in csv´s within the input folder (#374)
- Change relative folder path to absolute in tests files (#396)
- Replace all variables wacc, discount_factor and project_lifetime in the project (#383)
- Improve styling of the pdf report (#369)
- `LIST_OF_NEW_PARAMETERS` renamed `EXTRA_CSV_PARAMETERS` and moved from `A1` to `constants.py
` (#384)
- Order of parameters in `tests/inputs`, fixed missing parameters  (#384)
- Only a single output flow for sources (instead of multiple possible) as discussed in #149  (#391)
- Move `existing` parameter into Investment objects of D1 components (was before added to output flow) (#391)
- Use pyppeteers instead of selenium to emulate the webbrowser and print the pdf report
 automatically (#407)
- Update flowchart again (#409)
- Label of storage components (storage capacity, input power, output power) will by default be redefined to the name of the storage and this component (#415)
- Version number and date is only to be edited in one file (#419)
- Add `ìnputs` folder to `.gitignore` (#401)
- Change the calculation of the residual value for specific capex in C2 and test_C2 (#289, #247, PR #431): Now the present value of the residual value is considered
- Explicitly return the dataframe with parameters value in function
 `check_for_newly_added_parameter` (#428)
- Rename function `check_for_newly_added_parameter` in `check_for_official_extra_parameters` (#428)
- Add `ìnputs` folder to `.gitignore` (#401)
- Readthedocs links to simple scenario `tests/inputs` (#420)
- Adapt and add logging messages for components added to the model in D1 (#429)
- Moved list of keys to be printed in `scalars.xlsx` to `constants_output.py` (#453)
- Renamed `"peak_flow"` to `PEAK_FLOW` and `"average_flow"` to `AVERAGE_FLOW` (#453)
- Changed function `E2.lcoe_asset()` and its tests, now processes one asset at a time (#453)
- Added arguments ``-f`, `-log`, `warning`` to all `parse_args` and `main()` in `tests` (#456)
- File `Developing.rst` with new description of tests and conventions (#456)
- Added a `setup_class` (remove dir) to `test_B0.TestTemporaryJsonFileDisposal` (#379)
- Created function to read version number and date from file instead of importing it from module
 (#463)
- Fixed `E0.store_results_matrix()`, now available types: `str`, `bool`, `None`, dict (with key VALUE), else (`int`/`float`). If KPI not in asset, no value is attributed. Added test for function (#468, #470)
- Fixed `main()` calls in `test_F1_plotting.py` (#468)
- Added `pyppdf==0.0.12` to `requirements.txt` (#473)
- Tests for A0: Now new dirs are only created if not existant
- Function `A0.check_output_folder()`, now after `shutil.rmtree` we still `try-except os.mkdirs`, this fixes local issues with `FileExistsError`.  (#474)
- Added `pyppdf==0.0.12` to `requirements.txt` (#473)

### Removed
- Selenium to print the automatic project report for help (#407)
- `MaximumCap` from list of required parameters for `energyStorage` assets (#415)
- `inputs` folder (#401)
- `tests/test_benchmark.py` module (#401)
- Outdated table of tests of MVS `docs/tables/table_tests.csv` (#456)
- Removed function `C0.complete_missing_cost_data()` as this should be covered by A1 for csv files (#379)
- Old plots in `F2_autoreport.py` generated with matplotlib (#439)
- Parameter `restore_from_oemof_file` from all files (inputs, tests) (#483)
- Deleted columns from `fixcost.csv` as this is currently not used (#362)

### Fixed
- Bug connected to global variables (#356)
- Duplicate of timeseries files (#388)
- Warnings from local readthedocs compilation (#426)
- Bug on local install (#437)
- Input folder `tests/inputs` with simple example scenario (#420)
- Description of storage efficiency in readthedocs (#457)
- MVS can now be run with argument `-pdf` (fix pyppeteer issue) (#473)
- Adapted benchmark tests input folders to template (#386)
- Local failing pytests (`FileExistsError`) on Ubuntu and Win10 (#474, #483)
- 9 Warnings due to excess parameter `restore_from_oemof_file` (#483)

## [0.3.0] - 2020-06-08

### Added
- Test for re-running a simulation with `json_input_processed.json` file (#343)

### Changed
- Test input files (#343)
- All parameters of the json/csv input files are now defined by constant variables (i.e, `CRATE="crate"` instead of string `"crate"`) (#346)
- Use `is` instead of `==` in if clauses for True, False and None (#346)
- Categorize constants in `constants_json_strings.py` (#347)
- Renaming CAPEX_FIX = "capex_fix" into COST_DEVELOPMENT = "development_costs" (#347, #350)
- Renaming CAPEX_VAR = "capex_var" into SPECIFIC_COST = "specific_costs" (#347, #350)
- Renaming OPEX_FIX = "opex_fix" into SPECIFIC_COST_OM = "specific_costs_om" (#347, #350)
- Renaming OPEX_VAR = "opex_var" into PRICE_DISPATCH = "dispatch_price" (#347, #350)
- Change last strings into global constants in "constants_json_strings.py" (#349)
- Autoreport now refers to actual project and scenario name + ID (#349)


## [0.2.1] - 2020-05-28

### Added
- Tests for the module B0 (#140, #255)
- Tests for the module A1 (#141)
- Tests for the module E3 (#143)
- Tests for the module F0 (#142, #304, #335)
- Some tests for E2 (#144)
- Tests function names for E1 (#145)
- Tests for the module E0 (#146)
- Tests for module D2 (#147)
- Some tests for module C0 (#148)
- Tests for the module D1 (still - partly - open: transformers, sources. finished: sinks, storages, other functions) (#149)
- Tests for the module D0 (#150)
- Tests for module C2 (#151)
- Tests for the module C1 (only used function) (#152)
- Tests for module F1 (#157, #297, #284)
- Pull request template (#198)
- Issue template (#212)
- File `troubleshooting.rst` to readthedocs (#229)
- File `simulating_with_the_mvs.rst` to readthedocs: How to use the input files (csv/json) (#130), how to create an own simulation/project
tipps for module building, and hint that units in the MVS are not checked (#229)
- Images for `simulating_with_the_mvs.rst`: images/energy_system.png, images/energy_system_model
.png, images/folder_structure_inputs.png (#229)
- Tables for `simulating_with_the_mvs.rst`: files_to_be_displayed/example_multiple_inputs_energyConversion.csv
, files_to_be_displayed/example_scalar_as_timeseries_energyConversion.csv (#229)
- Benchmark test for csv inputs (#254)
- Benchmark test with only PV and grid (#258)
- Module F2 for auto-reporting results of MVS simulation (#232)
- Json entries including paths to all plotted graphs (#232)
- Technical parameters: Energy flows (aggregated) per asset, Renewable share (#223, #257)
- Save network graph as png to output folder if new parameter `store_nx_graph` is true (#242)
- Tests for storage for the module A1 (#299)
- Benchmark test with only battery and grid (#302)
- Flowchart and relative description (#305)
- Reference to license (#305)
- Description of validation scheme into readthedocs (#306)
- Possibility to save the report generated in F2 as a pdf (#284)
- Possibility to run benchmark tests selectively and make sure they are all run on master branch
 (#320)
- Possibility to deploy the report of the results in a browser (#323)
- A main() function to be used by a server which only accepts json variable and returns json
 variable (not saving to a file) (#327)
- Add information about the feature to view the web app and generate PDF of the automatic report to readthedocs (#283)

### Changed
- Default input files from "inputs": Changed some parameters (#143)
- Moved some functions between F0 and F1, rearranged functions in F1 (#157)
- Shore power randomization improved + amount of available docks can be chosen (#202)
- Update kwargs of main func in docstring and in documentation (#208)
- `troubleshooting.rst`: Added help for `pygraphviz` (#218), `xlrd` (#11), `json.decoder.JSONDecodeError` (#206)
- FileNotFoundError messages in A0 (#227)
- Update json file `mvs_config.json`: Default with no peak demand pricing. Replace string "False" by boolean `false`. Remove depreciated parameters from `simulation_settings`(`input_file_name`, `overwrite`, `path_input_file`, `path_input_folder`, `path_input_sequences`, `path_output_folder`, `path_output_folder_inputs`) (#234)
- Renamed `plot_nx_graph` to `display_nx_graph` and added `store_nx_graph` (#242)
- Variables `required_files_list` and `ALLOWED_FILES` have been replaced by `REQUIRED_FILES` (#251)
- The columns of the storage_xx files are renamed and the specific parameters for each column are
 checked in A1 (#259)
- Possibility to move the json file after reading it (useful if json file created from csv files
) (#255)
- Call timeseries plot function for each bus (#278)
- The input from the csv files produce the same json than the json file (#286)
- Rename "storage" parameter in A1 and tests_A1 to "asset_is_a_storage" (#300)
- Serialize the DataFrame and arrays into the json_with_results.json (#304)
- Convert serialized DataFrame and arrays back into these types in the B0.load_json function
 (#304, #322, #326)
- Move the CSS styling code to a style sheet (#317)
- Change the input data for creating the dataframes for generating the optimization and costs' tables from xlsx file to json (#317) 
- Rename mvs_eland_tool/mvs_eland_tool.py --> mvs_eland_tool/local_deploy.py (#327)
- Now main (local use) and run_simulation (server use) are available in mvs_eland_tool package
  (#327)

 
### Removed
- Removed parameter `oemof_file_name` from `simulation_settings.csv`, as well as from all input
 files etc. The name is hardcoded now (#150)

### Fixed
- Fix naming error for storages (#166)
- Fix json file (#203)
- Delete duplicated entry of `plot_nx_graph` from json file (#209)
- Rename "boolean" to "bool" in example json file (#214)
- Fix searching for dict key "input_bus_name" (#210) and using input_name instead of output_name (#219)
- Fix plotting error in F1, plot only if Data frame is not empty (#230, #234)
- Benchmark test that the simulation is running with default settings (#254)
- Fix specific parameters for each storage column (#259)
- Overwrite local results when running through brenchmark tests (#260)
- Allow more than one separator for csv files(#263)
- Fix plotting pie chart for costs, if statement added if no costs are available (#267)
- Fix long label resulting from total project costs (#270)
- Bug when the output path had contained an unexisting folder within an unexisting folder it
 would return an error (#278)
- Display SOC (#278)
- Automatic update of the test coverage with coveralls.io (#307)
- Logging message for maximumCap value (#310)
- Create_app function in F0 for standalone execution (#317)
- Crashing evaluation when `evaluated_period < 365/peak_demand_pricing_periods` by raising an
 error (#331) 

## [0.2.0] - 2020-03-13

### Added
- Readthedocs documentation for input parameters (#128)
- Doctring of module A0 (#138)
- Constants in `src/constants.py` (#153, #154)
- Readthedocs documentation for installation (#162)
- Plotting an networkx graph can now be turned of/on via "plot_nx_graph" in simulation_settings (#172)
- Plot all timeseries used as input data (#171)
- Integrate new parameter maximumCap as nominal value for energyProduction assets, ie. PV or wind plants (#125 )
- Integrate new parameter maximumCap as nominal value for storage assets and transformers (PR #243, comp. issue #125)

### Changed
- Give priority from kwargs on command line arguments (#112, #138)
- Docstrings of module A1 (#113)
- Changed keyword argument to positional argument for `create_input_json` function (#113)
- function `get_user_inputs` renamed `process_user_arguments` (#138)
- Tests for the module A0 (#138)
- Terminal commands (#135)
- PR request template (open/done/not applicable) (#205)
- URL of coverall badge (#265) 
- Function converting json to dict (#142)

### Removed
- Function welcome from module A0 (#138)
- Parameters `input_file_name`, `overwrite`, `path_input_file`, `path_input_folder`, `path_input_sequences`, `path_output_folder`, `path_output_folder_inputs` from `simulation_settings.csv` (#178)

### Fixed
- Input directory of csv files specified by user is handed to `load_data_from_csv.create_input_json()` (#112)
- \#111 & \#114 fix user choice of output folder via command line arguments(#115)
- Demand is no longer aggregated across sectors when processing/plotting in E1 (#169)
- Optimized storage capacities are printed into results matrix (#188)
- Sector diagrams now also include SOC diagrams (#189)
- Sources can now have variable costs (#173)
- \#182 Boolean simulation settings now also take affect
- Demand is no longer aggregated across sectors when processing/plotting in E1 (#169)

## [0.1.1] -2020-01-30

### Added
- test for running the main function (#109)
- the user can run the tool simply with `python mvs_tool.py` (#109)
### Fixed
- \#108 (#109)


## [0.1.0] - 2020-01-29

### Added
- tests for the A0 module (#87)
- badge for coveralls.io (#90)
- tests for the parsing of arguments (#97)
- exceptions for missing input file/folder (#98)
### Changed 
- removed unused class structure in all modules, execution stay the same (#86)
- link to build for this repository instead of previous one (#95)
- use argparser to parse the arguments from command line (#97)
- the full path of input folder containing csv is now required (#98)
### Removed
- argument parsing using sys.argv (#97)

## [0.0.3] - 2020-01-22

### Added
- LICENSE.md with GPL v2.0 (#38, smartie2076)
- folder "docs" and content to generate readthedocs (#39, smartie2076)
- Started readthedocs homepage (not working): https://readthedocs.org/projects/mvs-eland/ (#39, smartie2076, #57, Bachibouzouk)
- new feature to create the input json file from a collection of csv files (@Piranias)
- new module added: A1_csv_to_json.py (@Piranias)
- Badges for build and docs (#70, Bachibouzouk)
- Setup file (#72, Bachibouzouk)
- Parameters can now be a list of values, eg. efficiencies for two busses or multiple input/output vectors (#52, @marc-juanpera) 
- Parameters can now be a timeseries (eg. efficiency of a converter, electricity prices) (#37, #82, @marc-juanpera) 
- Parameters can now be defined as a list as well as as a timeseries (#52,#82, @marc-juanpera) 

### Changed
- requirements.txt only includes packages needed for users of MVS (#39, smartie2076)
- test_requirements.txt includes packages used by developers of MVS (#39, smartie2076)
- CONTRIBUTING: Now with read the docs (@smartie2076)
- README: Now with contextualization of MVS, setup & installation, utilization of and contributing to MVS (#47, smartie2076)
- directory structure of input/ (#49 @Piranias)
- json data structure reduced to 2 (main) levels: goup and asset (#49 @smartie2076)
- logging now stores into appropriate logfile (@smartie2076)
- change code_folder to src (#80)

### Removed
- Output files excluded from repro  (@smartie2076)

## [0.0.2] - 2019-11-25

### Added
- Introduced test for correct code formatting (blacks, closed issue #31, #18)
- Now unlimited number of busses possible
- Now with monthly peak demand pricing 
- Two test json files
- Files to create wiki page "Exemplary Workflow"

### Changed
- Introduced new code structure (folder "code") and updated relative import paths (closed #17)
- Introduced (basic) plots of optimized capacities and costs (addresses issue #29)
- CONTRIBUTING
- CHANGELOG
- Tests and travis file
- requirements.txt

### Removed
- Excel input file
- Python files to read from excel

## [0.0.1] - 2019-10-14

### Added
- CONTRIBUTING (#8)
- CHANGELOG (#8)
- Tests (#8, #10)

### Changed
- relative imports (#10)
- moved `mvs_eland_tool`'s content in a function (#10)

### Removed
- yet another thing
