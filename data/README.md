# Data

`charlotte_daily_2016_2025.csv` is daily weather for Charlotte Douglas International Airport (NOAA station USW00013881) from January 1, 2016 to December 31, 2025. It comes from NOAA's Global Historical Climatology Network daily dataset (GHCN-Daily), which is public domain.

To rebuild it, download the full station file from https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily/access/USW00013881.csv into this folder, then run `python prepare_data.py` from the main folder.

Columns:

- `date`
- `rain_in`: rain for the day, in inches
- `tmax_f`, `tmin_f`: high and low temperature, °F
- `wind_mph`: average wind speed
- `humidity_pct`: average relative humidity
- `pressure_hpa`: average sea level pressure
- `dewpoint_f`: average dew point, °F

Humidity, pressure and dew point are missing on about 1 in 10 days, so those cells are blank.
