import pandas as pd
import pytest

from water_balance import daily_et, on_schedule, soil_check, sun_energy, when_dry


def test_sun_energy_book_example():
    # FAO-56 example 8
    assert sun_energy(246, -20) == pytest.approx(32.2, abs=0.05)


def test_daily_et_by_hand():
    # 86F/68F, energy 40
    assert daily_et(86, 68, 40) == pytest.approx(0.200, abs=0.001)
    # no spread
    assert daily_et(70, 70, 40) == 0


def make_season(rain, loss):
    dates = pd.date_range("2024-04-01", periods=len(rain))
    return pd.DataFrame({"date": dates, "rain_in": rain, "water_loss_in": loss})


def test_soil_rule():
    # dry, dry, dry, dry, storm, dry
    season = make_season([0, 0, 0, 0, 1.0, 0], [0.2] * 6)
    applied, wasted, dry_days, watered = soil_check(season, when_dry)
    assert [d.day for d in watered] == [3]
    assert applied == pytest.approx(0.5)
    assert wasted == pytest.approx(0)
    assert dry_days == 0


def test_fixed_schedule_waste():
    season = make_season([0, 0, 0, 0, 1.0, 0], [0.2] * 6)
    days = season["date"].iloc[[0, 4]]
    applied, wasted, dry_days, watered = soil_check(season, on_schedule(days))
    assert applied == pytest.approx(1.0)
    # 0.3 day 1, 0.5 day 5
    assert wasted == pytest.approx(0.8)
    assert dry_days == 0


def test_dry_days():
    season = make_season([0] * 5, [0.3] * 5)
    assert soil_check(season, on_schedule([]))[2] == 2


def test_edges():
    # exact quarters
    season = make_season([0] * 6, [0.25] * 6)
    assert [d.day for d in soil_check(season, when_dry)[3]] == [2, 4, 6]

    # watered when full
    applied, wasted, dry_days, watered = soil_check(season, on_schedule(season["date"].iloc[[0]]))
    assert wasted == pytest.approx(0.25)
    assert dry_days == 1
