r"""
Module E3 indicator calculation
------------------------

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

    :param dict_values:
    :return:
    """
    for column in dict_values["kpi"]["cost_matrix"].columns:
        dict_values["kpi"]["scalars"].update(
            {column: dict_values["kpi"]["cost_matrix"][column].sum()}
        )
    return
