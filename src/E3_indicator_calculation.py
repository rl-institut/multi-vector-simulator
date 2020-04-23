r"""
Module E3 indicator calculation
-------------------------------

In module E3 the technical KPI are evaluated:
- calculate renewable share
- calculate degree of autonomy
- calculate total generation of each asset
- calculate energy flows between sectors
- calculate degree of autonomy me
- calculate degree of sector coupling
"""


def all_totals(dict_values):
    """
    Calculate sum of all cost parameters
    :param dict_values: dict all input parameters and restults up to E0
    :return: List of all total cost parameters for the project
    """
    for column in dict_values["kpi"]["cost_matrix"].columns:
        if column != "label":
            dict_values["kpi"]["scalars"].update(
                {column: dict_values["kpi"]["cost_matrix"][column].sum()}
            )
    return
