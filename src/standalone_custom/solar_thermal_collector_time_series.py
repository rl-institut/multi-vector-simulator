"""
This module calculates time series for solar thermal collectors using the
oemof-thermal package. For information about the model please see the documentation:
https://oemof-thermal.readthedocs.io/en/stable/solar_thermal_collector.html

Assumptions in this module:
- Collectors inlet temperature in (temp_collector_inlet) = 20°C
- Temperature difference between collector inlet and mean temperature (delta_temp_n) = 10°C
- azimuth 190°
- Losses:  heat transfer 15 %, peripheral losses 15 % storage losses 5 % --> 35 %

ERA5 weather data was downloaded for the corresponding weather data point
(ambient temperature, global and diffuse horizontal irradiance) using `era5_weather_download.py`.

"""

import pandas as pd
import os
import logging

from oemof.thermal.flat_plate_collector import flat_plate_precalc

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None

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
    "04_Projekte/250_E-Land/03-Projektinhalte/WP4.4_MVS/03_Pilots/03_UVTgv_Romania/02_Data_Aquisition/2020-07-23_solar_thermal_collector",
)


# collectors to be analysed
collectors = ["ST1", "ST2", "ST3"]

# define parameters that are not given in the csv file
temp_collector_inlet = 20  #  Collectors inlet temperature in C°.
delta_temp_n = (
    10  # Temperature difference between collector inlet and mean temperature.
)
losses = 0.35
time_zone = "Europe/Bucharest"

############### Get data - pre-processing ###############
logging.info("Necessary data is loaded and pre-processing is done.")
# load weather
weather = pd.read_csv("era5_weather_UVTgV_2018.csv", parse_dates=True).set_index("time")
weather.index = pd.to_datetime(weather.index, utc=True).tz_convert(time_zone)
weather.reset_index("time", inplace=True)

# load collector data
filename_collector_data = os.path.join(
    path_to_data_folder, "2020-06-05_technical_data_UVTgV_system_sh.csv",
)

rename_inds = {
    "alpha_coll": "collector_azimuth",
    "Beta": "collector_tilt",
    "Lat": "lat",
    "Long": "long",
}
solar_collector_data = (
    pd.read_csv(filename_collector_data, header=0, index_col=0, sep=";")
    .dropna(how="all")
    .reset_index()
    .rename(columns={"index": "explanation"})
)
solar_collector_data.index = (
    solar_collector_data["explanation"].apply(lambda x: x.split("-")[0]).str.strip()
)
# replace gaps with underscore and rename indices
solar_collector_data.rename(
    index={ind: ind.replace(" ", "_") for ind in solar_collector_data.index},
    inplace=True,
)
solar_collector_data.rename(index=rename_inds, inplace=True)


############### Calculations ###############
logging.info("The collector's heat is calculated.")
keep_indices = [
    "eta_0",
    "c_1",
    "c_2",
    "collector_tilt",
    "collector_azimuth",
    "lat",
    "long",
]

heat_kwh_df = pd.DataFrame()
for collector in collectors:
    coll_data = solar_collector_data[collector]
    coll_data_dict = coll_data[keep_indices].apply(float).to_dict()
    precalc_data = flat_plate_precalc(
        df=weather,
        periods=len(weather),
        tz=time_zone,
        temp_collector_inlet=temp_collector_inlet,
        delta_temp_n=delta_temp_n,
        date_col="time",
        irradiance_global_col="ghi",
        irradiance_diffuse_col="dhi",
        temp_amb_col="temp_air",
        **coll_data_dict,
    )

    # total collector heat (kWh)
    precalc_data["heat_kWh"] = (
        precalc_data["collectors_heat"]
        * float(coll_data.A_coll)
        * float(coll_data.Number_of_panels)
        / 1000
    )

    # save precalc data to file and collectors heat to heat df
    filename_precalc = os.path.join(
        path_to_results_folder, f"solar_thermal_precal_data_{collector}.csv",
    )
    precalc_data.to_csv(filename_precalc)

    # apply losses and add to data frame
    heat_kwh = precalc_data["heat_kWh"] * (1 - losses)
    heat_kwh_df = pd.concat([heat_kwh_df, heat_kwh], axis=1).rename(
        columns={"heat_kWh": f"heat_kWh_{collector}"}
    )

    coll_area = float(coll_data.A_coll) * float(coll_data.Number_of_panels)

    print(collector)
    print(f"Total collector's heat: {round(heat_kwh.sum(), 2)} kWh")
    print(f"Collector's heat per m2: {round(heat_kwh.sum() / coll_area, 2)} kWh/m2")


# save collectors heat df to file
filename_collector_data = os.path.join(
    path_to_results_folder, f"solar_thermal_collectors_heat.csv"
)
heat_kwh_df.to_csv(filename_collector_data)

if plt:
    fig, ax = plt.subplots()
    heat_kwh_df.plot(ax=ax)
    plt.xlabel("time")
    plt.ylabel("collector's heat in kWh")
    plt.show()
