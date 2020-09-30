import logging
from mvs_eland.utils.constants_json_strings import (
    CONSTRAINTS,
    MINIMAL_RENEWABLE_SHARE,
    VALUE,
    KPI,
    KPI_SCALARS_DICT,
    RENEWABLE_SHARE,
)


def minimal_renewable_share_test(dict_values):
    r"""
    Test if renewable share constraint was correctly applied

    Parameters
    ----------
    dict_values

    Returns
    -------
    Nothing

    - Nothing if the constraint is confirmed
    - Prints logging.warning message if the deviation from the constraint is 10^-6.
    - Prints a logging.error message if the deviation from the constraint is >10^-6.

    """
    if dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_SHARE][VALUE] > 0:
        boolean_test = (
            dict_values[KPI][KPI_SCALARS_DICT][RENEWABLE_SHARE]
            >= dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_SHARE][VALUE]
        )
        if boolean_test is False:
            deviation = (
                dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_SHARE][VALUE]
                - dict_values[KPI][KPI_SCALARS_DICT][RENEWABLE_SHARE]
            ) / dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_SHARE][VALUE]
            if abs(deviation) < 10 ** (-6):
                logging.warning(
                    "Minimal renewable share criterion strictly not fullfilled, but deviation is less then e6."
                )
            else:
                logging.error(
                    f"ATTENTION: Minimal renewable share criterion NOT fullfilled! The deviation is {round(deviation,5)}."
                )
                return False

        else:
            logging.debug(
                f"Minimal renewable share of {dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_SHARE][VALUE]} is fullfilled."
            )
    else:
        pass

    return

