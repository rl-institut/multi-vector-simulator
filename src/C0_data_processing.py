import logging
import os
import shutil
import sys

import matplotlib.pyplot as plt
import pandas as pd

logging.getLogger("matplotlib.font_manager").disabled = True

from src.constants import (
    TIME_SERIES,
    PATH_INPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
    TYPE_BOOL,
    HEADER,
)

from src.constants_json_strings import *
import src.C1_verification as verify
import src.C2_economic_functions as economics
import src.F0_output as output
import src.F1_plotting as F1  # only function F1.plot_input_timeseries()

"""
Module C0 prepares the data red from csv or json for simulation, ie. pre-processes it. 
- Verify input values with C1
- Identify energyVectors and write them to project_data/sectors
- Create create an excess sink for each bus
- Process start_date/simulation_duration to pd.datatimeindex (future: Also consider timesteplenghts)
- Add economic parameters to json with C2
- Calculate "simulation annuity" used in oemof model
- Add demand sinks to energyVectors (this should actually be changed and demand sinks should be added to bus relative to input_direction, also see issue #179)
- Translate input_directions/output_directions to bus names
- Add missing cost data to automatically generated objects (eg. DSO transformers)
- Read timeseries of assets and store into json (differ between one-column csv, multi-column csv)
- Read timeseries for parameter of an asset, eg. efficiency
- Parse list of inputs/outputs, eg. for chp
- Define dso sinks, soures, transformer stations (this will be changed due to bug #119), also for peak demand pricing
- Add a source if a conversion object is connected to a new input_direction (bug #186)
- Define all necessary energyBusses and add all assets that are connected to them specifically with asset name and label
"""


class InvalidPeakDemandPricingPeriods(ValueError):
    # Exeption if an input is not valid
    pass


def all(dict_values):
    """
    Function executing all pre-processing steps necessary
    :param dict_values
    All input data in dict format

    :return Pre-processed dictionary with all input parameters

    """
    simulation_settings(dict_values[SIMULATION_SETTINGS])
    economic_parameters(dict_values[ECONOMIC_DATA])
    identify_energy_vectors(dict_values)

    ## Verify inputs
    # todo check whether input values can be true
    # verify.check_input_values(dict_values)
    # todo Check, whether files (demand, generation) are existing

    # Adds costs to each asset and sub-asset
    process_all_assets(dict_values)

    output.store_as_json(
        dict_values,
        dict_values[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER],
        "json_input_processed",
    )
    return


def identify_energy_vectors(dict_values):
    """
    Identifies all energyVectors used in the energy system by checking every entry 'energyVector' of all assets.
    energyVectors later will be used to distribute costs and KPI amongst the sectors (not implemented)

    :param: dict

    All input data in dict format

    :return:

    Update dict['project_data'] by used sectors
    """
    dict_of_sectors = {}
    names_of_sectors = ""
    for level1 in dict_values.keys():
        for level2 in dict_values[level1].keys():
            if (
                isinstance(dict_values[level1][level2], dict)
                and ENERGY_VECTOR in dict_values[level1][level2].keys()
            ):
                energy_vector_name = dict_values[level1][level2][ENERGY_VECTOR]
                if energy_vector_name not in dict_of_sectors.keys():
                    dict_of_sectors.update(
                        {energy_vector_name: energy_vector_name.replace("_", " ")}
                    )
                    names_of_sectors = names_of_sectors + energy_vector_name + ", "

    dict_values[PROJECT_DATA].update({SECTORS: dict_of_sectors})
    logging.info(
        "The energy system modelled includes following energy vectors / sectors: %s",
        names_of_sectors[:-2],
    )
    return


def simulation_settings(simulation_settings):
    """
    Updates simulation settings by all time-related parameters.
    :param: dict
    Simulation parameters of the input data
    :return: dict
    Update simulation_settings by start date, end date, timeindex, and number of simulation periods
    """
    simulation_settings.update(
        {START_DATE: pd.to_datetime(simulation_settings[START_DATE])}
    )
    simulation_settings.update(
        {
            END_DATE: simulation_settings[START_DATE]
            + pd.DateOffset(days=simulation_settings[EVALUATED_PERIOD][VALUE], hours=-1)
        }
    )
    # create time index used for initializing oemof simulation
    simulation_settings.update(
        {
            TIME_INDEX: pd.date_range(
                start=simulation_settings[START_DATE],
                end=simulation_settings[END_DATE],
                freq=str(simulation_settings[TIMESTEP][VALUE]) + UNIT_MINUTE,
            )
        }
    )

    simulation_settings.update({PERIODS: len(simulation_settings[TIME_INDEX])})
    return simulation_settings


def economic_parameters(economic_parameters):
    """
    Calculate annuity factor

    :param economic_parameters:
    :return:
    """

    economic_parameters.update(
        {
            ANNUITY_FACTOR: {
                VALUE: economics.annuity_factor(
                    economic_parameters[PROJECT_DURATION][VALUE],
                    economic_parameters[DISCOUNTFACTOR][VALUE],
                ),
                UNIT: "?",
            }
        }
    )
    # Calculate crf
    economic_parameters.update(
        {
            CRF: {
                VALUE: economics.crf(
                    economic_parameters[PROJECT_DURATION][VALUE],
                    economic_parameters[DISCOUNTFACTOR][VALUE],
                ),
                UNIT: "?",
            }
        }
    )
    return


def process_all_assets(dict_values):
    """defines dict_values['energyBusses'] for later reference

    :param dict_values:
    :return:
    """
    #
    define_busses(dict_values)

    # Define all excess sinks for each energy bus
    for bus_name in dict_values[ENERGY_BUSSES]:
        define_sink(
            dict_values=dict_values,
            asset_name=bus_name + EXCESS,
            price={VALUE: 0, UNIT: CURR + "/" + UNIT},
            input_bus_name=bus_name,
        )
        logging.debug(
            "Created excess sink for energy bus %s", bus_name,
        )

    # process all energyAssets:
    # Attention! Order of asset_groups important. for energyProviders/energyConversion sinks and sources
    # might be defined that have to be processed in energyProduction/energyConsumption

    # The values of the keys are functions!
    asset_group_list = {
        ENERGY_PROVIDERS: energyProviders,
        ENERGY_CONVERSION: energyConversion,
        ENERGY_STORAGE: energyStorage,
        ENERGY_PRODUCTION: energyProduction,
        ENERGY_CONSUMPTION: energyConsumption,
    }

    for asset_group, asset_function in asset_group_list.items():
        logging.info("Pre-processing all assets in asset group %s.", asset_group)
        # call asset function connected to current asset group (see asset_group_list)
        asset_function(dict_values, asset_group)

        logging.debug(
            "Finished pre-processing all assets in asset group %s.", asset_group
        )

    logging.info("Processed cost data and added economic values.")
    return


