import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from rain_skip import load_data, recent_rain, rule_days, timer_days
from water_balance import add_water_loss, compare


def main():
    data = load_data()
    timer = timer_days(data)
    timer["after_rain"] = timer.apply(recent_rain, axis=1)

    years = sorted(timer["date"].dt.year.unique())
    timer_count = timer.groupby(timer["date"].dt.year).size()
    percent = timer.groupby(timer["date"].dt.year)["after_rain"].mean() * 100

    # chart 1
    plt.figure(figsize=(8, 4))
    plt.bar(years, percent, color="#4a7fb5")
    plt.title("Timer waterings that came right after real rain (Charlotte, Apr-Oct)")
    plt.ylabel("% of timer waterings")
    plt.xticks(years)
    plt.tight_layout()
    plt.savefig("figures/after_rain_by_year.png", dpi=150)

    # chart 2
    width = 0.4
    plt.figure(figsize=(8, 4))
    for shift, sensor, color, label in [
        (-width / 2, False, "#4a9b5f", "Past rain only"),
        (width / 2, True, "#2f6b8f", "Knows today's rain"),
    ]:
        rule = rule_days(data, sensor)
        saved = timer_count - rule.groupby(rule["date"].dt.year).size()
        plt.bar([y + shift for y in years], saved, width, color=color, label=label)
    plt.title(f"Waterings saved each season (out of {timer_count.iloc[0]} timer waterings)")
    plt.ylabel("Waterings saved")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(years)
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/waterings_saved.png", dpi=150)

    # chart 3
    results = compare(add_water_loss(data))
    names = list(results)[::-1]
    seasons_count = len(years)
    used = [(results[n][1] - results[n][2]) / seasons_count for n in names]
    wasted = [results[n][2] / seasons_count for n in names]
    plt.figure(figsize=(8, 4))
    plt.barh(names, used, color="#4a9b5f", label="Used by the lawn")
    plt.barh(names, wasted, left=used, color="#b0b0b0", label="Ran off")
    for i, (u, w) in enumerate(zip(used, wasted, strict=True)):
        plt.text(u + w + 0.4, i, f"{u + w:.1f} in", va="center")
    plt.title("Watering per season, Apr-Oct (average of 2016-2025)")
    plt.xlabel("Inches of water")
    plt.xlim(0, max(u + w for u, w in zip(used, wasted, strict=True)) * 1.15)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig("figures/water_used.png", dpi=150)

    print("Saved charts to figures/")


if __name__ == "__main__":
    main()
