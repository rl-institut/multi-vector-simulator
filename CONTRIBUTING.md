## Development

### Prerequisites

- [Git](https://git-scm.com/)


### Philosophy

Development of a feature for this repository should follow the workflow described 
by [Vincent Driessen](https://nvie.com/posts/a-successful-git-branching-model/).

Here are the minimal procedure you should follow : 

0. Create [an issue](https://help.github.com/en/articles/creating-an-issue) on the github repository, describing the problem you will then address with your feature/fix.
This is an important step as it forces one to think about the issue (to describe an issue to others, one has to think it through first).

1. Create a separate branch from `dev`, to work on
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

3. Push your local branch on the remote server `origin`
```bash
git push
```
If your branch does not exist on the remote server yet, git will provide you with instructions, simply follow them.


#### Step 3: Run tests locally

To install all packages required for the integration tests locally:
```bash
pip install -r tests/test_requirements.txt
```

**!!! Important !!!**: You also need to install the mvs package locally in develop mode:
```bash
python setup.py develop
```
Otherwise your changes will not be perceived by the tests unless you run `python setup.py install` each time.

Please run the tests locally before pushing your feature to the developer branch. You do that by running:
```bash
pytest
```
Integrated tests (see ./tests/tests.py):

|Name of test | Issue tested | Description| ToDo if test fails |
|---|---|---|---|
|test_run_smoothly | Code not terminating | Test checking whether mvs_eland_tool.py runs through | Re-check execution of mvs_eland_tool.py and make sure it does not terminate. |
| test_blacks_main | Code formatting |  Python code is tested with [Blacks](https://github.com/psf/black) for correct formatting ie. line breaks and line lenghts. Tested for mvs_eland_tool.py  | run 'black mvs_eland_tool.py' and commit changes with own commit message.|
| test_blacks_src | Code formatting |  Python code is tested with [Blacks](https://github.com/psf/black) for correct formatting ie. line breaks and line lenghts. Tested for all python code files in './src'.  | run 'src/*.py' and commit changes with own commit message. |

We want more integration tests.

We do not have a suite of unit tests yet.

#### Step 4: Submit a pull request (PR)

Follow the [steps](https://help.github.com/en/articles/creating-a-pull-request) of the github help to create the PR.
Please note that you PR should be directed from your branch (for example `myfeature`) towards the branch `dev`.

Add a line `Fix #<number of the issue created in Step 2.0>` in the description of your PR, so that when it is merged, it automatically closes the issue.

TODO elaborate on the pull request


## Contributing to Readthedocs

Readthedocs of the MVS is compiled with the content of folder "docs". After editing, execute

    cd docs
    make html

To update the html pages of readthedocs. Then you can commit, push and pull it like normal code. 

An introduction to creating the readthedocs with Sphinx is given here: https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html.