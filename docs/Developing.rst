===================
Contributing to MVS
===================

Proposed workflow
-----------------
The workflow is described in the CONTRIBUTING.md file in the repository

Build documentation
-------------------

You can build the documentation locally moving inside the `docs/` folder and typing

.. code-block:: bash

    html build

into a console, then go to `docs/_build/` and open `index.html` into your favorite browser.

All functions in the code will be automatically documented via their docstrings. Please make sure they follow the `Numpy format <https://numpydoc.readthedocs.io/en/latest/format.html>`_.

Here is how to set that in pycharm

.. image:: _static/docstring-setting.png
  :width: 600
  :alt: pycharm docstring's format setting

Tests
-----

Some tests are integrated into the MVS reprository. They should execute correctly on each developer's computer after adding a new feature and will be tested when attempting to merge into the developer/master branch of the github project.

.. csv-table:: Implemented tests
   :file: ./tables/table_tests.csv
   :widths: 30, 50, 70, 70
   :header-rows: 1
