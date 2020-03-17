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
- Pull request template (#198)

### Changed

### Removed


## [0.2.0] - 2020-03-13

### Added
- Readthedocs documentation for input parameters (#128)
- Doctring of module A0 (#138)
- Constants in `src/constants.py` (#153, #154)
- Readthedocs documentation for installation (#162)
- Plotting an networkx graph can now be turned of/on via "plot_nx_graph" in simulation_settings (#172)
- Plot all timeseries used as input data (#171)

### Changed
- Give priority from kwargs on command line arguments (#112, #138)
- Docstrings of module A1 (#113)
- Changed keyword argument to positional argument for `create_input_json` function (#113)
- function `get_user_inputs` renamed `process_user_arguments` (#138)
- Tests for the module A0 (#138)
- Terminal commands changed (#135)
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

## [0.1.0] -2020-01-30

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