def energyConversion(dict_values, group):
    """Add lifetime capex (incl. replacement costs), calculate annuity (incl. om), and simulation annuity to each asset

    :param dict_values:
    :param group:
    :return:
    """
    #
    for asset in dict_values[group]:
        define_missing_cost_data(dict_values, dict_values[group][asset])
        evaluate_lifetime_costs(
            dict_values[SIMULATION_SETTINGS],
            dict_values[ECONOMIC_DATA],
            dict_values[group][asset],
        )
        # check if maximumCap exists and add it to dict_values
        add_maximum_cap(dict_values=dict_values, group=group, asset=asset)

        # in case there is only one parameter provided (input bus and one output bus)
        if isinstance(dict_values[group][asset][EFFICIENCY][VALUE], dict):
            receive_timeseries_from_csv(
                dict_values,
                dict_values[SIMULATION_SETTINGS],
                dict_values[group][asset],
                EFFICIENCY,
            )
        # in case there is more than one parameter provided (either (A) n input busses and 1 output bus or (B) 1 input bus and n output busses)
        # dictionaries with filenames and headers will be replaced by timeseries, scalars will be mantained
        elif isinstance(dict_values[group][asset][EFFICIENCY][VALUE], list):
            treat_multiple_flows(dict_values[group][asset], dict_values, EFFICIENCY)

            # same distinction of values provided with dictionaries (one input and one output) or list (multiple).
            # They can at turn be scalars, mantained, or timeseries
            logging.debug(
                "Asset %s has multiple input/output busses with a list of efficiencies. Reading list",
                dict_values[group][asset][LABEL],
            )
    return


def energyProduction(dict_values, group):
    """

    :param dict_values:
    :param group:
    :return:
    """
    for asset in dict_values[group]:
        define_missing_cost_data(dict_values, dict_values[group][asset])
        evaluate_lifetime_costs(
            dict_values[SIMULATION_SETTINGS],
            dict_values[ECONOMIC_DATA],
            dict_values[group][asset],
        )

        if FILENAME in dict_values[group][asset]:
            receive_timeseries_from_csv(
                dict_values,
                dict_values[SIMULATION_SETTINGS],
                dict_values[group][asset],
                "input",
            )
        # check if maximumCap exists and add it to dict_values
        add_maximum_cap(dict_values, group, asset)

    return


def energyStorage(dict_values, group):
    """

    :param dict_values:
    :param group:
    :return:
    """
    for asset in dict_values[group]:
        for subasset in [STORAGE_CAPACITY, INPUT_POWER, OUTPUT_POWER]:
            # Redefining the label of storage components, ie. so that is is clear to which storage a component (eg. input power) belongs.
            dict_values[group][asset][subasset].update(
                {
                    LABEL: dict_values[group][asset][LABEL]
                    + "_"
                    + dict_values[group][asset][subasset][LABEL]
                }
            )
            define_missing_cost_data(
                dict_values, dict_values[group][asset][subasset],
            )
            evaluate_lifetime_costs(
                dict_values[SIMULATION_SETTINGS],
                dict_values[ECONOMIC_DATA],
                dict_values[group][asset][subasset],
            )

            # check if parameters are provided as timeseries
            for parameter in [EFFICIENCY, SOC_MIN, SOC_MAX]:
                if parameter in dict_values[group][asset][subasset] and isinstance(
                    dict_values[group][asset][subasset][parameter][VALUE], dict
                ):
                    receive_timeseries_from_csv(
                        dict_values,
                        dict_values[SIMULATION_SETTINGS],
                        dict_values[group][asset][subasset],
                        parameter,
                    )
                elif parameter in dict_values[group][asset][subasset] and isinstance(
                    dict_values[group][asset][subasset][parameter][VALUE], list
                ):
                    treat_multiple_flows(
                        dict_values[group][asset][subasset], dict_values, parameter
                    )
            # check if maximumCap exists and add it to dict_values
            add_maximum_cap(dict_values, group, asset, subasset)

        # define input and output bus names
        dict_values[group][asset].update(
            {INPUT_BUS_NAME: bus_suffix(dict_values[group][asset][INFLOW_DIRECTION])}
        )
        dict_values[group][asset].update(
            {OUTPUT_BUS_NAME: bus_suffix(dict_values[group][asset][OUTFLOW_DIRECTION])}
        )
    return


def energyProviders(dict_values, group):
    """

    :param dict_values:
    :param group:
    :return:
    """
    # add sources and sinks depending on items in energy providers as pre-processing
    for asset in dict_values[group]:
        define_dso_sinks_and_sources(dict_values, asset)

        # Add lifetime capex (incl. replacement costs), calculate annuity
        # (incl. om), and simulation annuity to each asset
        define_missing_cost_data(dict_values, dict_values[group][asset])
        evaluate_lifetime_costs(
            dict_values[SIMULATION_SETTINGS],
            dict_values[ECONOMIC_DATA],
            dict_values[group][asset],
        )
    return


def energyConsumption(dict_values, group):
    """

    :param dict_values:
    :param group:
    :return:
    """
    for asset in dict_values[group]:
        define_missing_cost_data(dict_values, dict_values[group][asset])
        evaluate_lifetime_costs(
            dict_values[SIMULATION_SETTINGS],
            dict_values[ECONOMIC_DATA],
            dict_values[group][asset],
        )
        if INPUT_BUS_NAME not in dict_values[group][asset]:
            dict_values[group][asset].update(
                {INPUT_BUS_NAME: bus_suffix(dict_values[group][asset][ENERGY_VECTOR])}
            )

        if FILENAME in dict_values[group][asset]:
            receive_timeseries_from_csv(
                dict_values,
                dict_values[SIMULATION_SETTINGS],
                dict_values[group][asset],
                "input",
                is_demand_profile=True,
            )
    return


def define_missing_cost_data(dict_values, dict_asset):
    """

    :param dict_values:
    :param dict_asset:
    :return:
    """

    # read timeseries with filename provided for variable costs.
    # if multiple dispatch_price are given for multiple busses, it checks if any v
    # alue is a timeseries
    if DISPATCH_PRICE in dict_asset:
        if isinstance(dict_asset[DISPATCH_PRICE][VALUE], dict):
            receive_timeseries_from_csv(
                dict_values,
                dict_values[SIMULATION_SETTINGS],
                dict_asset,
                DISPATCH_PRICE,
            )
        elif isinstance(dict_asset[DISPATCH_PRICE][VALUE], list):
            treat_multiple_flows(dict_asset, dict_values, DISPATCH_PRICE)

    economic_data = dict_values[ECONOMIC_DATA]

    basic_costs = {
        OPTIMIZE_CAP: {VALUE: False, UNIT: TYPE_BOOL},
        UNIT: "?",
        INSTALLED_CAP: {VALUE: 0.0, UNIT: UNIT},
        DEVELOPMENT_COSTS: {VALUE: 0, UNIT: CURR},
        SPECIFIC_COSTS: {VALUE: 0, UNIT: CURR + "/" + UNIT},
        SPECIFIC_COSTS_OM: {VALUE: 0, UNIT: CURR + "/" + UNIT_YEAR},
        DISPATCH_PRICE: {VALUE: 0, UNIT: CURR + "/" + UNIT + "/" + UNIT_YEAR},
        LIFETIME: {VALUE: economic_data[PROJECT_DURATION][VALUE], UNIT: UNIT_YEAR,},
    }

    # checks that an asset has all cost parameters needed for evaluation.
    # Adds standard values.
    str = ""
    for cost in basic_costs:
        if cost not in dict_asset:
            dict_asset.update({cost: basic_costs[cost]})
            str = str + " " + cost

    if len(str) > 1:
        logging.debug("Added basic costs to asset %s: %s", dict_asset[LABEL], str)
    return


