import pandas as pd

from rain_model import simulate
from rain_skip import load_data, recent_rain, rule_days, timer_days

# test rain
RAIN = [0, 0, 0, 1.0, 0, 0, 0, 0.6, 0, 0]


def make_data(tmp_path):
    dates = list(pd.date_range("2024-04-01", periods=10)) + [pd.Timestamp("2024-11-01")]
    path = tmp_path / "days.csv"
    pd.DataFrame({"date": dates, "rain_in": RAIN + [0]}).to_csv(path, index=False)
    return load_data(path)


def days(frame):
    return [d.day for d in frame["date"]]


def test_timer(tmp_path):
    timer = timer_days(make_data(tmp_path))
    assert days(timer) == [1, 4, 7, 10]
    assert list(timer.apply(recent_rain, axis=1)) == [False, False, False, True]


def test_past_rain_only(tmp_path):
    # storm day
    assert days(rule_days(make_data(tmp_path))) == [1, 4, 7]


def test_knows_today(tmp_path):
    assert days(rule_days(make_data(tmp_path), sensor=True)) == [1, 7]


def test_model_waits(tmp_path):
    data = make_data(tmp_path)
    data["rain_tomorrow"] = (data["rain_in"].shift(-1) >= 0.5).astype(int)
    season = data[data["date"].dt.month == 4].copy()
    season["chance"] = 0.0
    assert simulate(season, 0.5) == (2, 0, 0)

    # good wait
    season.loc[season["date"].dt.day == 7, "chance"] = 0.9
    assert simulate(season, 0.5) == (1, 1, 0)

    # bad wait
    season.loc[season["date"].dt.day == 1, "chance"] = 0.9
    assert simulate(season, 0.5) == (1, 2, 1)


def test_march_lookback(tmp_path):
    # rain Mar 31
    dates = pd.date_range("2024-03-30", periods=8)
    rain = [0, 0.8, 0, 0, 0, 0, 0, 0]
    path = tmp_path / "march.csv"
    pd.DataFrame({"date": dates, "rain_in": rain}).to_csv(path, index=False)
    data = load_data(path)

    timer = timer_days(data)
    assert days(timer) == [1, 4]
    assert list(timer.apply(recent_rain, axis=1)) == [True, False]
    assert days(rule_days(data)) == [3, 6]
    assert days(rule_days(data, sensor=True)) == [3, 6]
