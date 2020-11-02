import pprint
import logging

from multi_vector_simulator.utils.constants_json_strings import (
    PROJECT_DATA,
    ECONOMIC_DATA,
    SIMULATION_SETTINGS,
    CONSTRAINTS,
    ENERGY_CONSUMPTION,
    ENERGY_CONVERSION,
    ENERGY_PRODUCTION,
    ENERGY_STORAGE,
    ENERGY_BUSSES,
    ENERGY_PROVIDERS,
    UNIT,
    LABEL,
    OEMOF_ASSET_TYPE,
    ENERGY_VECTOR,
    INFLOW_DIRECTION,
    CONNECTED_CONSUMPTION_SOURCE,
    CONNECTED_FEEDIN_SINK,
    ENERGY_PRICE,
    FEEDIN_TARIFF,
    PEAK_DEMAND_PRICING,
    PEAK_DEMAND_PRICING_PERIOD,
    RENEWABLE_SHARE_DSO,
    INPUT_BUS_NAME,
    OUTPUT_BUS_NAME,
    OUTFLOW_DIRECTION,
    DEVELOPMENT_COSTS,
    DISPATCH_PRICE,
    DISPATCHABILITY,
    INSTALLED_CAP,
    LIFETIME,
    MAXIMUM_CAP,
    OPTIMIZE_CAP,
    SPECIFIC_COSTS,
    SPECIFIC_COSTS_OM,
    TIMESERIES,
    AGE_INSTALLED,
    RENEWABLE_ASSET_BOOL,
    EFFICIENCY,
    INPUT_POWER,
    OUTPUT_POWER,
    STORAGE_CAPACITY,
    PROJECT_ID,
    PROJECT_NAME,
    SCENARIO_ID,
    SCENARIO_NAME,
    START_DATE,
    EVALUATED_PERIOD,
    TIMESTEP,
)

pp = pprint.PrettyPrinter(indent=4)

MAP_EPA_MVS = {
    "economic_data": ECONOMIC_DATA,
    "energyProviders": ENERGY_PROVIDERS,
    "energy_busses": ENERGY_BUSSES,
    "energy_consumption": ENERGY_CONSUMPTION,
    "energy_conversion": ENERGY_CONVERSION,
    "energy_production": ENERGY_PRODUCTION,
    "energy_storage": ENERGY_STORAGE,
    "project_data": PROJECT_DATA,
    "simulation_settings": SIMULATION_SETTINGS,
    "energy_vector": ENERGY_VECTOR,
    "installed_capacity": INSTALLED_CAP,
    "optimize_capacity": OPTIMIZE_CAP,
    "maximum_capacity": MAXIMUM_CAP,
    "input_timeseries": TIMESERIES,
    "constraints": CONSTRAINTS,
    "renewable_asset": RENEWABLE_ASSET_BOOL,
}

MAP_MVS_EPA = {value: key for (key, value) in MAP_EPA_MVS.items()}

# Fields expected for parameters of json returned to EPA
EPA_PARAM_KEYS = {
    PROJECT_DATA: [PROJECT_ID, PROJECT_NAME, SCENARIO_ID, SCENARIO_NAME,],
    SIMULATION_SETTINGS: [START_DATE, EVALUATED_PERIOD, TIMESTEP],
}

