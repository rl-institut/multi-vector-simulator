import pandas as pd

from src.constants_json_strings import *

VALID_INTERVAL = "Valid interval"
VALID_TYPE = "Valid type"
PARAMETER_EXAMPLE = "Example"
PARAMETER_DEFINITION = "Definition"
DEFAULT = "Default value"
def extend_definitions(parameter_definitions, parameter, valid_interval, valid_type, example, definition, default):

    dict_parameter = {
        parameter: {VALID_INTERVAL: valid_interval,
                    VALID_TYPE: valid_type,
                    PARAMETER_EXAMPLE: example,
                    PARAMETER_DEFINITION: definition,
                    DEFAULT: default}
    }
    parameter_definitions = parameter_definitions.append(pd.DataFrame.from_dict(dict_parameter))
    return parameter_definitions

parameter_definitions = pd.DataFrame(
    columns=[LABEL, VALID_INTERVAL, VALID_TYPE, PARAMETER_EXAMPLE, PARAMETER_DEFINITION, DEFAULT])

extend_definitions(parameter_definitions,
                   parameter=UNIT,
                   definition="Unit of a paramter",
                   valid_interval=None,
                   valid_type= str(),
                   example="kW",
                   default="kW"
                   )

extend_definitions(parameter_definitions,
                   parameter=VALUE,
                   definition="Value of a parameter, can be of different types",
                   valid_interval=None,
                   valid_type= None,
                   example="float",
                   default=None
                   )

extend_definitions(parameter_definitions,
                   parameter=CURR,
                   definition="Currency to be used in the simulation report",
                   valid_interval=None,
                   valid_type= str(),
                   example="Euro",
                   default="Euro"
                   )

extend_definitions(parameter_definitions,
                   parameter=DISCOUNTFACTOR,
                   definition="Discount factor to be used for the economic evaluation",
                   valid_interval=[0,1],
                   valid_type= float(),
                   example=0.1,
                   default=0.1
                   )


extend_definitions(parameter_definitions,
                   parameter=LABEL,
                   definition="Label of an asset",
                   valid_interval=None,
                   valid_type= str(),
                   example="Asset 1",
                   default=None # this means that the asset name is required and a simulation does not run though without
                   )

extend_definitions(parameter_definitions,
                   parameter=TAX,
                   definition="Tax added on top of all costs (OM, investment, expenses)",
                   valid_interval=[0,1],
                   valid_type= float(),
                   example=0.1,
                   default=0.0
                   )