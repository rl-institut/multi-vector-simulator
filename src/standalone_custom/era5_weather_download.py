"""
This module provides a download of ERA5 weather data for a single
weather data point (coordinate) and the conversion into the format needed by pvlib.
For downloading a region see
http://localhost:8888/notebooks/load_era5_weather_data.ipynb for information.
For downloading ERA5 weather data you need an account at CDS, see above mentioned link or
https://cds.climate.copernicus.eu/api-how-to for an instruction on how to get
the account and install cdsapi.

This modules requires the following installations:
feedinlib==0.1.0rc2
cdsapi
"""

import xarray as xr
import os
from feedinlib import era5


latitude, longitude = 44.943507, 25.457978
location = "UVTgV"  # only used for file name
year = 2019

# set start and end date (end date will be included)
start_date, end_date = f"{year}-01-01", f"{year}-12-31"

# output filename for weather data (csv)
output_filename = f"era5_weather_{location}_{year}.csv"

# filename of downloaded data
era5_netcdf_filename = f"ERA5_pvlib_{year}.nc"

# set variable set to download ("pvlib" or "windpowerlib")
variable = "pvlib"

# get pvlib weather data for specified location (only if not already downloaded)
if not os.path.isfile(era5_netcdf_filename):
    era5.get_era5_data_from_datespan_and_position(
        variable=variable,
        start_date=start_date,
        end_date=end_date,
        latitude=latitude,
        longitude=longitude,
        target_file=era5_netcdf_filename,
    )


# # import downloaded data
# ds = xr.open_dataset(era5_netcdf_filename)

# transform to pvlib format
pvlib_df = era5.weather_df_from_era5(
    era5_netcdf_filename=era5_netcdf_filename, lib="pvlib", area=[latitude, longitude]
)

print(pvlib_df.head())

# save to file
pvlib_df.to_csv(output_filename)
