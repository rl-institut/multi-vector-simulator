"""
This module gathers all constraints that can be added to the MVS optimisation. 
we will probably require another input CSV file or further parameters in simulation_settings.

Future constraints are discussed in issue #133 (https://github.com/rl-institut/mvs_eland/issues/133)

constraints should be tested in-code (examples) and by comparing the lp file generated.
"""
import logging


def modelling_constraints():
    logging.info("No modelling constraint to be introduced.")
    return
