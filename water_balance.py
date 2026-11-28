import numpy as np

from rain_skip import load_data, rule_days, seasons, timer_days

# airport station
LATITUDE = 35.22

# lawn grass
CROP_FACTOR = 0.8

# soil bucket, inches
WATER_AMOUNT = 0.5
REFILL_AT = 0.5
DRY_LIMIT = 1.0


def sun_energy(day, latitude):
    # FAO-56 method
    lat = np.radians(latitude)
    distance = 1 + 0.033 * np.cos(2 * np.pi * day / 365)
    tilt = 0.409 * np.sin(2 * np.pi * day / 365 - 1.39)
    sunset = np.arccos(-np.tan(lat) * np.tan(tilt))
    angle = sunset * np.sin(lat) * np.sin(tilt) + np.cos(lat) * np.cos(tilt) * np.sin(sunset)
    return 24 * 60 / np.pi * 0.0820 * distance * angle


def daily_et(tmax_f, tmin_f, energy):
    tmax = (tmax_f - 32) / 1.8
    tmin = (tmin_f - 32) / 1.8
    spread = np.sqrt(np.maximum(tmax - tmin, 0))
    # Hargreaves, in mm
    et_mm = 0.0023 * ((tmax + tmin) / 2 + 17.8) * spread * energy * 0.408
    return et_mm / 25.4


def add_water_loss(data):
    energy = sun_energy(data["date"].dt.dayofyear, LATITUDE)
    data["water_loss_in"] = daily_et(data["tmax_f"], data["tmin_f"], energy) * CROP_FACTOR
    return data


def soil_check(season, should_water):
    short = 0
    applied, wasted, dry_days = 0, 0, 0
    watered = []
    for _, row in season.iterrows():
        # rain refills
        short = max(short + row["water_loss_in"] - row["rain_in"], 0)
        if should_water(row, short):
            watered.append(row["date"])
            applied += WATER_AMOUNT
            # runs off
            wasted += max(WATER_AMOUNT - short, 0)
            short = max(short - WATER_AMOUNT, 0)
        if short > DRY_LIMIT:
            dry_days += 1
    return applied, wasted, dry_days, watered


def on_schedule(dates):
    dates = set(dates)
    return lambda row, short: row["date"] in dates


def when_dry(row, short):
    return short >= REFILL_AT


def compare(data):
    schedules = {
        "Timer": on_schedule(timer_days(data)["date"]),
        "Past rain only": on_schedule(rule_days(data)["date"]),
        "Knows today's rain": on_schedule(rule_days(data, sensor=True)["date"]),
        "Soil rule": when_dry,
    }
    results = {}
    for name, rule in schedules.items():
        waterings, applied, wasted, dry_days = 0, 0, 0, 0
        for season in seasons(data):
            a, w, d, watered = soil_check(season, rule)
            waterings += len(watered)
            applied += a
            wasted += w
            dry_days += d
        results[name] = (waterings, applied, wasted, dry_days)
    return results


def main():
    data = add_water_loss(load_data())
    in_season = seasons(data)
    years = len(in_season)
    loss = sum(season["water_loss_in"].sum() for season in in_season) / years
    rain = sum(season["rain_in"].sum() for season in in_season) / years

    print(f"Lawn water loss, Apr-Oct: {loss:.1f} in per season (crop factor {CROP_FACTOR})")
    print(f"Rain, Apr-Oct: {rain:.1f} in per season")
    print(f"Each watering: {WATER_AMOUNT} in. Soil rule waters when {REFILL_AT} in short.")
    print(f"Dry day: soil more than {DRY_LIMIT} in short\n")

    results = compare(data)
    timer_applied = results["Timer"][1]
    print("Schedule             waterings   applied   wasted   dry days   vs timer")
    for name, (waterings, applied, wasted, dry_days) in results.items():
        less = "" if name == "Timer" else f"{(1 - applied / timer_applied) * 100:.1f}% less"
        print(f"{name:<19}  {waterings:>9}   {applied:>7.1f}   {wasted:>6.1f}   "
              f"{dry_days:>8}   {less}")
    print(f"\n2016-2025, {years} seasons. Water amounts in inches.")


if __name__ == "__main__":
    main()
