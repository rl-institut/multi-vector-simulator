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
```

## [Unreleased]

### Added
- `Model_Assumptions` added, including outline for component models, bulletpoints on limitations, energyProviders and peak demand pricing model. (#454)
- Proposal for a file where the default values of input parameters are defined (`constant_valid_intervals.py`). Might also be of use to automatically update the parameter descriptions in readthedocs?

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

### Removed
-

### Fixed
- Peak demand pricing feature (#454)

## [0.3.1] - 2020-07-30

### Added
- Release protocol in CONTRIBUTING.md file (#353)
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
 - Tests for LCOE function in test_E2_economics (#438)
 - Output of `scalars.xlsx`now also includes `INSTALLED_CAP` and `LCOE_ASSET`(#438)
- File "constants_output.py" to contain all keys included in "scalars.xlsx" (#453)
- Installation help for `pygraphviz` on Win10/64bit systems in `troubleshooting.rst` (#379)
 - Add Plotly-based blots (line diagrams for energy flows and bar charts) to `F2_autoreport.py` (#439)
- LCOE_ASSET (Levelized Cost of Energy of Asset) explaination in KPI documentation (#458)
- Heat demand profiles with option of using monitored weather data (ambient temperature) at the use case uvtgv. note: file not provided so far (#474)
- Benchmark test for simple case grid and diesel without test for fuel consumption (#386)

### Changed
- Use selenium to print the automatic project report, `python mvs_report.py -h` for help (#356)
- Sort parameters in csv´s within the input folder (#374)
- Change relative folder path to absolute in tests files (#396)
- Replace all variables wacc, discount_factor and project_lifetime in the project (#383)
- Improve styling of the pfd report (#369)
- `LIST_OF_NEW_PARAMETERS` renamed `EXTRA_CSV_PARAMETERS` and moved from `A1` to `constants.py
` (#384)
- Order of parameters in tests/inputs, fixed missing parameters  (#384)
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
- Moved list of keys to be printed in "scalars.xlsx" to "constants_output.py" (#453)
- Renamed "peak_flow" to `PEAK_FLOW` and "average_flow" to `AVERAGE_FLOW` (#453)
- Changed function "E2.lcoe_asset()" and its tests, now processes one asset at a time (#453)
- Added arguments `"-f", "-log", "warning"` to all `parse_args` and `main()` in `tests` (#456)
- File `Developing.rst` with new description of tests and conventions (#456)
- Added a setup_class (remove dir) to `test_B0.TestTemporaryJsonFileDisposal` (#379)
- Created function to read version number and date from file instead of importing it from module
 (#463)
- Fixed E0.store_results_matrix(), now available types: 'str', 'bool', 'None', dict (with key VALUE), else ('int'/'float'). If KPI not in asset, no value is attributed. Added test for function (#468, #470)
- Fixed main() calls in 'test_F1_plotting.py' (#468)
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
- Removed function C0.complete_missing_cost_data() as this should be covered by A1 for csv files (#379)
- Old plots in `F2_autoreport.py` generated with matplotlib (#439)
- Parameter `restore_from_oemof_file` from all files (inputs, tests) (#483)

### Fixed
- Deleted columns from ´fixcost.csv´ as this is currently not used (#362)
- Issue #357 Bug connected to global variables (#356)
- Issue #168 Duplicate of timeseries files (#388)
- Warnings from local readthedocs compilation (#426)
- Issue #430 Bug on local install (#437)
- Input folder `tests/inputs` with simple example scenario (#420)
- Description of storage efficiency in readthedocs (#457)
- Bug connected to global variables (#356)
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
- Use "is" instead of "==" in if clauses for True, False and None (#346)
- Categorize constants in 'constants_json_strings.py' (#347)
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
- Tables for `simulating_with_the_mvs.rst`: tables/example_multiple_inputs_energyConversion.csv
, tables/example_scalar_as_timeseries_energyConversion.csv (#229)
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
- Removed parameter ´oemof_file_name´ from ´simulation_settings.csv´, as well as from all input
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
