r"""
Module data_parser
==================

This module defines all functions to convert formats between EPA and MVS
- Define similar parameters mapping between the EPA and MVS in MAP_EPA_MVS and MAP_MVS_EPA
- Define which fields are expected in asset list of EPA for various assets' groups in EPA_ASSET_KEYS
- Convert MVS to EPA
- Convert EPA to MVS
"""

import pprint
import logging
import json
from copy import deepcopy

from multi_vector_simulator.utils import compare_input_parameters_with_reference


from multi_vector_simulator.utils.constants import (
    MISSING_PARAMETERS_KEY,
    DATA_TYPE_JSON_KEY,
    TYPE_SERIES,
    TYPE_NONE,
    TYPE_BOOL,
    KNOWN_EXTRA_PARAMETERS,
    DEFAULT_VALUE,
)

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
    SPECIFIC_REPLACEMENT_COSTS_INSTALLED,
    SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED,
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
    OUTPUT_LP_FILE,
    MINIMAL_RENEWABLE_FACTOR,
    MINIMAL_DEGREE_OF_AUTONOMY,
    FIX_COST,
    KPI,
    TIMESTEP,
    KPI_SCALARS_DICT,
    VALUE,
    EMISSION_FACTOR,
    MAXIMUM_EMISSIONS,
    FLOW,
    KPI_UNCOUPLED_DICT,
    KPI_COST_MATRIX,
    KPI_SCALAR_MATRIX,
    SOC_INITIAL,
    SCENARIO_DESCRIPTION,
    TIMESERIES_SOC,
    TYPE_ASSET,
    DSM,
    THERM_LOSSES_REL,
    THERM_LOSSES_ABS,
)

from multi_vector_simulator.utils.exceptions import MissingParameterError

pp = pprint.PrettyPrinter(indent=4)

MAP_EPA_MVS = {
    "economic_data": ECONOMIC_DATA,
    "energy_providers": ENERGY_PROVIDERS,
    "energy_busses": ENERGY_BUSSES,
    "energy_consumption": ENERGY_CONSUMPTION,
    "energy_conversion": ENERGY_CONVERSION,
    "energy_production": ENERGY_PRODUCTION,
    "energy_storage": ENERGY_STORAGE,
    "project_data": PROJECT_DATA,
    "input_bus_name": INFLOW_DIRECTION,  # TODO remove this when it is updated on EPA side
    "output_bus_name": OUTFLOW_DIRECTION,  # TODO remove this when it is updated on EPA side
    "simulation_settings": SIMULATION_SETTINGS,
    "energy_vector": ENERGY_VECTOR,
    "installed_capacity": INSTALLED_CAP,
    "capacity": STORAGE_CAPACITY,
    "input_power": INPUT_POWER,
    "output_power": OUTPUT_POWER,
    "optimize_capacity": OPTIMIZE_CAP,
    "maximum_capacity": MAXIMUM_CAP,
    "input_timeseries": TIMESERIES,
    "constraints": CONSTRAINTS,
    "renewable_asset": RENEWABLE_ASSET_BOOL,
    KPI: KPI,
    FIX_COST: FIX_COST,
    "time_step": TIMESTEP,
    "data": VALUE,
    "replacement_costs_during_project_lifetime": "Replacement_costs_during_project_lifetime",
    "specific_replacement_costs_of_installed_capacity": SPECIFIC_REPLACEMENT_COSTS_INSTALLED,
    "specific_replacement_costs_of_optimized_capacity": SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED,
    "asset_type": TYPE_ASSET,
}

MAP_MVS_EPA = {value: key for (key, value) in MAP_EPA_MVS.items()}

