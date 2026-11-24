import pandas as pd

DATA_FILE = "data/charlotte_daily_2016_2025.csv"

# settings
SEASON_START = 4    # April
SEASON_END = 10     # October
WATER_EVERY = 3     # days
RAIN_LIMIT = 0.5    # inches
LOOKBACK = 2        # days


def load_data():
    data = pd.read_csv(DATA_FILE, parse_dates=["date"])
    # biggest rain
    recent = [data["rain_in"].shift(i) for i in range(1, LOOKBACK + 1)]
    data["rain_recent"] = pd.concat(recent, axis=1).max(axis=1).fillna(0)
    return data


def seasons(data):
    months = data["date"].dt.month.between(SEASON_START, SEASON_END)
    in_season = data[months]
    return [season for _, season in in_season.groupby(in_season["date"].dt.year)]


def recent_rain(row):
    return row["rain_recent"] >= RAIN_LIMIT


def timer_days(data):
    return pd.concat([season.iloc[::WATER_EVERY] for season in seasons(data)])


def rule_days(data, sensor=False):
    days = []
    for season in seasons(data):
        since = WATER_EVERY  # first watering
        for _, row in season.iterrows():
            wet = recent_rain(row)
            if sensor:
                wet = wet or row["rain_in"] >= RAIN_LIMIT
            if since >= WATER_EVERY and not wet:
                days.append(row)
                since = 0
            since += 1
    return pd.DataFrame(days)


def main():
    data = load_data()
    timer = timer_days(data)
    timer["after_rain"] = timer.apply(recent_rain, axis=1)

    per_year = timer.groupby(timer["date"].dt.year)["after_rain"].agg(["count", "sum"])
    per_year.columns = ["waterings", "after_rain"]
    per_year["percent"] = (per_year["after_rain"] / per_year["waterings"] * 100).round(1)

    total = len(timer)
    wasted = int(timer["after_rain"].sum())
    print(f"Timer: water every {WATER_EVERY} days, months {SEASON_START}-{SEASON_END}")
    print(f"Counted as after rain: a day with {RAIN_LIMIT}+ in during the {LOOKBACK} days before\n")
    print(per_year.to_string())
    print(f"\nTotal: {wasted} of {total} waterings came right after rain ({wasted / total * 100:.1f}%)")

    # rain-aware rules
    print(f"\nRules: water every {WATER_EVERY}+ days, but skip after {RAIN_LIMIT}+ in of rain")
    for name, sensor in [("past rain only", False), ("knows today's rain", True)]:
        rule = rule_days(data, sensor)
        saved = total - len(rule)
        stormy = int((rule["rain_in"] >= RAIN_LIMIT).sum())
        print(f"  {name:<19} {len(rule)} waterings, saves {saved} ({saved / total * 100:.1f}%), "
              f"{stormy} on days with {RAIN_LIMIT}+ in")


if __name__ == "__main__":
    main()
