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
    df = pd.read_csv(input_csv_file)
    df = df.loc[df.category != "hidden"]
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

        if isinstance(props.see_also, str):
            see_also = [
                "",
                "",
                "See also: "
                + ", ".join([f":ref:`{ref}`" for ref in props.see_also.split(";")]),
            ]
        else:
            see_also = []
        lines = (
            lines
            + [f".. _{props.ref}:", "", props.label, "^" * len(props.label), "",]
            + [f"{p} {props[p]}" for p in parameter_properties]
            + [""]
            + [
                "This parameter is used within the following categories: "
                + ", ".join([f":ref:`{cat}`" for cat in props.category.split(";")])
            ]
            + see_also
            + ["", "",]
        )

    with open(output_rst_file, "w") as ofs:
        ofs.write("\n".join(lines))


def generate_parameter_categories(
    input_param_csv_file, input_cat_csv_file, output_rst_file
):
    """Rassemble the MVS parameter categories from csv file and generate a .rst formatted document

    Parameters
    ----------
    input_param_csv_file: str
        path of the file with extensive description of all mvs parameters
    input_cat_csv_file: str
        path of the file with extensive description of all mvs parameters categories
    output_rst_file: str
        path of the rst file with RTD formatted mvs parameter categories

    Returns
    -------
    None

    """
    df_param = pd.read_csv(input_param_csv_file)
    df_cat = pd.read_csv(input_cat_csv_file)

    lines = []
    # formats following the template:
    # .._<ref_name>:
    #
    # <name>
    # ^^^^^^
    #
    # * :ref:`param1`
    # * :ref:`param2`
    #
    # ----
    #

    for row in df_cat.iterrows():
        props = row[1]
        cat_label = props.csv_file_name + ".csv"

        # lookup all parameters for which the category is tagged
        df_param["in_category"] = df_param.category.apply(
            lambda x: True if props.ref in x.split(";") else False
        )
        parameter_per_cat = df_param.loc[df_param.in_category == True, "ref"].to_list()

        lines = (
            lines
            + [f".. _{props.ref}:", "", cat_label, "^" * len(cat_label), "",]
            + props.description.split("\\n")
            + ["",]
            + [f"* :ref:`{p}`" for p in parameter_per_cat]
            + ["", "",]
        )

    with open(output_rst_file, "w") as ofs:
        ofs.write("\n".join(lines))


def generate_parameter_table(input_csv_file, output_csv_file):
    df = pd.read_csv(input_csv_file)
    df = df.loc[df.category != "hidden"]

    parameter_properties = [
        ":Type:",
        ":Unit:",
        ":Default:",
    ]

    name_mapping = {c: c.replace(":", "") for c in parameter_properties}
    name_mapping["label"] = "Parameter"

    # replace the label by a RTD reference
    df["label"] = df["ref"].apply(lambda x: f":ref:`{x}`")

    df[["label"] + parameter_properties].rename(columns=name_mapping).to_csv(
        output_csv_file, index=False
    )


def copy_readme():
    with open("../README.rst", "r", encoding="utf8") as fp:
        data = fp.readlines()
    with open("readme.inc", "w") as fp:
        fp.writelines(data[data.index("Setup\n") :])


def generate_kpi_description(input_csv_file, output_path):
    """Generate a .rst formatted document for each kpi in a given csv file

    Parameters
    ----------
    input_csv_file: str
        path of the file with extensive description of all mvs kpis
    output_path: str
        path of where the .inc files should be saved for each parameter

    Returns
    -------
    None

    """
    df = pd.read_csv(input_csv_file)
    df = df.loc[df.category != "hidden"]
    parameter_properties = [
        ":Definition:",
        ":Type:",
        ":Unit:",
        ":Valid Interval:",
    ]

    # formats following the template:
    # .._<ref_name>:
    #
    # <name>
    # ^^^^^^
    #
    # :Definition:
    # :Type:
    # :Unit:
    # :Valid Interval:
    #
    for row in df.iterrows():
        props = row[1]
        lines = (
            [f".. _{props.ref}:", "", props.label, "^" * len(props.label), "",]
            + [f"{p} {props[p]}" for p in parameter_properties]
            + [""]
            + [
                "This parameter is used within the following categories: "
                + ", ".join([f"{cat}" for cat in props.category.split(";")])
            ]
            + ["", "",]
        )

        with open(os.path.join(output_path, props.ref + ".inc"), "w") as ofs:
            ofs.write("\n".join(lines))


generate_parameter_description(
    "MVS_parameters_list.csv", "model/parameters/MVS_parameters_list.inc"
)
generate_parameter_table(
    "MVS_parameters_list.csv", "model/parameters/MVS_parameters_list.tbl"
)
generate_parameter_categories(
    "MVS_parameters_list.csv",
    "MVS_parameters_categories.csv",
    "model/parameters/MVS_parameters_categories.inc",
)

generate_kpi_description("MVS_kpis_list.csv", "model/outputs")

copy_readme()

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
    "sphinxcontrib.rsvgconverter",
    "numpydoc",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# generate autosummary even if no references
autosummary_generate = True
autosummary_imported_members = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
import sphinx_rtd_theme

numpydoc_show_class_members = False

html_theme = "sphinx_rtd_theme"

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
