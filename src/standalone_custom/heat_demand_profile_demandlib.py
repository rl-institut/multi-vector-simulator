"""
This module calculates heat demand time series using oemof demandlib and
BDEW profiles. See the demandlib documentation for more information:
https://demandlib.readthedocs.io/en/latest/description.html#model-description

ERA5 weather data was downloaded for the corresponding weather data point
(ambient temperature, global and diffuse horizontal irradiance) using `era5_weather_download.py`.

Installation requirements:
demandlib==0.1.6
importlib==1.0.4
sys
workalendar==8.1.0


optionally (for working hours shift):
pvcompare - install via: git@github.com:greco-project/pvcompare.git, pip install -e path/to/pvcompare

"""

import pandas as pd
import os
import logging
import sys
from pkgutil import iter_modules
import inspect
import demandlib.bdew as bdew
from importlib import import_module
import workalendar

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None

from pvcompare import demand as pvcompare_demand

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

# please adapt
path_to_server = "/home/sabine/rl-institut/"

path_to_data_folder = os.path.join(
    path_to_server,
    "04_Projekte/250_E-Land/03-Projektinhalte/WP4.4_MVS/03_Pilots/03_UVTgv_Romania/02_Data_Aquisition",
)
path_to_results_folder = os.path.join(
    path_to_server,
    "04_Projekte/250_E-Land/03-Projektinhalte/WP4.4_MVS/03_Pilots/03_UVTgv_Romania/02_Data_Aquisition/2020-07-23_heat_demand",
)

time_zone = "Europe/Bucharest"

### parameters ###
weather_data_name = "uvtgv"  # "uvtgv" is processed monitored data, "era5" is ERA5 data
year = 2018
profile_type = "GKO"  # BDEW profile type
country = "Romania"  # needed for holiday detection
hour_shift = True  # If True: The load profile is shifted due to countrys specific behaviour - for more information see https://github.com/greco-project/pvcompare/blob/bc4425abaf3f4957e3aa68dbe7cbeffb3d530719/pvcompare/demand.py#L330
# heat demand from natural gas consumption and solar thermal collector's heat
gas_consumption = 179578.24  # in kWh
efficiency_gas_boiler = 0.954  # email from UVTgV
annual_demand_gas = gas_consumption * efficiency_gas_boiler  # in kWh

# add annual collectors heat to annual demand
filename_coll = os.path.join(
    path_to_data_folder,
    "2020-06-17_solar_thermal_collector",
    "solar_thermal_collectors_heat.csv",
)
collectors_heat = pd.read_csv(filename_coll, index_col=0, header=0).sum().sum()
annual_demand = annual_demand_gas + collectors_heat  # in kWh

filename_heat_demand = os.path.join(path_to_results_folder, "heat_demand.csv")