def define_busses(dict_values):
    """
    This function defines the ENERGY_BUSSES that the energy system model is compised of.
    For that, it adds each new bus defined as INPUT_DIRECTION or OUTPUT_DIRECTION in all assets
    of all the energyAsset types (ENERGY_CONVERSION, ENERGY_PRODUCTION, ENERGY_CONSUMPTION, ENERGY_PROVIDERS, ENERGY_STORAGE)

    Parameters
    ----------
    dict_values: dict
        Dictionary with all simulation information

    Returns
    -------
    Extends dict_values by key "ENERGY_BUSSES" and all their names.

    """
    # create new group of assets: busses
    dict_values.update({ENERGY_BUSSES: {}})

    # Interatively adds busses to ENERGY_BUSSES for each new bus in the inflow/outflow direction of subsequent assets
    for group in [
        ENERGY_CONVERSION,
        ENERGY_PRODUCTION,
        ENERGY_CONSUMPTION,
        ENERGY_PROVIDERS,
        ENERGY_STORAGE,
    ]:
        for asset in dict_values[group]:
            add_busses_of_asset_depending_on_in_out_direction(
                dict_values, dict_values[group][asset], asset
            )

    return


def add_busses_of_asset_depending_on_in_out_direction(
    dict_values, dict_asset, asset_key
):
    """
    Check if the INPUT_DIRECTION and OUTPUT_DIRECTION, ie the bus, of an asset is already included in energyBusses.
    Otherwise, add to dict_values(ENERGY_BUSSES).

    Translates INPUT_DIRECTION and OUTPUT_DIRECTION into INPUT_BUS_NAME and OUTPUT_BUS_NAME.

    Parameters
    ----------
    dict_values: dict
        All simulation information

    dict_asset: dict
        All information of the current asset

    asset_key: str
        Key that calls the dict_asset from dict_values[asset_group][key]

    Returns
    -------
    Updated dict_values with potentially additional busses of the energy system.
    Updated dict_asset with the input_bus_name
    """

    for direction in [INFLOW_DIRECTION, OUTFLOW_DIRECTION]:
        # This is the parameter that will be added to dict_asset as the bus_name_key
        if direction == INFLOW_DIRECTION:
            bus_name_key = INPUT_BUS_NAME
        else:
            bus_name_key = OUTPUT_BUS_NAME

        # Check if the asset has an INFLOW_DIRECTION or OUTFLOW_DIRECTION
        if direction in dict_asset:
            bus = dict_asset[direction]
            # Check if a list ob busses is in INFLOW_DIRECTION or OUTFLOW_DIRECTION
            if isinstance(bus, list):
                # If true: All busses need to be checked
                bus_list = []
                # Checking each bus of the list
                for subbus in bus:
                    # Append bus name to bus_list
                    bus_list.append(bus_suffix(subbus))
                    # Check if bus of the direction is already contained in energyBusses
                    update_bus(
                        bus=subbus,
                        dict_values=dict_values,
                        asset_key=asset_key,
                        asset_label=dict_asset[LABEL],
                    )
                # Add bus_name_key to dict_asset
                dict_asset.update({bus_name_key: bus_list})
            # If false: Only one bus
            else:
                # Check if bus of the direction is already contained in energyBusses
                update_bus(
                    bus=bus,
                    dict_values=dict_values,
                    asset_key=asset_key,
                    asset_label=dict_asset[LABEL],
                )
                # Add bus_name_key to dict_asset
                dict_asset.update({bus_name_key: bus_suffix(bus)})
    return


def bus_suffix(bus_direction):
    """
    Returns the name of a bus with the suffix defined in constants_json_strings.py (BUS_SUFFIX)

    It is possible that the suffix will be dropped later on, in case that users always enter the directions with suffix " bus" anyway.

    Parameters
    ----------
    bus_direction: str
        A string, ie. a bus name

    Returns
    -------
    Above string with BUS_SUFFIX
    """
    bus_label = bus_direction + BUS_SUFFIX
    return bus_label


def remove_bus_suffix(bus_label):
    """
    Removes suffix from a INPUT / OUTPUT BUS LABEL to get the INPUT / OUTPUT DIRECTION.

    Parameters
    ----------
    bus_label: str
        Bus label with suffix

    Returns
    -------
    Bus direction (without suffix)
    """
    bus_direction = bus_label[: -len(BUS_SUFFIX)]
    return bus_direction


def update_bus(bus, dict_values, asset_key, asset_label):
    """
    Checks if an bus is already included in ENERGY_BUSSES and otherwise adds it.
    Adds asset key and label to list of assets attached to a bus.

    Parameters
    ----------
    dict_values: dict
        Dict of all simulation parameters

    bus: str
        A bus label

    asset_key: str
        Key with with an dict_asset would be called from dict_values[groups][key]

    asset_label: str
        Label of the asset

    Returns
    -------
    Updated dict_values[ENERGY_BUSSES], optionally with new busses and/or by adding an asset to a bus
    """
    bus_label = bus_suffix(bus)

    if bus_label not in dict_values[ENERGY_BUSSES]:
        # add bus to asset group energyBusses
        dict_values[ENERGY_BUSSES].update({bus_label: {}})

    # Asset should added to respective bus
    dict_values[ENERGY_BUSSES][bus_label].update({asset_key: asset_label})
    logging.debug("Added asset %s to bus %s", asset_label, bus_label)
    return


