import pytest

from water_balance import daily_et, sun_energy


def test_sun_energy_book_example():
    # FAO-56 example 8
    assert sun_energy(246, -20) == pytest.approx(32.2, abs=0.05)


def test_daily_et_by_hand():
    # 86F/68F, energy 40
    assert daily_et(86, 68, 40) == pytest.approx(0.200, abs=0.001)
    # no spread
    assert daily_et(70, 70, 40) == 0
