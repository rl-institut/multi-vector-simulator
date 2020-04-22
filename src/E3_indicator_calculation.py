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

def total_renewable_and_non_renewable_energy_origin(dict_values):
    """
    Identifies all renewable generation assets and summs up their total generation to total renewable generation
    :param dict_values: dict with all project input data and results up to E0
    :return: Updated dict_values with total internal/overall renewable and non-renewable energy origin
    """
    renewable_origin = {}
    non_renewable_origin = {}
    for sector in dict_values["project_data"]["sectors"]:
        renewable_origin.update({sector: 0})
        non_renewable_origin.update({sector: 0})

    for asset in dict_values["energyProduction"]:
        if "renewableAsset" in dict_values["energyProduction"][asset]:
            sector = dict_values["energyProduction"][asset]["energyVector"]
            if dict_values["energyProduction"][asset]["renewableAsset"]["value"] is True:
                renewable_origin[sector] += dict_values["energyProduction"][asset]["total_flow"]["value"]
            else:
                non_renewable_origin[sector] += dict_values["energyProduction"][asset]["total_flow"]["value"]


    dict_values["kpi"]["scalars"].update({"Total internal renewable generation": renewable_origin.copy(),
                                          "Total internal non-renewable generation": non_renewable_origin.copy()})

    for DSO in dict_values["energyProviders"]:
        sector = dict_values["energyProviders"][DSO]["energyVector"]
        for DSO_source in dict_values["energyProviders"][DSO]["connected_consumption_sources"]:
            renewable_origin[sector] += dict_values["energyProduction"][DSO_source]["total_flow"]["value"] \
                                            * dict_values["energyProviders"][DSO]["renewable_share"]["value"]
            non_renewable_origin[sector] += dict_values["energyProduction"][DSO_source]["total_flow"]["value"] \
                                            * (1-dict_values["energyProviders"][DSO]["renewable_share"]["value"])

    dict_values["kpi"]["scalars"].update({"Total renewable energy use": renewable_origin,
                                          "Total non-renewable energy use": non_renewable_origin})
    return


def renewable_share_sector_specific(dict_values):
    """
    Determination of renewable share of one sector
    :param dict_values: dict with all project information and results, after applying total_renewable_and_non_renewable_energy_origin
    :param sector: Sector for which renewable share is being calculated
    :return: updated dict_values with renewable share of a specific sector
    """
    dict_renewable_share = {}
    for sector in dict_values["project_data"]["sectors"]:
        total_res = dict_values["kpi"]["scalars"]["Total renewable energy use"][sector]
        total_non_res = dict_values["kpi"]["scalars"]["Total non-renewable energy use"][sector]
        renewable_share = total_res/(total_non_res+total_res)
        dict_renewable_share.update({sector: renewable_share})

    dict_values["kpi"]["scalars"].update({"Sector-specific renewable share": dict_renewable_share})
    return