def define_dso_sinks_and_sources(dict_values, dso):
    r"""
    Defines all sinks and sources that need to be added to model the transformer using assets of energyConsumption, energyProduction and energyConversion.

    Parameters
    ----------
    dict_values
    dso

    Returns
    -------
    Updated dict_values
    """

    number_of_pricing_periods = dict_values[ENERGY_PROVIDERS][dso][
        PEAK_DEMAND_PRICING_PERIOD
    ][VALUE]

    months_in_a_period = determine_months_in_a_peak_demand_pricing_period(
        number_of_pricing_periods,
        dict_values[SIMULATION_SETTINGS][EVALUATED_PERIOD][VALUE],
    )

    dict_availability_timeseries = define_availability_of_peak_demand_pricing_assets(
        dict_values, number_of_pricing_periods, months_in_a_period,
    )

    list_of_dso_energyConversion_assets = add_a_transformer_for_each_peak_demand_pricing_period(
        dict_values, dict_values[ENERGY_PROVIDERS][dso], dict_availability_timeseries
    )

    define_source(
        dict_values=dict_values,
        asset_key=dso + DSO_CONSUMPTION,
        output_bus_direction=dict_values[ENERGY_PROVIDERS][dso][OUTFLOW_DIRECTION]
        + DSO_PEAK_DEMAND_BUS_NAME,
        price=dict_values[ENERGY_PROVIDERS][dso][ENERGY_PRICE],
    )

    # define feed-in sink of the DSO
    define_sink(
        dict_values=dict_values,
        asset_name=dso + DSO_FEEDIN + AUTO_SINK,
        price=dict_values[ENERGY_PROVIDERS][dso][FEEDIN_TARIFF],
        input_bus_name=dict_values[ENERGY_PROVIDERS][dso][INPUT_BUS_NAME],
        specific_costs={VALUE: 0, UNIT: CURR + "/" + UNIT},
    )

    dict_values[ENERGY_PROVIDERS][dso].update(
        {
            CONNECTED_CONSUMPTION_SOURCE: dso + DSO_CONSUMPTION + AUTO_SOURCE,
            CONNECTED_PEAK_DEMAND_PRICING_TRANSFORMERS: list_of_dso_energyConversion_assets,
            CONNECTED_FEEDIN_SINK: dso + DSO_FEEDIN + AUTO_SINK,
        }
    )

    return


def define_availability_of_peak_demand_pricing_assets(
    dict_values, number_of_pricing_periods, months_in_a_period
):
    r"""
    Determined the availability timeseries for the later to be defined dso assets for taking into account the peak demand pricing periods.

    Parameters
    ----------
    dict_values: dict
        All simulation inputs
    number_of_pricing_periods: int
        Number of pricing periods in a year. Valid: 1,2,3,4,6,12
    months_in_a_period: int
        Duration of a period

    Returns
    -------
    dict_availability_timeseries: dict
        Dict with all availability timeseries for each period

    """
    dict_availability_timeseries = {}
    for period in range(1, number_of_pricing_periods + 1):
        availability_in_period = pd.Series(
            0, index=dict_values[SIMULATION_SETTINGS][TIME_INDEX]
        )
        time_period = pd.date_range(
            # Period start
            start=dict_values[SIMULATION_SETTINGS][START_DATE]
            + pd.DateOffset(months=(period - 1) * months_in_a_period),
            # Period end, with months_in_a_period durartion
            end=dict_values[SIMULATION_SETTINGS][START_DATE]
            + pd.DateOffset(months=(period) * months_in_a_period, hours=-1),
            freq=str(dict_values[SIMULATION_SETTINGS][TIMESTEP][VALUE]) + UNIT_MINUTE,
        )

        availability_in_period = availability_in_period.add(
            pd.Series(1, index=time_period), fill_value=0
        )
        dict_availability_timeseries.update({period: availability_in_period})

    return dict_availability_timeseries


def add_a_transformer_for_each_peak_demand_pricing_period(
    dict_values, dict_dso, dict_availability_timeseries
):
    r"""
    Adds transformers that are supposed to model the peak_demand_pricing periods for each period.
    This is changed compared to MVS 0.3.0, as there a peak demand pricing period was added by adding a source, not a transformer.

    Parameters
    ----------
    dict_values: dict
        dict with all simulation parameters

    dict_dso: dict
        dict with all info on the specific dso at hand

    dict_availability_timeseries: dict
        dict with all availability timeseries for each period

    Returns
    -------
    list_of_dso_energyConversion_assets: list
        List of names of newly added energy conversion assets,

    Updated dict_values with a transformer for each peak demand pricing period
    """

    list_of_dso_energyConversion_assets = []
    for key in dict_availability_timeseries.keys():
        if len(dict_availability_timeseries.keys()) == 1:
            transformer_name = (
                dict_dso[LABEL] + DSO_CONSUMPTION + DSO_PEAK_DEMAND_PERIOD
            )
        else:
            transformer_name = (
                dict_dso[LABEL]
                + DSO_CONSUMPTION
                + DSO_PEAK_DEMAND_PERIOD
                + "_"
                + str(key)
            )

        define_transformer_for_peak_demand_pricing(
            dict_values=dict_values,
            dict_dso=dict_dso,
            transformer_name=transformer_name,
            timeseries_availability=dict_availability_timeseries[key],
        )

        F1.plot_input_timeseries(
            dict_values=dict_values,
            user_input=dict_values[SIMULATION_SETTINGS],
            timeseries=dict_availability_timeseries[key],
            asset_name="Availability of " + transformer_name,
        )

        list_of_dso_energyConversion_assets.append(transformer_name)

    logging.debug(
        f"The peak demand pricing price of {dict_dso[PEAK_DEMAND_PRICING][VALUE]} {dict_values[ECONOMIC_DATA][CURR]} "
        f"is set as specific_costs_om of the peak demand pricing transformers of the DSO."
    )
    return list_of_dso_energyConversion_assets


def determine_months_in_a_peak_demand_pricing_period(
    number_of_pricing_periods, simulation_period_lenght
):
    r"""
    Check if the number of peak demand pricing periods is valid.
    Warns user that in case the number of periods exceeds 1 but the simulation time is not a year,
    there could be an unexpected number of timeseries considered.
    Raises error if number of peak demand pricing periods is not valid.

    Parameters
    ----------
    number_of_pricing_periods: int
        Defined in csv, is number of pricing periods within a year
    simulation_period_lenght: int
        Defined in csv, is number of days of the simulation

    Returns
    -------
    months_in_a_period: float
        Number of months that make a period, will be used to determine availability of dso assets
    """

    # check number of pricing periods - if >1 the simulation has to cover a whole year!
    if number_of_pricing_periods > 1:
        if simulation_period_lenght != 365:
            logging.debug(
                f"\n Message for dev: Following warning is not technically true, "
                f"as the evaluation period has to approximately be "
                f"larger than 365/peak demand pricing periods (see #331)."
            )
            logging.warning(
                f"You have chosen a number of peak demand pricing periods > 1."
                f"Please be advised that if you are not simulating for a year (365d)"
                f"an possibly unexpected number of periods will be considered."
            )
    if number_of_pricing_periods not in [1, 2, 3, 4, 6, 12]:
        raise InvalidPeakDemandPricingPeriods(
            f"You have defined a number of peak demand pricing periods of {number_of_pricing_periods}. "
            f"Acceptable values are, however: 1 (yearly), 2 (half-yearly), 3 (each trimester), 4 (quarterly), 6 (every two months) and 1 (monthly)."
        )

    # defines the number of months that one period constists of.
    months_in_a_period = 12 / number_of_pricing_periods
    logging.info(
        "Peak demand pricing is taking place %s times per year, ie. every %s "
        "months.",
        number_of_pricing_periods,
        months_in_a_period,
    )
    return months_in_a_period


