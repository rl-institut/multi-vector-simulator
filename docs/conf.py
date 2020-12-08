# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(".."))


def generate_parameter_description(input_csv_file, output_rst_file):
    """Read the MVS parameter description and generate a .rst formatted document

    Parameters
    ----------
    input_csv_file: str
        path of the file with extensive description of all mvs parameters
    output_rst_file: str
        path of the rst file with RTD formatted mvs parameters

    Returns
    -------
    None

    """
    df = pd.read_csv(input_csv_file, index_col=0)

    parameter_properties = [
        ":Definition:",
        ":Type:",
        ":Unit:",
        ":Example:",
        ":Restrictions:",
        ":Default:",
    ]

    lines = []
    # formats following the template:
    # .._<ref_name>:
    #
    # <name>
    # ^^^^^^
    #
    # :Definition:
    # :Type:
    # :Unit:
    # :Example:
    # :Restrictions:
    # :Default:
    #
    # ----
    #
    for row in df.iterrows():
        props = row[1]
        lines = (
            lines
            + [f".. _{props.ref}:", "", props.label, "^" * len(props.label), "",]
            + [f"{p} {props[p]}" for p in parameter_properties]
            + ["", "----", "",]
        )

    with open(output_rst_file, "w") as ofs:
        ofs.write("\n".join(lines))


generate_parameter_description("MVS_parameters_list.csv", "MVS_parameters_list.inc")

# -- Project information -----------------------------------------------------

project = "Multi-Vector Simulator (MVS)"
copyright = "2019, Reiner Lemoine Institut and Martha M. Hoffmann"
author = "Reiner Lemoine Institut and Martha M. Hoffmann"

from multi_vector_simulator.version import version_num
release = version_num

# -- General configuration ---------------------------------------------------

master_doc = "index"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.imgmath",
    "sphinx.ext.autosummary",
    "numpydoc",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
import sphinx_rtd_theme

html_theme = "sphinx_rtd_theme"

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
