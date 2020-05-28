# from .constants import JSON_PATH
import src.E1_process_results as E1

# Note: test functions might be summed up in classes..


def test_get_timeseries_per_bus_one_bus():
    pass
    # check updated dict_values


def test_get_timeseries_per_bus_three_busses():
    pass


def test_get_storage_results_optimize():
    pass
    # check dict_asset updated. updated are for all functions:
    # charging_power (see add_info_flow,),
    #  discharging_power (see add_info_flow,),
    #  capacity, (see add_info_flow),
    # timeseries_soc

    # additionally only optimize is true. (false: 0 is added as optimizedAddCap)
    #  optimizedAddCap of charging_power, discharging_power and capacity


def test_get_storage_results_no_optimization():
    pass
    # NOTE: optimizedAddCap = 0 for no optimization


def test_get_storage_results_optimizeCap_not_in_dict_asset():
    pass
    # optimizedAddCap not added to dict_asset


def test_get_results_only_input_bus_single():
    pass


def test_get_results_only_output_bus_single():
    pass


def test_get_results_input_and_output_bus_single():
    pass


def test_get_results_multiple_input_busses():
    pass


def test_get_results_multiple_output_busses():
    pass
    # check if dict_asset is updated. see add_info_flows for keys
    # check optimal capacity


def test_get_optimal_cap_optimize_input_flow_timeseries_peak_provided():
    pass


def test_get_optimal_cap_optimize_input_flow_timeseries_peak_not_provided():
    pass


def test_get_optimal_cap_optimize_output_flow():
    pass
    # check dict_asset updated with optimizedAddCap


def test_get_optimal_cap_optimize_invalid_direction_raises_value_error():
    pass


def test_get_optimal_cap_optimize_negative_time_series_peak_logging_warning():
    pass


def test_get_optimal_cap_optimize_time_series_peak_is_zero_logging_warning():
    pass


def test_get_opitmal_cap_no_optimization():
    pass
    # check dict_asset updated with optimizedAddCap = 0


def test_get_optimal_cap_optimizeCap_not_in_dict_asset():
    pass
    # check that dict_asset did not change


# NOTE: I decided to not test get_flow() and add_info_flow() as they are tested by other functions extensively.
#       Please comment if you are of another opinion.

# def test_get_flow_input():
#     pass
#
# def test_get_flow_output():
#     pass
#
# def test_get_flow_invalid_direction_raises_value_error():
#     pass
# same tests as add_info_flow() just that bus and direction is provided.
