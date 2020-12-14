"""
Output definition
=================

This file contains multiple lists of paramters that are written to the "scalars.xlsx" output file of the MVS.
One should simply import new KPI names from constants.py or constants_json_strings.py
and add them to the list to make them appear in the excel output sheet "scalars".
"""

from multi_vector_simulator.utils.constants import (
    COST_TOTAL,
    COST_OPERATIONAL_TOTAL,
    COST_INVESTMENT,
    COST_UPFRONT,
    COST_REPLACEMENT,
    COST_DISPATCH,
    COST_OM,
    ANNUITY_TOTAL,
    ANNUITY_OM,
    UNIT,
    LCOE_ASSET,
    INSTALLED_CAP,
    OPTIMIZED_ADD_CAP,
    TOTAL_FLOW,
    ANNUAL_TOTAL_FLOW,
    PEAK_FLOW,
    AVERAGE_FLOW,
    TOTAL_EMISSIONS,
)

from multi_vector_simulator.utils.constants_json_strings import LABEL

######################
# Tab "cost_matrix"  #
######################
KPI_COST_MATRIX_ENTRIES = [
    LABEL,
    COST_TOTAL,
    COST_OPERATIONAL_TOTAL,
    COST_INVESTMENT,
    COST_UPFRONT,
    COST_REPLACEMENT,
    COST_DISPATCH,
    COST_OM,
    ANNUITY_TOTAL,
    ANNUITY_OM,
    LCOE_ASSET,
]

########################
# Tab "scalar_matrix"  #
########################

KPI_SCALAR_MATRIX_ENTRIES = [
    LABEL,
    UNIT,
    INSTALLED_CAP,
    OPTIMIZED_ADD_CAP,
    TOTAL_FLOW,
    ANNUAL_TOTAL_FLOW,
    PEAK_FLOW,
    AVERAGE_FLOW,
    TOTAL_EMISSIONS,
]
##################
# Tab "scalars"  #
##################

#############################
# KPI "individual_sectors"  #
#############################
