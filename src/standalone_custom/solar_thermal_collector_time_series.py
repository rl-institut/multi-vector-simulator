import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt

from oemof.thermal.flat_plate_collector import flat_plate_precalc

# please adapt
path_to_server = '/home/sabine/rl-institut/'

path_to_data_folder = "04_Projekte/250_E-Land/03-Projektinhalte/WP4.4_MVS/03_Pilots/03_UVTgv_Romania/02_Data_Aquisition"

# collectors to be analysed
collectors = [
    # "ST1",
    # "ST2",
    "ST3"
]

# define parameters that are not given in the csv file
temp_collector_inlet = 20  #  Collectors inlet temperature in C°.
delta_temp_n = 10  # Temperature difference between collector inlet and mean temperature.
time_zone = 'Europe/Madrid'  # todo

############### Get data - pre-processing ###############

# load dummy weather
weather = pd.read_csv("example_weather.csv")

# load collector data
# filename_collector_data = os.path.join(path_to_server, path_to_data_folder,
#                                        "2020-05-13_technical_data_UVTgV_system_solar_thermal.csv")
filename_collector_data = "/home/sabine/Schreibtisch/Offline/rl-institut/250_E-LAND/03-Projektinhalte/03_Pilots/03_UVTgv_Romania/02_Data_Aquisition/2020-05-13_technical_data_UVTgV_system_solar_thermal.csv" # offline
rename_inds = {
    "alpha_coll": 'collector_azimuth',
    "Beta": 'collector_tilt',
    "Lat": "lat",
    "Long": "long"
}
solar_collector_data = pd.read_csv(
    filename_collector_data, header=0, index_col=0,
    sep=";").dropna(how="all").reset_index().rename(
        columns={"index": "explanation"})
solar_collector_data.index = solar_collector_data["explanation"].apply(lambda x: x.split("-")[0]).str.strip()
# replace gaps with underscore and rename indices
solar_collector_data.rename(index={ind: ind.replace(" ", "_") for ind in solar_collector_data.index}, inplace=True)
solar_collector_data.rename(index=rename_inds, inplace=True)

print(solar_collector_data)

############### Calculations ###############

keep_indices = [
    'eta_0', "c_1", "c_2", 'collector_tilt', 'collector_azimuth', "lat", "long"]

for collector in collectors:
    coll_data = solar_collector_data[collector]
    coll_data_dict = coll_data[keep_indices].to_dict()

    precalc_data = flat_plate_precalc(df=weather, periods=len(weather),tz=time_zone,
                                      temp_collector_inlet=temp_collector_inlet,
                                      delta_temp_n=delta_temp_n,
                                      date_col='time',
                                      irradiance_global_col='ghi',
                                      irradiance_diffuse_col='dhi',
                                      temp_amb_col='temp_air', **coll_data_dict)

    # total collector heat (kWh)
    precalc_data['heat_kWh'] = precalc_data['collectors_heat'] * coll_data.A_coll * coll_data.Number_of_panels

print(precalc_data)

# todo
# solve time zone
# strings to ints