def define_transformer_for_peak_demand_pricing(
    dict_values, dict_dso, transformer_name, timeseries_availability
):
    r"""
    Defines a transformer for peak demand pricing in energyConverion

    Parameters
    ----------
    dict_values: dict
        All simulation parameters

    dict_dso: dict
        All values connected to the DSO

    transformer_name: str
        label of the transformer to be added

    timeseries_availability: pd.Series
        Timeseries of transformer availability. Introduced to cover peak demand pricing.

    Returns
    -------
    Updated dict_values with newly added transformer asset in the energyConversion asset group.
    """

    default_dso_transformer = {
        LABEL: transformer_name,
        OPTIMIZE_CAP: {VALUE: True, UNIT: TYPE_BOOL},
        INSTALLED_CAP: {VALUE: 0, UNIT: dict_dso[UNIT]},
        INFLOW_DIRECTION: dict_dso[INFLOW_DIRECTION] + DSO_PEAK_DEMAND_BUS_NAME,
        INPUT_BUS_NAME: bus_suffix(
            dict_dso[INFLOW_DIRECTION] + DSO_PEAK_DEMAND_BUS_NAME
        ),
        OUTFLOW_DIRECTION: dict_dso[OUTFLOW_DIRECTION],
        OUTPUT_BUS_NAME: bus_suffix(dict_dso[OUTFLOW_DIRECTION]),
        AVAILABILITY_DISPATCH: timeseries_availability,
        EFFICIENCY: {VALUE: 1, UNIT: "factor"},
        DEVELOPMENT_COSTS: {VALUE: 0, UNIT: CURR},
        SPECIFIC_COSTS: {
            VALUE: 0,
            UNIT: CURR + "/" + dict_dso[UNIT],
        },
        SPECIFIC_COSTS_OM: {
            VALUE: dict_dso[PEAK_DEMAND_PRICING][VALUE],
            UNIT: CURR + "/" + dict_dso[UNIT] + "/" + UNIT_YEAR,
        },
        DISPATCH_PRICE: {VALUE: 0, UNIT: CURR + "/" + dict_dso[UNIT] + "/" + UNIT_HOUR},
        OEMOF_ASSET_TYPE: OEMOF_TRANSFORMER,
    }

    dict_values[ENERGY_CONVERSION].update({transformer_name: default_dso_transformer})

    logging.debug(
        f"Model for peak demand pricing: Adding transfomer {transformer_name}."
    )
    return


def define_source(dict_values, asset_key, output_bus_direction, **kwargs):
    f"""
    Defines a source with default input values. If kwargs are given, the default values are overwritten.

    Parameters
    ----------
    dict_values: dict
        Dictionary to which source should be added, with all simulation parameters

    asset_key: str
        key under which the asset is stored in the asset group
        
    kwargs: Misc.
        Kwargs that can overwrite the default values.
        Typical kwargs:
            - TIMESERIES
            - SPECIFIC_COSTS_OM
            - SPECIFIC_COSTS
            - "price"

    Returns
    -------
    Standard source defined as:
    """

    output_bus_name = get_name_or_names_of_in_or_output_bus(output_bus_direction)

    default_source_dict = {
        OEMOF_ASSET_TYPE: OEMOF_SOURCE,
        LABEL: asset_key + AUTO_SOURCE,
        OUTFLOW_DIRECTION: output_bus_direction,
        OUTPUT_BUS_NAME: output_bus_name,
        DISPATCHABILITY: True,
        # OPEX_VAR: {VALUE: price, UNIT: CURR + "/" + UNIT},
        LIFETIME: {
            VALUE: dict_values[ECONOMIC_DATA][PROJECT_DURATION][VALUE],
            UNIT: UNIT_YEAR,
        },
        OPTIMIZE_CAP: {VALUE: True, UNIT: TYPE_BOOL},
        MAXIMUM_CAP: {VALUE: None, UNIT: "?"},
    }

    for item in kwargs:
        if item in [SPECIFIC_COSTS_OM, SPECIFIC_COSTS]:
            default_source_dict.update({item: kwargs[item]})
        if item == TIMESERIES:
            default_source_dict.update({DISPATCHABILITY: False})
            logging.debug(
                f"{default_source_dict[LABEL]} can provide a total generation of {sum(kwargs[TIMESERIES].values)}"
            )
            default_source_dict.update(
                {
                    OPTIMIZE_CAP: {VALUE: True, UNIT: TYPE_BOOL},
                    TIMESERIES_PEAK: {VALUE: max(kwargs[TIMESERIES]), UNIT: "kW"},
                    # todo if we have normalized timeseries hiere, the capex/opex (simulation) have changed, too
                    TIMESERIES_NORMALIZED: kwargs[TIMESERIES] / max(kwargs[TIMESERIES]),
                }
            )
        if item == "price":
            determine_dispatch_price(dict_values, kwargs[item], default_source_dict)

    dict_values[ENERGY_PRODUCTION].update({asset_key: default_source_dict})

    logging.info(
        f"Asset {default_source_dict[LABEL]} was added to the energyProduction assets."
    )

    apply_function_to_single_or_list(
        function=update_bus,
        parameter=output_bus_direction,
        dict_values=dict_values,
        asset_key=asset_key,
        asset_label=default_source_dict[LABEL],
    )
    return


def get_name_or_names_of_in_or_output_bus(bus):
    """
    Returns the bus names of one or multiple in- or output busses.

    Parameters
    ----------
    bus: str
        A bus name without bus suffix

    Returns
    -------
    Bus name with suffix
    """
    if isinstance(bus, list):
        bus_name = []
        for bus_item in bus:
            bus_name.append(bus_suffix(bus_item))
    else:
        bus_name = bus_suffix(bus)
    return bus_name


def determine_dispatch_price(dict_values, price, source):

    # check if multiple busses are provided
    # for each bus, read time series for dispatch_price if a file name has been
    # provided in energy price
    if isinstance(price[VALUE], list):
        source.update({DISPATCH_PRICE: {VALUE: [], UNIT: price[UNIT]}})
        values_info = []
        for element in price[VALUE]:
            if isinstance(element, dict):
                source[DISPATCH_PRICE][VALUE].append(
                    get_timeseries_multiple_flows(
                        dict_values[SIMULATION_SETTINGS],
                        source,
                        element[FILENAME],
                        element[HEADER],
                    )
                )
                values_info.append(element)
            else:
                source[DISPATCH_PRICE][VALUE].append(element)
        if len(values_info) > 0:
            source[DISPATCH_PRICE]["values_info"] = values_info

    elif isinstance(price[VALUE], dict):
        source.update(
            {
                DISPATCH_PRICE: {
                    VALUE: {
                        FILENAME: price[VALUE][FILENAME],
                        HEADER: price[VALUE][HEADER],
                    },
                    UNIT: price[UNIT],
                }
            }
        )
        receive_timeseries_from_csv(
            dict_values, dict_values[SIMULATION_SETTINGS], source, DISPATCH_PRICE
        )
    else:
        source.update({DISPATCH_PRICE: {VALUE: price[VALUE], UNIT: price[UNIT]}})

    if type(source[DISPATCH_PRICE][VALUE]) == pd.Series:
        logging.warning(
            "Attention! %s is created, with a price defined as a timeseries (average: %s). "
            "If this is DSO supply, this could be improved. Please refer to Issue #23.",
            source[LABEL],
            source[DISPATCH_PRICE][VALUE].mean(),
        )
    else:
        logging.warning(
            "Attention! %s is created, with a price of %s."
            "If this is DSO supply, this could be improved. Please refer to Issue #23. ",
            source[LABEL],
            source[DISPATCH_PRICE][VALUE],
        )
    return


