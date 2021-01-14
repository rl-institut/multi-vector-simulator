"""
Exceptions of the MVS
=====================
"""


class MissingParameterError(ValueError):
    """Exception raised for missing parameters of a csv input file."""

    pass


class WrongParameterWarning(UserWarning):
    """Exception raised for errors in the parameters of a csv input file."""

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
    """Exception raised in case an label is defined multiple times as Oemof requires labels to be unique"""

    pass