# Fields expected for parameters of json returned to EPA, all assets will be returned
EPA_PARAM_KEYS = {
    PROJECT_DATA: [PROJECT_ID, PROJECT_NAME, SCENARIO_ID, SCENARIO_NAME],
    SIMULATION_SETTINGS: [START_DATE, EVALUATED_PERIOD, TIMESTEP],
    KPI: [KPI_SCALARS_DICT, KPI_UNCOUPLED_DICT, KPI_COST_MATRIX, KPI_SCALAR_MATRIX],
}

# Fields expected for assets' parameters of json returned to EPA
EPA_ASSET_KEYS = {
    ENERGY_PROVIDERS: [
        "unique_id",
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
        FLOW,
    ],
    ENERGY_CONSUMPTION: [
        "unique_id",
        "asset_type",
        LABEL,
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
        FLOW,
    ],
    ENERGY_CONVERSION: [
        "unique_id",
        "asset_type",
        LABEL,
        "energy_vector",
        OEMOF_ASSET_TYPE,
        INFLOW_DIRECTION,
        OUTFLOW_DIRECTION,
        OUTFLOW_DIRECTION,
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
        FLOW,
    ],
    ENERGY_PRODUCTION: [
        "unique_id",
        "asset_type",
        LABEL,
        OEMOF_ASSET_TYPE,
        OUTFLOW_DIRECTION,
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
        FLOW,
    ],
    ENERGY_STORAGE: [
        "unique_id",
        "asset_type",
        LABEL,
        "energy_vector",
        INFLOW_DIRECTION,
        OUTFLOW_DIRECTION,
        OUTFLOW_DIRECTION,
        OEMOF_ASSET_TYPE,
        INPUT_POWER,
        OUTPUT_POWER,
        STORAGE_CAPACITY,
        "optimize_capacity",
        "input_timeseries",
        TIMESERIES_SOC,
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

    epa_dict = deepcopy(epa_dict)
    dict_values = {}

    for param_group in [
        PROJECT_DATA,
        ECONOMIC_DATA,
        SIMULATION_SETTINGS,
        CONSTRAINTS,
        FIX_COST,
    ]:

        if MAP_MVS_EPA[param_group] in epa_dict:

            dict_values[param_group] = epa_dict[MAP_MVS_EPA[param_group]]

            # convert fields names from EPA convention to MVS convention, if applicable
            keys_list = list(dict_values[param_group].keys())
            for k in keys_list:
                if k in MAP_EPA_MVS:
                    dict_values[param_group][MAP_EPA_MVS[k]] = dict_values[
                        param_group
                    ].pop(k)

            if param_group == SIMULATION_SETTINGS:
                timestep = dict_values[param_group].get(TIMESTEP)
                if timestep is not None:
                    dict_values[param_group][TIMESTEP] = {
                        UNIT: "min",
                        VALUE: timestep,
                    }
            if param_group == PROJECT_DATA:
                if SCENARIO_DESCRIPTION not in dict_values[param_group]:
                    dict_values[param_group][
                        SCENARIO_DESCRIPTION
                    ] = "[No scenario description available]"

            # Never save the oemof lp file when running on the server
            if param_group == SIMULATION_SETTINGS:
                dict_values[param_group][OUTPUT_LP_FILE] = {
                    UNIT: TYPE_BOOL,
                    VALUE: False,
                }

        else:
            logging.warning(
                f"The parameters group '{MAP_MVS_EPA[param_group]}' is not present in the EPA parameters to be parsed into MVS json format"
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

                # change EPA style keys of an asset to MVS style ones
                for k in asset_keys:

                    if k in MAP_EPA_MVS:
                        dict_asset[asset_label][MAP_EPA_MVS[k]] = dict_asset[
                            asset_label
                        ].pop(k)

                    # for energy_storage there is an extra indentation level
                    if asset_group == ENERGY_STORAGE:
                        if k in (
                            MAP_MVS_EPA[STORAGE_CAPACITY],
                            MAP_MVS_EPA[INPUT_POWER],
                            MAP_MVS_EPA[OUTPUT_POWER],
                        ):
                            subasset = dict_asset[asset_label][MAP_EPA_MVS[k]]
                            subasset_keys = list(subasset.keys())

                            for sk in subasset_keys:
                                if sk in MAP_EPA_MVS:
                                    subasset[MAP_EPA_MVS[sk]] = subasset.pop(sk)

                            # remove non-implemented parameter if provided faultily
                            if OPTIMIZE_CAP in subasset:
                                subasset.pop(OPTIMIZE_CAP)

                            # add unit if not provided
                            # TODO deal with other vectors than electricity
                            if UNIT not in subasset:
                                if k == MAP_MVS_EPA[STORAGE_CAPACITY]:
                                    subasset[UNIT] = "kWh"
                                else:
                                    subasset[UNIT] = "kW"
                            # set the initial value of the state of charge to None
                            if k == MAP_MVS_EPA[STORAGE_CAPACITY]:
                                subasset[SOC_INITIAL] = {VALUE: None, UNIT: TYPE_NONE}

                # move the unit outside the timeseries dict
                if TIMESERIES in dict_asset[asset_label]:
                    unit = dict_asset[asset_label][TIMESERIES].pop(UNIT)
                    data = dict_asset[asset_label][TIMESERIES].pop(VALUE)
                    dict_asset[asset_label][
                        UNIT
                    ] = unit  # todo this is a trick, as "UNIT" was not given
                    dict_asset[asset_label][TIMESERIES][VALUE] = data
                    dict_asset[asset_label][TIMESERIES][
                        DATA_TYPE_JSON_KEY
                    ] = TYPE_SERIES

                # typically DSO
                if asset_group == ENERGY_PROVIDERS:
                    # unit is not provided, so default is kWh
                    if UNIT not in dict_asset[asset_label]:
                        dict_asset[asset_label][UNIT] = "kWh"
                    # if inflow direction is not provided, the same as outflow direction is used
                    if INFLOW_DIRECTION not in dict_asset[asset_label]:
                        dict_asset[asset_label][INFLOW_DIRECTION] = dict_asset[
                            asset_label
                        ][OUTFLOW_DIRECTION]

                # TODO remove this when change has been made on EPA side
                if asset_group == ENERGY_STORAGE:

                    if (
                        THERM_LOSSES_REL
                        not in dict_asset[asset_label][STORAGE_CAPACITY]
                    ):
                        dict_asset[asset_label][STORAGE_CAPACITY][THERM_LOSSES_REL] = {
                            UNIT: "factor",
                            VALUE: 0,
                        }
                    if (
                        THERM_LOSSES_ABS
                        not in dict_asset[asset_label][STORAGE_CAPACITY]
                    ):
                        dict_asset[asset_label][STORAGE_CAPACITY][THERM_LOSSES_ABS] = {
                            UNIT: "kWh",
                            VALUE: 0,
                        }

                    if OPTIMIZE_CAP not in dict_asset[asset_label]:
                        dict_asset[asset_label][OPTIMIZE_CAP] = {
                            UNIT: TYPE_BOOL,
                            VALUE: False,
                        }
                    else:
                        logging.warning(
                            "The optimized cap has been updated on EPA side so you can look for "
                            "this warning in data_parser.py and remove the warning and the 7 "
                            "lines of code above it as well"
                        )

                if asset_group == ENERGY_CONSUMPTION:
                    if DSM not in dict_asset[asset_label]:
                        dict_asset[asset_label][DSM] = False

                if EMISSION_FACTOR not in dict_asset[asset_label]:
                    dict_asset[asset_label][EMISSION_FACTOR] = {
                        VALUE: KNOWN_EXTRA_PARAMETERS[EMISSION_FACTOR][DEFAULT_VALUE]
                    }

            dict_values[asset_group] = dict_asset
        else:
            logging.info(
                f"The assets parameters '{MAP_MVS_EPA[asset_group]}' is not present in the EPA parameters to be parsed into MVS json format"
            )

    comparison = compare_input_parameters_with_reference(dict_values)

    if MISSING_PARAMETERS_KEY in comparison:
        error_msg = []

        missing_params = comparison[MISSING_PARAMETERS_KEY]
        # this should not be missing on EPA side, but in case it is take default value 0
        if CONSTRAINTS in missing_params:
            dict_values[CONSTRAINTS] = {
                MINIMAL_RENEWABLE_FACTOR: {UNIT: "factor", VALUE: 0},
                MAXIMUM_EMISSIONS: {UNIT: "factor", VALUE: 0},
                MINIMAL_DEGREE_OF_AUTONOMY: {UNIT: "factor", VALUE: 0},
            }
            missing_params.pop(CONSTRAINTS)

        if SIMULATION_SETTINGS in missing_params:
            if (
                OUTPUT_LP_FILE in missing_params[SIMULATION_SETTINGS]
                and len(missing_params[SIMULATION_SETTINGS]) == 1
            ):
                dict_values[SIMULATION_SETTINGS][OUTPUT_LP_FILE] = {
                    UNIT: TYPE_BOOL,
                    VALUE: False,
                }
                missing_params.pop(SIMULATION_SETTINGS)
        if FIX_COST in missing_params:
            dict_values[FIX_COST] = {}
            missing_params.pop(FIX_COST)

        error_msg.append(" ")
        error_msg.append(" ")
        error_msg.append(
            "The following parameter groups and sub parameters are missing from input parameters:"
        )

        if len(missing_params.keys()) > 0:

            for asset_group in missing_params.keys():
                error_msg.append(asset_group)
                if missing_params[asset_group] is not None:
                    for k in missing_params[asset_group]:
                        error_msg.append(f"\t`{k}` parameter")

            raise (MissingParameterError("\n".join(error_msg)))

    return dict_values


def convert_mvs_params_to_epa(mvs_dict, verbatim=False):
    """Convert the MVS output parameters to EPA format

    Parameters
    ----------
    mvs_dict: dict
        output parameters from MVS

    Returns
    -------
    epa_dict: dict
        epa parameters

    """

    epa_dict = {}

    # manage which parameters are kept and which one are removed in epa_dict
    for param_group in EPA_PARAM_KEYS:

        # translate field name from mvs to epa
        param_group_epa = MAP_MVS_EPA[param_group]

        # assign the whole MVS value to the EPA field
        epa_dict[param_group_epa] = mvs_dict[param_group]

        keys_list = list(epa_dict[param_group_epa].keys())
        for k in keys_list:
            # ditch all subfields which are not present in the EPA_PARAM_KEYS value corresponding
            # to the parameter group (except for CONSTRAINTS)
            if k not in EPA_PARAM_KEYS[param_group] or param_group in (CONSTRAINTS,):
                epa_dict[param_group_epa].pop(k)
            else:
                # convert fields names from MVS convention to EPA convention, if applicable
                if k in MAP_MVS_EPA:
                    epa_dict[param_group_epa][MAP_MVS_EPA[k]] = epa_dict[
                        param_group_epa
                    ].pop(k)

                if k == KPI_UNCOUPLED_DICT:
                    epa_dict[param_group_epa][k] = json.loads(
                        epa_dict[param_group_epa][k].to_json(orient="index")
                    )

                if k in (KPI_SCALAR_MATRIX, KPI_COST_MATRIX):
                    epa_dict[param_group_epa][k] = json.loads(
                        epa_dict[param_group_epa][k]
                        .set_index("label")
                        .to_json(orient="index")
                    )

    # manage which assets parameters are kept and which one are removed in epa_dict
    for asset_group in EPA_ASSET_KEYS:
        list_asset = []
        for asset_label in mvs_dict[asset_group]:
            # mvs[asset_group] is a dict we want to change into a list

            # each asset is also a dict
            asset = mvs_dict[asset_group][asset_label]

            # if the asset possesses a unit field
            if UNIT in asset:
                unit = asset.pop(UNIT)
            else:
                unit = None

            unit_soc = None

            # keep the information about the dict key, but move it into the dict value
            asset[LABEL] = asset_label

            asset_keys = list(asset.keys())
            for k in asset_keys:
                if k in MAP_MVS_EPA:
                    # convert some keys MVS to EPA style according to the mapping
                    asset[MAP_MVS_EPA[k]] = asset.pop(k)
                # TODO change energy busses from dict to list in MVS
                if asset_group == ENERGY_BUSSES and k == "Asset_list":
                    asset["assets"] = list(asset.pop(k).keys())
                if asset_group == ENERGY_STORAGE:
                    if k in (INPUT_POWER, OUTPUT_POWER, STORAGE_CAPACITY):
                        asset[k] = mvs_dict[asset_group][asset_label][MAP_MVS_EPA[k]]
                        subasset_keys = list(asset[k].keys())

                        # if the asset possesses a unit field
                        if UNIT in asset[k]:
                            subunit = asset[k].pop(UNIT)
                            if k == STORAGE_CAPACITY:
                                unit_soc = subunit
                        else:
                            subunit = None

                        for sk in subasset_keys:
                            if sk in MAP_MVS_EPA:
                                # convert some keys MVS to EPA style according to the mapping
                                asset[k][MAP_MVS_EPA[sk]] = asset[k].pop(sk)
                        # convert pandas.Series to a timeseries dict with key DATA value list,
                        # move the unit inside the timeseries dict under key UNIT
                        if FLOW in asset[k]:
                            timeseries = asset[k][FLOW].to_list()
                            asset[k][FLOW] = {UNIT: subunit, VALUE: timeseries}

            if MAP_MVS_EPA[TIMESERIES] in asset:
                asset.pop(MAP_MVS_EPA[TIMESERIES])

            # convert pandas.Series to a timeseries dict with key DATA value list,
            # move the unit inside the timeseries dict under key UNIT
            if FLOW in asset:
                timeseries = asset[FLOW].to_list()
                asset[FLOW] = {UNIT: unit, VALUE: timeseries}

            if TIMESERIES_SOC in asset:
                timeseries = asset[TIMESERIES_SOC].to_list()
                asset[TIMESERIES_SOC] = {UNIT: unit_soc, VALUE: timeseries}

            if "_excess" not in asset_label and "_sink" not in asset_label:
                list_asset.append(asset)

        epa_dict[MAP_MVS_EPA[asset_group]] = list_asset

    # verify that there are extra keys, besides the one expected by EPA data structure
    extra_keys = {}
    # verify that there are keys expected by the EPA which are not filled
    missing_keys = {}
    for asset_group in EPA_ASSET_KEYS:
        extra_keys[asset_group] = []
        missing_keys[asset_group] = []
        for asset in epa_dict[MAP_MVS_EPA[asset_group]]:
            asset_keys = list(asset.keys())
            # loop over the actual fields of the asset
            for k in asset_keys:
                # remove any field which is not listed under the asset_group in EPA_ASSET_KEYS
                if k not in EPA_ASSET_KEYS[asset_group]:
                    asset.pop(k)
                    # keep trace of this extra key
                    if k not in extra_keys[asset_group]:
                        extra_keys[asset_group].append((asset[LABEL], k))
            # loop over the expected fields of the asset_group in EPA_ASSET_KEYS
            for k in EPA_ASSET_KEYS[asset_group]:
                # if a field is missing in the actual asset, keep trace of it
                if k not in asset:
                    missing_keys[asset_group].append((asset[LABEL], k))

    if verbatim is True:
        print("#" * 10 + " Missing values " + "#" * 10)
        pp.pprint(missing_keys)

        print("#" * 10 + " Extra values " + "#" * 12)
        pp.pprint(extra_keys)

    return epa_dict