def define_sink(dict_values, asset_name, price, input_bus_name, **kwargs):
    r"""
    This automatically defines a sink for an oemof-sink object. The sinks are added to the energyConsumption assets.

    Parameters
    ----------
    dict_values: dict
        All information of the simulation

    asset_name: str
        label of the asset to be generated

    price: float
        Price of dispatch of the asset

    input_direction: str
        Direction from which energy is provided to the sink, used to create inbut bus name

    kwargs: Misc
        Common parameters:
        -

    Returns
    -------
    Updates dict_values[ENERGY_CONSUMPTION] with a new sink

    Notes
    -----
    Examples:
    - Used to define excess sinks for all energyBusses
    - Used to define feed-in sink for each DSO
    """

    # create name of bus. Check if multiple busses are given
    input_direction = remove_bus_suffix(input_bus_name)

    # create a dictionary for the sink
    sink = {
        OEMOF_ASSET_TYPE: OEMOF_SINK,
        LABEL: asset_name + AUTO_SINK,
        INFLOW_DIRECTION: input_direction,
        INPUT_BUS_NAME: input_bus_name,
        # OPEX_VAR: {VALUE: price, UNIT: CURR + "/" + UNIT},
        LIFETIME: {
            VALUE: dict_values[ECONOMIC_DATA][PROJECT_DURATION][VALUE],
            UNIT: UNIT_YEAR,
        },
    }

    # check if multiple busses are provided
    # for each bus, read time series for dispatch_price if a file name has been provided in feedin tariff
    if isinstance(price[VALUE], list):
        sink.update({DISPATCH_PRICE: {VALUE: [], UNIT: price[UNIT]}})
        values_info = []
        for element in price[VALUE]:
            if isinstance(element, dict):
                timeseries = get_timeseries_multiple_flows(
                    dict_values[SIMULATION_SETTINGS],
                    sink,
                    element[FILENAME],
                    element[HEADER],
                )
                if asset_name[-6:] == "feedin":
                    sink[DISPATCH_PRICE][VALUE].append([-i for i in timeseries])
                else:
                    sink[DISPATCH_PRICE][VALUE].append(timeseries)
            else:
                sink[DISPATCH_PRICE][VALUE].append(element)
        if len(values_info) > 0:
            sink[DISPATCH_PRICE]["values_info"] = values_info

    elif isinstance(price[VALUE], dict):
        sink.update(
            {
                DISPATCH_PRICE: {
                    VALUE: {
                        FILENAME: price[VALUE][FILENAME],
                        HEADER: price[VALUE][HEADER],
                    },
                    UNIT: price[UNIT],
                }
            }
        )
        receive_timeseries_from_csv(
            dict_values, dict_values[SIMULATION_SETTINGS], sink, DISPATCH_PRICE
        )
        if (
            asset_name[-6:] == "feedin"
        ):  # change into negative value if this is a feedin sink
            sink[DISPATCH_PRICE].update(
                {VALUE: [-i for i in sink[DISPATCH_PRICE][VALUE]]}
            )
    else:
        if asset_name[-6:] == "feedin":
            value = -price[VALUE]
        else:
            value = price[VALUE]
        sink.update({DISPATCH_PRICE: {VALUE: value, UNIT: price[UNIT]}})

    if SPECIFIC_COSTS in kwargs:
        sink.update(
            {
                SPECIFIC_COSTS: kwargs[SPECIFIC_COSTS],
                OPTIMIZE_CAP: {VALUE: True, UNIT: TYPE_BOOL},
            }
        )
    if SPECIFIC_COSTS_OM in kwargs:
        sink.update(
            {
                SPECIFIC_COSTS_OM: kwargs[SPECIFIC_COSTS_OM],
                OPTIMIZE_CAP: {VALUE: True, UNIT: TYPE_BOOL},
            }
        )
    else:
        sink.update({OPTIMIZE_CAP: {VALUE: False, UNIT: TYPE_BOOL}})

    # update dictionary
    dict_values[ENERGY_CONSUMPTION].update({asset_name: sink})

    # If multiple input busses exist
    apply_function_to_single_or_list(
        function=update_bus,
        parameter=input_direction,
        dict_values=dict_values,
        asset_key=asset_name,
        asset_label=sink[LABEL],
    )

    return


def apply_function_to_single_or_list(function, parameter, **kwargs):
    """
    Applies function to a paramter or to a list of parameters and returns resut

    Parameters
    ----------
    function: func
        Function to be applied to a parameter

    parameter: float/str/boolean or list
        Parameter, either float/str/boolean or list to be evaluated
    kwargs
        Miscellaneous arguments for function to be called

    Returns
    -------
    Processed parameter (single) or list of processed para<meters
    """
    if isinstance(parameter, list):
        parameter_processed = []
        for parameter_item in parameter:
            parameter_processed.append(function(parameter_item, **kwargs))
    else:
        parameter_processed = function(parameter, **kwargs)

    return parameter_processed


