## Development

### Prerequisites

- [Git](https://git-scm.com/)

- Install the dev requirements with
```bash
pip install -e .[test,dev]
```
### Philosophy

Development of a feature for this repository should follow the workflow described 
by [Vincent Driessen](https://nvie.com/posts/a-successful-git-branching-model/).

Here is the minimal procedure you should follow : 

#### Step 1: Create an issue.
 
 Create [an issue](https://help.github.com/en/articles/creating-an-issue) on the github repository, describing the problem you will then address with your feature/fix.
This is an important step as it forces one to think about the issue (to describe an issue to others, one has to think it through first).

#### Step 2: Create a branch to work on the issue.

1. Create a separate branch from `dev` (make sure you have the latest version of `dev`), to work on
```bash
git checkout -b feature/myfeature dev
```
The convention is to always have `feature/` in the branch name. The `myfeature` part should describe shortly what the feature is about (separate words with `_`).

2. Try to follow [these conventions](https://chris.beams.io/posts/git-commit) for commit messages:
- Keep the subject line [short](https://chris.beams.io/posts/git-commit/#limit-50) (i.e. do not commit more than a few changes at the time)
- Use [imperative](https://chris.beams.io/posts/git-commit/#imperative) for commit messages 
- Do not end the commit message with a [period](https://chris.beams.io/posts/git-commit/#end) 
You can use 
```bash
git commit --amend
```
to edit the commit message of your latest commit (provided it is not already pushed on the remote server).
With `--amend` you can even add/modify changes to the commit.

3. Push your local branch on the remote server `origin` (please push your branch immediately so
 that everyone knows you are working on it, you are also encouraged to do the first part of Step 4)
```bash
git push
```
If your branch does not exist on the remote server yet, git will provide you with instructions, simply follow them.

#### Step 3.1: Write test for your code

It is important to write some test(s) to test that the feature you introduce works the way you want it to. In future development, your test(s) could always be ran to ensure your feature still works properly.

Look at the files existing in the `tests` folder if the test for your new feature could be placed
 in one of the existing test modules. If not, you can create your own module (the only requirement
  is that it must starts with `test_`).

When you test with `assert` you can add a string message which will be displayed if the test
 fails (`assert <condition>, <string message>`). It could be very useful to understand what exactly
 went wrong in the test for a developer 6 months from now.
 If you are testing a function in a module, it would be nice to indicate in the docstring of this
  function (under the section `Notes`) that this test exist, cf [example docstring](https://multi-vector-simulator.readthedocs.io/en/latest/Developing.html#format-of-docstrings)!


#### Step 3.2: Run tests locally

To install all packages required for the integration tests locally (if not done yet):
```bash
pip install -r requirements/test.txt
```

**!!! Important !!!**: You also need to install the mvs package locally in develop mode:
```bash
pip install -e .
```
Otherwise your changes will not be perceived by the tests.

Please run the tests locally before pushing your feature to the developer branch. You do that by running:
```bash
pytest
```

If a test fails, it is only due to what you changed (the test must passed before the code is
 merged, so you know that the tests were passing before you start working on your branch). The
  test names and error messages are there to help you find the error, please read them to try to
   debug yourself before seeking assistance :)

Some tests take more time to run (run a simulation) and were therefore disabled by default. It is
 nevertheless important that you run a simulation test before you ask a review, or whenever you
  are ready to merge, to make sure the
  code still works.
 ```bash
EXECUTE_TESTS_ON=dev pytest
```
will execute only the main simulation once to make sure it runs smoothly, whereas
 ```bash
EXECUTE_TESTS_ON=master pytest
```
will execute *all* benchmark tests (it takes thus a longer time to run)

*Note*: for windows users you can set the environnement variable with `set EXECUTE_TESTS_ON=master` and run the tests simply with `pytest`


#### Step 4: Submit a pull request (PR)

Follow the [steps](https://help.github.com/en/articles/creating-a-pull-request) of the github help to create the PR.
Please note that you PR should be directed from your branch (for example `myfeature`) towards the branch `dev`.

Add a line `Fix #<number of the issue created at Step 1>` in the description of your PR, so
 that when it is merged, it automatically closes the issue.

The previous steps could be performed even before you solved the issue, to let other people know
 you are working on the issue.
 
 Please follow the indications in the pull request template and update the appropriate checkboxes :)

Once you are satisfied with your PR you should ask someone to review it. Before that please lint
 your code with [Black](https://github.com/psf/black) (run `black . --exclude docs/`) and
  described succinctly what you have done in the [CHANGELOG](https://github.com/rl-institut/multi-vector-simulator/blob/dev/CHANGELOG.md) file (indicating the number of the PR in parenthesis after
  the description, not the number of the issue).

## Release protocol

This protocol explains how to perform a release of the code on ´master´ branch before releasing the code to pypi.org. If you don't want to release on pypi.org, skip the part under "The actual release".

### Local packaging test

Before starting uploading things to pypi.org, there are a few tests one can perform locally.

0. Make sure your local tests are all passing with environment variable `EXECUTE_TESTS_ON=master pytest` (see step Run tests locally above)

1. Open a fresh python3 virtual environment and make sure you have the latest versions of setuptools and wheel installed:

    ```bash
    pip install --upgrade setuptools wheel twine
    ```
2. Move to the root of your local copy of this repository and prepare the python package and remove previous version distribution files with 
    ```bash
    python prepare_package.py
    ```
3. Install multi-vector-simulator from the local packages
    ```bash
    pip install -e .
    ```
4. Move outside of this repository (with `cd ..`)
    ```bash
    cd ..
    ```
5. Create a new empty folder
    ```bash
    mkdir empty_folder
    ```
6. Test the multi-vector-simulator default simulation
    ```bash
    mvs_tool
    ```
    It should run the simulation and save the results in the default output folder.
    If the simulation does not run through, find out why and fix it.
    If you run this local packaging test multiple times, either create a new empty folder or run `mvs_tool -f` to overwrite the default output folder.

If this test passes locally, you can move to next step, upload a release candidate on pypi.org

### Release candidate on pypi.org

As on pypi.org, one is allowed to upload a given version only once, one need a way to test a release before making it official. This is the purpose of a release candidate.
Technically, a release candidate is similar to a normal release in the sense that someone can `pip install` them. However users will know that the release candidate is only there for test purposes.

1. Open a working python3 virtual environment and make sure you have the latest versions of setuptools and wheel installed:
    ```bash
    pip install --upgrade setuptools wheel twine
    ```
2. Make sure you pulled the latest version of `dev` branch from `origin`: `git checkout dev`, `git pull origin`.
3. Change the version (without committing) with release candidates (add `rc1` to the `version_num`, for example `vX.Y.Zrc1`) before the actual release, as a release with a specific version number can only be uploaded once on pypi.
4. Move to the root of your local copy of this repository and prepare the python package and remove previous version distribution files with 
    ```bash
    python prepare_package.py
    ```
    The last two lines should show the result of the twine check:
    ```
    Checking dist/multi_vector_simulator-X.Y.Zrci-py3-none-any.whl: PASSED
    Checking dist/multi-vector-simulator-X.Y.Zrci.tar.gz: PASSED
    ```
    If one of the two is not `PASSED`, find out why and fix it.

5. If the twine check passed you can now upload the package release candidate to pypi.org
    1. Check the credentials of our pypi@rl-institut.de account on https://pypi.org.
    2. Type `twine upload dist/*`
    3. Enter `__token__` for username and your pypi token for password.

6. Create a fresh virtual environment and install the release candidate version of the package
    ```bash
    pip install multi-vector-simulator==X.Y.Zrci
    ```
7. Move outside of this repository (with `cd ..`)
    ```bash
    cd ..
    ```
8. Create a new empty folder
    ```bash
    mkdir empty_folder
    ```
9. Test the multi-vector-simulator default simulation
    ```bash
    mvs_tool
    ```
    It should run the simulation and save the results in the default output folder.
    If the simulation does not run through, find out why and fix it.
    If you run this local packaging test multiple times, either create a new empty folder or run `mvs_tool -f` to overwrite the default output folder.

10. If you notice errors in the uploaded package, fix them and bump up `rc1` to `rc2` and repeat steps 3. to 9. until you don't see any more errors.

    It is encouraged to make sure step 6. to 9. are also performed on a different os than yours (ask a colleague for example)

11. If your release candidate works well you can now do the actual release on `master`, followed by the release on pypi.org

### Release on master

1. Create a release branch by branching off from `dev`
    ```bash
    git checkout -b release/vX.Y.Z dev
    ```
    For meaning of X, Y and Z version numbers, please refer to this [semantic versioning guidelines](https://semver.org/spec/v2.0.0.html).
2. In your release branch, update the version number in [`src/multi-vector-simulator/version.py`](https://github.com/rl-institut/multi-vector-simulator/blob/dev/src/multi_vector_simulator/version.py) in  in the format indicated under 1 (commit message: "Bump version number").
3. Replace the header `[Unreleased]` in the [`CHANGELOG.md`](https://github.com/rl-institut/multi-vector-simulator/blob/dev/CHANGELOG.md)
with the version number (see 2.) and the date of the release in [ISO format](https://xkcd.com/1179/): `[Version] - YYYY-MM-DD`.
4. After pushing these changes, create a pull request from `release/vX.Y.Z` towards `master` and merge it into `master`. It is normal that git tells you your release is out of date with master, do not hit the "update button"!
5. Create a [release tag](https://github.com/rl-institut/multi-vector-simulator/releases) on github.
Please choose `master` as target and use `vX.Y.Z` as tag version. In the description field simply copy-paste the content of the `CHANGELOG`descriptions for this release and you're done!
For help look into the [github release description](https://help.github.com/en/github/administering-a-repository/creating-releases).

### The actual release on pypi.org
*Note*: The packaging process is automatized with running `python prepare_package.py`. For details on how the packaging is preformed, check that script.

Follow the steps from the "Release candidate on pypi.org" section, without adding `rci` after the version number and ignoring step 11.

Congratulations, you just updated the package on pypi.org, you deserve a treat!

*Note*: should you notice a mistake/error after making the official release to pypi.org, you will have to bump the version number `Z` and publish a new version. Try to make careful checks with release candidate to prevent this from happening !

### After the release

1. Locally, merge `release/vX.Y.Z` into `dev` and push to the remote version of dev.
--> The idea is to avoid creating a merge commit in `dev` (because `master` would otherwise have two merge commits for this release once you merge the next release).
2. Set version for next release in [`src/multi-vector-simulator/version.py`](https://github.com/rl-institut/multi-vector-simulator/blob/dev/src/multi_vector_simulator/version.py) of the `dev`: for example `0.5.1dev`
3. Add the structure for a new `unreleased` version to the [`CHANGELOG.md`](https://github.com/rl-institut/multi-vector-simulator/blob/dev/CHANGELOG.md) in `dev`:
```
## [unreleased]

### Added
-
### Changed 
-
### Removed
-
### Fixed
-
```
4. Commit the steps 2. and 3. together with commit message "Start vX.Y.Zdev"

## Contributing to Readthedocs

You need to first install the required packages

```bash
pip install -r requirements/docs.txt
```

Readthedocs of the MVS is compiled with the content of folder "docs". After editing, execute

    cd docs

and then

    make html

To update the html pages of readthedocs. You will find the html files them under `docs/_build/html`
and can open them in your favorite browser. After you are done editing, you can commit, push and
 pull it like normal code.

Note: the compilation of certain docstrings requires latex amsmath package, if it is not
 available on your local computer, the math expression will not render nicely.

An introduction to creating the readthedocs with Sphinx is given here: https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html.
