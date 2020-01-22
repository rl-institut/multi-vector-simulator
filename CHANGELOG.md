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

## [Developer version] - 2020-01-22

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


