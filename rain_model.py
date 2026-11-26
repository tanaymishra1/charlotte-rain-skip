import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import TimeSeriesSplit, cross_val_score

from rain_skip import RAIN_LIMIT, WATER_EVERY, load_data, recent_rain, seasons

TRAIN_END = 2022    # train cutoff
CHANCES = [1.0, 0.3, 0.2, 0.1]  # wait cutoffs

FEATURES = [
    "rain_in", "tmax_f", "tmin_f", "temp_range", "wind_mph", "humidity_pct",
    "pressure_hpa", "pressure_change", "dewpoint_f", "month", "rain_3day",
]


def add_features(data):
    data["temp_range"] = data["tmax_f"] - data["tmin_f"]
    data["pressure_change"] = data["pressure_hpa"].diff()
    data["month"] = data["date"].dt.month
    data["rain_3day"] = data["rain_in"].rolling(3).sum()
    data["rain_tomorrow"] = (data["rain_in"].shift(-1) >= RAIN_LIMIT).astype(int)
    return data.iloc[:-1]


def simulate(season, chance):
    waterings = 0
    waits = 0
    bad_waits = 0
    since = WATER_EVERY
    waited = False
    for _, row in season.iterrows():
        wet = recent_rain(row) or row["rain_in"] >= RAIN_LIMIT
        if row["rain_in"] >= RAIN_LIMIT:
            waited = False
        if since >= WATER_EVERY and not wet:
            if not waited and row["chance"] >= chance:
                # wait once
                waited = True
                waits += 1
                if not row["rain_tomorrow"]:
                    bad_waits += 1
            else:
                waterings += 1
                since = 0
                waited = False
        since += 1
    return waterings, waits, bad_waits


def make_model():
    return HistGradientBoostingClassifier(
        max_depth=3, learning_rate=0.05, max_iter=200, random_state=0
    )


def main():
    data = add_features(load_data())
    train = data[data["date"].dt.year <= TRAIN_END]
    test = data[data["date"].dt.year > TRAIN_END].copy()
    actual = test["rain_tomorrow"]

    # cross-validation
    folds = TimeSeriesSplit(n_splits=5)
    cv_auc = cross_val_score(
        make_model(), train[FEATURES], train["rain_tomorrow"], cv=folds, scoring="roc_auc"
    )
    print(f"5-fold time-series CV AUC (2016-2022): {cv_auc.mean():.2f} +/- {cv_auc.std():.2f}")

    model = make_model()
    model.fit(train[FEATURES], train["rain_tomorrow"])
    test["chance"] = model.predict_proba(test[FEATURES])[:, 1]
    auc = roc_auc_score(actual, test["chance"])
    print(f"Test AUC (2023-2025): {auc:.2f} (0.5 = random guessing, 1.0 = perfect)\n")

    # baselines
    rate = actual.mean()
    print(f"Days followed by {RAIN_LIMIT}+ in of rain: {rate * 100:.1f}%")
    print("Accuracy:")
    print(f"  random 50/50 guess        {50.0:.1f}%")
    print(f"  random guess at real rate {(rate ** 2 + (1 - rate) ** 2) * 100:.1f}%")
    print(f"  always 'no big rain'      {(1 - rate) * 100:.1f}%")
    for cut in [0.5, 0.3, 0.2, 0.1]:
        right = ((test["chance"] >= cut).astype(int) == actual).mean()
        print(f"  model, cutoff {cut}         {right * 100:.1f}%")

    # roc curve
    fpr, tpr, _ = roc_curve(actual, test["chance"])
    plt.figure(figsize=(5, 5))
    plt.plot(fpr, tpr, color="#4a7fb5", label=f"Model (AUC {auc:.2f})")
    plt.plot([0, 1], [0, 1], "--", color="#999999", label="Random guess (AUC 0.50)")
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.title("Predicting 0.5+ in of rain tomorrow")
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/rain_model_roc.png", dpi=150)

    # schedules
    print("\nRule that knows today's rain, waiting a day when the model expects rain (2023-2025)")
    print("Wait if chance >=   waterings   saved   waits   rain caught   extra dry days")
    baseline = None
    for chance in CHANCES:
        waterings, waits, bad_waits = 0, 0, 0
        for season in seasons(test):
            w, n, b = simulate(season, chance)
            waterings += w
            waits += n
            bad_waits += b
        if baseline is None:
            baseline = waterings  # never wait
        saved = baseline - waterings
        caught = waits - bad_waits
        label = "never" if chance >= 1 else chance
        print(f"{label:>17}   {waterings:>9}   {saved:>5}   {waits:>5}   "
              f"{caught:>11}   {bad_waits:>14}")

if __name__ == "__main__":
    main()