def evaluate_lifetime_costs(settings, economic_data, dict_asset):
    r"""
    Evaluates specific costs of an asset over the project lifetime. This includes:
    - LIFETIME_PRICE_DISPATCH (determine_lifetime_price_dispatch)
    - LIFETIME_SPECIFIC_COST
    - LIFETIME_SPECIFIC_COST_OM
    - ANNUITY_SPECIFIC_INVESTMENT_AND_OM
    - SIMULATION_ANNUITY

    The DEVELOPMENT_COSTS are not processed here, as they are not necessary for the optimization.

    Parameters
    ----------
    settings: dict
        dict of simulation settings, including:
        - EVALUATED_PERIOD

    economic_data: dict
        dict of economic data of the simulation, including
        - project duration (PROJECT_DURATION)
        - discount factor (DISCOUNTFACTOR)
        - tax (TAX)
        - CRF
        - ANNUITY_FACTOR

    dict_asset: dict
        dict of all asset parameters, including
        - SPECIFIC_COSTS
        - SPECIFIC_COSTS_OM
        - LIFETIME

    Returns
    -------
    Updates asset dict with
    - LIFETIME_PRICE_DISPATCH (determine_lifetime_price_dispatch)
    - LIFETIME_SPECIFIC_COST
    - LIFETIME_SPECIFIC_COST_OM
    - ANNUITY_SPECIFIC_INVESTMENT_AND_OM
    - SIMULATION_ANNUITY
    """

    determine_lifetime_price_dispatch(dict_asset, economic_data)

    dict_asset.update(
        {
            LIFETIME_SPECIFIC_COST: {
                VALUE: economics.capex_from_investment(
                    dict_asset[SPECIFIC_COSTS][VALUE],
                    dict_asset[LIFETIME][VALUE],
                    economic_data[PROJECT_DURATION][VALUE],
                    economic_data[DISCOUNTFACTOR][VALUE],
                    economic_data[TAX][VALUE],
                ),
                UNIT: dict_asset[SPECIFIC_COSTS][UNIT],
            }
        }
    )

    # Annuities of components including opex AND capex #
    dict_asset.update(
        {
            ANNUITY_SPECIFIC_INVESTMENT_AND_OM: {
                VALUE: economics.annuity(
                    dict_asset[LIFETIME_SPECIFIC_COST][VALUE],
                    economic_data[CRF][VALUE],
                )
                + dict_asset[SPECIFIC_COSTS_OM][VALUE],  # changes from dispatch_price
                UNIT: dict_asset[LIFETIME_SPECIFIC_COST][UNIT] + "/" + UNIT_YEAR,
            }
        }
    )

    dict_asset.update(
        {
            LIFETIME_SPECIFIC_COST_OM: {
                VALUE: dict_asset[SPECIFIC_COSTS_OM][VALUE]
                * economic_data[ANNUITY_FACTOR][VALUE],
                UNIT: dict_asset[SPECIFIC_COSTS_OM][UNIT][:-2],
            }
        }
    )

    dict_asset.update(
        {
            SIMULATION_ANNUITY: {
                VALUE: economics.simulation_annuity(
                    dict_asset[ANNUITY_SPECIFIC_INVESTMENT_AND_OM][VALUE],
                    settings[EVALUATED_PERIOD][VALUE],
                ),
                UNIT: CURR + "/" + UNIT + "/" + EVALUATED_PERIOD,
            }
        }
    )

    return


def determine_lifetime_price_dispatch(dict_asset, economic_data):
    """
    #todo I am not sure that this makes sense. is this used in d0?
    Parameters
    ----------
    dict_asset
    economic_data

    Returns
    -------

    """
    if isinstance(dict_asset[DISPATCH_PRICE][VALUE], float) or isinstance(
        dict_asset[DISPATCH_PRICE][VALUE], int
    ):
        lifetime_price_dispatch = get_lifetime_price_dispatch_one_value(
            dict_asset, economic_data
        )

    elif isinstance(dict_asset[DISPATCH_PRICE][VALUE], list):
        lifetime_price_dispatch = get_lifetime_price_dispatch_list(
            dict_asset, economic_data
        )

    elif isinstance(dict_asset[DISPATCH_PRICE][VALUE], pd.Series):
        lifetime_price_dispatch = get_lifetime_price_dispatch_timeseries(
            dict_asset, economic_data
        )

    else:
        raise ValueError(
            f"Type of dispatch_price neither int, float, list or pd.Series, but of type {dict_asset[DISPATCH_PRICE][VALUE]}. Is type correct?"
        )

    dict_asset.update(
        {LIFETIME_PRICE_DISPATCH: {VALUE: lifetime_price_dispatch, UNIT: "?",}}
    )
    return


def get_lifetime_price_dispatch_one_value(dict_asset, economic_data):
    """
    dispatch_price can be a fix value
    Returns
    -------

    """
    lifetime_price_dispatch = (
        dict_asset[DISPATCH_PRICE][VALUE] * economic_data[ANNUITY_FACTOR][VALUE]
    )
    return lifetime_price_dispatch


def get_lifetime_price_dispatch_list(dict_asset, economic_data):
    """
    dispatch_price can be a list, for example if there are two input flows to a component, eg. water and electricity.
    Their ratio for providing cooling in kWh therm is fix. There should be a lifetime_price_dispatch for each of them.

    Returns
    -------

    """

    # if multiple busses are provided, it takes the first dispatch_price (corresponding to the first bus)

    first_value = dict_asset[DISPATCH_PRICE][VALUE][0]
    if isinstance(first_value, float) or isinstance(first_value, int):
        dispatch_price = first_value
    else:
        dispatch_price = sum(first_value) / len(first_value)

    lifetime_price_dispatch = dispatch_price * economic_data[ANNUITY_FACTOR][VALUE]
    return lifetime_price_dispatch


def get_lifetime_price_dispatch_timeseries(dict_asset, economic_data):
    """
    dispatch_price can be a timeseries, eg. in case that there is an hourly pricing
    Returns
    -------

    """
    # take average value of dispatch_price if it is a timeseries

    dispatch_price = sum(dict_asset[DISPATCH_PRICE][VALUE]) / len(
        dict_asset[DISPATCH_PRICE][VALUE]
    )
    lifetime_price_dispatch = (
        dict_asset[DISPATCH_PRICE][VALUE] * economic_data[ANNUITY_FACTOR][VALUE]
    )
    return lifetime_price_dispatch


