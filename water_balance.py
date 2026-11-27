import numpy as np

# airport station
LATITUDE = 35.22

# lawn grass
CROP_FACTOR = 0.8


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
