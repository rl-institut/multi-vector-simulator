'''
This file contains multiple lists of paramters that are written to the "scalars.xlsx" output file of the MVS.
One should simply import new KPI names from constants.py or constants_json_strings.py
and add them to the list to make them appear in the excel output sheet "scalars".
'''

from src.constants import (
    COST_TOTAL,
    COST_OM_TOTAL,
    COST_INVESTMENT,
    COST_UPFRONT,
    COST_DISPATCH,
    COST_OM_FIX,
    ANNUITY_TOTAL,
    ANNUITY_OM,
    LCOE_ASSET,
    INSTALLED_CAP,
    OPTIMIZED_ADD_CAP,
    TOTAL_FLOW,
    ANNUAL_TOTAL_FLOW,
"peak_flow",
"average_flow",
)

from src.constants_json_strings import LABEL
######################
# Tab "cost_matrix"  #
######################
KPI_COST_MATRIX_ENTRIES = [
    LABEL,
    COST_TOTAL,
    COST_OM_TOTAL,
    COST_INVESTMENT,
    COST_UPFRONT,
    COST_DISPATCH,
    COST_OM_FIX,
    ANNUITY_TOTAL,
    ANNUITY_OM,
    LCOE_ASSET

]
########################
# Tab "scalar_matrix"  #
########################

KPI_SCALAR_MATRIX_ENTRIES = [
    LABEL,
    INSTALLED_CAP,
    OPTIMIZED_ADD_CAP,
    TOTAL_FLOW,
    ANNUAL_TOTAL_FLOW,
    "peak_flow",
    "average_flow",
]
##################
# Tab "scalars"  #
##################

#############################
# KPI "individual_sectors"  #
#############################