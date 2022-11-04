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
    EXTRA_PARAMETERS_KEY,
    DATA_TYPE_JSON_KEY,
    TYPE_SERIES,
    TYPE_NONE,
    TYPE_BOOL,
    KNOWN_EXTRA_PARAMETERS,
    DEFAULT_CONSTRAINT_VALUES,
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
    MAXIMUM_ADD_CAP,
    OPTIMIZE_CAP,
    OPTIMIZED_ADD_CAP,
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
    NET_ZERO_ENERGY,
    COST_REPLACEMENT,
    ASSET_DICT,
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
    "simulation_settings": SIMULATION_SETTINGS,
    "energy_vector": ENERGY_VECTOR,
    "installed_capacity": INSTALLED_CAP,
    "capacity": STORAGE_CAPACITY,
    # "input_bus_name": INFLOW_DIRECTION,
    # "output_bus_name": OUTFLOW_DIRECTION,
    "input_power": INPUT_POWER,
    "output_power": OUTPUT_POWER,
    "optimize_capacity": OPTIMIZE_CAP,
    "optimized_add_cap": OPTIMIZED_ADD_CAP,
    "maximum_capacity": MAXIMUM_CAP,
    "maximum_add_cap": MAXIMUM_ADD_CAP,
    "input_timeseries": TIMESERIES,
    "constraints": CONSTRAINTS,
    "renewable_asset": RENEWABLE_ASSET_BOOL,
    KPI: KPI,
    FIX_COST: FIX_COST,
    "time_step": TIMESTEP,
    "data": VALUE,
    "replacement_costs_during_project_lifetime": COST_REPLACEMENT,
    "specific_replacement_costs_of_installed_capacity": SPECIFIC_REPLACEMENT_COSTS_INSTALLED,
    "specific_replacement_costs_of_optimized_capacity": SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED,
    "asset_type": TYPE_ASSET,
    "capex_fix": DEVELOPMENT_COSTS,
    "capex_var": SPECIFIC_COSTS,
    "opex_fix": SPECIFIC_COSTS_OM,
    "opex_var": DISPATCH_PRICE,
}

MAP_MVS_EPA = {value: key for (key, value) in MAP_EPA_MVS.items()}

