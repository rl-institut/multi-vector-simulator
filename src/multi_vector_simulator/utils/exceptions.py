"""
Exceptions of the MVS
=====================
"""


class MVSOemofError(ValueError):
    """Exception raised for missing parameters of a csv input file."""


class WrongOemofAssetForGroupError(ValueError):
    """Exception raised when an asset group has an asset with an denied oemof type"""

    pass


class UnknownOemofAssetType(ValueError):
    """Exception raised in case an asset type is defined for an asset group constants_json_strings but the oemof function is not yet defined (only dev)"""

    pass


class MissingCsvEndingError(ValueError):
    """Exeption raised if the filename of a storage input file in energyStorage.csv misses the suffix '.csv'."""

    pass


class MissingParameterError(ValueError):
    """Exception raised for missing parameters of a csv input file."""

    pass


class CsvParsingError(ValueError):
    """Exception raised for errors in the parameters of a csv input file."""

    pass


class WrongStorageColumn(ValueError):
    """Exception raised for wrong column name in "storage_xx" input file."""

    pass


class InvalidPeakDemandPricingPeriodsError(ValueError):
    """Exeption if an input is not valid"""

    pass


class UnknownEnergyVectorError(ValueError):
    """Exception if an energy carrier is not in DEFAULT_WEIGHTS_ENERGY_CARRIERS"""

    pass


class DuplicateLabels(ValueError):
    """Exception raised in case a label is defined multiple times as Oemof requires labels to be unique"""

    pass


class MaximumCapValueInvalid(ValueError):
    """Exception raised if the defined maximum capacity of an asset is invalid"""

    pass