def calculate_heat_demand_time_series(
    year,
    annual_demand,
    ambient_temperature,
    profile_type,
    country,
    start_date=[1, 1],
    filename=None,
    frequency="H",
    hour_shift=False,
):
    """
    Calculates heat demand profile for a year with oemof demandlib.

    Parameters
    ----------
    year : int
        year for which profile is calculated.
    annual_demand : float
        Annual total heat demand in kWh.
    ambient_temperature : pd.Series
        Time series of ambient temperature in °C.
    profile_type : str
        BDEW profile type, for more information see
        https://www.enwg-veroeffentlichungen.de/badtoelz/Netze/Gasnetz/Netzbeschreibung/LF-Abwicklung-von-Standardlastprofilen-Gas-20110630-final.pdf
        For different profile types than 'GKO' please see the Notes.
    country : str
        Country starting with capital letter; needed for holiday detection.
    start_date : list of ints
        Default: [1, 1].
    filename : str
        File name incl. path for saving demand. If None: not saved. Default: None.
    frequency : str
        Frequency of time series. Default: "H".
    hour_shift : bool
        If True: the load profile is shifted due to "country's specific habits".
        For this you need to install pvcompare, see https://github.com/greco-project/pvcompare#installation
        Default: False.

    Notes
    -----
    For different profile types the parameter `building_class` might have to be
    an input to `bdew.HeatBuilding()`. This is for example the case for 'MFH'.
    As for the current use case is not needed this stays an open todo
    until we need this or require a generic function.

    Returns
    -------
    demand : pd.DataFrame
        Demand time series with data in column "kWh".

    """

    # load workelendar for country
    cal = get_workalendar_class(country)
    holidays = dict(cal.holidays(int(year)))

    # Create DataFrame for demand timeseries
    demand = pd.DataFrame(
        index=pd.date_range(
            pd.datetime(int(year), start_date[0], start_date[1], 0),
            periods=ambient_temperature.count(),
            freq=frequency,
        )
    )

    # get demand profile of profile_type
    demand["h0"] = bdew.HeatBuilding(
        demand.index,
        holidays=holidays,
        temperature=ambient_temperature,
        shlp_type=profile_type,
        # building_class=2,  # needed for f.e. "MFH"
        wind_class=0,
        annual_heat_demand=annual_demand,
        name=profile_type,
    ).get_bdew_profile()

    if hour_shift == True:
        demand = pvcompare_demand.shift_working_hours(country=country, ts=demand)

    # rename column
    demand.rename(columns={"h0": "kWh"}, inplace=True)

    if filename is not None:
        demand.to_csv(filename)

    return demand


def get_workalendar_class(country):
    """
    loads workalender for a given country.

    This function was copied from pvcompare.

    Parameters
    ---------
    country: str
        name of the country

    Returns
    ------

        class of the country specific workalender

    """
    country_name = country
    for finder, name, ispkg in iter_modules(workalendar.__path__):
        module_name = "workalendar.{}".format(name)
        import_module(module_name)
        classes = inspect.getmembers(sys.modules[module_name], inspect.isclass)
        for class_name, _class in classes:
            if _class.__doc__ == country_name:
                return _class()

    return None


if __name__ == "__main__":
    plots = True

    # load weather
    if weather_data_name == "era5":
        weather = pd.read_csv(
            f"era5_weather_UVTgV_{year}.csv", parse_dates=True
        ).set_index("time")
        weather.index = pd.to_datetime(weather.index, utc=True).tz_convert(time_zone)
        weather.reset_index("time", inplace=True)
    elif weather_data_name == "uvtgv":
        filename_weather = "enter_filename_including_path"
        filename_weather = os.path.join(
            path_to_data_folder, "2020-07-23_uvtgv_weather_processed.csv"
        )
        cols = {"Amb Temp": "temp_air"}
        weather = pd.read_csv(filename_weather, parse_dates=True, index_col=0).rename(
            columns=cols
        )
        weather.index = pd.to_datetime(weather.index, utc=True).tz_convert(time_zone)
    else:
        raise ValueError(
            f"weather_data_name must be 'era5' or 'uvtgv' but is {weather_data_name}"
        )

    demand = calculate_heat_demand_time_series(
        year=year,
        annual_demand=annual_demand,
        ambient_temperature=weather["temp_air"],
        profile_type=profile_type,
        country=country,
        filename=filename_heat_demand,
        frequency="H",
        hour_shift=hour_shift,
    )

    if plots and plt:
        folder = os.path.join(path_to_results_folder, "plots")
        fig, ax = plt.subplots()
        demand.plot(ax=ax)
        plt.xlabel("time")
        plt.ylabel("heat demand in kWh")
        # plt.show()
        fig.savefig(os.path.join(folder, "heat_demand_year.pdf"))

    print(f"Annual heat demand: {round(annual_demand, 2)} kWh")
    print(f"Retrieved from gas: {round(annual_demand_gas, 2)} kWh")
    print(f"Retrieved from solar thermal heat: {round(collectors_heat, 2)} kWh")
