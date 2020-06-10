"""
This module calculates heat demand time series using oemof demandlib.

Installation requirements:
demandlib==0.1.6
importlib==1.0.4
pkgutil==
inspect
sys
workalendar==8.1.0


optionally (for working hours shift):
pvcompare

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

# path_to_data_folder = "04_Projekte/250_E-Land/03-Projektinhalte/WP4.4_MVS/03_Pilots/03_UVTgv_Romania/02_Data_Aquisition"
path_to_results_folder = "04_Projekte/250_E-Land/03-Projektinhalte/WP4.4_MVS/03_Pilots/03_UVTgv_Romania/02_Data_Aquisition/heat_demand"

time_zone = "Europe/Berlin"  # todo

### parameters ###
year = 2020
profile_type = "GKO"  # BDEW profile type
country = "Romania"  # needed for holiday detection
hour_shift = True  # If True: The load profile is shifted due to countrys specific behaviour - for more information see https://github.com/greco-project/pvcompare/blob/bc4425abaf3f4957e3aa68dbe7cbeffb3d530719/pvcompare/demand.py#L330
# heat demand from natural gas consumption
gas_consumption = 179578.24  # in kWh
efficiency_gas_boiler = 0.954  # email from UVTgV
annual_demand = gas_consumption * efficiency_gas_boiler  # in kWh

filename_heat_demand = os.path.join(
    path_to_server, path_to_results_folder, "heat_demand.csv"
)


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

    # load dummy weather
    weather = pd.read_csv("example_weather.csv", parse_dates=True).set_index(
        "time")
    weather.index = pd.to_datetime(weather.index, utc=True).tz_convert(
        time_zone)
    weather.reset_index("time", inplace=True)

    demand = calculate_heat_demand_time_series(
        year=year,
        annual_demand=annual_demand,
        ambient_temperature=weather["temp_air"],
        profile_type=profile_type,
        country=country,
        # filename=filename_heat_demand,
        frequency="H",
        hour_shift=hour_shift,
    )

    print(demand.head())

    if plots and plt:
        folder = os.path.join(path_to_server, path_to_results_folder, "plots")
        # year
        fig = plt.figure()
        demand.plot()
        plt.xlabel("time")
        plt.ylabel("heat demand in kWh")
        # plt.show()
        # fig.savefig(os.path.join(folder, "heat_demand_year.pdf"))
        # only January
        plt.xlim([demand.index[0], demand.index[24*31 - 1]])
        fig.savefig(os.path.join(folder, "heat_demand_year_january.pdf"))

        # sum in January - annual heat demand calc
        sum_jan = demand.iloc[0:24*31].sum()


        # calculate heat demand of only January:
        annual_demand_jan = 45630.42 * efficiency_gas_boiler  # kWh
        demand_jan = calculate_heat_demand_time_series(
            year=year,
            annual_demand=annual_demand_jan,
            ambient_temperature=weather["temp_air"].iloc[0:24*31],
            profile_type=profile_type,
            country=country,
            # filename=filename_heat_demand,
            frequency="H",
            hour_shift=hour_shift,
        )

        fig = plt.figure()
        demand_jan.plot()
        plt.xlabel("time")
        plt.ylabel("heat demand in kWh")
        # plt.show()
        # fig.savefig(os.path.join(folder, "heat_demand_year.pdf"))
        # only January
        plt.xlim([demand_jan.index[0], demand_jan.index[24 * 31 - 1]])
        fig.savefig(os.path.join(folder, "heat_demand_single_january.pdf"))

        # sum in January - only monthly calc
        sum_jan_single = demand_jan.sum()

        print(f"Demand January yearly calc: {round(sum_jan, 2)} kWh \nDemand January single calc: {round(sum_jan_single, 2)} kWh")

        print(f"January yearly calc: Min: {round(demand.min(), 2)} Max: {round(demand.max(), 2)} Diff: {round(demand.max()-demand.min(), 2)}\n"
              f"January monthly calc: Min: {round(demand_jan.min(), 2)} Max: {round(demand_jan.max(),2)} Diff: {round(demand_jan.max()-demand_jan.min(), 2)}")

        # check for July