# read timeseries. 2 cases are considered: Input type is related to demand or generation profiles,
# so additional values like peak, total or average must be calculated. Any other type does not need this additional info.
def receive_timeseries_from_csv(
    dict_values, settings, dict_asset, input_type, is_demand_profile=False
):
    """

    :param settings:
    :param dict_asset:
    :param type:
    :return:
    """
    if input_type == "input" and "input" in dict_asset:
        file_name = dict_asset[input_type][FILENAME]
        header = dict_asset[input_type][HEADER]
        unit = dict_asset[input_type][UNIT]
    elif FILENAME in dict_asset:
        # todo this input/file_name thing is a workaround and has to be improved in the future
        # if only filename is given here, then only one column can be in the csv
        file_name = dict_asset[FILENAME]
        unit = dict_asset[UNIT] + "/" + UNIT_HOUR
    else:
        file_name = dict_asset[input_type][VALUE][FILENAME]
        header = dict_asset[input_type][VALUE][HEADER]
        unit = dict_asset[input_type][UNIT]

    file_path = os.path.join(settings[PATH_INPUT_FOLDER], TIME_SERIES, file_name)
    verify.lookup_file(file_path, dict_asset[LABEL])

    data_set = pd.read_csv(file_path, sep=",")

    if FILENAME in dict_asset:
        header = data_set.columns[0]

    if len(data_set.index) == settings[PERIODS]:
        if input_type == "input":
            dict_asset.update(
                {
                    TIMESERIES: pd.Series(
                        data_set[header].values, index=settings[TIME_INDEX]
                    )
                }
            )
        else:
            dict_asset[input_type]["value_info"] = dict_asset[input_type][VALUE]
            dict_asset[input_type][VALUE] = pd.Series(
                data_set[header].values, index=settings[TIME_INDEX]
            )

        logging.debug("Added timeseries of %s (%s).", dict_asset[LABEL], file_path)
    elif len(data_set.index) >= settings[PERIODS]:
        if input_type == "input":
            dict_asset.update(
                {
                    TIMESERIES: pd.Series(
                        data_set[header][0 : len(settings[TIME_INDEX])].values,
                        index=settings[TIME_INDEX],
                    )
                }
            )
        else:
            dict_asset[input_type]["value_info"] = dict_asset[input_type][VALUE]
            dict_asset[input_type][VALUE] = pd.Series(
                data_set[header][0 : len(settings[TIME_INDEX])].values,
                index=settings[TIME_INDEX],
            )

        logging.info(
            "Provided timeseries of %s (%s) longer than evaluated period. "
            "Excess data dropped.",
            dict_asset[LABEL],
            file_path,
        )

    elif len(data_set.index) <= settings[PERIODS]:
        logging.critical(
            "Input error! "
            "Provided timeseries of %s (%s) shorter then evaluated period. "
            "Operation terminated",
            dict_asset[LABEL],
            file_path,
        )
        sys.exit()

    if input_type == "input":
        dict_asset.update(
            {
                TIMESERIES_PEAK: {VALUE: max(dict_asset[TIMESERIES]), UNIT: unit,},
                "timeseries_total": {VALUE: sum(dict_asset[TIMESERIES]), UNIT: unit,},
                "timeseries_average": {
                    VALUE: sum(dict_asset[TIMESERIES]) / len(dict_asset[TIMESERIES]),
                    UNIT: unit,
                },
            }
        )

        if dict_asset[OPTIMIZE_CAP][VALUE] is True:
            logging.debug("Normalizing timeseries of %s.", dict_asset[LABEL])
            dict_asset.update(
                {
                    TIMESERIES_NORMALIZED: dict_asset[TIMESERIES]
                    / dict_asset[TIMESERIES_PEAK][VALUE]
                }
            )
            # just to be sure!
            if any(dict_asset[TIMESERIES_NORMALIZED].values) > 1:
                logging.warning(
                    "Error, %s timeseries not normalized, greater than 1.",
                    dict_asset[LABEL],
                )
            if any(dict_asset[TIMESERIES_NORMALIZED].values) < 0:
                logging.warning("Error, %s timeseries negative.", dict_asset[LABEL])

    # plot all timeseries that are red into simulation input
    try:
        F1.plot_input_timeseries(
            dict_values=dict_values,
            user_input=settings,
            timeseries=dict_asset[TIMESERIES],
            asset_name=dict_asset[LABEL],
            column_head=header,
            is_demand_profile=is_demand_profile,
        )
    except:
        F1.plot_input_timeseries(
            dict_values=dict_values,
            user_input=settings,
            timeseries=dict_asset[input_type][VALUE],
            asset_name=dict_asset[LABEL],
            column_head=header,
            is_demand_profile=is_demand_profile,
        )


def treat_multiple_flows(dict_asset, dict_values, parameter):
    """
    This function consider the case a technical parameter on the json file has a list of values because multiple
    inputs or outputs busses are considered.
    Parameters
    ----------
    dict_values:
    dictionary of current values of the asset
    parameter:
    usually efficiency. Different efficiencies will be given if an asset has multiple inputs or outputs busses,
    so a list must be considered.

    Returns
    -------

    """
    updated_values = []
    values_info = (
        []
    )  # filenames and headers will be stored to allow keeping track of the timeseries generation
    for element in dict_asset[parameter][VALUE]:
        if isinstance(element, dict):
            updated_values.append(
                get_timeseries_multiple_flows(
                    dict_values[SIMULATION_SETTINGS],
                    dict_asset,
                    element[FILENAME],
                    element[HEADER],
                )
            )
            values_info.append(element)
        else:
            updated_values.append(element)
    dict_asset[parameter][VALUE] = updated_values
    if len(values_info) > 0:
        dict_asset[parameter].update({"values_info": values_info})

    return


# reads timeseries specifically when the need comes from a multiple or output busses situation
# returns the timeseries. Does not update any dictionary
def get_timeseries_multiple_flows(settings, dict_asset, file_name, header):
    """

    Parameters
    ----------
    dict_asset:
    dictionary of the asset
    file_name:
    name of the file to read the time series
    header:
    name of the column where the timeseries is provided

    Returns
    -------

    """
    file_path = os.path.join(settings[PATH_INPUT_FOLDER], TIME_SERIES, file_name)
    verify.lookup_file(file_path, dict_asset[LABEL])

    data_set = pd.read_csv(file_path, sep=",")
    if len(data_set.index) == settings[PERIODS]:
        return pd.Series(data_set[header].values, index=settings[TIME_INDEX])
    elif len(data_set.index) >= settings[PERIODS]:
        return pd.Series(
            data_set[header][0 : len(settings[TIME_INDEX])].values,
            index=settings[TIME_INDEX],
        )
    elif len(data_set.index) <= settings[PERIODS]:
        logging.critical(
            "Input error! "
            "Provided timeseries of %s (%s) shorter then evaluated period. "
            "Operation terminated",
            dict_asset[LABEL],
            file_path,
        )
        sys.exit()


def add_maximum_cap(dict_values, group, asset, subasset=None):
    """
    Checks if maximumCap is in the csv file and if not, adds it to the dict

    Parameters
    ----------
    dict_values: dict
        dictionary of all assets
    asset: str
        asset name
    subasset: str
        subasset name

    Returns
    -------

    """
    if subasset is None:
        dict = dict_values[group][asset]
    else:
        dict = dict_values[group][asset][subasset]
    if MAXIMUM_CAP in dict:
        # check if maximumCap is greater that installedCap
        if dict[MAXIMUM_CAP][VALUE] is not None:
            if dict[MAXIMUM_CAP][VALUE] < dict[INSTALLED_CAP][VALUE]:

                logging.warning(
                    f"The stated maximumCap in {group} {asset} is smaller than the "
                    "installedCap. Please enter a greater maximumCap."
                    "For this simulation, the maximumCap will be "
                    "disregarded and not be used in the simulation"
                )
                dict[MAXIMUM_CAP][VALUE] = None
            # check if maximumCao is 0
            elif dict[MAXIMUM_CAP][VALUE] == 0:
                logging.warning(
                    f"The stated maximumCap of zero in {group} {asset} is invalid."
                    "For this simulation, the maximumCap will be "
                    "disregarded and not be used in the simulation."
                )
                dict[MAXIMUM_CAP][VALUE] = None
    else:
        dict.update({MAXIMUM_CAP: {VALUE: None, UNIT: dict[UNIT]}})
