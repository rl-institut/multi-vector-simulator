r"""
Module E3 indicator calculation
-------------------------------

In module E3 the technical KPI are evaluated:
- calculate renewable share
- calculate degree of autonomy
- calculate total generation of each asset
- calculate energy flows between sectors
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

def total_demand_each_sector(dict_values):
    """

    :param dict_values: dict with all project input data and results up to E0
    :return:
    """
    return

def total_renewable_energy(dict_values):
    """
    Identifies all renewable generation assets and summs up their total generation to total renewable generation
    :param dict_values: dict with all project input data and results up to E0
    :return: Updated dict_values with list of all renewable sources and their total generation
    """
    renewable_generation = {}
    for sector in dict_values["project_data"]["sectors"]:
        renewable_generation.update({sector: 0})

    for asset in dict_values["energyProduction"]:
        if "renewableAsset" in dict_values["energyProduction"][asset] \
                and dict_values["energyProduction"][asset]["renewableAsset"]["value"] is True:
            sector = dict_values["energyProduction"][asset]["energyVector"]
            renewable_generation[sector] += dict_values["energyProduction"][asset]["total_flow"]["value"]

    dict_values["kpi"]["scalars"].update({"Total internal renewable generation": renewable_generation.copy()})

    for DSO in dict_values["energyProviders"]:
        sector = dict_values["energyProviders"][DSO]["energyVector"]
        for DSO_source in dict_values["energyProviders"][DSO]["connected_consumption_sources"]:
            renewable_generation[sector] += dict_values["energyProduction"][DSO_source]["total_flow"]["value"] \
                                            * dict_values["energyProviders"][DSO]["renewable_share"]["value"]

    dict_values["kpi"]["scalars"].update({"Total renewable energy use": renewable_generation})
    return

def total_non_renewable_generation():
    return