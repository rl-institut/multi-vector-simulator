import mvs_eland.E4_verification as E4

from mvs_eland.utils.constants_json_strings import (
    CONSTRAINTS,
    MINIMAL_RENEWABLE_SHARE,
    VALUE,
    KPI,
    KPI_SCALARS_DICT,
    RENEWABLE_SHARE,
)


def test_minimal_renewable_share_test_passes():
    # No minimal renewable share
    dict_values = {CONSTRAINTS: {MINIMAL_RENEWABLE_SHARE: {VALUE: 0}}}
    E4.minimal_renewable_share_test(dict_values)
    # Min res < res
    dict_values = {
        CONSTRAINTS: {MINIMAL_RENEWABLE_SHARE: {VALUE: 0.2}},
        KPI: {KPI_SCALARS_DICT: {RENEWABLE_SHARE: 0.3}},
    }
    E4.minimal_renewable_share_test(dict_values)
    # Min res < res, minimal deviation
    dict_values = {
        CONSTRAINTS: {MINIMAL_RENEWABLE_SHARE: {VALUE: 0.2}},
        KPI: {KPI_SCALARS_DICT: {RENEWABLE_SHARE: 0.2 - 10 ** (-7)}},
    }
    E4.minimal_renewable_share_test(dict_values)


def test_minimal_renewable_share_test_fails():
    dict_values = {
        CONSTRAINTS: {MINIMAL_RENEWABLE_SHARE: {VALUE: 0.2}},
        KPI: {KPI_SCALARS_DICT: {RENEWABLE_SHARE: 0.2 - 10 ** (-5)}},
    }
    return_value = E4.minimal_renewable_share_test(dict_values)
    assert return_value == False