# Fields expected for assets' parameters of json returned to EPA
EPA_ASSET_KEYS = {
    ENERGY_PROVIDERS: [
        "asset_type",
        LABEL,
        OEMOF_ASSET_TYPE,
        "energy_vector",
        INFLOW_DIRECTION,
        OUTFLOW_DIRECTION,
        CONNECTED_CONSUMPTION_SOURCE,
        CONNECTED_FEEDIN_SINK,
        DEVELOPMENT_COSTS,
        DISPATCH_PRICE,
        ENERGY_PRICE,
        FEEDIN_TARIFF,
        "installed_capacity",
        LIFETIME,
        "optimize_capacity",
        PEAK_DEMAND_PRICING,
        PEAK_DEMAND_PRICING_PERIOD,
        RENEWABLE_SHARE_DSO,
        SPECIFIC_COSTS,
        SPECIFIC_COSTS_OM,
        UNIT,
    ],
    ENERGY_CONSUMPTION: [
        "asset_type",
        LABEL,
        INPUT_BUS_NAME,
        INFLOW_DIRECTION,
        OEMOF_ASSET_TYPE,
        DEVELOPMENT_COSTS,
        DISPATCH_PRICE,
        "installed_capacity",
        LIFETIME,
        "optimize_capacity",
        SPECIFIC_COSTS,
        SPECIFIC_COSTS_OM,
        "input_timeseries",
        "energy_vector",
    ],
    ENERGY_CONVERSION: [
        "asset_type",
        LABEL,
        "energy_vector",
        OEMOF_ASSET_TYPE,
        INFLOW_DIRECTION,
        INPUT_BUS_NAME,
        OUTFLOW_DIRECTION,
        OUTPUT_BUS_NAME,
        AGE_INSTALLED,
        DEVELOPMENT_COSTS,
        DISPATCH_PRICE,
        EFFICIENCY,
        "installed_capacity",
        LIFETIME,
        "maximum_capacity",
        "optimize_capacity",
        SPECIFIC_COSTS,
        SPECIFIC_COSTS_OM,
    ],
    ENERGY_PRODUCTION: [
        "asset_type",
        LABEL,
        OEMOF_ASSET_TYPE,
        OUTPUT_BUS_NAME,
        OUTFLOW_DIRECTION,
        DEVELOPMENT_COSTS,
        DISPATCH_PRICE,
        DISPATCHABILITY,
        "installed_capacity",
        LIFETIME,
        "maximum_capacity",
        "optimize_capacity",
        SPECIFIC_COSTS,
        SPECIFIC_COSTS_OM,
        "input_timeseries",
        AGE_INSTALLED,
        "renewable_asset",
        "energy_vector",
    ],
    ENERGY_STORAGE: [
        "asset_type",
        LABEL,
        "energy_vector",
        INFLOW_DIRECTION,
        INPUT_BUS_NAME,
        OUTFLOW_DIRECTION,
        OUTPUT_BUS_NAME,
        OEMOF_ASSET_TYPE,
        INPUT_POWER,
        OUTPUT_POWER,
        STORAGE_CAPACITY,
        "optimize_capacity",
        "input_timeseries",
    ],
    ENERGY_BUSSES: [LABEL, "assets", "energy_vector"],
}


def convert_epa_params_to_mvs(epa_dict):
    """Convert the EPA output parameters to MVS input parameters

    Parameters
    ----------
    epa_dict: dict
        parameters from EPA user interface

    Returns
    -------
    dict_values: dict
        mvs parameters

    """

    dict_values = {}

    for param_group in [PROJECT_DATA, ECONOMIC_DATA, SIMULATION_SETTINGS, CONSTRAINTS]:

        if MAP_MVS_EPA[param_group] in epa_dict:

            dict_values[param_group] = epa_dict[MAP_MVS_EPA[param_group]]

            # convert fields names from EPA convention to MVS convention, if applicable
            keys_list = list(dict_values[param_group].keys())
            for k in keys_list:
                if k in MAP_EPA_MVS:
                    dict_values[param_group][MAP_EPA_MVS[k]] = dict_values[
                        param_group
                    ].pop(k)
        else:
            logging.warning(
                f"The parameters {MAP_MVS_EPA[param_group]} are not present in the parameters to be parsed into mvs json format"
            )

    for asset_group in [
        ENERGY_CONSUMPTION,
        ENERGY_CONVERSION,
        ENERGY_PRODUCTION,
        ENERGY_STORAGE,
        ENERGY_BUSSES,
        ENERGY_PROVIDERS,
    ]:
        if MAP_MVS_EPA[asset_group] in epa_dict:
            dict_asset = {}
            for asset in epa_dict[MAP_MVS_EPA[asset_group]]:

                asset_label = asset[LABEL]
                dict_asset[asset_label] = asset

                asset_keys = list(dict_asset[asset_label].keys())
                for k in asset_keys:
                    if k in MAP_EPA_MVS:
                        dict_asset[asset_label][MAP_EPA_MVS[k]] = dict_asset[
                            asset_label
                        ].pop(k)

            # move the unit outside the timeseries dict
            if TIMESERIES in dict_asset:
                unit = dict_asset[TIMESERIES].pop(UNIT)
                dict_asset[UNIT] = unit

            dict_values[asset_group] = dict_asset
        else:
            logging.warning(
                f"The parameters {MAP_MVS_EPA[asset_group]} are not present in the parameters to be parsed into mvs json format"
            )

    return dict_values

