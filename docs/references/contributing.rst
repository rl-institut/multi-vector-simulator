===================
Contributing to MVS
===================

Proposed workflow
-----------------
The workflow is described in the  `CONTRIBUTING.md<https://github.com/rl-institut/multi-vector-simulator/blob/dev/CONTRIBUTING.md>`__ file in the repository.


Unit tests (pytests)
--------------------

When developing code for the MVS please make sure that you always also develop test in `tests`. We integrate those unit tests with `pytest`.
Make sure that your tests are as lightweight as possible - this means that you do not always have to run the whole code to test for one feature, but can test a function with a standalone tests. Please refer to the other tests that have already been introduced.

Always aim for the test coverage button on `the main page of the github repository <https://github.com/rl-institut/multi-vector-simulator/>`__ to reach 100%!

When you do have to run the MVS itself for a test, eg. for benchmark tests, please always use the arguments `-f -log warning` to make the test results better readable.

Build documentation
-------------------

You can build the documentation locally moving inside the `docs/` folder and typing

.. code-block:: bash

    html build

into a console, then go to `docs/_build/` and open `index.html` into your favorite browser.

All functions in the code will be automatically documented via their docstrings. Please make sure they follow the `Numpy format <https://numpydoc.readthedocs.io/en/latest/format.html>`__.

Here is how to set that in pycharm

.. image:: _static/docstring-setting.png
  :width: 600
  :alt: pycharm docstring's format setting


Format of Docstrings
--------------------
Please add docstrings for every function you add. As docstrings are a powerful means of documentation we give an example here:

Download: :download:`Example docstring <files_to_be_displayed/example_docstring.py>`

.. literalinclude:: files_to_be_displayed/example_docstring.py
   :language: python


