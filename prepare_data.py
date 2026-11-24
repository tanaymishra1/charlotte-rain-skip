import pandas as pd

RAW_FILE = "data/USW00013881.csv"
OUT_FILE = "data/charlotte_daily_2016_2025.csv"

raw = pd.read_csv(RAW_FILE, low_memory=False, parse_dates=["DATE"])
raw = raw[(raw["DATE"] >= "2016-01-01") & (raw["DATE"] <= "2025-12-31")]

# unit conversions
data = pd.DataFrame()
data["date"] = raw["DATE"].dt.date
data["rain_in"] = (raw["PRCP"] / 254).round(2)
data["tmax_f"] = (raw["TMAX"] / 10 * 9 / 5 + 32).round(1)
data["tmin_f"] = (raw["TMIN"] / 10 * 9 / 5 + 32).round(1)
data["wind_mph"] = (raw["AWND"] / 10 * 2.23694).round(1)
data["humidity_pct"] = raw["RHAV"]
data["pressure_hpa"] = (raw["ASLP"] / 10).round(1)
data["dewpoint_f"] = (raw["ADPT"] / 10 * 9 / 5 + 32).round(1)

data.to_csv(OUT_FILE, index=False)
print(f"Saved {len(data)} days to {OUT_FILE}")
