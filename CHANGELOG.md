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
-
### Changed
-
### Removed

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

### Removed



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
