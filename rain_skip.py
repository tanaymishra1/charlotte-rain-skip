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


def timer_days(data):
    days = []
    for year, season in data.groupby(data["date"].dt.year):
        season = season[season["date"].dt.month.between(SEASON_START, SEASON_END)]
        days.append(season.iloc[::WATER_EVERY])
    return pd.concat(days)


def rule_days(data):
    days = []
    for year, season in data.groupby(data["date"].dt.year):
        season = season[season["date"].dt.month.between(SEASON_START, SEASON_END)]
        since = WATER_EVERY  # first watering
        for _, row in season.iterrows():
            if since >= WATER_EVERY:
                days.append(row)
                since = 0
            if row["rain_in"] >= RAIN_LIMIT:
                since = 0
            since += 1
    return pd.DataFrame(days)


def main():
    data = load_data()
    timer = timer_days(data)
    timer["after_rain"] = timer["rain_recent"] >= RAIN_LIMIT

    per_year = timer.groupby(timer["date"].dt.year)["after_rain"].agg(["count", "sum"])
    per_year.columns = ["waterings", "after_rain"]
    per_year["percent"] = (per_year["after_rain"] / per_year["waterings"] * 100).round(1)

    total = len(timer)
    wasted = int(timer["after_rain"].sum())
    print(f"Timer: water every {WATER_EVERY} days, months {SEASON_START}-{SEASON_END}")
    print(f"Counted as after rain: a day with {RAIN_LIMIT}+ in during the {LOOKBACK} days before\n")
    print(per_year.to_string())
    print(f"\nTotal: {wasted} of {total} waterings came right after rain ({wasted / total * 100:.1f}%)")

    # rain-aware rule
    rule = rule_days(data)
    saved = total - len(rule)
    print(f"\nRule: water when it's been {WATER_EVERY}+ days since the last watering or {RAIN_LIMIT}+ in of rain")
    print(f"Rule waterings: {len(rule)} (saves {saved}, or {saved / total * 100:.1f}% of the timer's waterings)")


if __name__ == "__main__":
    main()
