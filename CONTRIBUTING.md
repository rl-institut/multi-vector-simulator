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
  function (under the section `Notes`) that this test exist, cf [example docstring](https://mvs-eland.readthedocs.io/en/latest/Developing.html#format-of-docstrings)!


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

Once you are ready to publish a release, branch off from `dev`
    ```bash
    git checkout -b release/vX.Y.Z dev
    ```
For meaning of X, Y and Z version numbers, please refer to this [semantic versioning guidelines](https://semver.org/spec/v2.0.0.html).

In this branch, you should normally only update the version number in the `src/multi-vector-simulator/version.py` and in the `CHANGELOG.md` files, respecting the indicated formats. Commit the first one with "Bump version number" as commit message.

Your `CHANGELOG.md` file could look like this before the release
```
## [unreleased]

### Added
- feature 1
- feature 2
### Changed 
- thing 1
- thing 2
### Removed
- some stuff
```

Simply replace `unreleased` by `X.Y.Z` and add the date of release in [ISO format](https://xkcd.com/1179/), then add the structure for a new `unreleased` version

```
## [unreleased]

### Added
-
### Changed 
-
### Removed
-

## [X.Y.Z] - 20**-**-**
### Added
- feature 1
- feature 2
### Changed 
- thing 1
- thing 2
### Removed
- some stuff
```
Commit this with "Update changelog" as commit message.

After pushing these changes, create a pull request from `release/vX.Y.Z` towards `master` and merge it in `master`.

Locally, merge `release/vX.Y.Z` into `dev`
```
git checkout release/vX.Y.Z
```

```
git pull
```
    
```
git checkout dev
```

```
git merge release/vX.Y.Z
```
And push your these updates to the remote version of dev
```
git push
```

The idea behind this procedure is to avoid creating a merge commit in `dev` (because `master` would otherwise have two merge commit for this release once you merge the next release).

Finally, [create a release](https://help.github.com/en/github/administering-a-repository/creating-releases) on github. Please choose master as the target for the tag and format the tag as `vX.Y.Z`. In the description field simply copy-paste the content of the `CHANGELOG`descriptions for this release and you're done!

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