# Fields expected for parameters of json returned to EPA, all assets will be returned
EPA_PARAM_KEYS = {
    PROJECT_DATA: [PROJECT_ID, PROJECT_NAME, SCENARIO_ID, SCENARIO_NAME],
    SIMULATION_SETTINGS: [START_DATE, EVALUATED_PERIOD, TIMESTEP, OUTPUT_LP_FILE],
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
        SPECIFIC_COSTS,
        SPECIFIC_COSTS_OM,
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
        AGE_INSTALLED,
        DEVELOPMENT_COSTS,
        DISPATCH_PRICE,
        EFFICIENCY,
        "installed_capacity",
        LIFETIME,
        "optimize_capacity",
        "optimized_add_cap",
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
        DEVELOPMENT_COSTS,
        DISPATCH_PRICE,
        DISPATCHABILITY,
        "installed_capacity",
        LIFETIME,
        "maximum_capacity",
        "maximum_add_cap",
        "optimize_capacity",
        "optimized_add_cap",
        SPECIFIC_COSTS,
        SPECIFIC_COSTS_OM,
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
        OEMOF_ASSET_TYPE,
        INPUT_POWER,
        OUTPUT_POWER,
        STORAGE_CAPACITY,
        "optimize_capacity",
        "optimized_add_cap",
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
        MVS json file, generated from EPA inputs, to be provided as MVS input

    Notes
    -----

    - For `simulation_settings`:
        - parameter `TIMESTEP` is parsed as unit-value pair
        - `OUTPUT_LP_FILE` is set to `False` by default
    - For `project_data`: parameter `SCENARIO_DESCRIPTION` is defined as placeholder string.
    - `fix_cost` is not required, default value will be set if it is not provided.
    - For missing asset group `CONSTRAINTS` following parameters are added:
        - MINIMAL_RENEWABLE_FACTOR: 0
        - MAXIMUM_EMISSIONS: None
        - MINIMAL_DEGREE_OF_AUTONOMY: 0
        - NET_ZERO_ENERGY: False
    - `ENERGY_STORAGE` assets:
        - Optimize cap written to main asset and removed from subassets
        - Units defined automatically (assumed: electricity system)
        - `SOC_INITIAL`: None
        - `THERM_LOSSES_REL`: 0
        - `THERM_LOSSES_ABS`: 0
    - If `TIMESERIES` parameter in asset dictionary: Redefine unit, value and label.
    - `ENERGY_PROVIDERS`:
        - Auto-define unit as kWh(el)
        - `INFLOW_DIRECTION=OUTFLOW_DIRECTION`
        - Default value for `EMISSION_FACTOR` added
    - `ENERGY_CONSUMPTION`:
        - `DSM` is `False`
        - `DISPATCHABILITY` is FALSE
    - `ENERGY_PRODUCTION`:
        - Default value for `EMISSION_FACTOR` added
        - `DISPATCHABILITY` is always `False`, as no dispatchable fuel assets possible right now. Must be tackeld by EPA.
     """
    epa_dict = deepcopy(epa_dict)
    dict_values = {}

    # Loop though one-dimensional energy system data (parameters directly in group)
    # Warnings for missing param_groups, will result in fatal error (except for fix_cost) as they can not be replaced with default values
    for param_group in [
        PROJECT_DATA,
        ECONOMIC_DATA,
        SIMULATION_SETTINGS,
        CONSTRAINTS,
        FIX_COST,
    ]:

        if MAP_MVS_EPA[param_group] in epa_dict:
            # Write entry of EPA to MVS json file
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
                # by default the lp file will not be outputted
                output_lp_file = dict_values[param_group].get(OUTPUT_LP_FILE)
                if output_lp_file is None:
                    dict_values[param_group][OUTPUT_LP_FILE] = {
                        UNIT: TYPE_BOOL,
                        VALUE: False,
                    }
                else:
                    dict_values[param_group][OUTPUT_LP_FILE] = {
                        UNIT: TYPE_BOOL,
                        VALUE: True if output_lp_file == "true" else False,
                    }

            if param_group == PROJECT_DATA:
                if SCENARIO_DESCRIPTION not in dict_values[param_group]:
                    dict_values[param_group][
                        SCENARIO_DESCRIPTION
                    ] = "[No scenario description available]"

        else:
            logging.warning(
                f"The parameters group '{MAP_MVS_EPA[param_group]}' is not present in the EPA parameters to be parsed into MVS json format"
            )

    # Loop through energy system asset groups and their assets
    # Logging warning message for missing asset groups, will not raise error if an asset group does not contain any assets
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
                                # move the optimize cap property from STORAGE_CAPACITY to the asset level
                                if OPTIMIZE_CAP in subasset:
                                    dict_asset[asset_label][
                                        OPTIMIZE_CAP
                                    ] = subasset.pop(OPTIMIZE_CAP)

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

                if asset_group == ENERGY_CONVERSION:
                    if DISPATCH_PRICE not in dict_asset[asset_label]:
                        dict_asset[asset_label].update(
                            {DISPATCH_PRICE: {VALUE: 0, UNIT: "factor"}}
                        )
                    if DEVELOPMENT_COSTS not in dict_asset[asset_label]:
                        dict_asset[asset_label].update(
                            {DEVELOPMENT_COSTS: {VALUE: 0, UNIT: "factor"}}
                        )

                # TODO remove this when change has been made on EPA side
                if asset_group == ENERGY_PRODUCTION:
                    dict_asset[asset_label].update({DISPATCHABILITY: False})

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
                    # format the energy price and feedin tariffs as timeseries
                    for asset_param in (ENERGY_PRICE, FEEDIN_TARIFF):
                        param_value = dict_asset[asset_label][asset_param][VALUE]
                        if isinstance(param_value, list):
                            dict_asset[asset_label][asset_param][VALUE] = {
                                VALUE: param_value,
                                DATA_TYPE_JSON_KEY: TYPE_SERIES,
                            }

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
                    # DSM not used parameters, but to be sure it will be defined as False
                    if DSM not in dict_asset[asset_label]:
                        dict_asset[asset_label][DSM] = False
                    # Dispatchability of energy consumption assets always False
                    dict_asset[asset_label].update(
                        {DISPATCHABILITY: {UNIT: TYPE_BOOL, VALUE: False},}
                    )

                if asset_group == ENERGY_PRODUCTION or ENERGY_PROVIDERS:
                    # Emission factor only applicable for energy production assets and energy providers
                    if EMISSION_FACTOR not in dict_asset[asset_label]:
                        dict_asset[asset_label][EMISSION_FACTOR] = {
                            VALUE: KNOWN_EXTRA_PARAMETERS[EMISSION_FACTOR][
                                DEFAULT_VALUE
                            ]
                        }

            dict_values[asset_group] = dict_asset
        else:
            logging.info(
                f"The assets parameters '{MAP_MVS_EPA[asset_group]}' is not present in the EPA parameters to be parsed into MVS json format"
            )
            epa_dict.update({asset_group: {}})
            dict_values.update({asset_group: {}})

    # Check if all necessary input parameters are provided
    comparison = compare_input_parameters_with_reference(dict_values, set_default=True)

    # ToDo compare_input_parameters_with_reference() does not identify excess/missing parameters in the subassets of energyStorages.
    if EXTRA_PARAMETERS_KEY in comparison:
        warning_extra_parameters = "Following parameters are provided to the MVS that may be excess information: \n"
        for group in comparison[EXTRA_PARAMETERS_KEY]:
            warning_extra_parameters += f"- {group} ("
            for parameter in comparison[EXTRA_PARAMETERS_KEY][group]:
                if parameter not in [LABEL, "unique_id"]:
                    warning_extra_parameters += f"{parameter}, "
            warning_extra_parameters = warning_extra_parameters[:-2] + ") \n"
        logging.warning(warning_extra_parameters)

    if MISSING_PARAMETERS_KEY in comparison:
        error_msg = []

        missing_params = comparison[MISSING_PARAMETERS_KEY]
        if CONSTRAINTS in missing_params:

            if CONSTRAINTS not in dict_values:
                dict_values[CONSTRAINTS] = {}

            for missing_constraint in missing_params[CONSTRAINTS]:
                dict_values[CONSTRAINTS][
                    missing_constraint
                ] = DEFAULT_CONSTRAINT_VALUES[missing_constraint]

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
                # Only raise an error about missing parameter if an asset group contains assets
                if len(dict_values[asset_group].keys()) > 0:
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

                    cols = epa_dict[param_group_epa][k].columns
                    epa_dict[param_group_epa][k].columns = [
                        MAP_MVS_EPA.get(k, k) for k in cols
                    ]
                    epa_dict[param_group_epa][k] = json.loads(
                        epa_dict[param_group_epa][k]
                        .set_index("label")
                        .to_json(orient="index")
                    )

                # if the parameter is of type
                if k == OUTPUT_LP_FILE:
                    if epa_dict[param_group_epa][k][UNIT] == TYPE_BOOL:
                        epa_dict[param_group_epa].pop(k)

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
                if asset_group == ENERGY_BUSSES and k == ASSET_DICT:
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
                if isinstance(asset.get(OUTFLOW_DIRECTION, None), list):
                    timeseries = {}
                    for bus in asset[OUTFLOW_DIRECTION]:
                        timeseries[bus] = asset[FLOW][bus].to_list()
                    asset[FLOW] = {UNIT: unit, VALUE: timeseries}
                else:
                    timeseries = asset[FLOW].to_list()
                    asset[FLOW] = {UNIT: unit, VALUE: timeseries}

            if TIMESERIES_SOC in asset:
                timeseries = asset[TIMESERIES_SOC].to_list()
                asset[TIMESERIES_SOC] = {UNIT: unit_soc, VALUE: timeseries}

            # Excess sinks should not be provided to the EPA
            if "_excess" not in asset_label:
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
