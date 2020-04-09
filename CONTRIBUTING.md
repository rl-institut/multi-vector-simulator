## Development

### Prerequisites

- [Git](https://git-scm.com/)


### Philosophy

Development of a feature for this repository should follow the workflow described 
by [Vincent Driessen](https://nvie.com/posts/a-successful-git-branching-model/).

Here are the minimal procedure you should follow : 

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

If a test fails, it is only due to what you changed (the test must passed before the code is
 merged, so you know that the tests were passing before you start working on your branch). The
  test names and error messages are there to help you find the error, please read them to try to
   debug yourself before seeking assistance :)

#### Step 4: Submit a pull request (PR)

Follow the [steps](https://help.github.com/en/articles/creating-a-pull-request) of the github help to create the PR.
Please note that you PR should be directed from your branch (for example `myfeature`) towards the branch `dev`.

Add a line `Fix #<number of the issue created at Step 1>` in the description of your PR, so
 that when it is merged, it automatically closes the issue.

The previous steps could be performed even before you solved the issue, to let other people know
 you are working on the issue.

Once you are satisfied with your PR you should ask someone to review it. Before that please lint
 your code with [Black](https://github.com/psf/black) (run `black . --exclude docs/`) and
  described succinctly what you have done in the [CHANGELOG](https://github.com/rl-institut/mvs_eland/blob/dev/CHANGELOG.md) file (indicating the number of the PR in parenthesis after
  the description, not the number of the issue)


## Contributing to Readthedocs

Readthedocs of the MVS is compiled with the content of folder "docs". After editing, execute

    cd docs
    make html

To update the html pages of readthedocs. Then you can commit, push and pull it like normal code. 

An introduction to creating the readthedocs with Sphinx is given here: https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html.